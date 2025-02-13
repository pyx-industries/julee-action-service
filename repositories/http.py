import httpx
import httpx
from typing import Optional
from ..domain.direction import ActionDirection
import os

from ..domain import Action, Event, Connection
from ..interfaces.repositories import ActionExecutor, EventRepository

class HttpActionRepository(ActionExecutor):
    """HTTP implementation for executing actions."""
    
    def __init__(self):
        self.base_url = os.getenv('JULEE_API_URL', 'http://julee-service:8000')
        self.api_key = os.getenv('JULEE_API_KEY')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def execute(self, action: Action) -> dict:
        """Execute an HTTP action."""
        with httpx.Client() as client:
            response = client.request(
                method=action.config.get('method', 'GET'),
                url=action.config['url'],
                headers={**self.headers, **action.config.get('headers', {})},
                json=action.config.get('body'),
                params=action.config.get('params')
            )
            response.raise_for_status()
            return {'status': response.status_code, 'data': response.json()}

class HttpEventRepository(EventRepository):
    """HTTP implementation for event recording."""
    
    def __init__(self):
        self.base_url = os.getenv('JULEE_API_URL', 'http://julee-service:8000')
        self.api_key = os.getenv('JULEE_API_KEY')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def record_success(self, action_id: str, result: dict) -> None:
        """Record successful action execution."""
        direction = ActionDirection.EFFERENT
        self.logger.debug(
            f"Recording success for action {action_id}: direction={direction}, "
            f"result_keys={list(result.keys())}, endpoint={self.base_url}/events/"
        )
        if not ActionDirection.is_valid(direction):
            self.logger.error(f"Invalid direction '{direction}' for action {action_id}")
            raise ValueError(f"Invalid direction: {direction}")
            
        with httpx.Client() as client:
            client.post(
                f"{self.base_url}/events/",
                headers=self.headers,
                json={
                    'action_id': action_id,
                    'status': 'success',
                    'result': result,
                    'direction': ActionDirection.normalize(direction)
                }
            )

    def record_failure(self, action_id: str, error: str) -> None:
        """Record failed action execution."""
        with httpx.Client() as client:
            client.post(
                f"{self.base_url}/events/",
                headers=self.headers,
                json={
                    'action_id': action_id,
                    'status': 'error',
                    'error': error
                }
            )
