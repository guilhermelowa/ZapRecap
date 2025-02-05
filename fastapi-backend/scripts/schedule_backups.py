import schedule
import time
from analyze_suggestions import export_to_csv
import logging
from cleanup_parsed_conversations import cleanup_old_conversations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_job():
    try:
        logger.info("Starting daily backup...")
        export_to_csv()
        logger.info("Backup completed successfully")
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")

def cleanup_job():
    try:
        logger.info("Starting conversation cleanup...")
        cleanup_old_conversations()
        logger.info("Cleanup completed successfully")
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")

# Schedule backup for 3 AM every day
schedule.every().day.at("03:00").do(backup_job)

# Add cleanup job to run at 4 AM
schedule.every().day.at("04:00").do(cleanup_job)

if __name__ == "__main__":
    logger.info("Backup scheduler started")
    while True:
        schedule.run_pending()
        time.sleep(60) 