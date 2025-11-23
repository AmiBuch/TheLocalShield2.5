# PowerShell script to test TheLocalShield API endpoints
# Make sure the server is running first: python -m uvicorn main:app --host 0.0.0.0 --port 8000

Write-Host "=== Testing TheLocalShield API ===" -ForegroundColor Cyan

# Test root endpoint
Write-Host "`n1. Testing root endpoint (GET /)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -Method GET
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

# Test health endpoint
Write-Host "`n2. Testing health endpoint (GET /health)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

# Test location update endpoint
Write-Host "`n3. Testing location update (POST /location/update)..." -ForegroundColor Yellow
try {
    $body = @{
        user_id = 1
        latitude = 40.7128
        longitude = -74.0060
    } | ConvertTo-Json
    
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-WebRequest -Uri "http://localhost:8000/location/update" -Method POST -Body $body -Headers $headers
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody" -ForegroundColor Red
    }
}

# Test get all locations endpoint
Write-Host "`n4. Testing get all locations (GET /location/all)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/location/all" -Method GET
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

# Test emergency notify nearby endpoint
Write-Host "`n5. Testing emergency notify nearby (POST /emergency/notify_nearby)..." -ForegroundColor Yellow
try {
    $body = @{
        user_id = 1
        latitude = 40.7128
        longitude = -74.0060
    } | ConvertTo-Json
    
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-WebRequest -Uri "http://localhost:8000/emergency/notify_nearby" -Method POST -Body $body -Headers $headers
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n=== Testing Complete ===" -ForegroundColor Cyan

