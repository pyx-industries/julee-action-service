# Action Service Public API

This document describes the public-facing webhook API that external systems use to interact with the Action Service.

## Overview
The Public API is a lightweight, minimally-authenticated
service optimized for high-throughput, high-reliability,
low cost webhook reception.

The configuration of callback id (and web hook keys)
is not managed by this API. It uses a shared state mechanism
implemented with a common repository implementation
(i.e. the management api creates the callback addresses
and web hook keys, the public api uses them).

## Authentication
- Simple key-based validation (webhook_id must match key)
- No authentication headers required
- Designed for secure webhook handling

webhook keys may be single use, infinite use,
usabile at most some number of times,
or usable up until an expiry date time,
or a combination of max-times and not-after (date-time).

## Endpoints

### POST /webhooks/{webhook_id}
Submit webhook payload for processing.

- Authentication: `?key={key}`
- Request: ActionCallbackRequest
- Response: ActionAcceptedResponse
- Usecase: HandleCallback

If the webhook_id is valid,
and the key passes validation,
then the posted payload is stored,
and a submission id is generated,
and a processing job is dispatched
(for the submission id),
and the good news is returned in a a response
that includes the submission id.

Subsequently, the poster is able to GET
the status of the submission.

#### Request Format
```json
{
    "protocol_id": "string",
    "action_type_id": "string",
    "payload": {
        // Protocol-specific payload
    },
    "metadata": {
        // Optional metadata
    }
}
```

#### Response Format
```json
{
    "response_id": "uuid",
    "status": "accepted"
}
```

### GET /status/{response_id}
Check submission status.

- Authentication: None required
- Request: N/A
- Response: ActionStatusResponse
- Usecase: N/A (direct repository query)

#### Response Format
```json
{
    "request_id": "string",
    "correlation_id": "string",
    "status": "pending|processing|completed|failed",
    "completion_time": "datetime",
    "result": {
        // Result data if completed
    },
    "error": "string"  // Error message if failed
}
```

## Error Handling
Standard error responses:
```json
{
    "error": "error_code",
    "message": "Human readable message"
}
```

Common error codes:
- invalid_key
- invalid_webhook_id
- invalid_payload
- rate_limited

## Rate Limiting
- Per-webhook rate limits apply
- Headers indicate limit status:
  - X-RateLimit-Limit
  - X-RateLimit-Remaining
  - X-RateLimit-Reset
# Action Service Public API

This document describes the public-facing webhook API that external systems use to interact with the Action Service.

## Overview
The Public API is a lightweight, minimal-authentication service optimized for high-throughput webhook reception.

## Authentication
- Simple key-based validation (webhook_id must match key)
- No authentication headers required
- Designed for secure webhook handling

## Endpoints

### POST /webhooks/{webhook_id}
Submit webhook payload for processing.

- Authentication: `?key={key}`
- Request: ActionCallbackRequest
- Response: ActionAcceptedResponse
- Usecase: HandleCallback

#### Request Format
```json
{
    "protocol_id": "string",
    "action_type_id": "string",
    "payload": {
        // Protocol-specific payload
    },
    "metadata": {
        // Optional metadata
    }
}
```

#### Response Format
```json
{
    "response_id": "uuid",
    "status": "accepted"
}
```

### GET /status/{response_id}
Check submission status.

- Authentication: None required
- Request: N/A
- Response: ActionStatusResponse
- Usecase: N/A (direct repository query)

#### Response Format
```json
{
    "request_id": "string",
    "correlation_id": "string",
    "status": "pending|processing|completed|failed",
    "completion_time": "datetime",
    "result": {
        // Result data if completed
    },
    "error": "string"  // Error message if failed
}
```

## Error Handling
Standard error responses:
```json
{
    "error": "error_code",
    "message": "Human readable message"
}
```

Common error codes:
- invalid_key
- invalid_webhook_id
- invalid_payload
- rate_limited

## Rate Limiting
- Per-webhook rate limits apply
- Headers indicate limit status:
  - X-RateLimit-Limit
  - X-RateLimit-Remaining
  - X-RateLimit-Reset
