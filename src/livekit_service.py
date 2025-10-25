import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class LiveKitService:
    def __init__(self):
        self.enabled = os.getenv('ENABLE_LIVEKIT_AGENT', 'false').lower() == 'true'
        self.url = os.getenv('LIVEKIT_URL')
        self.api_key = os.getenv('LIVEKIT_API_KEY')
        self.api_secret = os.getenv('LIVEKIT_API_SECRET')
        self.room_prefix = os.getenv('LIVEKIT_ROOM_PREFIX', 'customer-service')
        
        if self.enabled and not all([self.url, self.api_key, self.api_secret]):
            logger.warning("LiveKit is enabled but credentials are not fully configured")
            self.enabled = False
    
    def is_available(self) -> bool:
        return self.enabled and all([self.url, self.api_key, self.api_secret])
    
    def get_status(self) -> Dict[str, Any]:
        return {
            'enabled': self.enabled,
            'configured': self.is_available(),
            'url': self.url if self.is_available() else None
        }
    
    def generate_room_name(self, user_id: str) -> str:
        return f"{self.room_prefix}-{user_id}"
    
    def create_access_token(self, room_name: str, participant_identity: str) -> Optional[str]:
        if not self.is_available():
            return None
        
        try:
            from livekit import api
            
            token = api.AccessToken(self.api_key, self.api_secret)
            token.with_identity(participant_identity)
            token.with_name(participant_identity)
            token.with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True
            ))
            
            return token.to_jwt()
        except Exception as e:
            logger.error(f"Error generating LiveKit token: {e}")
            return None


livekit_service = LiveKitService()
