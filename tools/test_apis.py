#!/usr/bin/env python3
"""
Test script to verify API connections for Cinema Agent Lab
This script tests TMDb and MovieGlu APIs without requiring watsonx Orchestrate
"""

import os
import sys
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

def test_tmdb_api():
    """Test TMDb API connection"""
    print("🎬 Testing TMDb API...")
    
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print("❌ TMDB_API_KEY not found in environment")
        return False
    
    try:
        url = f"https://api.themoviedb.org/3/movie/popular"
        params = {"api_key": api_key, "page": 1}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            movies = data.get('results', [])
            print(f"✅ TMDb API working! Found {len(movies)} popular movies")
            if movies:
                print(f"   Sample movie: {movies[0].get('title', 'Unknown')}")
            return True
        else:
            print(f"❌ TMDb API error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TMDb API connection error: {e}")
        return False

def test_movieglu_api():
    """Test MovieGlu API connection"""
    print("\n🏢 Testing MovieGlu API...")
    
    client = os.getenv('MOVIEGLU_CLIENT')
    api_key = os.getenv('MOVIEGLU_API_KEY')
    authorization = os.getenv('MOVIEGLU_AUTHORIZATION')
    territory = os.getenv('MOVIEGLU_TERRITORY', 'FR')
    geolocation = os.getenv('MOVIEGLU_GEOLOCATION', '48.8566;2.3522')
    
    if not all([client, api_key, authorization]):
        print("❌ MovieGlu credentials not found in environment")
        print("   Missing: MOVIEGLU_CLIENT, MOVIEGLU_API_KEY, or MOVIEGLU_AUTHORIZATION")
        return False
    
    try:
        headers = {
            'client': client,
            'x-api-key': api_key,
            'authorization': authorization,
            'territory': territory,
            'api-version': 'v201',
            'geolocation': geolocation,
            'device-datetime': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        }
        
        url = "https://api-gate2.movieglu.com/cinemasNearby/"
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            cinemas = data.get('cinemas', [])
            print(f"✅ MovieGlu API working! Found {len(cinemas)} cinemas in {territory}")
            if cinemas:
                print(f"   Sample cinema: {cinemas[0].get('cinema_name', 'Unknown')}")
            return True
        else:
            print(f"❌ MovieGlu API error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ MovieGlu API connection error: {e}")
        return False

def test_python_tools():
    """Test that our Python tools can be imported"""
    print("\n🔧 Testing Python tool imports...")
    
    try:
        # Test movie search tools
        sys.path.append('.')
        from movie_search import search_movies
        print("✅ movie_search tools imported successfully")
        
        from cinema_showtimes import find_cinemas_nearby
        print("✅ cinema_showtimes tools imported successfully")
        
        from booking import check_seat_availability
        print("✅ booking tools imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Tool import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Cinema Agent Lab - API Testing")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Run tests
    tmdb_ok = test_tmdb_api()
    movieglu_ok = test_movieglu_api()
    tools_ok = test_python_tools()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   TMDb API:      {'✅ PASS' if tmdb_ok else '❌ FAIL'}")
    print(f"   MovieGlu API:  {'✅ PASS' if movieglu_ok else '❌ FAIL'}")
    print(f"   Python Tools:  {'✅ PASS' if tools_ok else '❌ FAIL'}")
    
    if all([tmdb_ok, movieglu_ok, tools_ok]):
        print("\n🎉 All tests passed! Your Cinema Agent lab is ready!")
    else:
        print("\n⚠️  Some tests failed. Check your configuration:")
        if not tmdb_ok:
            print("   - Verify TMDB_API_KEY in .env file")
        if not movieglu_ok:
            print("   - Verify MovieGlu credentials in .env file")
        if not tools_ok:
            print("   - Check Python tool files in tools/ directory")
    
    print("=" * 60)

if __name__ == "__main__":
    main()