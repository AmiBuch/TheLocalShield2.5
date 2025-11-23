"""
Emergency-related API routes.
Handles emergency requests and responses.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional, Dict, Any
from models import EmergencyRequest, EmergencyResponse, NotifyNearbyRequest, EmergencyEvent
from database import db, upsert_location, get_user_push_tokens_except, get_recent_emergencies, create_emergency
from auth_routes import get_current_user_id
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


# IMPORTANT: /recent must come BEFORE /{emergency_id} to avoid route collision
@router.get("/recent")
async def get_recent_emergencies_endpoint(
    request: Request,
    since: Optional[str] = None
):
    """
    Get recent emergency events (for POC polling).
    
    Args:
        since: ISO timestamp - only return emergencies after this time
        
    Returns:
        List of recent emergency events (always a list, never None)
    """
    print(f"🔍 /recent called with since={since}")
    result = []
    
    try:
        # Try to get user_id from token
        exclude_id = None
        try:
            auth_header = request.headers.get("authorization", "")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
                try:
                    from auth_routes import verify_token
                    user_data = verify_token(token)
                    if user_data and isinstance(user_data, dict):
                        exclude_id = user_data.get("user_id")
                        print(f"🔑 Authenticated user_id: {exclude_id}")
                except Exception as e:
                    print(f"⚠️ Token verification failed: {e}")
        except Exception as e:
            print(f"⚠️ Auth header extraction failed: {e}")
        
        # Get emergencies from database
        try:
            emergencies = get_recent_emergencies(since, exclude_id)
            print(f"📊 Database returned {len(emergencies) if emergencies else 0} emergencies")
            print(f"📋 Raw emergencies: {emergencies}")
            
            if emergencies and isinstance(emergencies, list):
                for emergency in emergencies:
                    if emergency and isinstance(emergency, dict):
                        try:
                            validated = {
                                'id': int(emergency.get('id', 0)),
                                'user_id': int(emergency.get('user_id', 0)),
                                'latitude': float(emergency.get('latitude', 0.0)),
                                'longitude': float(emergency.get('longitude', 0.0)),
                                'created_at': str(emergency.get('created_at', ''))
                            }
                            if validated['id'] > 0 and validated['user_id'] > 0:
                                result.append(validated)
                                print(f"✅ Added emergency: {validated}")
                        except Exception as e:
                            print(f"❌ Failed to validate emergency: {e}")
                            continue
        except Exception as e:
            print(f"❌ Database error: {e}")
            import traceback
            traceback.print_exc()
    
    except Exception as e:
        print(f"❌ Critical error in endpoint: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"🎯 Returning {len(result)} emergencies: {result}")
    return result

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
async def notify_nearby(
    request: NotifyNearbyRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Notify nearby users about an emergency.
    
    Args:
        request: Notify nearby request with user_id, latitude, and longitude
        
    Returns:
        dict: Status and number of recipients notified
    """
    # Use authenticated user_id instead of request.user_id
    user_id = current_user_id
    
    # 1. Upsert location for sender
    upsert_location(user_id, request.latitude, request.longitude)
    
    # 2. Create emergency event in database (for POC polling)
    emergency_id = create_emergency(user_id, request.latitude, request.longitude)
    
    # 3. Query all other users' Expo push tokens
    push_tokens = get_user_push_tokens_except(user_id)
    
    # 4. For each token, send a push notification (if available)
    title = "Emergency Alert"
    body = f"A nearby user is in an emergency. Location: {request.latitude}, {request.longitude}"
    
    sent_count = 0
    for token in push_tokens:
        success = await push_service.send_push(token, title, body)
        if success:
            sent_count += 1
    
    return {
        "status": "sent",
        "recipients": sent_count,
        "emergency_id": emergency_id
    }