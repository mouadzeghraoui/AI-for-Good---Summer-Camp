"""
Cinema Simulation Tool for watsonx Orchestrate
Simulates MovieGlu API responses with realistic French cinema data
"""

import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ibm_watsonx_orchestrate.agent_builder.tools import tool

# French cinema chains and locations
FRENCH_CINEMAS = [
    {"id": 19001, "name": "Pathé Opéra", "address": "2 Boulevard des Capucines", "city": "Paris", "lat": 48.8707, "lng": 2.3322},
    {"id": 19002, "name": "UGC Ciné Cité Les Halles", "address": "7 Place de la Rotonde", "city": "Paris", "lat": 48.8606, "lng": 2.3470},
    {"id": 19003, "name": "Gaumont Champs-Élysées", "address": "66 Avenue des Champs-Élysées", "city": "Paris", "lat": 48.8704, "lng": 2.3075},
    {"id": 19004, "name": "MK2 Bibliothèque", "address": "128 Avenue de France", "city": "Paris", "lat": 48.8299, "lng": 2.3763},
    {"id": 19005, "name": "Luminor Hôtel de Ville", "address": "20 rue du Temple", "city": "Paris", "lat": 48.8586, "lng": 2.3535},
    {"id": 19006, "name": "Pathé Beaugrenelle", "address": "7 Rue Linois", "city": "Paris", "lat": 48.8470, "lng": 2.2877},
    {"id": 19007, "name": "UGC Montparnasse", "address": "83 Boulevard du Montparnasse", "city": "Paris", "lat": 48.8436, "lng": 2.3266},
    {"id": 19008, "name": "Gaumont Aquaboulevard", "address": "8 Rue du Colonel Pierre Avia", "city": "Paris", "lat": 48.8362, "lng": 2.2816},
    {"id": 19009, "name": "Pathé La Villette", "address": "30 Avenue Corentin Cariou", "city": "Paris", "lat": 48.8958, "lng": 2.3904},
    {"id": 19010, "name": "UGC Lyon Bastille", "address": "15 Rue du Faubourg Saint-Antoine", "city": "Paris", "lat": 48.8515, "lng": 2.3710},
]

# French cinema name components for realistic generation
CINEMA_CHAINS = ["Pathé", "UGC", "Gaumont", "MK2", "Luminor", "Studio", "Cinéma", "Le Grand Rex", "Espace"]
CINEMA_LOCATIONS = ["Opéra", "Bastille", "Châtelet", "République", "Nation", "Belleville", "Montmartre", "Marais", "Saint-Germain", "Beaubourg", "Halles", "Bibliothèque", "Beaugrenelle", "Villette", "Vincennes", "Neuilly", "Boulogne", "Issy", "Créteil", "Rosny"]
CINEMA_TYPES = ["", "Cinéma", "Multiplex", "IMAX", "Premium", "Digital"]

# Movie genres for random assignment
MOVIE_GENRES = [
    ["Action", "Adventure"], ["Drama", "Romance"], ["Comedy", "Family"], 
    ["Horror", "Thriller"], ["Science Fiction", "Action"], ["Animation", "Family"],
    ["Documentary"], ["Mystery", "Thriller"], ["War", "Drama"], ["Western", "Action"],
    ["Crime", "Drama"], ["Fantasy", "Adventure"], ["Biography", "Drama"], ["Music", "Drama"]
]

def generate_film_id_from_title(title: str) -> int:
    """Generate a consistent film ID from movie title"""
    # Simple hash-like function to generate consistent IDs
    hash_value = sum(ord(char) for char in title.lower())
    return 340000 + (hash_value % 9999)

def generate_cinema_name() -> str:
    """Generate a realistic French cinema name"""
    chain = random.choice(CINEMA_CHAINS)
    location = random.choice(CINEMA_LOCATIONS)
    cinema_type = random.choice(CINEMA_TYPES)
    
    if cinema_type:
        return f"{chain} {location} {cinema_type}"
    else:
        return f"{chain} {location}"

def generate_cinema_address(city: str = "Paris") -> str:
    """Generate a realistic French address"""
    street_numbers = [str(random.randint(1, 200))]
    street_types = ["Rue", "Avenue", "Boulevard", "Place", "Passage"]
    street_names = ["de la République", "du Temple", "Saint-Antoine", "de Rivoli", "des Champs-Élysées", "Montmartre", "de la Bastille", "Saint-Germain", "du Louvre", "de Belleville", "Voltaire", "Danton", "Lafayette", "Haussmann", "Faubourg"]
    
    return f"{random.choice(street_numbers)} {random.choice(street_types)} {random.choice(street_names)}"

