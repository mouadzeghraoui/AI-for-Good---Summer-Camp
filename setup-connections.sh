#!/usr/bin/env bash

echo "=== Setting up API Key Connections for Cinema Agent ==="
echo ""
echo "This script will configure the necessary API key connections using your provided credentials."
echo "Setting up:"
echo "1. TMDb API Key for movie information"
echo "2. MovieGlu API credentials for French evaluation environment (75 requests)"
echo ""

# Create TMDb connection
echo "=== Creating and Configuring TMDb Connection ==="
echo "Step 1: Creating TMDb connection app..."
orchestrate connections add -a tmdb_api

echo "Step 2: Configuring TMDb connection for draft environment..."
orchestrate connections configure -a tmdb_api --env draft -k key_value -t team

echo "Step 3: Configuring TMDb connection for live environment..."
orchestrate connections configure -a tmdb_api --env live -k key_value -t team

echo "Step 4: Setting TMDb API key for both environments..."
TMDB_KEY="6ca12353845bff48ef6fbc7dd502ec5f"
orchestrate connections set-credentials -a tmdb_api --env draft -e "api_key=$TMDB_KEY"
orchestrate connections set-credentials -a tmdb_api --env live -e "api_key=$TMDB_KEY"

# Create MovieGlu connection  
echo ""
echo "=== Creating and Configuring MovieGlu Connection ==="
echo "Step 1: Creating MovieGlu connection app..."
orchestrate connections add -a movieglu_api

echo "Step 2: Configuring MovieGlu connection for draft environment..."
orchestrate connections configure -a movieglu_api --env draft -k key_value -t team

echo "Step 3: Configuring MovieGlu connection for live environment..."
orchestrate connections configure -a movieglu_api --env live -k key_value -t team

echo "Step 4: Setting MovieGlu credentials for both environments..."
MOVIEGLU_CLIENT="ZN"
MOVIEGLU_KEY="g5l4jjtcPUkjtQFGZdPs4mB9AFL3I2Talwt7t1Z7"
MOVIEGLU_AUTH="Basic Wk46dnNvSlNCek5Rb2ND"
MOVIEGLU_TERRITORY="FR"
MOVIEGLU_GEO="48.8566;2.3522"

orchestrate connections set-credentials -a movieglu_api --env draft -e "client=$MOVIEGLU_CLIENT" -e "api_key=$MOVIEGLU_KEY" -e "authorization=$MOVIEGLU_AUTH" -e "territory=$MOVIEGLU_TERRITORY" -e "geolocation=$MOVIEGLU_GEO"
orchestrate connections set-credentials -a movieglu_api --env live -e "client=$MOVIEGLU_CLIENT" -e "api_key=$MOVIEGLU_KEY" -e "authorization=$MOVIEGLU_AUTH" -e "territory=$MOVIEGLU_TERRITORY" -e "geolocation=$MOVIEGLU_GEO"

echo ""
echo "=== Connection Setup Complete ==="
echo "Connections configured for both draft and live environments."
echo "To verify your connections, run: orchestrate connections list"
echo ""
echo "Connection IDs created:"
echo "- tmdb_api (for TMDb API) - configured for draft and live"
echo "- movieglu_api (for MovieGlu French Evaluation API) - configured for draft and live"
echo ""
echo "MovieGlu French Evaluation Environment:"
echo "- Territory: FR (France)"
echo "- Requests: 75 total (evaluation limit)"
echo "- Real current movie data for French cinemas"