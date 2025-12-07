"""
Email Pipeline Module

Handles newsletter generation and delivery using Gemini 2.5 LLM.

Components:
- retrieval_context: Extract trend data from Module 4
- newsletter_generator: Generate newsletter content with Gemini 2.5
- email_sender: Send emails via SMTP
- main_email_pipeline: Orchestrate the full workflow
- email_scheduler: Schedule weekly newsletter execution

Author: Gen-Eezes Team
Date: December 2025
"""

__version__ = "1.0.0"
__author__ = "Gen-Eezes Team"

from .retrieval_context import RetrievalContext
from .newsletter_generator import NewsletterGenerator
from .email_sender import EmailSender
from .main_email_pipeline import EmailPipeline
from .email_scheduler import EmailScheduler

__all__ = [
    'RetrievalContext',
    'NewsletterGenerator',
    'EmailSender',
    'EmailPipeline',
    'EmailScheduler'
]
