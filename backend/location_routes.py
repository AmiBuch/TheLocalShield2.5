"""
Location-related API routes.
Handles location tracking and retrieval endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from models import LocationModel, LocationUpdateRequest, LocationResponse, RegisterPushTokenRequest
from database import db, upsert_location, get_all_locations, register_push_token

# Initialize router
router = APIRouter()


@router.post("/track", response_model=dict)
async def track_location(location: LocationModel):
    """
    Track and store a user's location.
    
    Args:
        location: Location data to track
        
    Returns:
        dict: Success message and location ID
    """
    pass


@router.get("/history/{user_id}", response_model=List[LocationModel])
async def get_location_history(
    user_id: str,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0
):
    """
    Retrieve location history for a user.
    
    Args:
        user_id: User identifier
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of location records
    """
    pass


@router.get("/current/{user_id}", response_model=LocationModel)
async def get_current_location(user_id: str):
    """
    Get the most recent location for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Current location data
    """
    pass


@router.delete("/history/{user_id}")
async def clear_location_history(user_id: str):
    """
    Clear location history for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        dict: Success message
    """
    pass


@router.post("/update")
async def update_location(request: LocationUpdateRequest):
    """
    Update a user's location.
    
    Args:
        request: Location update request with user_id, latitude, and longitude
        
    Returns:
        dict: Success message
    """
    success = upsert_location(request.user_id, request.latitude, request.longitude)
    
    if success:
        return {"status": "success", "message": "Location updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update location")


@router.get("/all", response_model=List[LocationResponse])
async def get_all_locations_endpoint():
    """
    Get all location records.
    
    Returns:
        List of location records with user_id, latitude, longitude, and last_updated
    """
    locations = get_all_locations()
    return locations


@router.post("/register_token")
async def register_token(request: RegisterPushTokenRequest):
    """
    Register or update a user's Expo push token.
    
    Args:
        request: Push token registration request with user_id and expo_push_token
        
    Returns:
        dict: Success message
    """
    success = register_push_token(request.user_id, request.expo_push_token, request.name)
    
    if success:
        return {"status": "success", "message": "Push token registered successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to register push token")

