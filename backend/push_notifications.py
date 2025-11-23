"""
Push notification service module.
Handles sending push notifications to users.
"""

import httpx
from typing import Optional, Dict, Any
from models import PushNotificationRequest


class PushNotificationService:
    """Service for managing push notifications."""
    
    def __init__(self):
        """Initialize push notification service."""
        self.api_key: Optional[str] = None
        self.api_url: Optional[str] = None
    
    def configure(self, api_key: str, api_url: str):
        """
        Configure push notification service.
        
        Args:
            api_key: API key for push notification service
            api_url: Base URL for push notification API
        """
        pass
    
    async def send_notification(self, request: PushNotificationRequest) -> bool:
        """
        Send a push notification to a user.
        
        Args:
            request: Push notification request data
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        pass
    
    async def send_bulk_notifications(self, requests: list[PushNotificationRequest]) -> Dict[str, bool]:
        """
        Send multiple push notifications.
        
        Args:
            requests: List of push notification requests
            
        Returns:
            Dictionary mapping user_id to success status
        """
        pass
    
    async def register_device_token(self, user_id: str, device_token: str) -> bool:
        """
        Register a device token for push notifications.
        
        Args:
            user_id: User identifier
            device_token: Device push notification token
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        pass
    
    async def unregister_device_token(self, user_id: str, device_token: str) -> bool:
        """
        Unregister a device token.
        
        Args:
            user_id: User identifier
            device_token: Device push notification token
            
        Returns:
            bool: True if unregistration successful, False otherwise
        """
        pass
    
    async def send_push(self, expo_token: str, title: str, body: str) -> bool:
        """
        Send a push notification to a specific Expo push token.
        
        Args:
            expo_token: Expo push token
            title: Notification title
            body: Notification message body
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        try:
            # Expo Push Notification API endpoint
            expo_api_url = "https://exp.host/--/api/v2/push/send"
            
            # Prepare the notification payload
            payload = {
                "to": expo_token,
                "sound": "default",
                "title": title,
                "body": body
            }
            
            # Send the notification using httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    expo_api_url,
                    json=payload,
                    headers={
                        "Accept": "application/json",
                        "Accept-Encoding": "gzip, deflate",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Expo returns a data array with status for each notification
                    if isinstance(result, dict) and result.get("data"):
                        return result["data"][0].get("status") == "ok"
                    return True
                return False
        except Exception as e:
            print(f"Error sending push notification: {e}")
            return False


# Global push notification service instance
push_service = PushNotificationService()

