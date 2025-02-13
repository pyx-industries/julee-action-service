from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from ..domain import Protocol
from ..interfaces.protocol import ProtocolHandler
from ..domain import Action, ActionResult

class GithubIssueConfig(BaseModel):
    """Configuration for GitHub issue creation"""
    model_config = ConfigDict(extra="forbid")
    
    repo_owner: str = Field(..., description="GitHub repository owner")
    repo_name: str = Field(..., description="GitHub repository name")
    title: str = Field(..., description="Issue title")
    body: str = Field(..., description="Issue body content")
    labels: List[str] = Field(default_factory=list, description="Issue labels")
    assignee: Optional[str] = Field(None, description="GitHub username to assign")
    token: str = Field(..., description="GitHub API token")

class GithubProtocol(ProtocolHandler):
    """Protocol implementation for GitHub issues"""
    
    def validate_config(self) -> bool:
        try:
            GithubIssueConfig(**self.config)
            self.last_error = None
            return True
        except Exception as e:
            self.last_error = str(e)
            return False
            
    def test_connection(self) -> bool:
        import httpx
        try:
            headers = {
                "Authorization": f"token {self.config['token']}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = httpx.get(
                f"https://api.github.com/repos/{self.config['repo_owner']}/{self.config['repo_name']}",
                headers=headers
            )
            response.raise_for_status()
            self.last_error = None
            return True
        except Exception as e:
            self.last_error = str(e)
            return False
            
    def execute(self, action: Action) -> ActionResult:
        import httpx
        try:
            # Validate config first
            if not self.validate_config():
                raise ValueError(f"Invalid config: {self.last_error}")
                
            headers = {
                "Authorization": f"token {self.config['token']}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Prepare issue data
            issue_data = {
                "title": self.config["title"],
                "body": self.config["body"],
                "labels": self.config["labels"]
            }
            if self.config.get("assignee"):
                issue_data["assignee"] = self.config["assignee"]
                
            # Create issue via GitHub API
            response = httpx.post(
                f"https://api.github.com/repos/{self.config['repo_owner']}/{self.config['repo_name']}/issues",
                headers=headers,
                json=issue_data
            )
            response.raise_for_status()
            
            return ActionResult(
                action_id=action.id,
                success=True,
                result=response.json()
            )
            
        except Exception as e:
            return ActionResult(
                action_id=action.id,
                success=False,
                error=str(e)
            )
