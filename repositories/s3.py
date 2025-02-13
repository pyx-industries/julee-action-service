"""S3/MinIO implementation of webhook repository"""
import json
from typing import Optional, Dict, List
from datetime import datetime
from uuid import uuid4
import boto3
import base64
from ..log_utils import ActionServiceLogger
from botocore.exceptions import ClientError
from botocore.config import Config

from ..domain import Webhook, WebhookResult, EventStatus
from ..domain.direction import ActionDirection
from ..interfaces.repositories import WebhookRepository

class S3WebhookRepository(WebhookRepository):
    """S3/MinIO-backed webhook repository"""
    
    def __init__(
        self,
        endpoint_url: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        bucket: str,
        use_ssl: bool = True
    ):
        self.logger = ActionServiceLogger()
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            use_ssl=use_ssl,
            # Required for MinIO compatibility
            config=Config(signature_version='s3v4')
        )
        self.bucket = bucket
        
        # Ensure bucket exists
        try:
            self.client.head_bucket(Bucket=bucket)
        except ClientError:
            self.client.create_bucket(Bucket=bucket)

    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook by ID"""
        self.logger.debug(
            f"Fetching webhook {webhook_id} from bucket {self.bucket}, "
            f"path=webhooks/{webhook_id}.json"
        )
        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=f"webhooks/{webhook_id}.json"
            )
            data = json.loads(response['Body'].read())
            self.logger.debug(f"Successfully retrieved webhook {webhook_id}")
            return Webhook(
                id=data['id'],
                key=data['key'],
                config=data.get('config', {})
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                self.logger.debug(f"Webhook not found: {webhook_id}")
                return None
            self.logger.error(
                f"S3 error fetching webhook {webhook_id}: {str(e)}",
                exc_info=True
            )
            raise

    def store_webhook(self, webhook: Webhook) -> None:
        """Store webhook configuration"""
        data = {
            'id': webhook.id,
            'key': webhook.key,
            'config': webhook.config
        }
        self.client.put_object(
            Bucket=self.bucket,
            Key=f"webhooks/{webhook.id}.json",
            Body=json.dumps(data)
        )

    def delete_webhook(self, webhook_id: str) -> None:
        """Delete webhook configuration"""
        self.client.delete_object(
            Bucket=self.bucket,
            Key=f"webhooks/{webhook_id}.json"
        )

    def list_webhooks(self) -> List[Webhook]:
        """List all webhooks"""
        response = self.client.list_objects_v2(
            Bucket=self.bucket,
            Prefix="webhooks/"
        )
        webhooks = []
        for obj in response.get('Contents', []):
            webhook = self.get_webhook(
                obj['Key'].replace('webhooks/', '').replace('.json', '')
            )
            if webhook:
                webhooks.append(webhook)
        return webhooks

    def validate_key(self, webhook_id: str, key: str) -> bool:
        """Validate webhook key"""
        self.logger.debug(f"Validating key for webhook {webhook_id}")
        webhook = self.get_webhook(webhook_id)
        valid = webhook is not None and webhook.key == key
        if not valid:
            self.logger.error(f"Invalid key for webhook {webhook_id}")
        return valid

    def record_received(
        self,
        webhook_id: str,
        raw_headers: Dict[str, str],
        raw_body: bytes,
        content_type: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """Record received webhook data"""
        self.logger.debug(
            f"Recording webhook {webhook_id} with correlation_id {correlation_id}"
        )
        data = {
            'webhook_id': webhook_id,
            'headers': dict(raw_headers),  # Ensure headers are serializable
            'body': raw_body.decode('utf-8'),
            'direction': ActionDirection.normalize(ActionDirection.AFFERENT),
            'content_type': content_type,
            'correlation_id': correlation_id,
            'timestamp': datetime.now().isoformat()
        }
        # Generate response ID
        response_id = str(uuid4())

        self.client.put_object(
            Bucket=self.bucket,
            Key=f"received/{response_id}.json",
            Body=json.dumps(data)
        )

        return response_id

    def get_status(self, response_id: str) -> Optional[EventStatus]:
        """Get current processing status"""
        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=f"status/{response_id}.json"
            )
            data = json.loads(response['Body'].read())
            return EventStatus(
                id=response_id,
                state=data['state'],
                correlation_id=data.get('correlation_id')
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            raise

    def get_result(self, response_id: str) -> Optional[WebhookResult]:
        """Get webhook processing result"""
        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=f"results/{response_id}.json"
            )
            data = json.loads(response['Body'].read())
            return WebhookResult(
                id=response_id,
                success=data['success'],
                result=data.get('result'),
                error=data.get('error')
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            raise
