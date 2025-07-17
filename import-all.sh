#!/usr/bin/env bash
set -x

echo "=== Importing Cinema Agent for IBM watsonx Orchestrate ==="

echo "=== Importing Tools ==="

# Import Movie Search Tool with fallback credentials
orchestrate tools import -k python \
  -f "tools/python/movie_search_tool/source/movie_search_tool.py" \
  -r "tools/python/movie_search_tool/requirements.txt"

# Import Cinema Simulation Tool (replaces MovieGlu API)
orchestrate tools import -k python \
  -f "tools/python/cinema_simulation_tool/source/cinema_simulation_tool.py" \
  -r "tools/python/cinema_simulation_tool/requirements.txt"

# Import Booking Tool
orchestrate tools import -k python \
  -f "tools/python/booking_tool/source/booking_tool.py" \
  -r "tools/python/booking_tool/requirements.txt"

echo "=== Importing Agent ==="

# Import Cinema Agent
orchestrate agents import -f ./agents/cinema_agent.yaml

echo "=== Import Complete ==="
echo "Available tools: search_movies, get_movie_details, get_movie_recommendations, find_cinemas_nearby, get_cinema_showtimes, search_film_by_title, check_film_showtimes, check_seat_availability, create_booking, process_payment, get_booking_status"
echo "Agent 'cinema_agent' is ready to use!"