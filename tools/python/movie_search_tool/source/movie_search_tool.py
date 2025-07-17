"""
Movie Search Tool for watsonx Orchestrate
Uses TMDb API for movie information
"""

import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ibm_watsonx_orchestrate.agent_builder.tools import tool

# TMDb API Configuration
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

def get_tmdb_api_key():
    """Get TMDb API key from environment variables"""
    # Try different possible environment variable names:
    # 1. Connection-injected variables
    # 2. Direct environment variables
    # 3. Hardcoded fallback from your .env
    api_key = (
        os.getenv('API_KEY') or 
        os.getenv('TMDB_API_KEY') or 
        os.getenv('api_key') or
        "6ca12353845bff48ef6fbc7dd502ec5f"  # Fallback from your .env
    )
    return api_key

@tool
def search_movies(query: str = "", 
                  status: str = "now_playing",
                  genre: str = "",
                  region: str = "FR",
                  limit: int = 10) -> Dict[str, Any]:
    """
    Search for movies using TMDb API
    
    Args:
        query: Search query for movie title (optional, empty string for no filter)
        status: Movie status - 'now_playing', 'upcoming', or 'popular'
        genre: Genre name to filter by (optional, empty string for no filter)
        region: Region code (e.g., 'FR' for France, 'GB' for UK)
        limit: Maximum number of movies to return (default: 10)
    
    Returns:
        Dictionary containing list of movies with their details
    """
    
    TMDB_API_KEY = get_tmdb_api_key()
    
    if not TMDB_API_KEY:
        return {"error": "TMDb API key not configured. Please configure the tmdb_api connection."}
    
    try:
        # Determine the endpoint based on status
        if query and query.strip():
            # Search by title
            endpoint = f"{TMDB_BASE_URL}/search/movie"
            params = {
                "api_key": TMDB_API_KEY,
                "query": query,
                "region": region
            }
        else:
            # Get movies by status
            status_endpoints = {
                "now_playing": "/movie/now_playing",
                "upcoming": "/movie/upcoming",
                "popular": "/movie/popular"
            }
            endpoint = f"{TMDB_BASE_URL}{status_endpoints.get(status, '/movie/now_playing')}"
            params = {
                "api_key": TMDB_API_KEY,
                "region": region,
                "page": 1
            }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        data = response.json()
        movies = data.get('results', [])
        
        # If genre filter is specified, get genre mappings first
        if genre and genre.strip():
            genre_response = requests.get(
                f"{TMDB_BASE_URL}/genre/movie/list",
                params={"api_key": TMDB_API_KEY}
            )
            genres_data = genre_response.json()
            genre_map = {g['name'].lower(): g['id'] for g in genres_data.get('genres', [])}
            
            genre_id = genre_map.get(genre.lower())
            if genre_id:
                movies = [m for m in movies if genre_id in m.get('genre_ids', [])]
        
        # Format the response
        formatted_movies = []
        for movie in movies[:limit]:  # Limit to specified number of results
            formatted_movie = {
                "id": str(movie['id']),
                "title": movie['title'],
                "release_date": movie.get('release_date', 'TBA'),
                "overview": movie.get('overview', 'No description available'),
                "rating": movie.get('vote_average', 0),
                "poster_url": f"{TMDB_IMAGE_BASE}{movie['poster_path']}" if movie.get('poster_path') else None,
                "popularity": movie.get('popularity', 0)
            }
            formatted_movies.append(formatted_movie)
        
        return {
            "status": "success",
            "count": len(formatted_movies),
            "movies": formatted_movies,
            "region": region
        }
        
    except requests.RequestException as e:
        return {"error": f"Failed to fetch movies: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@tool
def get_movie_details(movie_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific movie
    
    Args:
        movie_id: TMDb movie ID
    
    Returns:
        Dictionary containing detailed movie information
    """
    
    TMDB_API_KEY = get_tmdb_api_key()
    
    if not TMDB_API_KEY:
        return {"error": "TMDb API key not configured. Please configure the tmdb_api connection."}
    
    try:
        # Get movie details with additional information
        endpoint = f"{TMDB_BASE_URL}/movie/{movie_id}"
        params = {
            "api_key": TMDB_API_KEY,
            "append_to_response": "credits,videos,release_dates"
        }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        movie = response.json()
        
        # Extract main cast (top 5)
        cast = []
        if 'credits' in movie and 'cast' in movie['credits']:
            cast = [actor['name'] for actor in movie['credits']['cast'][:5]]
        
        # Extract director
        director = "Unknown"
        if 'credits' in movie and 'crew' in movie['credits']:
            directors = [crew['name'] for crew in movie['credits']['crew'] if crew['job'] == 'Director']
            if directors:
                director = directors[0]
        
        # Extract trailer URL
        trailer_url = None
        if 'videos' in movie and 'results' in movie['videos']:
            trailers = [v for v in movie['videos']['results'] 
                       if v['type'] == 'Trailer' and v['site'] == 'YouTube']
            if trailers:
                trailer_url = f"https://www.youtube.com/watch?v={trailers[0]['key']}"
        
        # Extract certification/rating for different regions
        certifications = {}
        if 'release_dates' in movie and 'results' in movie['release_dates']:
            for release in movie['release_dates']['results']:
                if release['iso_3166_1'] in ['GB', 'US', 'FR', 'DE']:
                    for date_info in release['release_dates']:
                        if date_info.get('certification'):
                            certifications[release['iso_3166_1']] = date_info['certification']
                            break
        
        return {
            "status": "success",
            "movie": {
                "id": str(movie['id']),
                "title": movie['title'],
                "tagline": movie.get('tagline', ''),
                "overview": movie.get('overview', 'No description available'),
                "release_date": movie.get('release_date', 'TBA'),
                "runtime": movie.get('runtime', 0),
                "genres": [g['name'] for g in movie.get('genres', [])],
                "director": director,
                "cast": cast,
                "rating": movie.get('vote_average', 0),
                "vote_count": movie.get('vote_count', 0),
                "poster_url": f"{TMDB_IMAGE_BASE}{movie['poster_path']}" if movie.get('poster_path') else None,
                "backdrop_url": f"{TMDB_IMAGE_BASE}{movie['backdrop_path']}" if movie.get('backdrop_path') else None,
                "trailer_url": trailer_url,
                "certifications": certifications,
                "budget": movie.get('budget', 0),
                "revenue": movie.get('revenue', 0),
                "production_companies": [c['name'] for c in movie.get('production_companies', [])][:3]
            }
        }
        
    except requests.RequestException as e:
        return {"error": f"Failed to fetch movie details: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@tool
def get_movie_recommendations(movie_id: str = "",
                             genres: List[str] = None,
                             min_rating: float = 7.0) -> Dict[str, Any]:
    """
    Get movie recommendations based on a movie or genres
    
    Args:
        movie_id: TMDb movie ID to base recommendations on (optional, empty string for no specific movie)
        genres: List of genre names to filter by (optional)
        min_rating: Minimum rating threshold (default: 7.0)
    
    Returns:
        Dictionary containing recommended movies
    """
    
    TMDB_API_KEY = get_tmdb_api_key()
    
    if not TMDB_API_KEY:
        return {"error": "TMDb API key not configured. Please configure the tmdb_api connection."}
    
    try:
        recommendations = []
        
        if movie_id and movie_id.strip():
            # Get recommendations based on a specific movie
            endpoint = f"{TMDB_BASE_URL}/movie/{movie_id}/recommendations"
            params = {"api_key": TMDB_API_KEY}
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            recommendations = data.get('results', [])
        
        elif genres:
            # Get popular movies filtered by genres
            # First, get genre IDs
            genre_response = requests.get(
                f"{TMDB_BASE_URL}/genre/movie/list",
                params={"api_key": TMDB_API_KEY}
            )
            genres_data = genre_response.json()
            genre_map = {g['name'].lower(): g['id'] for g in genres_data.get('genres', [])}
            
            genre_ids = [str(genre_map[g.lower()]) for g in genres if g.lower() in genre_map]
            
            if genre_ids:
                endpoint = f"{TMDB_BASE_URL}/discover/movie"
                params = {
                    "api_key": TMDB_API_KEY,
                    "sort_by": "popularity.desc",
                    "with_genres": ",".join(genre_ids),
                    "vote_average.gte": min_rating,
                    "vote_count.gte": 100  # Ensure movies have enough votes
                }
                
                response = requests.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                recommendations = data.get('results', [])
        
        else:
            # Get top rated movies as fallback
            endpoint = f"{TMDB_BASE_URL}/movie/top_rated"
            params = {"api_key": TMDB_API_KEY}
            
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            recommendations = data.get('results', [])
        
        # Filter by minimum rating and format response
        formatted_recommendations = []
        for movie in recommendations:
            if movie.get('vote_average', 0) >= min_rating:
                formatted_movie = {
                    "id": str(movie['id']),
                    "title": movie['title'],
                    "release_date": movie.get('release_date', 'TBA'),
                    "overview": movie.get('overview', 'No description available')[:200] + "...",
                    "rating": movie.get('vote_average', 0),
                    "poster_url": f"{TMDB_IMAGE_BASE}{movie['poster_path']}" if movie.get('poster_path') else None
                }
                formatted_recommendations.append(formatted_movie)
        
        # Limit to top 5 recommendations
        formatted_recommendations = formatted_recommendations[:5]
        
        return {
            "status": "success",
            "count": len(formatted_recommendations),
            "recommendations": formatted_recommendations,
            "based_on": f"movie_id: {movie_id}" if movie_id else f"genres: {genres}" if genres else "top_rated"
        }
        
    except requests.RequestException as e:
        return {"error": f"Failed to fetch recommendations: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}