# Action Service Public API Design

This document outlines the design of the Action Service's public webhook API, which provides an interface for external systems to submit data to Julee.

## Service Split

The Action Service exposes two distinct APIs with different security models and use cases. This document focuses on the public Webhook Receiver Service.

### Webhook Receiver Service
A lightweight, minimal-authentication service for receiving webhooks from external systems:

```http
POST /webhooks/{webhook_id}?key={key}  # Submit webhook payload
GET /status/{response_id}              # Check submission status
```

Key characteristics:
- Simple key-based validation only (webhook_id must match key)
- No authentication headers required
- Optimized for high-throughput webhook reception
- Returns response_id for status tracking
- Can run on separate infrastructure/ports for security isolation

Note: Webhook configurations and API keys are managed through the internal Management API.

## Implementation Requirements

### Asynchronous Operation Pattern

1. **Immediate Response**
   - API returns 202 Accepted with response tracking ID
   - Operation queued for worker service

2. **Status Checking**
   - Clients poll status endpoint using tracking ID
   - Status includes completion state and result/error

3. **Worker Communication**
   - API service dispatches work to worker service
   - Uses message queue for reliable delivery
   - Handles worker failures and retries

### Standard Response Formats

```json
// Success Response
{
    "response_id": "uuid",
    "status": "accepted",
    "timestamp": "ISO-8601"
}

// Error Response
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message"
    },
    "timestamp": "ISO-8601"
}
```

### Error Handling

1. **HTTP Status Codes**
   - 202: Accepted
   - 400: Invalid request
   - 401: Invalid API key
   - 429: Rate limit exceeded
   - 500: Server error

2. **Error Categories**
   - Validation errors
   - Authentication errors
   - Rate limiting
   - Server errors

### Rate Limiting

Protection against abuse:
- Per-webhook rate limits
- Burst allowances configurable per webhook
- Standard rate limit headers in responses

## Security Considerations

1. **API Key Validation**
   - Keys must be pre-configured per webhook
   - Keys stored securely in credential store
   - Key rotation supported

2. **Input Validation**
   - Strict payload size limits
   - Content type validation
   - Schema validation per webhook

3. **Infrastructure**
   - Can be deployed separately from internal APIs
   - Network isolation possible
   - Independent scaling
