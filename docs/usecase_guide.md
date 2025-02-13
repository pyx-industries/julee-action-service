# Action Service Usecases Guide

This guide describes the four main types of usecases in the Action Service, using a chicken protection system as an example.

## 1. Sensory/Input Protocol Usecases

Generic sensory protocols handle incoming data and events from external systems. They must:
- Receive and validate incoming data
- Process and categorize information
- Assess significance/priority
- Route processed data appropriately
- Handle partial failures gracefully

**Example: Fox Detection Protocol**
- Receives webhook data from sentry cameras
- Validates detection report format
- Assesses threat confidence levels
- Routes threats based on severity:
  * Critical (95%+) → immediate response
  * Significant (90%+) → human review
  * Minor → logging only

### Message Processing Architecture

The Action Service implements a store-and-forward architecture for handling inbound messages:

1. **Initial Reception**
   - Messages are immediately acknowledged and stored
   - Quick validation of basic format only
   - Assign unique message ID and timestamp
   - Record source protocol and metadata

2. **Message States**
   - **Received** - Raw data stored, minimally validated
   - **Validated** - Format and content verified
   - **Processed** - Business logic applied
   - **Queued** - Awaiting delivery to Julee
   - **Delivering** - Actively trying to deliver
   - **Completed** - Successfully delivered
   - **Failed** - Terminal failure state after retries exhausted
   - **Expired** - Message exceeded freshness window

State transitions follow a linear progression with retry loops:
Received → Validated → Processed → Queued → Delivering → Completed
                                         ↑           ↓
                                         └───Retry───┘
                                                    ↓
                                            Failed/Expired
   
3. **Delivery Semantics**
   Each protocol implements specific delivery guarantees:

   - **At-Most-Once** (Best Effort)
     * Single delivery attempt
     * No retry on failure
     * Acceptable message loss
     * Use case: High-volume sensor readings
     * Example: Temperature telemetry

   - **At-Least-Once** (Guaranteed Delivery)
     * Persistent until delivered
     * Aggressive retry strategy
     * May deliver duplicates
     * Use case: Critical state changes
     * Example: Security alerts

   - **Exactly-Once** (Strong Consistency)
     * Transactional delivery
     * Deduplication enabled
     * Highest overhead
     * Use case: Financial updates
     * Example: Balance changes

   - **Eventually Consistent**
     * Background retry mechanism
     * Exponential backoff
     * Order not guaranteed
     * Use case: Configuration updates
     * Example: Policy changes

4. **Delivery Implementation**
   Implementation strategy follows delivery semantics:

   - **At-Most-Once Implementation**
     * Fire-and-forget delivery
     * No persistence required
     * Minimal system overhead
     * Fast failure detection

   - **At-Least-Once Implementation**
     * Persistent message store
     * Aggressive retry queue
     * Success acknowledgment required
     * Duplicate detection optional

   - **Exactly-Once Implementation**
     * Two-phase delivery
     * Message deduplication
     * Distributed transaction log
     * Strict ordering enforcement

   - **Eventually Consistent Implementation**
     * Background delivery queue
     * Exponential backoff retry
     * Conflict resolution handling
     * Best-effort ordering

### Failure Handling

The system handles various failure modes:

1. **Message Reception**
   - Network issues → Retry with backoff
   - Invalid format → Reject immediately
   - Storage errors → Emergency queue
   
2. **Validation & Processing**
   - Schema mismatch → Version handling
   - Missing fields → Apply defaults
   - Business rule violations → Human review
   
3. **Delivery Failures**
   - Julee unavailable → Queue and retry
   - Network partition → Store and wait
   - Rate limiting → Backoff strategy
   
4. **Recovery Strategies**
   - Automatic retry for transient issues
   - Circuit breaker for systemic problems
   - Human escalation for critical messages
   - Message archival for audit/replay

5. **Message Expiry**
   - Time-Critical: Fail fast, alert operator
   - Time-Sensitive: Try until expiry window
   - Eventually Consistent: Keep retrying
   
6. **Resource Management**
   - Disk space monitoring
   - Queue depth tracking
   - Throughput optimization
   - Load shedding when needed

## 2. Response/Output Protocol Usecases

Response protocols control external systems based on processed inputs. They must:
- Receive action requests
- Validate action parameters
- Execute system controls
- Monitor execution
- Report outcomes

**Example: Chicken Defense Protocol**
- Receives threat coordinates
- Validates targeting parameters
- Controls mud-flinger system
- Monitors defense execution
- Reports defense effectiveness

### Message Processing Architecture

The Action Service implements a staged delivery architecture for outbound messages:

1. **Initial Reception**
   - Messages queued for delivery
   - Validate format and parameters
   - Assign delivery tracking ID
   - Record target system metadata

2. **Message States**
   - **Queued** - Validated and awaiting delivery
   - **Preparing** - Transforming for target system
   - **Connecting** - Establishing target connection
   - **Delivering** - Active transmission
   - **Delivered** - Successfully received by target
   - **Failed** - Terminal failure after retries
   - **Cancelled** - Delivery cancelled by system
   - **Expired** - Exceeded delivery window

