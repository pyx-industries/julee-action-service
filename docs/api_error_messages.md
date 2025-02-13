# API Error Message Handling Strategy

## Overview

This document outlines the error handling strategy for Action Service APIs, focusing on security, observability, and proper error management.

## Core Principles

1. **Security First**
   - Never expose internal system details in responses
   - Sanitize all error messages
   - Log detailed errors internally
   - Return generic messages externally

2. **Proper Error Classification**
   - Exceptions indicate bugs that need investigation
   - Expected failure cases should be handled gracefully
   - Use logging levels appropriately
   - Enable comprehensive debugging when needed

3. **Observability**
   - INFO: Track normal operations
   - WARNING: Note potential issues
   - ERROR: Flag actual bugs needing investigation
   - DEBUG: Enable detailed troubleshooting
   - Use correlation IDs for request tracing

## Standard Error Response Format

```json
{
    "error": {
        "message": "A user-friendly message",
        "reference_id": "unique-error-id"
    }
}
```

## Error Handling Guidelines

### Expected vs Unexpected Failures

Expected failures (handled gracefully):
- Invalid input validation
- Resource not found
- Permission denied
- Rate limiting

Unexpected failures (throw exceptions):
- Database connection failures
- Unhandled edge cases
- Configuration errors
- Integration failures

### Implementation Example

```python
async def get_action(action_id: str):
    try:
        # Log operation attempt
        logger.info(f"Retrieving action {action_id}")
        
        # Handle expected failure case
        action = repo.get_action(action_id)
        if not action:
            logger.warning(f"Action {action_id} not found")
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "message": "Action not found",
                        "reference_id": generate_reference_id()
                    }
                }
            )
            
        # Log success and return
        logger.info(f"Successfully retrieved action {action_id}")
        return action
        
    except Exception as e:
        # Log unexpected error with full details
        error_id = generate_reference_id()
        logger.error(
            f"Unexpected error retrieving action: {str(e)}",
            exc_info=True,
            extra={
                "error_id": error_id,
                "action_id": action_id
            }
        )
        
        # Return sanitized response
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "An unexpected error occurred",
                    "reference_id": error_id
                }
            }
        )
```

## Security Considerations

### Never Expose in Responses:
- Stack traces
- Database errors
- System paths
- Internal IPs/hostnames
- Configuration details
- Dependency versions

### Always Log Internally:
- Full exception details
- Stack traces
- Request context
- System state
- Configuration context

## Development vs Production

### Development
- Enable detailed logging to stdout
- Include debug information in logs
- Use structured logging format
- Never include sensitive data in responses

### Production
- Use proper logging service (e.g., Sentry)
- Enable error aggregation and alerting
- Maintain security standards
- Track error patterns
- Alert on unexpected errors

## Implementation Checklist

1. [ ] Set up proper logging configuration
2. [ ] Implement global exception handler
3. [ ] Configure error tracking service
4. [ ] Set up monitoring alerts
5. [ ] Create error response models
6. [ ] Add security headers
7. [ ] Document troubleshooting procedures

## Monitoring and Maintenance

- Monitor error frequencies
- Set up alerts for unexpected errors
- Regular security reviews
- Update documentation
- Review logging effectiveness
- Adjust logging levels as needed
