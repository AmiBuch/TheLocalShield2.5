"""
Pydantic models for request/response validation.
Defines data structures for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LocationModel(BaseModel):
    """Model for location data."""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    timestamp: Optional[datetime] = Field(None, description="Location timestamp")
    accuracy: Optional[float] = Field(None, description="Location accuracy in meters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timestamp": "2024-01-01T12:00:00",
                "accuracy": 10.5
            }
        }


class EmergencyRequest(BaseModel):
    """Model for emergency request data."""
    user_id: str = Field(..., description="User identifier")
    location: LocationModel = Field(..., description="Emergency location")
    emergency_type: str = Field(..., description="Type of emergency")
    description: Optional[str] = Field(None, description="Emergency description")
    timestamp: Optional[datetime] = Field(None, description="Emergency timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                "emergency_type": "medical",
                "description": "Need immediate medical assistance"
            }
        }


class EmergencyResponse(BaseModel):
    """Model for emergency response data."""
    emergency_id: str = Field(..., description="Emergency request identifier")
    status: str = Field(..., description="Emergency status")
    created_at: datetime = Field(..., description="Emergency creation timestamp")
    message: Optional[str] = Field(None, description="Response message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "emergency_id": "emergency123",
                "status": "active",
                "created_at": "2024-01-01T12:00:00",
                "message": "Emergency request received"
            }
        }


class PushNotificationRequest(BaseModel):
    """Model for push notification request."""
    user_id: str = Field(..., description="Target user identifier")
    title: str = Field(..., description="Notification title")
    body: str = Field(..., description="Notification body")
    data: Optional[dict] = Field(None, description="Additional notification data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "title": "Emergency Alert",
                "body": "Emergency assistance is on the way",
                "data": {"emergency_id": "emergency123"}
            }
        }


class NotifyNearbyRequest(BaseModel):
    """Model for notify nearby emergency request."""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    # user_id is now obtained from JWT token, not from request
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }


class LocationUpdateRequest(BaseModel):
    """Model for location update request."""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    # user_id is now obtained from JWT token, not from request
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }


class LocationResponse(BaseModel):
    """Model for location response data."""
    user_id: int = Field(..., description="User identifier")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    last_updated: str = Field(..., description="Last updated timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "last_updated": "2024-01-01T12:00:00"
            }
        }


class RegisterPushTokenRequest(BaseModel):
    """Model for push token registration request."""
    expo_push_token: str = Field(..., description="Expo push notification token")
    # user_id is now obtained from JWT token, not from request
    
    class Config:
        json_schema_extra = {
            "example": {
                "expo_push_token": "ExponentPushToken[xxxxx]"
            }
        }


class EmergencyEvent(BaseModel):
    """Model for emergency event (used in polling endpoint)."""
    id: int = Field(..., description="Emergency ID")
    user_id: int = Field(..., description="User ID who triggered the emergency")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    created_at: str = Field(..., description="Emergency creation timestamp (ISO format)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 2,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "created_at": "2024-01-01T12:00:00"
            }
        }

