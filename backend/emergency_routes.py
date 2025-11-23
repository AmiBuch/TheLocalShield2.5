"""
Emergency-related API routes.
Handles emergency requests and responses.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from models import EmergencyRequest, EmergencyResponse, NotifyNearbyRequest
from database import db, upsert_location, get_user_push_tokens_except
from push_notifications import push_service

# Initialize router
router = APIRouter()


@router.post("/request", response_model=EmergencyResponse)
async def create_emergency_request(request: EmergencyRequest):
    """
    Create a new emergency request.
    
    Args:
        request: Emergency request data
        
    Returns:
        Emergency response with request ID and status
    """
    pass


@router.get("/{emergency_id}", response_model=EmergencyResponse)
async def get_emergency(emergency_id: str):
    """
    Retrieve emergency request details.
    
    Args:
        emergency_id: Emergency request identifier
        
    Returns:
        Emergency response data
    """
    pass


@router.get("/user/{user_id}", response_model=List[EmergencyResponse])
async def get_user_emergencies(
    user_id: str,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0
):
    """
    Get all emergency requests for a user.
    
    Args:
        user_id: User identifier
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of emergency requests
    """
    pass


@router.put("/{emergency_id}/status")
async def update_emergency_status(
    emergency_id: str,
    status: str
):
    """
    Update the status of an emergency request.
    
    Args:
        emergency_id: Emergency request identifier
        status: New status value
        
    Returns:
        dict: Success message
    """
    pass


@router.delete("/{emergency_id}")
async def cancel_emergency(emergency_id: str):
    """
    Cancel an emergency request.
    
    Args:
        emergency_id: Emergency request identifier
        
    Returns:
        dict: Success message
    """
    pass


@router.post("/notify_nearby")
async def notify_nearby(request: NotifyNearbyRequest):
    """
    Notify nearby users about an emergency.
    
    Args:
        request: Notify nearby request with user_id, latitude, and longitude
        
    Returns:
        dict: Status and number of recipients notified
    """
    # 1. Upsert location for sender
    upsert_location(request.user_id, request.latitude, request.longitude)
    
    # 2. Query all other users' Expo push tokens
    push_tokens = get_user_push_tokens_except(request.user_id)
    
    # 3. For each token, send a push notification
    title = "Emergency Alert"
    body = f"A nearby user is in an emergency. Location: {request.latitude}, {request.longitude}"
    
    sent_count = 0
    for token in push_tokens:
        success = await push_service.send_push(token, title, body)
        if success:
            sent_count += 1
    
    return {
        "status": "sent",
        "recipients": sent_count
    }

