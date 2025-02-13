# Work In Progress

This document tracks the implementation status of usecases and repositories in the action service.

To maintain this document:
1. Review all usecase files in action_service/usecases/
2. For each usecase, identify repository methods it depends on
3. Review all repository implementations in action_service/repositories/
4. For each repository class, identify which methods are implemented and where they are used
5. Update the sections below to reflect current state

## Usecases

### ExecuteAction (execute.py)
- action_repo.get_action()
- behaviour_repo.get_protocol_handler()
- credential_repo.get_credential()
- event_repo.record_success()
- event_repo.record_failure()

### HandleCallback (webhooks.py)
- webhook_repo.get_webhook()
- webhook_repo.validate_key()
- event_repo.record_received()

### HandleInboundMessage (actions.py)
- behaviour_repo.get_protocol()
- message_repo.store_message()
- event_repo.record_received()

### HandlePushDelivery (delivery.py)
- event_repo.record_event()
- action_repo.execute()
- event_repo.record_success()
- event_repo.record_failure()
- result_repo.store_result()

### TrackDeliveryMetrics (monitoring.py)
- event_repo.record_event()
- event_repo.list_events()

### MonitorStreamHealth (monitoring.py)
- event_repo.list_events()
- event_repo.record_event()

## Repositories

### ActionRepository
- get_action()
  - Implemented in InMemoryActionRepository
  - Used by ExecuteAction usecase
  - Stub implementation in PostgresStreamRepository

- execute()
  - Implemented in HttpActionRepository
  - Used by HandlePushDelivery usecase

### EventRepository
- record_event()
  - Implemented in InMemoryEventRepository, PostgresEventRepository
  - Used by TrackDeliveryMetrics, MonitorStreamHealth

- record_success()
  - Implemented in HttpEventRepository, InMemoryEventRepository
  - Used by ExecuteAction, HandlePushDelivery

- record_failure() 
  - Implemented in HttpEventRepository, InMemoryEventRepository
  - Used by ExecuteAction, HandlePushDelivery

- list_events()
  - Implemented in InMemoryEventRepository
  - Used by TrackDeliveryMetrics, MonitorStreamHealth
  - Stub implementation in PostgresEventRepository

### WebhookRepository
- get_webhook()
  - Implemented in InMemoryWebhookRepository, S3WebhookRepository
  - Used by HandleCallback

- validate_key()
  - Implemented in InMemoryWebhookRepository, S3WebhookRepository
  - Used by HandleCallback

### BehaviourRepository
- get_protocol()
  - Implemented in HardcodedBehaviourCatalogue
  - Used by HandleInboundMessage

- get_protocol_handler()
  - Implemented in HardcodedBehaviourCatalogue
  - Used by ExecuteAction

### MessageRepository
- store_message()
  - Implemented in InMemoryMessageRepository
  - Used by HandleInboundMessage

### ResultRepository
- store_result()
  - Implemented in InMemoryResultRepository
  - Used by HandlePushDelivery