State transitions follow delivery semantics:
Queued → Preparing → Connecting → Delivering → Delivered
                               ↑           ↓
                          Retry Loop       ↓
                               ↑           ↓
                               └───────────┘
                                     ↓
                            Failed/Cancelled/Expired

3. **Delivery Patterns**

   - **Push Delivery**
     * Active outbound connection
     * Immediate delivery attempt
     * Connection management
     * Example: Webhook notifications

   - **Pull Delivery**
     * Passive endpoint exposure
     * Client-initiated retrieval
     * Request validation
     * Example: REST API endpoints

   - **Batch Delivery**
     * Grouped message delivery
     * Scheduled transmission
     * Batch size management
     * Example: Daily report emails

   - **Stream Delivery**
     * Continuous data flow
     * Back-pressure handling
     * Flow control
     * Example: Metrics streaming

4. **Delivery Semantics**

   - **Synchronous Delivery**
     * Immediate response required
     * Blocking operation
     * Strong consistency
     * Example: Critical commands

   - **Asynchronous Delivery**
     * Non-blocking operation
     * Background processing
     * Status polling
     * Example: Report generation

   - **Ordered Delivery**
     * Sequence preservation
     * Message ordering
     * Gap detection
     * Example: Transaction processing

   - **Unordered Delivery**
     * Independent messages
     * Parallel processing
     * Higher throughput
     * Example: Log shipping

### Failure Handling

The system implements comprehensive failure handling:

1. **Delivery Failures**
   - Connection issues → Retry with backoff
   - Target unavailable → Queue for retry
   - Invalid response → Error analysis
   - Timeout → Deadline checking

2. **Retry Strategies**
   - Exponential backoff
   - Circuit breaking
   - Fallback options
   - Dead letter queues

3. **Partial Failures**
   - Partial batch delivery
   - Individual message retry
   - Batch splitting
   - Progress tracking

4. **Recovery Procedures**
   - Automatic retry for transient issues
   - Manual intervention for critical messages
   - Failure notification
   - Audit logging

### Resource Management

1. **Rate Limiting**
   - Target system limits
   - Local capacity limits
   - Token bucket implementation
   - Adaptive rate control

2. **Backpressure Handling**
   - Queue depth monitoring
   - Flow control
   - Load shedding
   - Priority queuing

3. **Connection Management**
   - Connection pooling
   - Keep-alive handling
   - Resource cleanup
   - Health checking

4. **Queue Management**
   - Memory usage monitoring
   - Disk buffer management
   - Queue pruning
   - Priority scheduling

### Implementation Considerations

1. **Output Validation**
   - Parameter validation
   - Format verification
   - Schema compliance
   - Size limits

2. **Response Handling**
   - Status code processing
   - Response parsing
   - Error extraction
   - Success confirmation

3. **Error Reporting**
   - Structured error format
   - Error categorization
   - Error correlation
   - Debug information

4. **Performance Optimization**
   - Connection reuse
   - Batch optimization
   - Payload compression
   - Caching

5. **Monitoring and Metrics**
   - Delivery success rate
   - Response times
   - Error rates
   - Queue statistics
   - Resource utilization

## 3. Integration Usecases

Integration usecases handle the flow between protocols and external systems. They must:
- Transform data between formats
- Route information appropriately
- Handle errors gracefully
- Maintain system state
- Provide feedback loops

**Example: Fox Detection → Chicken Defense Integration**
- Transforms detection data into targeting coordinates
- Routes threats based on confidence levels
- Handles connection failures
- Maintains threat status
- Reports system effectiveness

## 4. Maintenance Usecases

Maintenance usecases ensure reliable system operation over time. They must:
- Monitor system health
- Track performance metrics
- Handle system failures
- Optimize configurations
- Validate operations
- Update system models

**Example: Chicken Protection System Maintenance**
- Monitors camera and defense system health
- Tracks response times and effectiveness
- Handles API outages
- Tunes threat thresholds
- Tests end-to-end operation
- Updates threat detection models

## Key Principles

When implementing any usecase:

1. **Clear Boundaries**
   - Each protocol handles one type of interaction
   - Clear input/output contracts
   - Well-defined responsibilities

2. **Independence**
   - Protocols work independently
   - No direct protocol-to-protocol coupling
   - Reusable with other systems

3. **Robustness**
   - Comprehensive error handling
   - Graceful degradation
   - Clear failure modes

4. **Observability**
   - Detailed logging
   - Performance metrics
   - Health monitoring

## Implementation Considerations

When implementing these usecases:

1. **Configuration**
   - What parameters are needed?
   - Which are required vs optional?
   - What are valid ranges/formats?

2. **Validation**
   - Input data format checking
   - Parameter validation
   - State validation

3. **Error Handling**
   - Expected error cases
   - Unexpected failures
   - Retry strategies

4. **Monitoring**
   - Health checks
   - Performance metrics
   - Usage statistics

5. **Testing**
   - Unit tests for logic
   - Integration tests for connections
   - End-to-end system tests
