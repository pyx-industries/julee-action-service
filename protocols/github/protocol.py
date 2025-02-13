"""GitHub protocol implementation"""
from typing import Dict, Any, Optional
import os
import uuid
import httpx
from jinja2 import Environment, FileSystemLoader

from ...domain import Action, ActionResult
from ...pdk import ProtocolHandler

class GithubProtocol(ProtocolHandler):
    """Handles GitHub API interactions"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )

    def validate_config(self) -> bool:
        """Validate GitHub configuration"""
        # Convert config list to dict if needed
        if isinstance(self.config, list):
            config_dict = {v.name: v.value for v in self.config}
        else:
            config_dict = self.config

        required = ['repo_owner', 'repo_name', 'token']
        missing = [key for key in required if key not in config_dict]
        if missing:
            self.last_error = f"Missing required config keys: {missing}"
            return False
        return True

    def test_connection(self) -> bool:
        """Test GitHub API connection"""
        try:
            headers = {'Authorization': f"token {self.config['token']}"}
            url = f"https://api.github.com/repos/{self.config['repo_owner']}/{self.config['repo_name']}"
            
            response = httpx.get(url, headers=headers)
            response.raise_for_status()
            
            self.last_error = None
            return True
            
        except Exception as e:
            self.last_error = str(e)
            return False

    def execute(self, action: Action) -> ActionResult:
        """Execute GitHub action"""
        try:
            if not self.validate_config():
                raise ValueError(f"Invalid config: {self.last_error}")

            # Convert config list to dict for template rendering
            config_dict = {v.name: v.value for v in action.config}

            # Load and render template
            template = self.env.get_template('issue.jinja')
            payload = template.render(**config_dict)

            # Make GitHub API call
            headers = {'Authorization': f"token {config_dict['token']}"}
            url = f"https://api.github.com/repos/{config_dict['repo_owner']}/{config_dict['repo_name']}/issues"
            
            response = httpx.post(url, headers=headers, json=payload)
            response.raise_for_status()

            response_data = response.json()
            return ActionResult(
                action_id=action.id,
                request_id=str(uuid.uuid4()),
                success=True,
                result={
                    "status": "created",
                    "number": response_data["number"],
                    "url": response_data["html_url"]
                }
            )

        except Exception as e:
            return ActionResult(
                action_id=action.id,
                request_id=str(uuid.uuid4()),
                success=False,
                error=str(e)
            )
