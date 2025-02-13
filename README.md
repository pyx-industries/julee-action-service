# Action Service

This is an early Work In Progress (WIP),
to implement a reference implementation
of the julee architecture action service.

The the action service is the only component
that interacts directly with the outside world.

You might like to think of it as having 3 kinds of interaction:
- action configuration, performed by the orchestrator component
- afferent flows, where information comes from the outside world
- efferent flows, where action is taken that impacts the world

## Implementation Strategy

This reference implementation uses a familiar pattern
of two "12-factor" containers plus supporting services
(e.g. data, event queue, etc).

The api container:
- surfaces a public interface (used by both afferent and efferent flows)
- sufraces a private interface (used by the orchestrator)
- accesses backing services
- dispatches IO-bound tasks to the message queue

The worker container:
- accesses backing services
- retrieves IO-bound tasks from the message queue
- interacts with the outside world as required

## Logical Model

The core concepts are "protocols", "actions" and "events".
An action is essentially a protocol instance.
An action is not atomic, it's a sequence of events.

- Protocols are implemented in code and are designed to be "generic and useful".
- Actions are related to a protocol. They encapsulate the config needed to execute the protocol.
- Events are generic structured logs 

The configuration establishes endpoints and rules
that allow actions to be taken.
A system integrator should be able to confgigure the action service
with minimal coding, if the protocols they need are already implemented.
Or they can implement custom protocols if required by their situation.

### 1. Protocol (Interface)
- Capabilities: validate_config, test_connection, execute
- Each implementation knows how to talk to one type of system
- Must be self-contained and handle all its own errors
- Protocols are independent and reusable

### 2. Action (Data Structure)
- References a protocol
- Contains configuration for that protocol
- Optional scheduling information
- Optional data transformations
- Actions are just data/configuration

### 3. Event (Data Structure)
- Records everything that happens
- Immutable
- Contains timestamps, correlation IDs, results
- Provides audit trail and debugging

### 4. Repository (Interface)
- Stores actions, events, results
- Could be in-memory, database, etc
- Must be consistent
- Handles persistence concerns

## System Flow

1. **Protocol Definition**
```
Protocol needs:
  - Configuration schema
  - Validation logic
  - Connection testing
  - Execution logic
  - Error handling
```

2. **Action Creation**
```
Action contains:
  - Unique ID
  - Protocol reference
  - Configuration data
  - Optional transforms
  - Optional scheduling
```

3. **Execution Flow**
```
When trigger received:
  create event(type="trigger_received")
  
  get action(action_id)
  get protocol(action.protocol)
  
  validate protocol.config
  if not valid:
    record_failure("invalid_config")
    return
    
  transform data if needed
  
  result = protocol.execute(data)
  
  record event(
    type="action_executed",
    action_id=action.id,
    success=result.success,
    error=result.error
  )
```

## Key Design Principles

1. **Independence**
   - Protocols are self-contained
   - Actions are just configuration
   - Events are immutable
   - Repositories are interchangeable

2. **Reliability**
   - Everything is recorded
   - Failures handled at every step
   - Clear audit trail
   - Consistent state

3. **Simplicity**
   - Core service just orchestrates
   - Clear separation of concerns
   - Minimal dependencies
   - Easy to extend

## Implementation Strategy

1. Start with:
   - Basic Protocol interface
   - Simple Action structure
   - In-memory Repository
   - Event logging

2. Add features:
   - More protocols
   - Data transforms
   - Scheduling
   - Persistent storage
   - Monitoring

3. Scale with:
   - Multiple workers
   - Load balancing
   - Rate limiting
   - Caching
   - Advanced monitoring

