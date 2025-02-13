"""HTTP Plugin Implementation"""
import httpx
from typing import Any, Dict, Optional
from .base import ActionPlugin
from ..domain import Protocol, Action, ActionResult

class HttpPlugin(ActionPlugin):
    protocol = Protocol.HTTP

    def validate_config(self, config: Dict[str, Any]) -> None:
        required = {'url', 'method'}
        if not all(k in config for k in required):
            raise ValueError(f"HTTP config must include: {required}")

    def execute(self, action: Action, input_data: Optional[Any] = None) -> ActionResult:
        try:
            with httpx.Client() as client:
                response = client.request(
                    method=action.config['method'],
                    url=action.config['url'],
                    headers=action.config.get('headers', {}),
                    json=input_data if input_data else action.config.get('body')
                )
                
                return ActionResult(
                    action_id=action.id,
                    success=response.is_success,
                    result=response.json() if response.is_success else None,
                    error=str(response.text) if not response.is_success else None,
                    metadata={
                        'status_code': response.status_code,
                        'headers': dict(response.headers)
                    }
                )
                
        except Exception as e:
            return ActionResult(
                action_id=action.id,
                success=False,
                error=str(e)
            )