def generate_movie_data(title: str) -> Dict[str, Any]:
    """Generate realistic movie data for any title"""
    film_id = generate_film_id_from_title(title)
    genres = random.choice(MOVIE_GENRES)
    duration = random.randint(85, 180)  # 1h25 to 3h
    
    return {
        "film_id": film_id,
        "title": title,
        "genres": genres,
        "duration": duration
    }

def generate_showtimes(date_str: str = None) -> List[Dict[str, str]]:
    """Generate realistic showtime schedule"""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Generate showtimes between 10:00 and 23:00
    base_times = ["10:30", "13:15", "16:00", "18:45", "21:30"]
    variations = ["10:00", "12:45", "15:30", "17:15", "19:00", "20:15", "22:00"]
    
    all_times = base_times + random.sample(variations, random.randint(2, 4))
    selected_times = random.sample(all_times, random.randint(3, 6))
    
    showtimes = []
    for time in sorted(selected_times):
        hour, minute = map(int, time.split(':'))
        start_time = f"{hour:02d}:{minute:02d}"
        
        # Calculate end time (add movie duration, assume 2 hours average)
        end_hour = hour + 2
        if end_hour >= 24:
            end_hour -= 24
        end_time = f"{end_hour:02d}:{minute:02d}"
        
        showtimes.append({
            "start_time": start_time,
            "end_time": end_time
        })
    
    return showtimes

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate approximate distance in miles"""
    # Simple distance calculation (not accurate, just for simulation)
    return round(((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2) ** 0.5 * 69, 2)

@tool
def search_film_by_title(title: str) -> Dict[str, Any]:
    """
    Search for a film by title (simulated - works with ANY movie title)
    
    Args:
        title: Film title to search for
    
    Returns:
        Dictionary containing film information
    """
    # Generate movie data for any title
    movie_data = generate_movie_data(title)
    
    # Generate realistic cast and director names
    first_names = ["Jean", "Marie", "Pierre", "Sophie", "Lucas", "Emma", "Antoine", "Camille", "Nicolas", "Julie"]
    last_names = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Petit", "Durand", "Leroy", "Moreau", "Simon"]
    
    cast = [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(3)]
    director = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    return {
        "status": "success",
        "film": {
            "movieglu_id": movie_data["film_id"],
            "title": movie_data["title"],
            "release_date": "2025-07-17",
            "age_rating": random.choice(["G", "PG", "PG-13", "R"]),
            "synopsis": f"An captivating {', '.join(movie_data['genres'])} film that tells the story of {title}. A masterpiece of cinema that will leave audiences on the edge of their seats.",
            "genres": movie_data["genres"],
            "cast": cast,
            "directors": [director],
            "duration_mins": movie_data["duration"],
            "images": {
                "poster": f"https://example.com/poster_{movie_data['film_id']}.jpg",
                "still": f"https://example.com/still_{movie_data['film_id']}.jpg"
            }
        },
        "alternative_titles": []
    }

@tool
def check_film_showtimes(film_id: str, date: str = "", latitude: float = 48.8566, longitude: float = 2.3522) -> Dict[str, Any]:
    """
    Check which cinemas are showing a specific film (simulated - works with ANY film ID)
    
    Args:
        film_id: Film ID to check
        date: Date in YYYY-MM-DD format (empty string for today)
        latitude: Latitude of the location (default: Paris)
        longitude: Longitude of the location (default: Paris)
    
    Returns:
        Dictionary containing cinemas showing the film
    """
    if not date or not date.strip():
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Generate movie title from film_id (reverse the hash process approximately)
    film_id_int = int(film_id)
    movie_title = f"Movie {film_id_int}"  # Fallback title
    
    # Generate random cinemas (3-6 cinemas showing the movie)
    num_cinemas = random.randint(3, 6)
    formatted_cinemas = []
    
    for i in range(num_cinemas):
        cinema_id = random.randint(20000, 29999)
        cinema_name = generate_cinema_name()
        cinema_address = generate_cinema_address()
        
        # Generate random coordinates around Paris
        lat_offset = random.uniform(-0.1, 0.1)
        lng_offset = random.uniform(-0.1, 0.1)
        cinema_lat = latitude + lat_offset
        cinema_lng = longitude + lng_offset
        
        distance = calculate_distance(latitude, longitude, cinema_lat, cinema_lng)
        
        cinema_data = {
            "id": cinema_id,
            "name": cinema_name,
            "address": cinema_address,
            "city": "Paris",
            "distance": distance,
            "showtime_count": random.randint(3, 8),
            "showtimes": generate_showtimes(date)
        }
        formatted_cinemas.append(cinema_data)
    
    # Sort by distance
    formatted_cinemas.sort(key=lambda x: x["distance"])
    
    return {
        "status": "success",
        "film": {
            "id": film_id_int,
            "title": movie_title,
            "age_rating": random.choice(["G", "PG", "PG-13", "R"])
        },
        "date": date,
        "cinemas": formatted_cinemas
    }

@tool
def find_cinemas_nearby(latitude: float = 48.8566, longitude: float = 2.3522, radius: int = 10) -> Dict[str, Any]:
    """
    Find cinemas near a specific location (simulated - generates random cinemas)
    
    Args:
        latitude: Latitude of the location (default: Paris)
        longitude: Longitude of the location (default: Paris)
        radius: Search radius in miles (default: 10)
    
    Returns:
        Dictionary containing list of nearby cinemas
    """
    # Generate 6-10 random cinemas nearby
    num_cinemas = random.randint(6, 10)
    nearby_cinemas = []
    
    for i in range(num_cinemas):
        cinema_id = random.randint(20000, 29999)
        cinema_name = generate_cinema_name()
        cinema_address = generate_cinema_address()
        
        # Generate random coordinates within radius
        angle = random.uniform(0, 2 * 3.14159)
        distance = random.uniform(0.1, radius)
        
        # Convert distance to approximate lat/lng offset
        lat_offset = distance * 0.014 * random.choice([-1, 1])  # Rough conversion
        lng_offset = distance * 0.014 * random.choice([-1, 1])
        
        cinema_lat = latitude + lat_offset
        cinema_lng = longitude + lng_offset
        
        formatted_cinema = {
            "id": cinema_id,
            "name": cinema_name,
            "address": cinema_address,
            "city": "Paris",
            "postcode": random.randint(75001, 75020),
            "distance": distance,
            "lat": cinema_lat,
            "lng": cinema_lng
        }
        nearby_cinemas.append(formatted_cinema)
    
    # Sort by distance
    nearby_cinemas.sort(key=lambda x: x["distance"])
    
    return {
        "status": "success",
        "count": len(nearby_cinemas),
        "cinemas": nearby_cinemas,
        "search_location": {
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius
        }
    }

@tool
def get_cinema_showtimes(cinema_id: str, movie_id: str = "", date: str = "") -> Dict[str, Any]:
    """
    Get showtimes for a specific cinema (simulated - generates random movies)
    
    Args:
        cinema_id: Cinema ID
        movie_id: Optional movie ID to filter showtimes (not used in simulation)
        date: Date in YYYY-MM-DD format (empty string for today)
    
    Returns:
        Dictionary containing showtimes information
    """
    if not date or not date.strip():
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Generate cinema data
    cinema_name = generate_cinema_name()
    cinema_address = generate_cinema_address()
    
    # Generate random movies playing at this cinema
    popular_movies = ["Avatar", "Dune", "Spider-Man", "Batman", "Superman", "Avengers", "Star Wars", "Jurassic Park", "Fast & Furious", "Mission Impossible", "James Bond", "Transformers", "Harry Potter", "Lord of the Rings", "The Matrix"]
    
    num_movies = random.randint(4, 8)
    films = []
    
    for i in range(num_movies):
        # Generate random movie title
        if i < len(popular_movies):
            movie_title = f"{popular_movies[i]}: {random.choice(['Revolution', 'Origins', 'Returns', 'Awakens', 'Rising', 'Legacy', 'Reborn', 'Forever', 'Unleashed', 'Destiny'])}"
        else:
            movie_title = f"Movie {random.randint(1000, 9999)}"
        
        movie_data = generate_movie_data(movie_title)
        
        film_data = {
            "id": movie_data["film_id"],
            "title": movie_data["title"],
            "age_rating": random.choice(["G", "PG", "PG-13", "R"]),
            "showtimes": generate_showtimes(date)
        }
        films.append(film_data)
    
    return {
        "status": "success",
        "cinema": {
            "id": int(cinema_id),
            "name": cinema_name,
            "address": cinema_address,
            "city": "Paris"
        },
        "date": date,
        "films": films
    }