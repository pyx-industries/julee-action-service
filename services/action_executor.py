"""Action Execution Service"""
from typing import Optional, Any
from ..domain import Action, ActionResult, Protocol
from ..plugins.base import PluginRegistry

class ActionExecutionService:
    def __init__(self, plugin_registry: PluginRegistry):
        self.registry = plugin_registry

    def execute_action(self, action: Action, input_data: Optional[Any] = None) -> ActionResult:
        # Get appropriate plugin
        plugin = self.registry.get_plugin(action.protocol)
        if not plugin:
            return ActionResult(
                action_id=action.id,
                success=False,
                error=f"No plugin found for protocol: {action.protocol}"
            )

        # Execute via plugin
        return plugin.execute(action, input_data)
