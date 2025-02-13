# Action Service Technical Specification

## Core Concepts

The Action Service is fundamentally an event broker that:
1. Publishes content from Julee to external systems ("Publishing")
2. Polls external systems and feeds content back to Julee ("Capturing")

## Publishing Scenarios

When Julee generates an artifact, it can be published through various channels:

### Communication Channels
- Email (SMTP)
  - Send artifact as attachment
  - Send artifact as formatted email body
  - Support for multiple recipients
  - Support for templates

- Messaging Platforms
  - Slack messages/threads
  - Microsoft Teams messages
  - Discord webhooks
  - Telegram messages

### Document Management
- SharePoint document upload
- Google Drive file creation
- Dropbox file sync
- OneDrive integration

### Task/Issue Management
- GitHub Issues
- Jira tickets
- Azure DevOps work items
- Trello cards
- Asana tasks

### Web Publishing
- WordPress posts
- Medium articles
- Custom website via API
- Static site generators

### Integration Platforms
- Zapier webhooks
- IFTTT triggers
- Microsoft Power Automate
- Custom webhooks

## Capture Scenarios

The Action Service can poll various sources for new content:

### Document Sources
- Email accounts (IMAP/POP3)
- SharePoint document libraries
- Google Drive folders
- Dropbox folders

### Web Sources
- RSS/Atom feeds
- Web page monitoring (detect changes)
- API endpoints (REST/GraphQL)

### Messaging Sources
- Slack channels
- Microsoft Teams channels
- Discord channels

### Task Systems
- GitHub Issues/PRs
- Jira ticket updates
- Azure DevOps changes

## Implementation Requirements

1. Message Queue Architecture
   - Handle asynchronous publishing
   - Manage polling schedules
   - Support retry logic
   - Track delivery status

2. Protocol Adapters
   - Modular design for different protocols
   - Consistent interface for adding new protocols
   - Configuration management for credentials

3. Content Transformation
   - Convert Julee artifacts to target formats
   - Transform captured content for Julee ingestion
   - Template support for formatting

4. Monitoring & Logging
   - Track success/failure of operations
   - Monitor polling health
   - Alert on failures
   - Audit trail of actions

5. Security
   - Credential management
   - Authentication to external services
   - Content encryption where needed
