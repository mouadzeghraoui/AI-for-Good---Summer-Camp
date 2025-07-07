#!/usr/bin/env python3
"""
Mock Cinema API Server for Lab
This server simulates a cinema booking system for educational purposes.
"""

from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import random
import uuid
import json
from typing import Dict, List, Any

app = Flask(__name__)

# Mock database
MOVIES = [
    {
        "id": "m001",
        "title": "The Quantum Paradox",
        "genre": ["Sci-Fi", "Thriller"],
        "rating": "PG-13",
        "duration": 148,
        "releaseDate": "2024-01-15",
        "posterUrl": "https://example.com/posters/quantum-paradox.jpg",
        "status": "now_showing",
        "synopsis": "A physicist discovers a way to manipulate quantum reality, but each change has unexpected consequences.",
        "director": "Christopher Nolan",
        "cast": ["Emma Stone", "Oscar Isaac", "Tilda Swinton"],
        "imdbRating": 8.2,
        "trailerUrl": "https://example.com/trailers/quantum-paradox"
    },
    {
        "id": "m002",
        "title": "Guardians of Tomorrow",
        "genre": ["Action", "Adventure", "Sci-Fi"],
        "rating": "PG-13",
        "duration": 135,
        "releaseDate": "2024-02-01",
        "posterUrl": "https://example.com/posters/guardians-tomorrow.jpg",
        "status": "now_showing",
        "synopsis": "A team of unlikely heroes must save Earth from an interdimensional threat.",
        "director": "James Gunn",
        "cast": ["Chris Pratt", "Zoe Saldana", "Dave Bautista"],
        "imdbRating": 7.9,
        "trailerUrl": "https://example.com/trailers/guardians-tomorrow"
    },
    {
        "id": "m003",
        "title": "Love in Paris",
        "genre": ["Romance", "Drama"],
        "rating": "PG",
        "duration": 112,
        "releaseDate": "2024-02-14",
        "posterUrl": "https://example.com/posters/love-paris.jpg",
        "status": "now_showing",
        "synopsis": "Two strangers meet in Paris and discover that love can transcend time and space.",
        "director": "Nancy Meyers",
        "cast": ["Ryan Gosling", "Emma Watson"],
        "imdbRating": 7.5,
        "trailerUrl": "https://example.com/trailers/love-paris"
    },
    {
        "id": "m004",
        "title": "The Last Detective",
        "genre": ["Mystery", "Thriller"],
        "rating": "R",
        "duration": 128,
        "releaseDate": "2024-03-01",
        "posterUrl": "https://example.com/posters/last-detective.jpg",
        "status": "coming_soon",
        "synopsis": "A retired detective is pulled back for one last case that threatens everything he holds dear.",
        "director": "David Fincher",
        "cast": ["Daniel Craig", "Rooney Mara", "Christopher Plummer"],
        "imdbRating": 0.0,
        "trailerUrl": "https://example.com/trailers/last-detective"
    },
    {
        "id": "m005",
        "title": "Animated Dreams",
        "genre": ["Animation", "Family", "Adventure"],
        "rating": "G",
        "duration": 95,
        "releaseDate": "2024-03-15",
        "posterUrl": "https://example.com/posters/animated-dreams.jpg",
        "status": "coming_soon",
        "synopsis": "A young artist's drawings come to life and embark on a magical adventure.",
        "director": "Pete Docter",
        "cast": ["Tom Hanks", "Amy Poehler", "Bill Hader"],
        "imdbRating": 0.0,
        "trailerUrl": "https://example.com/trailers/animated-dreams"
    }
]

# Storage for bookings
BOOKINGS: Dict[str, Any] = {}

# Helper functions
def generate_showtimes(movie_id: str, date: str) -> List[Dict[str, Any]]:
    """Generate mock showtimes for a movie on a specific date"""
    base_times = ["10:00", "13:00", "16:00", "19:00", "22:00"]
    formats = ["2D", "3D", "IMAX", "4DX"]
    theaters = ["Screen 1", "Screen 2", "Screen 3", "IMAX Theater"]
    
    showtimes = []
    for i, time in enumerate(base_times[:random.randint(3, 5)]):
        showtime_format = random.choice(formats)
        base_price = 12.0
        
        # Price adjustments
        if showtime_format == "3D":
            base_price += 3.0
        elif showtime_format == "IMAX":
            base_price += 5.0
        elif showtime_format == "4DX":
            base_price += 8.0
            
        if time >= "19:00":
            base_price += 2.0  # Evening surcharge
            
        start_datetime = f"{date}T{time}:00"
        showtime = {
            "id": f"st_{movie_id}_{date.replace('-', '')}_{i}",
            "movieId": movie_id,
            "startTime": start_datetime,
            "endTime": f"{date}T{int(time[:2])+2:02d}:{time[3:]}:00",
            "theater": random.choice(theaters),
            "screen": f"Screen {i+1}",
            "price": base_price,
            "format": showtime_format
        }
        showtimes.append(showtime)
    
    return showtimes

