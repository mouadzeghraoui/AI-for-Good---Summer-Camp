"""
Cinema Tool for watsonx Orchestrate
Uses MovieGlu API for cinema and showtime information
"""

import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ibm_watsonx_orchestrate.agent_builder.tools import tool

# MovieGlu API Configuration
MOVIEGLU_BASE_URL = "https://api-gate2.movieglu.com"

def get_movieglu_credentials():
    """Get MovieGlu API credentials from environment variables"""
    # Try different possible environment variable names and provide fallbacks from your .env
    credentials = {
        'client': (
            os.getenv('CLIENT') or 
            os.getenv('MOVIEGLU_CLIENT') or 
            os.getenv('client') or
            "PERS_241"  # Fallback from your .env
        ),
        'api_key': (
            os.getenv('API_KEY') or 
            os.getenv('MOVIEGLU_API_KEY') or 
            os.getenv('api_key') or
            "mZ1zYwcSGn6ayPETBsmEf1dIP9wgFRum2do95Cbu"  # Fallback from your .env
        ),
        'authorization': (
            os.getenv('AUTHORIZATION') or 
            os.getenv('MOVIEGLU_AUTHORIZATION') or 
            os.getenv('authorization') or
            "Basic UEVSU18yNDE6OFBCaHN3blZuSjlH"  # Fallback from your .env
        ),
        'territory': (
            os.getenv('TERRITORY') or 
            os.getenv('MOVIEGLU_TERRITORY') or 
            os.getenv('territory') or 
            'FR'  # Fallback from your .env
        ),
        'geolocation': (
            os.getenv('GEOLOCATION') or 
            os.getenv('MOVIEGLU_GEOLOCATION') or 
            os.getenv('geolocation') or 
            '48.8566;2.3522'  # Fallback from your .env
        )
    }
    return credentials

