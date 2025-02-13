"""
Shared pytest fixtures for action service tests
"""
import pytest
from action_service.domain import Action, ActionType, Protocol

@pytest.fixture
def catalogue():
    from action_service.repositories.behaviour import HardcodedBehaviourCatalogue
    return HardcodedBehaviourCatalogue()

@pytest.fixture
def sample_action(catalogue):
    """Provide a sample action for testing"""
    return Action(
        id="test-1",
        name="Test Action",
        description="Test action for unit tests",
        action_type=catalogue.get_action_type("fetch"),
        protocol=catalogue.get_protocol("http"),
        config={
            "url": "https://test.example.com/api",
            "method": "GET"
        }
    )