def generate_seat_map() -> List[Dict[str, Any]]:
    """Generate a mock seat map for a theater"""
    rows = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    seats_per_row = 12
    seat_map = []
    
    for row in rows:
        row_seats = []
        for seat_num in range(1, seats_per_row + 1):
            # Randomly mark some seats as occupied
            status = "occupied" if random.random() < 0.3 else "available"
            
            # Premium rows
            seat_type = "premium" if row in ["E", "F", "G"] else "standard"
            if row in ["H", "I", "J"]:
                seat_type = "vip"
                
            row_seats.append({
                "number": str(seat_num),
                "status": status,
                "type": seat_type
            })
        
        seat_map.append({
            "row": row,
            "seats": row_seats
        })
    
    return seat_map

# API Routes
@app.route('/api/v1/movies', methods=['GET'])
def search_movies():
    """Search for movies"""
    status = request.args.get('status', 'all')
    genre = request.args.get('genre')
    date = request.args.get('date')
    
    filtered_movies = MOVIES.copy()
    
    # Filter by status
    if status != 'all':
        filtered_movies = [m for m in filtered_movies if m['status'] == status]
    
    # Filter by genre
    if genre:
        filtered_movies = [m for m in filtered_movies if genre in m['genre']]
    
    return jsonify({"movies": filtered_movies})

@app.route('/api/v1/movies/<movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    """Get detailed information about a specific movie"""
    movie = next((m for m in MOVIES if m['id'] == movie_id), None)
    
    if not movie:
        return jsonify({"error": "Movie not found"}), 404
    
    return jsonify(movie)

@app.route('/api/v1/movies/<movie_id>/showtimes', methods=['GET'])
def get_showtimes(movie_id):
    """Get showtimes for a movie on a specific date"""
    date = request.args.get('date')
    
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400
    
    movie = next((m for m in MOVIES if m['id'] == movie_id), None)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404
    
    # Only generate showtimes for current movies
    if movie['status'] != 'now_showing':
        return jsonify({"showtimes": []})
    
    showtimes = generate_showtimes(movie_id, date)
    return jsonify({"showtimes": showtimes})

@app.route('/api/v1/showtimes/<showtime_id>/availability', methods=['GET'])
def check_availability(showtime_id):
    """Check seat availability for a showtime"""
    seat_map = generate_seat_map()
    
    # Calculate available seats
    total_seats = sum(len(row['seats']) for row in seat_map)
    available_seats = sum(1 for row in seat_map for seat in row['seats'] if seat['status'] == 'available')
    
    return jsonify({
        "showtimeId": showtime_id,
        "totalSeats": total_seats,
        "availableSeats": available_seats,
        "seatMap": seat_map
    })

@app.route('/api/v1/bookings', methods=['POST'])
def create_booking():
    """Create a new booking"""
    data = request.json
    
    if not all(k in data for k in ['showtimeId', 'seats', 'customerInfo']):
        return jsonify({"error": "Missing required fields"}), 400
    
    booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
    
    # Calculate total amount (simplified)
    base_price = 12.0  # Would normally get from showtime
    total_amount = base_price * len(data['seats'])
    
    booking = {
        "bookingId": booking_id,
        "status": "pending_payment",
        "totalAmount": total_amount,
        "bookingDetails": data,
        "expiresAt": (datetime.now() + timedelta(minutes=15)).isoformat(),
        "createdAt": datetime.now().isoformat()
    }
    
    BOOKINGS[booking_id] = booking
    
    return jsonify(booking), 201

@app.route('/api/v1/bookings/<booking_id>/payment', methods=['POST'])
def process_payment(booking_id):
    """Process payment for a booking"""
    booking = BOOKINGS.get(booking_id)
    
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
    
    data = request.json
    if not all(k in data for k in ['paymentMethod', 'amount']):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Simulate payment processing
    success = random.random() > 0.1  # 90% success rate
    
    if success:
        booking['status'] = 'confirmed'
        confirmation_code = f"CNF{uuid.uuid4().hex[:6].upper()}"
        
        response = {
            "transactionId": f"TXN{uuid.uuid4().hex[:10].upper()}",
            "status": "success",
            "bookingId": booking_id,
            "confirmationCode": confirmation_code,
            "receipt": {
                "amount": data['amount'],
                "tax": round(data['amount'] * 0.08, 2),
                "total": round(data['amount'] * 1.08, 2),
                "paymentMethod": data['paymentMethod']
            }
        }
    else:
        response = {
            "transactionId": f"TXN{uuid.uuid4().hex[:10].upper()}",
            "status": "failed",
            "bookingId": booking_id,
            "error": "Payment declined"
        }
    
    return jsonify(response)

@app.route('/api/v1/recommendations', methods=['GET'])
def get_recommendations():
    """Get movie recommendations"""
    genres = request.args.getlist('genres')
    limit = int(request.args.get('limit', 5))
    
    # Simple recommendation logic
    recommendations = []
    
    if genres:
        # Find movies with matching genres
        for movie in MOVIES:
            if any(g in movie['genre'] for g in genres):
                recommendations.append(movie)
    else:
        # Random recommendations
        recommendations = random.sample(MOVIES, min(limit, len(MOVIES)))
    
    return jsonify({"recommendations": recommendations[:limit]})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting Cinema API Server on http://localhost:8000")
    print("API documentation available at http://localhost:8000/api/v1")
    app.run(host='0.0.0.0', port=8000, debug=True)