#!/bin/bash

SERVICE_URL="http://127.0.0.1:37889/"  # adjust if needed

for i in {1..10}
do
    # Random RPS between 20 and 80
    RPS=$((20 + RANDOM % 61))
    
    # Random duration between 45 and 90 seconds
    DURATION=$((45 + RANDOM % 46))

    echo "Sending traffic: ${RPS} RPS for ${DURATION} seconds..."
    
    hey -z ${DURATION}s -q ${RPS} "$SERVICE_URL" &

    # Small random buffer between bursts (10 to 20 seconds)
    SLEEP_BUFFER=$((10 + RANDOM % 11))
    echo "Sleeping for ${SLEEP_BUFFER} seconds before next burst..."
    sleep $((DURATION + SLEEP_BUFFER))
done

echo "Traffic simulation complete!"
