import schedule
import time
import yaml
import sys
from config import CONFIG_FILE, logger
from main import run_agent_pipeline

def load_schedule_settings():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config.get("schedule_settings", {})
    except Exception as e:
        logger.error(f"Failed to load {CONFIG_FILE} in scheduler: {e}")
        return {}

def job():
    logger.info("⏰ Scheduled job triggered! Running Modawen Agent Pipeline...")
    try:
        run_agent_pipeline()
    except Exception as e:
        logger.error(f"Scheduled pipeline execution failed: {e}")

def run_scheduler():
    logger.info("Initializing Modawen Background Scheduler...")
    
    settings = load_schedule_settings()
    is_enabled = settings.get("enabled", False)
    run_time = settings.get("time", "08:00")
    
    if not is_enabled:
        logger.warning("Scheduler is currently DISABLED in config.yaml. Please enable it via the Web UI or manually.")
        logger.info("Exiting scheduler...")
        sys.exit(0)
        
    logger.info(f"Scheduler ENABLED. Modawen Agent will run daily at {run_time} system time.")
    
    schedule.every().day.at(run_time).do(job)
    
    logger.info("Scheduler loop started. Waiting for the scheduled time... (Press Ctrl+C to exit)")
    
    try:
        while True:
            # Dynamically check if settings changed while running?
            # For simplicity, we just run the schedule. If user changes time, they must restart the scheduler.
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Scheduler manually stopped.")

if __name__ == "__main__":
    run_scheduler()
