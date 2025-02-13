"""Base plugin architecture for Action Service"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..domain import Action, ActionResult, Protocol

class ActionPlugin(ABC):
    """Base class for all action plugins"""
    
    @property
    @abstractmethod
    def protocol(self) -> Protocol:
        """The protocol this plugin handles"""
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate plugin-specific configuration
        Raises ValidationError if invalid
        """
        pass

    @abstractmethod
    def execute(self, action: Action, input_data: Optional[Any] = None) -> ActionResult:
        """Execute the action"""
        pass

class PluginRegistry:
    """Central registry of available plugins"""
    
    def __init__(self):
        self._plugins: Dict[Protocol, ActionPlugin] = {}

    def register(self, plugin: ActionPlugin) -> None:
        """Register a plugin for a protocol"""
        self._plugins[plugin.protocol] = plugin

    def get_plugin(self, protocol: Protocol) -> Optional[ActionPlugin]:
        """Get plugin for protocol"""
        return self._plugins.get(protocol)

    def list_protocols(self) -> list[Protocol]:
        """List supported protocols"""
        return list(self._plugins.keys())
