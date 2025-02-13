"""
Email Protocol Implementation using IMAP

This protocol allows monitoring of email inboxes via IMAP, with support for:
- Checking new/unread messages
- Filtering by subject/sender
- Marking messages as read/unread
- Extracting message content
"""

import imaplib
import email
from email.message import EmailMessage
from typing import Dict, Any, Optional, List, Tuple
import uuid
from datetime import datetime

from ...pdk import ProtocolHandler
from ...domain import Action, ActionResult

class EmailProtocol(ProtocolHandler):
    """
    IMAP Email Protocol Handler
    
    Key Concepts:
    1. IMAP maintains message state using FLAGS
    2. \\Seen flag indicates read/unread status
    3. Message numbers are session-specific
    4. UIDs are permanent message identifiers
    """
    
    def validate_config(self) -> bool:
        """
        Validate IMAP configuration
        
        Required fields:
        - host: IMAP server hostname
        - username: Email account username
        - password: Email account password
        - folder: Mailbox folder to monitor (e.g. 'INBOX')
        
        Optional fields:
        - port: IMAP port (default: 993 for SSL)
        - use_ssl: Whether to use SSL (default: True)
        """
        required = ['host', 'username', 'password', 'folder']
        if not all(k in self.config for k in required):
            self.last_error = f"Missing required fields: {[k for k in required if k not in self.config]}"
            return False
            
        # Validate port if provided
        if 'port' in self.config:
            try:
                port = int(self.config['port'])
                if port < 1 or port > 65535:
                    self.last_error = "Port must be between 1 and 65535"
                    return False
            except ValueError:
                self.last_error = "Port must be a number"
                return False
                
        return True

    def test_connection(self) -> bool:
        """
        Test IMAP connection and folder access
        
        Steps:
        1. Connect to IMAP server
        2. Authenticate with credentials
        3. Try to select the target folder
        4. Verify read permissions
        """
        try:
            with self._get_connection() as client:
                # Try to select the folder - this tests both existence and permissions
                typ, data = client.select(self.config['folder'])
                if typ != 'OK':
                    self.last_error = f"Cannot access folder: {data[0].decode()}"
                    return False
                return True
        except Exception as e:
            self.last_error = f"Connection failed: {str(e)}"
            return False

    def execute(self, action: Action) -> ActionResult:
        """
        Execute email checking action
        
        Flow:
        1. Connect to IMAP server
        2. Select mailbox folder
        3. Search for messages matching criteria
        4. Fetch matching messages
        5. Process message content
        6. Update message flags if needed
        """
        try:
            with self._get_connection() as client:
                # Select the mailbox folder
                client.select(self.config['folder'])
                
                # Build search criteria from action config
                search_criteria = self._build_search_criteria(action.config)
                
                # Search for messages
                # IMAP SEARCH returns message numbers that match ALL criteria
                typ, message_numbers = client.search(None, *search_criteria)
                if typ != 'OK':
                    raise RuntimeError(f"Search failed: {message_numbers[0].decode()}")
                
                messages = []
                for num in message_numbers[0].split():
                    # Fetch message content
                    # Use BODY.PEEK instead of RFC822 to not mark as read automatically
                    typ, msg_data = client.fetch(num, '(BODY.PEEK[])')
                    if typ != 'OK':
                        continue
                        
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract message details
                    message = {
                        'id': num.decode(),
                        'subject': email_message['subject'],
                        'from': email_message['from'],
                        'date': email_message['date'],
                        'body': self._get_message_body(email_message)
                    }
                    messages.append(message)
                    
                    # Mark as seen if configured
                    # This explicitly sets the \\Seen flag
                    if action.config.get('mark_seen', True):
                        client.store(num, '+FLAGS', '\\\\Seen')
                
                return ActionResult(
                    action_id=action.id,
                    request_id=str(uuid.uuid4()),
                    success=True,
                    result={
                        'messages': messages,
                        'count': len(messages)
                    }
                )
                
        except Exception as e:
            return ActionResult(
                action_id=action.id,
                request_id=str(uuid.uuid4()),
                success=False,
                error=str(e)
            )

    def _get_connection(self) -> imaplib.IMAP4:
        """
        Create IMAP connection with proper SSL/TLS handling
        
        Note: Uses context manager pattern for automatic cleanup
        """
        if self.config.get('use_ssl', True):
            client = imaplib.IMAP4_SSL(
                host=self.config['host'],
                port=int(self.config.get('port', 993))
            )
        else:
            client = imaplib.IMAP4(
                host=self.config['host'],
                port=int(self.config.get('port', 143))
            )
            
        client.login(self.config['username'], self.config['password'])
        return client
        
    def _build_search_criteria(self, config: Dict[str, Any]) -> List[str]:
        """
        Build IMAP SEARCH command criteria
        
        IMAP SEARCH accepts space-separated criteria that are ANDed together.
        Common criteria:
        - UNSEEN: Messages without \\Seen flag
        - SUBJECT "text": Messages with text in subject
        - FROM "addr": Messages from specific address
        - SINCE "date": Messages after date
        """
        criteria = []
        
        # Add search filters
        if 'subject' in config:
            criteria.extend(['SUBJECT', config['subject']])
        if 'from' in config:
            criteria.extend(['FROM', config['from']])
        if 'since' in config:
            # IMAP date format: DD-Mon-YYYY
            if isinstance(config['since'], datetime):
                date_str = config['since'].strftime("%d-%b-%Y")
            else:
                date_str = config['since']
            criteria.extend(['SINCE', date_str])
        if config.get('unseen_only', False):
            criteria.append('UNSEEN')
            
        # Default to ALL if no criteria specified
        return criteria or ['ALL']
        
    def _get_message_body(self, message: EmailMessage) -> str:
        """
        Extract message body with proper handling of MIME parts
        
        Prefers text/plain over text/html for simplicity.
        Handles both multipart and simple messages.
        """
        if message.is_multipart():
            # Walk through message parts looking for text content
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
            # Fallback to first text part if no plain text
            for part in message.walk():
                if part.get_content_type().startswith("text/"):
                    return part.get_payload(decode=True).decode()
        else:
            # Simple messages can be decoded directly
            return message.get_payload(decode=True).decode()
        
        return ""  # Empty string if no text content found
