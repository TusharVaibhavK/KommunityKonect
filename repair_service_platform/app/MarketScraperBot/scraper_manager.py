import schedule
import time
import threading
from datetime import datetime
import sys
import os

# Add the parent directory to sys.path to make imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from repair_service_platform.app import create_app
from repair_service_platform.app.MarketScraperBot.market_scraper import (
    scrape_urbanclap_prices, 
    fetch_market_prices,
    scrape_urban_company_plumbing_services
)
from repair_service_platform.app.models import db

class ScraperManager:
    """
    Manages different scraping tasks and schedules
    """
    def __init__(self):
        self.app = create_app()
        self.running = False
        self.scheduler_thread = None
    
    def run_all_scrapers(self):
        """Run all scraping tasks"""
        with self.app.app_context():
            print(f"Running all scrapers at {datetime.now()}")
            
            # Run the specialized plumbing scraper
            try:
                print("Running Urban Company plumbing scraper...")
                result = scrape_urban_company_plumbing_services()
                print(f"Plumbing scraper found {len(result)} services")
            except Exception as e:
                print(f"Error in plumbing scraper: {str(e)}")
            
            # Run the general price scraper
            try:
                print("Running general price scraper...")
                fetch_market_prices()
            except Exception as e:
                print(f"Error in general price scraper: {str(e)}")
            
            # Run service-specific price scrapers
            try:
                print("Running wash basin repair price scraper...")
                wash_basin_prices = scrape_urbanclap_prices('wash_basin_repair')
                print(f"Found {len(wash_basin_prices)} wash basin repair prices")
            except Exception as e:
                print(f"Error in wash basin repair scraper: {str(e)}")
            
            try:
                print("Running electrician visit price scraper...")
                electrician_prices = scrape_urbanclap_prices('electrician_visit')
                print(f"Found {len(electrician_prices)} electrician prices")
            except Exception as e:
                print(f"Error in electrician scraper: {str(e)}")
    
    def schedule_jobs(self):
        """Schedule all scraping jobs"""
        # Run daily at 1 AM
        schedule.every().day.at("01:00").do(self.run_all_scrapers)
        
        # Also run specialized plumbing scraper once a week on Sunday at 2 AM for more detailed analysis
        schedule.every().sunday.at("02:00").do(self.run_plumbing_scraper)
        
        print("All scraping jobs scheduled")
    
    def run_plumbing_scraper(self):
        """Run just the plumbing scraper"""
        with self.app.app_context():
            print(f"Running plumbing scraper at {datetime.now()}")
            try:
                result = scrape_urban_company_plumbing_services()
                print(f"Plumbing scraper found {len(result)} services")
                return result
            except Exception as e:
                print(f"Error in plumbing scraper: {str(e)}")
                return []
    
    def start(self):
        """Start the scheduler in a background thread"""
        if self.running:
            print("Scheduler is already running")
            return
        
        self.running = True
        self.schedule_jobs()
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        print("Scheduler started in background thread")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2)
            self.scheduler_thread = None
        print("Scheduler stopped")
    
    def run_now(self, task_name="all"):
        """Run a specific scraper immediately"""
        if task_name == "plumbing":
            return self.run_plumbing_scraper()
        else:
            return self.run_all_scrapers()


if __name__ == "__main__":
    manager = ScraperManager()
    
    # If command line arguments are provided
    if len(sys.argv) > 1:
        task = sys.argv[1]
        manager.run_now(task)
    else:
        # Otherwise start the scheduler
        manager.start()
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop()
            print("Scraper manager stopped")
