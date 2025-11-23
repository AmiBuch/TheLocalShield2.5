#!/bin/bash
# Test script for TheLocalShield API
# Run this after starting the server with: python -m uvicorn main:app --host 0.0.0.0 --port 8000

echo "Testing root endpoint..."
curl http://localhost:8000/

echo -e "\n\nTesting health endpoint..."
curl http://localhost:8000/health

echo -e "\n\nTesting location update endpoint..."
curl -X POST http://localhost:8000/location/update \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "latitude": 40.7128, "longitude": -74.0060}'

echo -e "\n\nTesting get all locations endpoint..."
curl http://localhost:8000/location/all

echo -e "\n\nTesting emergency notify nearby endpoint..."
curl -X POST http://localhost:8000/emergency/notify_nearby \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "latitude": 40.7128, "longitude": -74.0060}'

echo -e "\n\nAll tests completed!"

