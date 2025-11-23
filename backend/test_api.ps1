# Test script for TheLocalShield API (PowerShell)
# Run this after starting the server with: python -m uvicorn main:app --host 0.0.0.0 --port 8000

Write-Host "Testing root endpoint..." -ForegroundColor Green
Invoke-WebRequest -Uri "http://localhost:8000/" -Method GET | Select-Object -ExpandProperty Content

Write-Host "`nTesting health endpoint..." -ForegroundColor Green
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET | Select-Object -ExpandProperty Content

Write-Host "`nTesting location update endpoint..." -ForegroundColor Green
$body = @{
    user_id = 1
    latitude = 40.7128
    longitude = -74.0060
} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/location/update" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content

Write-Host "`nTesting get all locations endpoint..." -ForegroundColor Green
Invoke-WebRequest -Uri "http://localhost:8000/location/all" -Method GET | Select-Object -ExpandProperty Content

Write-Host "`nTesting emergency notify nearby endpoint..." -ForegroundColor Green
$body = @{
    user_id = 1
    latitude = 40.7128
    longitude = -74.0060
} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/emergency/notify_nearby" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content

Write-Host "`nAll tests completed!" -ForegroundColor Green

