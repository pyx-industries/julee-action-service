"""Celery tasks"""
from .worker import app
from .settings import get_reposet
from ..usecases.execute import ExecuteAction

@app.task
def process_action(action_id: str, retry_count: int = 0):
    """Process an action"""
    reposet = get_reposet()
    usecase = ExecuteAction(reposet)
    
    try:
        result = usecase.execute(action_id=action_id, retry_count=retry_count)
        return result.dict()
    except Exception as e:
        # Handle retries here if needed
        raise
