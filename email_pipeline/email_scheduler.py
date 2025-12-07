"""
Email Scheduler

Manages weekly newsletter scheduling and execution.
Can be run as a persistent daemon or via Windows Task Scheduler/cron.

Author: Gen-Eezes Team
Date: December 2025
"""

import os
import sys
import logging
import schedule
import time
from typing import Optional, Callable
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_pipeline.main_email_pipeline import EmailPipeline

logger = logging.getLogger(__name__)


class EmailScheduler:
    """
    Manages scheduled execution of the email pipeline.
    
    Supports:
    - Weekly scheduling (configurable day and time)
    - Manual execution
    - Persistent daemon mode
    - Single-run mode
    
    Example:
        scheduler = EmailScheduler()
        scheduler.schedule_weekly(day_of_week='Sunday', time='09:00')
        scheduler.run_daemon()  # Keep running, execute on schedule
    """
    
    def __init__(
        self,
        gemini_api_key: str = None,
        smtp_server: str = None,
        smtp_port: int = None,
        sender_email: str = None,
        sender_password: str = None,
        mongo_uri: str = "mongodb://localhost:27017/",
        db_name: str = "gen_eezes"
    ):
        """
        Initialize the scheduler.
        
        Args:
            gemini_api_key: Gemini 2.5 API key
            smtp_server: SMTP server
            smtp_port: SMTP port
            sender_email: Sender email
            sender_password: Sender password
            mongo_uri: MongoDB URI
            db_name: Database name
        """
        
        self.pipeline = EmailPipeline(
            gemini_api_key=gemini_api_key,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            sender_email=sender_email,
            sender_password=sender_password,
            mongo_uri=mongo_uri,
            db_name=db_name
        )
        
        self.scheduled_jobs = []
        logger.info("EmailScheduler initialized")
    
    def schedule_weekly(
        self,
        day_of_week: str = 'Sunday',
        time: str = '09:00',
        preview_only: bool = False
    ):
        """
        Schedule weekly newsletter execution.
        
        Args:
            day_of_week: Day to run ('Monday', 'Tuesday', ..., 'Sunday')
            time: Time to run in 24-hour format (e.g., '09:00', '14:30')
            preview_only: If True, generate but don't send
        
        Returns:
            schedule.Job object
        """
        
        day_mapping = {
            'monday': 'monday',
            'tuesday': 'tuesday',
            'wednesday': 'wednesday',
            'thursday': 'thursday',
            'friday': 'friday',
            'saturday': 'saturday',
            'sunday': 'sunday'
        }
        
        day = day_mapping.get(day_of_week.lower())
        if not day:
            raise ValueError(f"Invalid day of week: {day_of_week}")
        
        # Create job function with parameters
        def run_job():
            logger.info(f"\n{'='*70}")
            logger.info(f"Scheduled pipeline execution - {datetime.now()}")
            logger.info(f"{'='*70}\n")
            
            try:
                self.pipeline.run(preview_only=preview_only)
            except Exception as e:
                logger.error(f"Scheduled job failed: {str(e)}")
        
        # Schedule the job
        job = getattr(schedule.every(), day).at(time).do(run_job)
        
        self.scheduled_jobs.append({
            'job': job,
            'day': day_of_week,
            'time': time,
            'preview_only': preview_only
        })
        
        logger.info(f"Scheduled weekly newsletter: Every {day_of_week} at {time} (preview_only={preview_only})")
        return job
    
    def schedule_interval(
        self,
        minutes: int = 60,
        preview_only: bool = False
    ):
        """
        Schedule execution at regular intervals.
        
        Args:
            minutes: Minutes between executions
            preview_only: If True, generate but don't send
        
        Returns:
            schedule.Job object
        """
        
        def run_job():
            logger.info(f"\n{'='*70}")
            logger.info(f"Interval pipeline execution - {datetime.now()}")
            logger.info(f"{'='*70}\n")
            
            try:
                self.pipeline.run(preview_only=preview_only)
            except Exception as e:
                logger.error(f"Interval job failed: {str(e)}")
        
        job = schedule.every(minutes).minutes.do(run_job)
        
        self.scheduled_jobs.append({
            'job': job,
            'interval': f"{minutes} minutes",
            'preview_only': preview_only
        })
        
        logger.info(f"Scheduled interval execution: Every {minutes} minutes (preview_only={preview_only})")
        return job
    
    def run_once(self, preview_only: bool = False):
        """
        Execute the pipeline once immediately.
        
        Args:
            preview_only: If True, generate but don't send
        
        Returns:
            Execution results
        """
        
        logger.info(f"\n{'='*70}")
        logger.info("Running pipeline once - immediate execution")
        logger.info(f"{'='*70}\n")
        
        return self.pipeline.run(preview_only=preview_only)
    
    def run_daemon(self, check_interval: int = 60):
        """
        Run as a persistent daemon, executing scheduled jobs.
        
        Args:
            check_interval: Seconds between checking schedule (default: 60)
        """
        
        if not self.scheduled_jobs:
            logger.warning("No jobs scheduled. Call schedule_weekly() or schedule_interval() first.")
            return
        
        logger.info(f"\n{'='*70}")
        logger.info("Starting Email Scheduler Daemon")
        logger.info("Scheduled jobs:")
        for job_info in self.scheduled_jobs:
            logger.info(f"  - {job_info}")
        logger.info(f"{'='*70}\n")
        logger.info(f"Check interval: {check_interval} seconds")
        logger.info("Press Ctrl+C to stop...")
        logger.info("="*70 + "\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(check_interval)
        except KeyboardInterrupt:
            logger.info("\nScheduler stopped by user")
    
    def next_run_time(self) -> Optional[datetime]:
        """
        Get the time of the next scheduled job.
        
        Returns:
            datetime of next run, or None if no jobs scheduled
        """
        
        if not schedule.jobs:
            return None
        
        # schedule.idle_seconds returns seconds until next job
        idle_seconds = schedule.idle_seconds()
        if idle_seconds is None:
            return None
        
        return datetime.now() + timedelta(seconds=idle_seconds)
    
    def get_scheduled_jobs_info(self) -> list:
        """
        Get information about all scheduled jobs.
        
        Returns:
            List of job info dictionaries
        """
        return self.scheduled_jobs
    
    def clear_schedule(self):
        """Clear all scheduled jobs."""
        schedule.clear()
        self.scheduled_jobs = []
        logger.info("All scheduled jobs cleared")


def main():
    """
    Main entry point for the scheduler.
    
    Usage examples:
    
    1. Run once immediately:
       python email_scheduler.py --run-once
    
    2. Run once in preview mode (generate but don't send):
       python email_scheduler.py --run-once --preview
    
    3. Run as daemon (schedule and keep running):
       python email_scheduler.py --daemon --day Sunday --time 09:00
    
    4. Run at specific interval:
       python email_scheduler.py --daemon --interval 60
    """
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Email Pipeline Scheduler')
    parser.add_argument('--run-once', action='store_true', help='Run pipeline once immediately')
    parser.add_argument('--daemon', action='store_true', help='Run as persistent daemon')
    parser.add_argument('--preview', action='store_true', help='Generate but don\'t send emails')
    parser.add_argument('--day', default='Sunday', help='Day of week for weekly schedule (default: Sunday)')
    parser.add_argument('--time', default='09:00', help='Time to run in HH:MM format (default: 09:00)')
    parser.add_argument('--interval', type=int, help='Run at interval (minutes) instead of weekly')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('email_scheduler.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        scheduler = EmailScheduler(
            gemini_api_key=os.getenv('GEMINI_API_KEY'),
            sender_email=os.getenv('SENDER_EMAIL'),
            sender_password=os.getenv('SENDER_PASSWORD')
        )
        
        if args.run_once:
            scheduler.run_once(preview_only=args.preview)
        
        elif args.daemon:
            if args.interval:
                scheduler.schedule_interval(minutes=args.interval, preview_only=args.preview)
            else:
                scheduler.schedule_weekly(day_of_week=args.day, time=args.time, preview_only=args.preview)
            
            scheduler.run_daemon()
        
        else:
            print("\nUsage:")
            print("  python email_scheduler.py --run-once [--preview]")
            print("  python email_scheduler.py --daemon [--day Sunday] [--time 09:00] [--preview]")
            print("  python email_scheduler.py --daemon --interval 60 [--preview]")
            print("\nFor more help:")
            print("  python email_scheduler.py --help")
    
    except Exception as e:
        logger.error(f"Scheduler failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
