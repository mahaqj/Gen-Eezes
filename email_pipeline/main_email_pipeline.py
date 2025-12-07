"""
Main Email Pipeline Orchestrator

Coordinates the complete email generation and delivery workflow:
1. Retrieve trend data from Module 4
2. Generate newsletter with Gemini 2.5
3. Send to subscribed users
4. Log results to MongoDB

Author: Gen-Eezes Team
Date: December 2025
"""

import os
import sys
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_pipeline.retrieval_context import RetrievalContext
from email_pipeline.newsletter_generator import NewsletterGenerator
from email_pipeline.email_sender_gmail import GmailAPISender
from pymongo import MongoClient

logger = logging.getLogger(__name__)


class EmailPipeline:
    """
    Main orchestrator for the email generation and delivery pipeline.
    
    Flow:
    1. RetrievalContext: Query Module 4 data (temporal_analysis_real)
    2. NewsletterGenerator: Convert context to newsletter with Gemini 2.5
    3. EmailSender: Deliver to all subscribed users
    4. MongoDB: Log delivery results
    """
    
    def __init__(
        self,
        gemini_api_key: str = None,
        gmail_credentials_file: str = None,
        gmail_token_file: str = None,
        sender_email: str = None,
        mongo_uri: str = "mongodb://localhost:27017/",
        db_name: str = "gen_eezes"
    ):
        """
        Initialize the email pipeline with Gmail API.
        
        Args:
            gemini_api_key: Gemini 2.5 API key
            gmail_credentials_file: Path to Google credentials.json
            gmail_token_file: Path to Gmail token.json
            sender_email: Gmail address to send from
            mongo_uri: MongoDB connection URI
            db_name: Database name
        """
        
        logger.info("Initializing Email Pipeline...")
        
        # Initialize components
        try:
            self.retrieval = RetrievalContext()
            logger.info("✓ RetrievalContext initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RetrievalContext: {str(e)}")
            raise
        
        try:
            self.generator = NewsletterGenerator(api_key=gemini_api_key)
            logger.info("✓ NewsletterGenerator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize NewsletterGenerator: {str(e)}")
            raise
        
        try:
            self.sender = GmailAPISender(
                credentials_file=gmail_credentials_file,
                token_file=gmail_token_file,
                sender_email=sender_email
            )
            logger.info("✓ Gmail API Sender initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Gmail API Sender: {str(e)}")
            raise
        
        try:
            self.mongo = MongoClient(mongo_uri)
            self.db = self.mongo[db_name]
            logger.info("✓ MongoDB client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB: {str(e)}")
            raise
    
    def run(
        self,
        preview_only: bool = False,
        test_recipients: List[str] = None,
        tone: str = "professional-friendly"
    ) -> Dict:
        """
        Execute the complete email pipeline.
        
        Args:
            preview_only: If True, generate newsletters but don't send (default: False)
            test_recipients: If provided, send only to these emails (for testing)
            tone: Newsletter writing tone
        
        Returns:
            Dictionary with execution results:
            - 'timestamp': When pipeline ran
            - 'phase': Which phase it ran (generation, sending, or both)
            - 'context': Retrieved trend data
            - 'newsletters': Generated newsletters
            - 'delivery_results': Email delivery results
            - 'logged_records': Stored results in MongoDB
        """
        
        execution_log = {
            'timestamp': datetime.now().isoformat(),
            'phase': 'full_pipeline',
            'context': None,
            'newsletters': {},
            'delivery_results': {},
            'logged_records': [],
            'errors': []
        }
        
        try:
            # Phase 1: Retrieve Module 4 data
            logger.info("\n" + "="*70)
            logger.info("PHASE 1: RETRIEVING TREND DATA FROM MODULE 4")
            logger.info("="*70)
            
            context = self.retrieval.get_latest_trends()
            if not context:
                raise ValueError("Failed to retrieve trend data from Module 4")
            
            execution_log['context'] = context
            logger.info(f"✓ Retrieved context for {len(context.get('keyword_shifts', {}))} keywords")
            
            # Phase 2: Get subscribed users
            logger.info("\n" + "="*70)
            logger.info("PHASE 2: FETCHING SUBSCRIBED USERS")
            logger.info("="*70)
            
            users = self._get_subscribed_users()
            
            if test_recipients:
                logger.info(f"Using test recipients: {test_recipients}")
                users = [{'email': email, 'name': email.split('@')[0]} for email in test_recipients]
            
            logger.info(f"✓ Found {len(users)} subscribed users")
            for user in users:
                logger.info(f"  - {user.get('name', 'Unknown')} <{user.get('email')}>")
            
            if not users:
                logger.warning("No users to send to. Exiting.")
                execution_log['phase'] = 'generation_only'
                return execution_log
            
            # Phase 3: Generate newsletters
            logger.info("\n" + "="*70)
            logger.info("PHASE 3: GENERATING NEWSLETTERS WITH GEMINI 2.5")
            logger.info("="*70)
            
            formatted_context_text, context_dict = self.retrieval.get_formatted_context_for_llm()
            
            # Adapt context format for newsletter generator
            adapted_context = {
                'keyword_shifts': {},
                'cluster_insights': context_dict.get('cluster_insights', {}),
                'narrative': context_dict.get('narrative', ''),
                'timestamp': context_dict.get('week_ending', '')
            }
            
            # Convert keyword list format to dict format expected by generator
            for kw in context_dict.get('keyword_shifts', {}).get('rising_keywords', []):
                percent_val = float(kw['change'].rstrip('%').lstrip('+'))
                adapted_context['keyword_shifts'][kw['keyword'].lower()] = {
                    'direction': 'RISING',
                    'percent_change': percent_val,
                    'start_freq': kw['start'],
                    'end_freq': kw['end']
                }
            
            for kw in context_dict.get('keyword_shifts', {}).get('falling_keywords', []):
                percent_val = float(kw['change'].rstrip('%').lstrip('+'))
                adapted_context['keyword_shifts'][kw['keyword'].lower()] = {
                    'direction': 'FALLING',
                    'percent_change': percent_val,
                    'start_freq': kw['start'],
                    'end_freq': kw['end']
                }
            
            # Generate ONE high-quality newsletter template
            logger.info(f"\nGenerating single newsletter template for {len(users)} subscribers...")
            
            try:
                # Generate with a generic placeholder name
                newsletter_template = self.generator.generate_newsletter(
                    context=adapted_context,
                    recipient_name="[USER_NAME]",
                    tone=tone
                )
                
                execution_log['master_newsletter'] = {
                    'subject': newsletter_template.get('subject'),
                    'generated_at': newsletter_template.get('generated_at'),
                    'recipient_count': len(users),
                    'template_based': True
                }
                
                logger.info(f"✓ Generated newsletter template")
                logger.info(f"  Will be personalized and sent to {len(users)} subscribers")
                
            except Exception as e:
                error_msg = f"Failed to generate newsletter template: {str(e)}"
                logger.error(error_msg)
                execution_log['errors'].append(error_msg)
                raise
            
            # Phase 4: Send emails (unless preview_only)
            if preview_only:
                logger.info("\n" + "="*70)
                logger.info("PREVIEW MODE: Skipping email delivery")
                logger.info("="*70)
                execution_log['phase'] = 'generation_only'
                
            else:
                logger.info("\n" + "="*70)
                logger.info("PHASE 4: PERSONALIZING AND SENDING EMAILS TO ALL SUBSCRIBERS")
                logger.info("="*70)
                
                # Prepare personalized emails by replacing [USER_NAME] with actual names
                emails_to_send = []
                for user in users:
                    email = user.get('email')
                    # Extract first name properly
                    name = user.get('name', '')
                    
                    # If no name stored, extract from email (take first part before number/underscore)
                    if not name or name == email:
                        email_prefix = email.split('@')[0]  # Get part before @
                        # Remove numbers and common suffixes
                        first_name = ''.join([c for c in email_prefix if not c.isdigit()]).rstrip('_.-')
                        if not first_name:  # Fallback if all chars were numbers
                            first_name = email_prefix.split('.')[0].split('_')[0]
                    else:
                        # If we have a proper name, get first part
                        first_name = name.split()[0] if ' ' in name else name
                    
                    # Capitalize first letter
                    first_name = first_name.capitalize()
                    
                    # Personalize the template by replacing [USER_NAME] with actual name
                    personalized_html = newsletter_template['html'].replace('[USER_NAME]', first_name)
                    personalized_text = newsletter_template['text'].replace('[USER_NAME]', first_name)
                    personalized_subject = newsletter_template['subject'].replace('[USER_NAME]', first_name)
                    
                    emails_to_send.append({
                        'to': email,
                        'subject': personalized_subject,
                        'html': personalized_html,
                        'text': personalized_text
                    })
                
                logger.info(f"✓ Personalized {len(emails_to_send)} newsletters with user names")
                
                # Send batch via Gmail API
                delivery_results = self.sender.send_batch(emails_to_send, delay_between_sends=2)
                execution_log['delivery_results'] = delivery_results
                
                # Phase 5: Log results to MongoDB
                logger.info("\n" + "="*70)
                logger.info("PHASE 5: LOGGING RESULTS TO MONGODB")
                logger.info("="*70)
                
                # Use the newsletter template for logging
                logged_records = self._log_delivery_results_batch(
                    newsletter_template,
                    delivery_results
                )
                execution_log['logged_records'] = logged_records
                
                logger.info(f"✓ Logged {len(logged_records)} delivery records")
            
            # Summary
            self._print_summary(execution_log)
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            execution_log['errors'].append(str(e))
        
        return execution_log
    
    def _get_subscribed_users(self) -> List[Dict]:
        """
        Get all users subscribed to the newsletter.
        
        Returns:
            List of user dictionaries with 'email' and 'name' keys
        """
        try:
            users_collection = self.db['users']
            users = list(users_collection.find({'subscribed': True}))
            
            return [
                {
                    'email': user.get('email'),
                    'name': user.get('name', user.get('email', 'Unknown'))
                }
                for user in users
            ]
        except Exception as e:
            logger.error(f"Failed to retrieve users: {str(e)}")
            return []
    
    def _log_delivery_results_batch(
        self,
        newsletter: Dict,
        delivery_results: Dict
    ) -> List[str]:
        """
        Log email delivery results to MongoDB for batch sending.
        
        Args:
            newsletter: Single generated newsletter sent to all users
            delivery_results: Delivery success/failure results keyed by recipient email
        
        Returns:
            List of MongoDB record IDs
        """
        try:
            email_logs_collection = self.db['email_logs']
            
            records = []
            for email, (success, message) in delivery_results.items():
                record = {
                    'timestamp': datetime.now(),
                    'recipient': email,
                    'subject': newsletter.get('subject', ''),
                    'success': success,
                    'message': message,
                    'sent_at': datetime.now().isoformat()
                }
                
                result = email_logs_collection.insert_one(record)
                records.append(str(result.inserted_id))
            
            return records
        except Exception as e:
            logger.error(f"Failed to log delivery results: {str(e)}")
            return []
    
    def _log_delivery_results(
        self,
        newsletters: Dict,
        delivery_results: Dict
    ) -> List[str]:
        """
        Log email delivery results to MongoDB.
        
        Args:
            newsletters: Generated newsletters
            delivery_results: Delivery success/failure results
        
        Returns:
            List of MongoDB record IDs
        """
        try:
            email_logs_collection = self.db['email_logs']
            
            records = []
            for email, (success, message) in delivery_results.items():
                record = {
                    'timestamp': datetime.now(),
                    'recipient': email,
                    'subject': newsletters.get(email, {}).get('subject', ''),
                    'success': success,
                    'message': message,
                    'sent_at': datetime.now().isoformat()
                }
                
                result = email_logs_collection.insert_one(record)
                records.append(str(result.inserted_id))
            
            return records
        except Exception as e:
            logger.error(f"Failed to log delivery results: {str(e)}")
            return []
    
    def _print_summary(self, execution_log: Dict):
        """Print execution summary."""
        
        # Check if master_newsletter exists (new single generation approach)
        if execution_log.get('master_newsletter'):
            newsletters_count = execution_log['master_newsletter'].get('recipient_count', 0)
            subject = execution_log['master_newsletter'].get('subject', 'Unknown')
        else:
            newsletters_count = len(execution_log.get('newsletters', {}))
            subject = "Multiple newsletters"
        
        summary = f"""
{'='*70}
                    PIPELINE EXECUTION SUMMARY
{'='*70}

Timestamp: {execution_log['timestamp']}
Phase: {execution_log['phase']}

NEWSLETTER GENERATED: {subject}
RECIPIENTS: {newsletters_count}
"""
        
        if execution_log.get('delivery_results'):
            successful = sum(1 for success, _ in execution_log['delivery_results'].values() if success)
            total = len(execution_log['delivery_results'])
            summary += f"DELIVERY RESULTS: {successful}/{total} successful\n"
        
        if execution_log.get('logged_records'):
            summary += f"RECORDS LOGGED: {len(execution_log['logged_records'])}\n"
        
        if execution_log.get('errors'):
            summary += f"\nERRORS ({len(execution_log['errors'])}):\n"
            for error in execution_log['errors']:
                summary += f"  - {error}\n"
        
        summary += "="*70
        logger.info(summary)


def main():
    """Run the email pipeline."""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        pipeline = EmailPipeline(
            gemini_api_key=os.getenv('GEMINI_API_KEY'),
            gmail_credentials_file=os.getenv('GMAIL_CREDENTIALS_FILE'),
            gmail_token_file=os.getenv('GMAIL_TOKEN_FILE'),
            sender_email=os.getenv('SENDER_EMAIL')
        )
        
        # Run with real sending enabled
        results = pipeline.run(preview_only=False, tone='professional-friendly')
        
        # Save results to JSON
        with open('pipeline_execution_log.json', 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            clean_results = json.loads(json.dumps(results, default=str))
            json.dump(clean_results, f, indent=2)
        
        logger.info(f"\nExecution log saved to pipeline_execution_log.json")
        
    except Exception as e:
        logger.error(f"Failed to run pipeline: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