def get_movieglu_headers(endpoint: str) -> Dict[str, str]:
    """Generate required headers for MovieGlu API"""
    creds = get_movieglu_credentials()
    headers = {
        "client": creds['client'],
        "x-api-key": creds['api_key'],
        "authorization": creds['authorization'],
        "territory": creds['territory'],
        "api-version": "v201",
        "geolocation": creds['geolocation'],
        "device-datetime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    }
    return headers


@tool
def find_cinemas_nearby(latitude: float = 48.8566, 
                       longitude: float = 2.3522,
                       radius: int = 10) -> Dict[str, Any]:
    """
    Find cinemas near a specific location
    
    Args:
        latitude: Latitude of the location (default: Paris)
        longitude: Longitude of the location (default: Paris)
        radius: Search radius in miles (default: 10)
    
    Returns:
        Dictionary containing list of nearby cinemas
    """
    
    creds = get_movieglu_credentials()
    if not all([creds['client'], creds['api_key'], creds['authorization']]):
        return {"error": "MovieGlu API credentials not configured. Please configure the movieglu_api connection."}
    
    try:
        endpoint = "/cinemasNearby/"
        url = f"{MOVIEGLU_BASE_URL}{endpoint}"
        
        # Update geolocation in headers
        headers = get_movieglu_headers(endpoint)
        headers["geolocation"] = f"{latitude};{longitude}"
        
        params = {
            "n": 10  # Limit to 10 cinemas
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        cinemas = data.get('cinemas', [])
        
        formatted_cinemas = []
        for cinema in cinemas:
            formatted_cinema = {
                "id": cinema.get('cinema_id'),
                "name": cinema.get('cinema_name'),
                "address": cinema.get('address'),
                "city": cinema.get('city'),
                "postcode": cinema.get('postcode'),
                "distance": cinema.get('distance', 0),
                "lat": cinema.get('lat'),
                "lng": cinema.get('lng')
            }
            formatted_cinemas.append(formatted_cinema)
        
        return {
            "status": "success",
            "count": len(formatted_cinemas),
            "cinemas": formatted_cinemas,
            "search_location": {
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius
            }
        }
        
    except requests.RequestException as e:
        return {"error": f"Failed to fetch cinemas: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@tool
def get_cinema_showtimes(cinema_id: str, 
                        movie_id: str = "",
                        date: str = "") -> Dict[str, Any]:
    """
    Get showtimes for a specific cinema
    
    Args:
        cinema_id: MovieGlu cinema ID
        movie_id: Optional TMDb movie ID to filter showtimes (empty string for all movies)
        date: Date in YYYY-MM-DD format (empty string for today)
    
    Returns:
        Dictionary containing showtimes information
    """
    
    creds = get_movieglu_credentials()
    if not all([creds['client'], creds['api_key'], creds['authorization']]):
        return {"error": "MovieGlu API credentials not configured. Please configure the movieglu_api connection."}
    
    try:
        # Use today's date if not specified
        if not date or not date.strip():
            date = datetime.now().strftime("%Y-%m-%d")
        
        endpoint = "/cinemaShowTimes/"
        url = f"{MOVIEGLU_BASE_URL}{endpoint}"
        
        headers = get_movieglu_headers(endpoint)
        
        params = {
            "cinema_id": cinema_id,
            "date": date
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        cinema = data.get('cinema', {})
        films = data.get('films', [])
        
        formatted_showtimes = {
            "status": "success",
            "cinema": {
                "id": cinema.get('cinema_id'),
                "name": cinema.get('cinema_name'),
                "address": cinema.get('address'),
                "city": cinema.get('city')
            },
            "date": date,
            "films": []
        }
        
        for film in films:
            film_data = {
                "id": film.get('film_id'),
                "title": film.get('film_name'),
                "age_rating": film.get('age_rating', [{}])[0].get('rating', 'TBC'),
                "showtimes": []
            }
            
            for showtime in film.get('showings', {}).get('Standard', {}).get('times', []):
                showtime_data = {
                    "start_time": showtime.get('start_time'),
                    "end_time": showtime.get('end_time')
                }
                film_data['showtimes'].append(showtime_data)
            
            # Only add films that match the movie_id if specified
            if not movie_id.strip() or str(film.get('film_id')) == movie_id:
                formatted_showtimes['films'].append(film_data)
        
        return formatted_showtimes
        
    except requests.RequestException as e:
        return {"error": f"Failed to fetch showtimes: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@tool
def search_film_by_title(title: str) -> Dict[str, Any]:
    """
    Search for a film in MovieGlu by title to get its ID
    
    Args:
        title: Film title to search for
    
    Returns:
        Dictionary containing film information from MovieGlu
    """
    
    creds = get_movieglu_credentials()
    if not all([creds['client'], creds['api_key'], creds['authorization']]):
        return {"error": "MovieGlu API credentials not configured. Please configure the movieglu_api connection."}
    
    try:
        endpoint = "/filmLiveSearch/"
        url = f"{MOVIEGLU_BASE_URL}{endpoint}"
        
        headers = get_movieglu_headers(endpoint)
        
        params = {
            "query": title,
            "n": 5  # Limit to 5 results
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        films = data.get('films', [])
        
        if not films:
            return {
                "status": "not_found",
                "message": f"No films found matching '{title}'"
            }
        
        # Return the first match with formatted data
        film = films[0]
        
        return {
            "status": "success",
            "film": {
                "movieglu_id": film.get('film_id'),
                "title": film.get('film_name'),
                "release_date": film.get('release_dates', [{}])[0].get('release_date', 'TBA'),
                "age_rating": film.get('age_rating', [{}])[0].get('rating', 'TBC'),
                "synopsis": film.get('synopsis_long', 'No synopsis available'),
                "genres": [g.get('genre_name') for g in film.get('genres', [])],
                "cast": [c.get('cast_name') for c in film.get('cast', [])][:5],
                "directors": [d.get('director_name') for d in film.get('directors', [])],
                "duration_mins": film.get('duration_mins', 0),
                "images": {
                    "poster": film.get('images', {}).get('poster', {}).get('1', {}).get('medium', {}).get('film_image'),
                    "still": film.get('images', {}).get('still', {}).get('1', {}).get('medium', {}).get('film_image')
                }
            },
            "alternative_titles": [f.get('film_name') for f in films[1:]]  # Other potential matches
        }
        
    except requests.RequestException as e:
        return {"error": f"Failed to search for film: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@tool
def check_film_showtimes(film_id: str,
                        date: str = "",
                        latitude: float = 48.8566,
                        longitude: float = 2.3522) -> Dict[str, Any]:
    """
    Check which cinemas are showing a specific film
    
    Args:
        film_id: MovieGlu film ID
        date: Date in YYYY-MM-DD format (empty string for today)
        latitude: Latitude of the location (default: Paris)
        longitude: Longitude of the location (default: Paris)
    
    Returns:
        Dictionary containing cinemas showing the film
    """
    
    # Convert film_id to string if it's passed as integer
    film_id = str(film_id)
    
    creds = get_movieglu_credentials()
    if not all([creds['client'], creds['api_key'], creds['authorization']]):
        return {"error": "MovieGlu API credentials not configured. Please configure the movieglu_api connection."}
    
    try:
        # Use today's date if not specified
        if not date or not date.strip():
            date = datetime.now().strftime("%Y-%m-%d")
        
        endpoint = "/filmShowTimes/"
        url = f"{MOVIEGLU_BASE_URL}{endpoint}"
        
        headers = get_movieglu_headers(endpoint)
        headers["geolocation"] = f"{latitude};{longitude}"
        
        params = {
            "film_id": film_id,
            "date": date,
            "n": 10  # Limit to 10 cinemas
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        film = data.get('film', {})
        cinemas = data.get('cinemas', [])
        
        formatted_availability = {
            "status": "success",
            "film": {
                "id": film.get('film_id'),
                "title": film.get('film_name'),
                "age_rating": film.get('age_rating', [{}])[0].get('rating', 'TBC')
            },
            "date": date,
            "cinemas": []
        }
        
        for cinema in cinemas:
            cinema_data = {
                "id": cinema.get('cinema_id'),
                "name": cinema.get('cinema_name'),
                "address": cinema.get('address'),
                "city": cinema.get('city'),
                "distance": cinema.get('distance', 0),
                "showtime_count": len(cinema.get('showings', {}).get('Standard', {}).get('times', []))
            }
            formatted_availability['cinemas'].append(cinema_data)
        
        return formatted_availability
        
    except requests.RequestException as e:
        return {"error": f"Failed to check film availability: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}