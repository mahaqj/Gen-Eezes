"""
Email Sender Module

Handles SMTP email delivery for newsletters.
Supports Gmail and other SMTP providers with authentication.

Author: Gen-Eezes Team
Date: December 2025
"""

import os
import smtplib
import logging
from typing import List, Dict, Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class EmailSender:
    """
    Handles email delivery via SMTP.
    
    Supports both text and HTML emails, batch sending, and error recovery.
    Configuration via environment variables or direct parameters.
    
    Environment Variables:
    - SMTP_SERVER: SMTP server address (default: smtp.gmail.com)
    - SMTP_PORT: SMTP port (default: 587)
    - SENDER_EMAIL: Email address to send from
    - SENDER_PASSWORD: Email password or app-specific password
    - USE_TLS: Whether to use TLS (default: True)
    """
    
    def __init__(
        self,
        smtp_server: str = None,
        smtp_port: int = None,
        sender_email: str = None,
        sender_password: str = None,
        use_tls: bool = True
    ):
        """
        Initialize email sender with SMTP configuration.
        
        Args:
            smtp_server: SMTP server address. If None, uses SMTP_SERVER env var or gmail default.
            smtp_port: SMTP port. If None, uses SMTP_PORT env var or 587 default.
            sender_email: Email address to send from. If None, uses SENDER_EMAIL env var.
            sender_password: Email password. If None, uses SENDER_PASSWORD env var.
            use_tls: Whether to use TLS encryption (default: True for Gmail).
        """
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = sender_email or os.getenv("SENDER_EMAIL")
        self.sender_password = sender_password or os.getenv("SENDER_PASSWORD")
        self.use_tls = use_tls
        
        # Validate configuration
        if not self.sender_email:
            raise ValueError(
                "Sender email not provided. Set SENDER_EMAIL environment variable "
                "or pass sender_email parameter."
            )
        if not self.sender_password:
            raise ValueError(
                "Sender password not provided. Set SENDER_PASSWORD environment variable "
                "or pass sender_password parameter."
            )
        
        logger.info(
            f"Initialized EmailSender: {self.sender_email} @ {self.smtp_server}:{self.smtp_port}"
        )
    
    def send_email(
        self,
        recipient_email: str,
        subject: str,
        html_body: str,
        text_body: str = None,
        retry_count: int = 3,
        retry_delay: int = 5
    ) -> Tuple[bool, str]:
        """
        Send a single email.
        
        Args:
            recipient_email: Email address to send to
            subject: Email subject line
            html_body: HTML version of email body
            text_body: Plain text version (optional, for fallback)
            retry_count: Number of retries on failure (default: 3)
            retry_delay: Seconds to wait between retries (default: 5)
        
        Returns:
            Tuple of (success: bool, message: str)
            - (True, "Email sent successfully") on success
            - (False, "Error message") on failure after retries
        """
        
        if not text_body:
            # Create simple text version by stripping HTML tags
            text_body = self._html_to_text(html_body)
        
        logger.info(f"Preparing email to {recipient_email}: '{subject}'")
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender_email
        message["To"] = recipient_email
        message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        # Attach text and HTML parts
        text_part = MIMEText(text_body, "plain")
        html_part = MIMEText(html_body, "html")
        
        message.attach(text_part)
        message.attach(html_part)
        
        # Attempt to send with retries
        for attempt in range(1, retry_count + 1):
            try:
                logger.info(f"Sending email attempt {attempt}/{retry_count}...")
                
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                    if self.use_tls:
                        server.starttls()
                    
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(message)
                
                logger.info(f"✓ Email sent successfully to {recipient_email}")
                return (True, f"Email sent to {recipient_email}")
            
            except smtplib.SMTPException as e:
                error_msg = f"SMTP error: {str(e)}"
                logger.warning(f"{error_msg} (attempt {attempt}/{retry_count})")
                
                if attempt < retry_count:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed to send email after {retry_count} attempts: {error_msg}")
                    return (False, error_msg)
            
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(f"{error_msg} (attempt {attempt}/{retry_count})")
                
                if attempt < retry_count:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed to send email after {retry_count} attempts: {error_msg}")
                    return (False, error_msg)
        
        return (False, "Unknown error - max retries exceeded")
    
    def send_batch(
        self,
        emails: List[Dict[str, str]],
        delay_between_sends: int = 2
    ) -> Dict[str, Tuple[bool, str]]:
        """
        Send emails to multiple recipients.
        
        Args:
            emails: List of email dictionaries with keys:
                - 'recipient': Email address
                - 'subject': Email subject
                - 'html': HTML body
                - 'text': Text body (optional)
            delay_between_sends: Seconds to wait between sending each email (default: 2)
        
        Returns:
            Dictionary mapping recipient email to (success, message) tuple
        """
        
        results = {}
        total = len(emails)
        
        logger.info(f"Starting batch send to {total} recipients")
        
        for idx, email_data in enumerate(emails, 1):
            recipient = email_data.get('recipient')
            subject = email_data.get('subject', 'No Subject')
            html = email_data.get('html', '')
            text = email_data.get('text')
            
            logger.info(f"\n[{idx}/{total}] Sending to {recipient}...")
            
            success, message = self.send_email(
                recipient_email=recipient,
                subject=subject,
                html_body=html,
                text_body=text
            )
            
            results[recipient] = (success, message)
            
            # Delay between sends to avoid rate limiting
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
        Send a test email to verify configuration.
        
        Args:
            test_recipient: Email address to send test to. If None, sends to self.sender_email.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        
        test_recipient = test_recipient or self.sender_email
        
        subject = "Gen-Eezes Newsletter - Test Email"
        html_body = """
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h1>Test Email</h1>
                <p>This is a test email from <strong>Gen-Eezes Newsletter System</strong>.</p>
                <p>If you received this, SMTP configuration is working correctly!</p>
                <hr>
                <p><small>Sent at: {}</small></p>
            </body>
        </html>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        text_body = "This is a test email from Gen-Eezes Newsletter System.\nIf you received this, SMTP configuration is working correctly!"
        
        logger.info(f"Sending test email to {test_recipient}...")
        return self.send_email(test_recipient, subject, html_body, text_body)
    
    @staticmethod
    def _html_to_text(html: str) -> str:
        """
        Convert HTML to plain text by removing tags.
        
        Args:
            html: HTML string
        
        Returns:
            Plain text version
        """
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
    
    def validate_email(self, email: str) -> bool:
        """
        Basic email validation.
        
        Args:
            email: Email address to validate
        
        Returns:
            True if email format looks valid
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


