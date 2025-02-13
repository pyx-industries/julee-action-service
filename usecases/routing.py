"""Message routing usecases"""
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..domain import Action, ActionResult, RoutingRule, RoutingConfiguration
from ..interfaces.repositories import ActionRepository, EventRepository

class RouteMessage:
    """Route a message according to rules"""
    
    def __init__(self, message: Any, routing_config: RoutingConfiguration):
        self.message = message
        self.routing_config = routing_config
        
    def execute(self) -> List[str]:
        """Execute routing rules and return destination list"""
        destinations = []
        
        if self.routing_config.strategy == "first-match":
            # Return first matching rule
            for rule in self.routing_config.rules:
                if self._evaluate_condition(rule):
                    destinations.append(rule.destination)
                    break
                    
        elif self.routing_config.strategy == "all-matching":
            # Return all matching rules
            for rule in self.routing_config.rules:
                if self._evaluate_condition(rule):
                    destinations.append(rule.destination)
                    
        elif self.routing_config.strategy == "priority":
            # Sort by priority and return first match
            sorted_rules = sorted(
                self.routing_config.rules,
                key=lambda r: r.priority,
                reverse=True
            )
            for rule in sorted_rules:
                if self._evaluate_condition(rule):
                    destinations.append(rule.destination)
                    break
                    
        # Add fallback if no matches
        if not destinations and self.routing_config.fallback:
            destinations.append(self.routing_config.fallback.destination)
            
        return destinations
        
    def _evaluate_condition(self, rule: RoutingRule) -> bool:
        """Evaluate a routing rule condition"""
        if not rule.condition:
            return True
            
        # TODO: Implement condition evaluation
        return False
"""Routing-related usecases"""
from typing import List, Optional, Dict, Any
from ..domain import Action, RoutingRule, RoutingConfiguration
from ..interfaces.repositories import ActionRepository, EventRepository

class RouteMessage:
    """Route a message according to rules"""
    
    def __init__(self, action_repo: ActionRepository, event_repo: EventRepository):
        self.action_repo = action_repo
        self.event_repo = event_repo
        
    def execute(self, message: Dict[str, Any], rules: List[RoutingRule]) -> List[str]:
        """Route message and return list of destination IDs"""
        destinations = []
        
        for rule in sorted(rules, key=lambda r: r.priority, reverse=True):
            if self._evaluate_condition(rule.condition, message):
                destinations.append(rule.destination)
                if rule.config.get("stop_processing", False):
                    break
                    
        return destinations
        
    def _evaluate_condition(self, condition: Optional[str], message: Dict[str, Any]) -> bool:
        """Evaluate routing condition against message"""
        if not condition:
            return True
            
        # Simple condition evaluation for now
        # Could be enhanced with proper expression parsing
        try:
            # Get value from message using dot notation
            parts = condition.split('.')
            value = message
            for part in parts:
                value = value[part]
                
            return bool(value)
        except:
            return False

class ValidateRouting:
    """Validate routing configuration"""
    
    def __init__(self, action_repo: ActionRepository):
        self.action_repo = action_repo
        
    def execute(self, config: RoutingConfiguration) -> bool:
        """Validate routing configuration"""
        try:
            # Validate rules exist
            if not config.rules:
                return False
                
            # Validate destinations exist
            for rule in config.rules:
                if not self.action_repo.get_action(rule.destination):
                    return False
                    
            # Validate strategy
            if config.strategy not in ["first-match", "all-matching", "priority"]:
                return False
                
            # Validate fallback if specified
            if config.fallback:
                if not self.action_repo.get_action(config.fallback.destination):
                    return False
                    
            return True
            
        except Exception:
            return False
