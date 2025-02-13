"""External service synchronization usecase"""
from typing import Dict, Any, List
from datetime import datetime, UTC

from ...types import RepoSet
from ...domain import Connection, ConnectionStatus

class SyncExternalServices:
    """Ensure external service connectivity and configuration sync
    
    This usecase handles synchronizing state with external services, including:
    - Verifying connectivity to all configured services
    - Ensuring configuration is in sync
    - Updating local connection status
    - Recording sync events and any errors
    """
    
    def __init__(self, reposet: RepoSet):
        self.connection_repo = reposet["connection_repository"]
        self.event_repo = reposet["event_repository"]
        
    def execute(self) -> Dict[str, Any]:
        """
        Synchronize with external services.
        
        Returns:
            Dict containing sync results:
                total: Total number of services
                synced: Number successfully synced
                failed: Number of sync failures
                errors: List of sync errors
        """
        results = {
            "total": 0,
            "synced": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            # Get all connections
            connections = self.connection_repo.list_connections()
            results["total"] = len(connections)
            
            # Sync each connection
            for conn in connections:
                try:
                    # Check connectivity
                    status = self.connection_repo.check_connection(conn.id)
                    
                    if status.severity == 0:  # Healthy
                        # Sync configuration
                        self._sync_config(conn)
                        results["synced"] += 1
                        
                        # Record sync event
                        self._record_sync(conn)
                    else:
                        error = f"Connection {conn.id} unhealthy: {conn.last_error}"
                        results["errors"].append(error)
                        results["failed"] += 1
                        
                        # Record failure
                        self._record_failure(conn, error)
                        
                except Exception as e:
                    error = f"Failed to sync {conn.id}: {str(e)}"
                    results["errors"].append(error)
                    results["failed"] += 1
                    self._record_failure(conn, error)
                    
            return results
            
        except Exception as e:
            results["errors"].append(f"Sync operation failed: {str(e)}")
            return results
            
    def _sync_config(self, connection: Connection) -> None:
        """Sync configuration with external service"""
        # Get remote config
        remote_config = self.connection_repo.get_remote_config(connection.id)
        
        # Update local config if needed
        if remote_config != connection.config:
            self.connection_repo.update_config(
                connection.id,
                remote_config
            )
            
    def _record_sync(self, connection: Connection) -> None:
        """Record successful sync"""
        self.event_repo.record_event(
            action_id="system",
            direction="system",
            content={
                "connection_id": connection.id,
                "status": "synced"
            },
            content_type="sync",
            metadata={
                "synced_at": datetime.now(UTC).isoformat()
            }
        )
        
    def _record_failure(self, connection: Connection, error: str) -> None:
        """Record sync failure"""
        self.event_repo.record_event(
            action_id="system",
            direction="system", 
            content={
                "connection_id": connection.id,
                "status": "failed",
                "error": error
            },
            content_type="sync",
            metadata={
                "failed_at": datetime.now(UTC).isoformat()
            }
        )
