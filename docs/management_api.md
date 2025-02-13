# Action Service Management API

This document describes the authenticated management API used by Julee and administrators to configure and monitor the Action Service.

## Authentication
- Bearer token authentication required
- API key authentication supported
- Role-based access control

## API to Usecase Mapping

### Action Management

#### POST /actions/
Create and execute new action.
- Request: ExecuteActionRequest
- Response: ActionAcceptedResponse
- Usecase: ExecuteAction

#### GET /actions/{action_id}/status
Check action execution status.
- Request: N/A
- Response: ActionStatusResponse
- Usecase: N/A (direct repository query)

### Protocol Management

#### GET /protocols/
List available protocols.
- Request: N/A
- Response: ProtocolListResponse
- Usecase: N/A (direct repository query)

#### GET /protocols/{protocol_id}
Get protocol details/schema.
- Request: N/A
- Response: ProtocolResponse
- Usecase: N/A (direct repository query)

#### GET /protocols/{protocol_id}/status
Check protocol connection status.
- Request: N/A
- Response: ConnectionStatusResponse
- Usecase: N/A (direct repository query)

### Monitoring Endpoints

#### GET /monitor/streams/{stream_id}/health
Check stream health status.
- Request: N/A
- Response: MonitorResponse
- Usecase: MonitorStreamHealth

#### GET /monitor/protocols/{protocol_id}/metrics
Get protocol metrics.
- Request: N/A
- Response: MonitorResponse
- Usecase: CollectProtocolMetrics

#### GET /monitor/actions/{action_id}/metrics
Get action metrics.
- Request: N/A
- Response: MonitorResponse
- Usecase: TrackDeliveryMetrics

## Standard Response Format
```json
{
    "request_id": "uuid",
    "status": "success|accepted|pending|failed",
    "data": {
        // Response-specific data
    },
    "metadata": {
        "timestamp": "ISO-8601"
    }
}
```

## Error Handling
```json
{
    "request_id": "uuid",
    "status": "error",
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {
            // Error-specific details
        }
    }
}
```

## Rate Limiting
- Per-client rate limits
- Per-endpoint limits
- Burst allowances supported

## Versioning
- URL versioning (/v1/)
- API-Version header support
# Action Service Management API

This document describes the authenticated management API used by Julee and administrators to configure and monitor the Action Service.

## Authentication
- Bearer token authentication required
- API key authentication supported
- Role-based access control

## API to Usecase Mapping

### Action Management

#### POST /actions/
Create and execute new action.
- Request: ExecuteActionRequest
- Response: ActionAcceptedResponse
- Usecase: ExecuteAction

#### GET /actions/{action_id}/status
Check action execution status.
- Request: N/A
- Response: ActionStatusResponse
- Usecase: N/A (direct repository query)

### Protocol Management

#### GET /protocols/
List available protocols.
- Request: N/A
- Response: ProtocolListResponse
- Usecase: N/A (direct repository query)

#### GET /protocols/{protocol_id}
Get protocol details/schema.
- Request: N/A
- Response: ProtocolResponse
- Usecase: N/A (direct repository query)

#### GET /protocols/{protocol_id}/status
Check protocol connection status.
- Request: N/A
- Response: ConnectionStatusResponse
- Usecase: N/A (direct repository query)

### Monitoring Endpoints

#### GET /monitor/streams/{stream_id}/health
Check stream health status.
- Request: N/A
- Response: MonitorResponse
- Usecase: MonitorStreamHealth

#### GET /monitor/protocols/{protocol_id}/metrics
Get protocol metrics.
- Request: N/A
- Response: MonitorResponse
- Usecase: CollectProtocolMetrics

#### GET /monitor/actions/{action_id}/metrics
Get action metrics.
- Request: N/A
- Response: MonitorResponse
- Usecase: TrackDeliveryMetrics

## Standard Response Format
```json
{
    "request_id": "uuid",
    "status": "success|accepted|pending|failed",
    "data": {
        // Response-specific data
    },
    "metadata": {
        "timestamp": "ISO-8601"
    }
}
```

## Error Handling
```json
{
    "request_id": "uuid",
    "status": "error",
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {
            // Error-specific details
        }
    }
}
```

## Rate Limiting
- Per-client rate limits
- Per-endpoint limits
- Burst allowances supported

## Versioning
- URL versioning (/v1/)
- API-Version header support
