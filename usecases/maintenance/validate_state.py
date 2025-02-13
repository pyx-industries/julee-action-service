"""System state validation usecase"""
from typing import Dict, Any, List
from datetime import datetime, UTC

from ...types import RepoSet
from ...domain import Connection, ConnectionStatus

class ValidateSystemState:
    """Check overall system health and component status
    
    This usecase performs comprehensive system health validation including:
    - Checking all required services are running
    - Validating database connections
    - Verifying external service connectivity
    - Checking queue depths and processing rates
    - Validating configuration consistency
    """
    
    def __init__(self, reposet: RepoSet):
        self.action_repo = reposet["action_repository"]
        self.event_repo = reposet["event_repository"]
        self.message_repo = reposet["message_repository"]
        self.connection_repo = reposet["connection_repository"]
        
    def execute(self) -> Dict[str, Any]:
        """
        Validate system state and component health.
        
        Returns:
            Dict containing validation results:
                status: Overall system status
                components: Status of individual components
                errors: List of validation errors
                warnings: List of validation warnings
                timestamp: Validation timestamp
        """
        results = {
            "status": "healthy",
            "components": {},
            "errors": [],
            "warnings": [],
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        try:
            # Check database connections
            db_status = self._check_database_connections()
            results["components"]["database"] = db_status
            if not db_status["connected"]:
                results["status"] = "error"
                results["errors"].append("Database connection failed")
            
            # Check external services
            service_status = self._check_external_services()
            results["components"]["external_services"] = service_status
            if service_status["errors"]:
                results["status"] = "degraded"
                results["errors"].extend(service_status["errors"])
            
            # Check queue status
            queue_status = self._check_queue_status()
            results["components"]["queues"] = queue_status
            if queue_status["warnings"]:
                results["warnings"].extend(queue_status["warnings"])
            
            # Check configuration
            config_status = self._validate_configuration()
            results["components"]["configuration"] = config_status
            if not config_status["valid"]:
                results["status"] = "error"
                results["errors"].extend(config_status["errors"])
            
            return results
            
        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"Validation failed: {str(e)}")
            return results
    
    def _check_database_connections(self) -> Dict[str, Any]:
        """Validate database connectivity"""
        try:
            # Test basic operations
            self.action_repo.get_action("test")
            self.event_repo.list_events(limit=1)
            return {
                "connected": True,
                "latency": 0  # TODO: Add actual latency check
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
    
    def _check_external_services(self) -> Dict[str, Any]:
        """Check external service connectivity"""
        results = {
            "total": 0,
            "available": 0,
            "errors": []
        }
        
        # Get all connections
        connections = self.connection_repo.list_connections()
        results["total"] = len(connections)
        
        for conn in connections:
            try:
                status = self.connection_repo.check_connection(conn.id)
                if status.severity == 0:  # Healthy
                    results["available"] += 1
                else:
                    results["errors"].append(
                        f"Service {conn.id} error: {conn.last_error}"
                    )
            except Exception as e:
                results["errors"].append(
                    f"Failed to check {conn.id}: {str(e)}"
                )
                
        return results
    
    def _check_queue_status(self) -> Dict[str, Any]:
        """Check message queue status"""
        results = {
            "depth": 0,
            "processing_rate": 0,
            "warnings": []
        }
        
        try:
            # Get queue metrics
            depth = self.event_repo.get_queue_depth()
            rate = self.event_repo.get_processing_rate()
            
            results["depth"] = depth
            results["processing_rate"] = rate
            
            # Check for concerning conditions
            if depth > 1000:  # TODO: Make configurable
                results["warnings"].append(
                    f"High queue depth: {depth} messages"
                )
            if rate < 10:  # TODO: Make configurable
                results["warnings"].append(
                    f"Low processing rate: {rate} msg/sec"
                )
                
        except Exception as e:
            results["warnings"].append(f"Queue check failed: {str(e)}")
            
        return results
    
    def _validate_configuration(self) -> Dict[str, Any]:
        """Validate system configuration"""
        results = {
            "valid": True,
            "errors": []
        }
        
        try:
            # TODO: Add actual config validation
            # For now just return valid
            pass
            
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Config validation failed: {str(e)}")
            
        return results
