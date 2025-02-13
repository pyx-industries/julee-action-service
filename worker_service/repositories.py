from abc import ABC, abstractmethod
from typing import Optional
import httpx
from ..domain import Connection, Subscription, Publisher

class ConnectionRepository:
    def get_connection(self, conn_id: str) -> Optional[Connection]:
        """Get connection configuration and state."""
        # Implementation would fetch from database
        pass

    def update_status(self, conn_id: str, status: str, error: Optional[str] = None) -> None:
        """Update connection status and error state."""
        # Implementation would update database
        pass

class SubscriptionRepository:
    def get_subscription(self, sub_id: str) -> Optional[Subscription]:
        """Get subscription configuration."""
        # Implementation would fetch from database
        pass

class PublisherRepository:
    def get_publisher(self, pub_id: str) -> Optional[Publisher]:
        """Get publisher configuration."""
        # Implementation would fetch from database
        pass

class MessageRepository:
    def is_processed(self, message_id: str) -> bool:
        """Check if a message has already been processed."""
        # Implementation would check database
        pass

    def mark_processed(self, message_id: str) -> None:
        """Mark a message as processed."""
        # Implementation would update database
        pass

class JuleeApiClient:
    def __init__(self):
        self.base_url = "http://julee-api/v1"
        self.client = httpx.Client()

    def create_capture(self, capture_data: dict):
        """Send capture to Julee API."""
        return self.client.post(
            f"{self.base_url}/captures/",
            json=capture_data
        )
