# Management API TODOs

```
Actions updated, deleted, and found
Credentials validated, safe and sound
Webhooks created, changed, and more
Messages flowing through every door

Each usecase crafted with care and skill
Every TODO item we did fulfill
The management API now complete
Ready to make our service fleet!
```

## New Usecases to Create

### Action Management
- [x] UpdateAction: Update action configuration
- [x] DeleteAction: Remove an action
- [x] GetAction: Get single action details

### Credential Management
- [x] UpdateCredential: Modify credential details
- [x] DeleteCredential: Remove stored credentials
- [x] ValidateCredential: Test if credentials are valid

### Webhook Management
- [x] CreateWebhook: Create new webhook endpoint
- [x] UpdateWebhook: Modify webhook configuration
- [x] DeleteWebhook: Remove webhook endpoint
- [x] ListWebhooks: Get all configured webhooks

### Message Management
- [x] CreateSystemMessage: Create new system notification
- [x] UpdateMessage: Modify message content
- [x] DeleteMessage: Remove message
- [x] AcknowledgeMessage: Mark message as seen
- [x] ListMessages: Query system messages

## Implementation Guidelines

### File Structure
```
action_service/
├── usecases/
│   ├── actions/
│   │   ├── update.py
│   │   ├── delete.py
│   │   └── get.py
│   ├── credentials/
│   │   ├── update.py
│   │   ├── delete.py
│   │   └── validate.py
│   ├── webhooks/
│   │   ├── create.py
│   │   ├── update.py
│   │   └── delete.py
│   └── messages/
│       ├── create.py
│       ├── update.py
│       └── delete.py
```

### Common Pattern
```python
class UpdateAction:
    """Update an existing action's configuration"""
    
    def __init__(self, reposet: RepoSet):
        self.action_repo = reposet["action_repository"]
        self.event_repo = reposet["event_repository"]
        
    def execute(self, request: UpdateActionRequest) -> ActionResponse:
        # Validate request
        # Update action
        # Record audit event
        # Return response
```

### Integration Points
1. Create new router files in `management_api/routers/`
2. Add new endpoints to existing routers
3. Update OpenAPI documentation
4. Add error handlers
5. Include new routers in main.py

### Testing Strategy
1. Create unit tests for each usecase
2. Create integration tests for API endpoints
3. Test error handling scenarios
4. Test validation rules
