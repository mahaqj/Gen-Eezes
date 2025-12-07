"""
Gmail API Email Sender

Uses Google Gmail API to send emails (instead of SMTP).
Perfect integration with existing Gmail credentials.

Author: Gen-Eezes Team
Date: December 2025
"""

import os
import base64
import logging
from typing import Tuple, Dict, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GmailAPISender:
    """
    Sends emails via Google Gmail API.
    
    No SMTP server needed - uses your Google account credentials.
    Perfect for newsletters, personalized bulk emails.
    
    Configuration via environment variables or direct parameters.
    
    Environment Variables:
    - GMAIL_CREDENTIALS_FILE: Path to credentials.json from Google OAuth
    - GMAIL_TOKEN_FILE: Path where token.json will be stored
    - SENDER_EMAIL: Your Gmail address (e.g., yourname@gmail.com)
    """
    
    GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    
    def __init__(
        self,
        credentials_file: str = None,
        token_file: str = None,
        sender_email: str = None
    ):
        """
        Initialize Gmail API sender.
        
        Args:
            credentials_file: Path to credentials.json from Google OAuth setup
            token_file: Path where token.json will be stored
            sender_email: Gmail address to send from
        """
        self.credentials_file = credentials_file or os.getenv("GMAIL_CREDENTIALS_FILE")
        self.token_file = token_file or os.getenv("GMAIL_TOKEN_FILE")
        self.sender_email = sender_email or os.getenv("SENDER_EMAIL")
        
        if not self.sender_email:
            raise ValueError(
                "Sender email not provided. Set SENDER_EMAIL environment variable "
                "or pass sender_email parameter."
            )
        
        # Authenticate with Gmail API
        try:
            self.service = self._authenticate()
            logger.info(f"✓ Gmail API authenticated as: {self.sender_email}")
        except Exception as e:
            logger.error(f"Failed to authenticate with Gmail API: {str(e)}")
            raise
    
    def _authenticate(self):
        """
        Authenticate with Google Gmail API.
        
        Handles OAuth flow and token refresh.
        """
        creds = None
        
        # Load existing token if available
        if self.token_file and os.path.exists(self.token_file):
            logger.info(f"Loading existing token from {self.token_file}")
            creds = Credentials.from_authorized_user_file(self.token_file, self.GMAIL_SCOPES)
        
        # If no valid credentials, create new flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired token...")
                creds.refresh(Request())
            else:
                if not self.credentials_file:
                    raise ValueError(
                        "credentials_file required. Download from Google Cloud Console "
                        "and set GMAIL_CREDENTIALS_FILE environment variable."
                    )
                
                logger.info(f"Creating new OAuth flow from {self.credentials_file}")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token for future use
            if self.token_file:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
                logger.info(f"Token saved to {self.token_file}")
        
        # Build and return Gmail API service
        return build('gmail', 'v1', credentials=creds)
    
    def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: str = None
    ) -> Tuple[bool, str]:
        """
        Send a single email via Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject line
            html_body: HTML version of email
            text_body: Plain text version (optional)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        
        if not text_body:
            # Create simple text version
            text_body = self._html_to_text(html_body)
        
        try:
            logger.info(f"Creating email to {to}: '{subject}'")
            
            # Create message
            message = MIMEMultipart("alternative")
            message["to"] = to
            message["from"] = self.sender_email
            message["subject"] = subject
            
            # Attach text and HTML parts
            part1 = MIMEText(text_body, "plain", _charset="utf-8")
            part2 = MIMEText(html_body, "html", _charset="utf-8")
            message.attach(part1)
            message.attach(part2)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send via Gmail API
            logger.info(f"Sending email to {to}...")
            result = self.service.users().messages().send(
                userId="me",
                body={"raw": raw_message}
            ).execute()
            
            logger.info(f"✓ Email sent successfully. Message ID: {result['id']}")
            return (True, f"Email sent to {to}")
        
        except HttpError as error:
            error_msg = f"Gmail API error: {error}"
            logger.error(error_msg)
            return (False, error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return (False, error_msg)
    
    def send_batch(
        self,
        emails: List[Dict[str, str]],
        delay_between_sends: int = 2
    ) -> Dict[str, Tuple[bool, str]]:
        """
        Send emails to multiple recipients.
        
        Args:
            emails: List of email dictionaries with keys:
                - 'to': Recipient email
                - 'subject': Email subject
                - 'html': HTML body
                - 'text': Text body (optional)
            delay_between_sends: Seconds to wait between emails
        
        Returns:
            Dictionary mapping recipient to (success, message) tuple
        """
        import time
        
        results = {}
        total = len(emails)
        
        logger.info(f"Starting batch send to {total} recipients")
        
        for idx, email_data in enumerate(emails, 1):
            recipient = email_data.get('to')
            subject = email_data.get('subject', 'No Subject')
            html = email_data.get('html', '')
            text = email_data.get('text')
            
            logger.info(f"\n[{idx}/{total}] Sending to {recipient}...")
            
            success, message = self.send_email(
                to=recipient,
                subject=subject,
                html_body=html,
                text_body=text
            )
            
            results[recipient] = (success, message)
            
            # Delay between sends (Gmail rate limiting)
            if idx < total:
                logger.info(f"Waiting {delay_between_sends}s before next email...")
                time.sleep(delay_between_sends)
        
        # Summary
        successful = sum(1 for success, _ in results.values() if success)
        logger.info(f"\n{'='*70}")
        logger.info(f"Batch send complete: {successful}/{total} successful")
        logger.info(f"{'='*70}")
        
        return results
    
    def send_test_email(self, test_recipient: str = None) -> Tuple[bool, str]:
        """
        Send a test email to verify Gmail API is working.
        
        Args:
            test_recipient: Email to send test to (defaults to self.sender_email)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        
        test_recipient = test_recipient or self.sender_email
        
        subject = "Gen-Eezes Newsletter - Gmail API Test"
        html_body = """
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h1>Test Email - Gmail API</h1>
                <p>This is a test email from <strong>Gen-Eezes Newsletter System</strong>.</p>
                <p>If you received this, Gmail API authentication is working correctly!</p>
                <hr>
                <p><small>Sent at: {}</small></p>
            </body>
        </html>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        text_body = "This is a test email from Gen-Eezes Newsletter System.\nIf you received this, Gmail API authentication is working correctly!"
        
        logger.info(f"Sending test email to {test_recipient}...")
        return self.send_email(test_recipient, subject, html_body, text_body)
    
    @staticmethod
    def _html_to_text(html: str) -> str:
        """Convert HTML to plain text by removing tags."""
        import re
        
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        
        # Remove HTML tags
        html = re.sub(r'<[^>]+>', '\n', html)
        
        # Decode HTML entities
        html = html.replace('&nbsp;', ' ')
        html = html.replace('&lt;', '<')
        html = html.replace('&gt;', '>')
        html = html.replace('&amp;', '&')
        html = html.replace('<br>', '\n')
        html = html.replace('<br/>', '\n')
        html = html.replace('<br />', '\n')
        
        # Remove extra whitespace
        lines = [line.strip() for line in html.split('\n')]
        text = '\n'.join(line for line in lines if line)
        
        return text


def main():
    """Test Gmail API email sender."""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*70)
    print("GMAIL API EMAIL SENDER TEST")
    print("="*70 + "\n")
    
    try:
        sender = GmailAPISender()
        
        print(f"✓ Gmail API Sender initialized")
        print(f"  From: {sender.sender_email}")
        
        print(f"\nTo test actual sending, set these environment variables:")
        print(f"  $env:GMAIL_CREDENTIALS_FILE = 'path/to/credentials.json'")
        print(f"  $env:GMAIL_TOKEN_FILE = 'path/to/token.json'")
        print(f"  $env:SENDER_EMAIL = 'your-email@gmail.com'")
        
        print(f"\n" + "="*70)
        print("Gmail API is ready to send newsletters!")
        print("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"Failed to initialize Gmail API sender: {str(e)}")


if __name__ == "__main__":
    main()