def main():
    """Test email sender functionality."""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Note: For production use, set these environment variables:
    # export SENDER_EMAIL="your-email@gmail.com"
    # export SENDER_PASSWORD="your-app-specific-password"
    
    print("\n" + "="*70)
    print("EMAIL SENDER TEST")
    print("="*70)
    
    try:
        # Initialize sender
        sender = EmailSender()
        
        print(f"\n✓ EmailSender initialized")
        print(f"  SMTP Server: {sender.smtp_server}:{sender.smtp_port}")
        print(f"  From: {sender.sender_email}")
        print(f"  TLS: {sender.use_tls}")
        
        # Email validation
        test_emails = [
            "valid.email@example.com",
            "invalid-email",
            "another.valid@domain.co.uk"
        ]
        
        print(f"\n--- Email Validation ---")
        for email in test_emails:
            is_valid = sender.validate_email(email)
            status = "✓ Valid" if is_valid else "✗ Invalid"
            print(f"{status}: {email}")
        
        # Test HTML to text conversion
        html_sample = "<p>Hello <strong>World</strong>!</p><br><p>This is a test.</p>"
        text_version = sender._html_to_text(html_sample)
        print(f"\n--- HTML to Text Conversion ---")
        print(f"HTML: {html_sample}")
        print(f"Text: {text_version}")
        
        print(f"\n{'='*70}")
        print("NOTE: To test actual email sending, set environment variables:")
        print("  SENDER_EMAIL=your-email@gmail.com")
        print("  SENDER_PASSWORD=your-app-specific-password")
        print(f"{'='*70}\n")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")


if __name__ == "__main__":
    main()
