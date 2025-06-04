from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
import time
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from ..utils.helpers import clean_text, parse_date
from ..processors.skill_processor import SkillProcessor

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class JobScraper:
    def __init__(self):
        """Initialize the job scraper with Selenium WebDriver"""
        self.driver = None
        self.skill_processor = SkillProcessor()
        self.setup_driver()

    def setup_driver(self):
        """Set up the Selenium WebDriver with appropriate options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def scrape_indeed_jobs(self, job_title: str, location: str = "", max_pages: int = 5) -> List[Dict]:
        """
        Scrape job postings from Indeed
        
        Args:
            job_title (str): Job title to search for
            location (str): Location to search in
            max_pages (int): Maximum number of pages to scrape
            
        Returns:
            List of job posting data
        """
        jobs = []
        try:
            # Format search URL
            search_url = f"https://www.indeed.com/jobs?q={job_title.replace(' ', '+')}"
            if location:
                search_url += f"&l={location.replace(' ', '+')}"
            
            self.driver.get(search_url)
            time.sleep(3)  # Allow page to load
            
            for page in range(max_pages):
                # Get job cards
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job_seen_beacon")
                
                for card in job_cards:
                    try:
                        # Extract job data
                        job_data = {
                            'title': self._get_text(card, ".jobTitle"),
                            'company': self._get_text(card, ".companyName"),
                            'location': self._get_text(card, ".companyLocation"),
                            'description': self._get_text(card, ".job-snippet"),
                            'posted_date': self._get_text(card, ".date"),
                            'url': self._get_job_url(card)
                        }
                        
                        # Extract skills from description
                        job_data['skills'] = self.skill_processor.extract_skills_from_text(
                            job_data['description']
                        )
                        
                        jobs.append(job_data)
                        
                    except Exception as e:
                        logger.error(f"Error extracting job data: {str(e)}")
                        continue
                
                # Try to click next page
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Next Page']")
                    if not next_button.is_enabled():
                        break
                    next_button.click()
                    time.sleep(3)
                except:
                    break
                    
        except Exception as e:
            logger.error(f"Error scraping Indeed jobs: {str(e)}")
            
        return jobs

    def scrape_glassdoor_jobs(self, job_title: str, location: str = "", max_pages: int = 5) -> List[Dict]:
        """
        Scrape job postings from Glassdoor
        
        Args:
            job_title (str): Job title to search for
            location (str): Location to search in
            max_pages (int): Maximum number of pages to scrape
            
        Returns:
            List of job posting data
        """
        jobs = []
        try:
            # Format search URL
            search_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={job_title.replace(' ', '+')}"
            if location:
                search_url += f"&loc={location.replace(' ', '+')}"
            
            self.driver.get(search_url)
            time.sleep(3)
            
            for page in range(max_pages):
                # Get job cards
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".react-job-listing")
                
                for card in job_cards:
                    try:
                        # Extract job data
                        job_data = {
                            'title': self._get_text(card, ".job-title"),
                            'company': self._get_text(card, ".employer-name"),
                            'location': self._get_text(card, ".location"),
                            'description': self._get_job_description(card),
                            'posted_date': self._get_text(card, ".listing-age"),
                            'url': self._get_job_url(card)
                        }
                        
                        # Extract skills from description
                        job_data['skills'] = self.skill_processor.extract_skills_from_text(
                            job_data['description']
                        )
                        
                        jobs.append(job_data)
                        
                    except Exception as e:
                        logger.error(f"Error extracting job data: {str(e)}")
                        continue
                
                # Try to click next page
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "[data-test='pagination-next']")
                    if not next_button.is_enabled():
                        break
                    next_button.click()
                    time.sleep(3)
                except:
                    break
                    
        except Exception as e:
            logger.error(f"Error scraping Glassdoor jobs: {str(e)}")
            
        return jobs

    def _get_text(self, element, selector: str) -> str:
        """Helper method to safely extract text from an element"""
        try:
            text = element.find_element(By.CSS_SELECTOR, selector).text
            return clean_text(text)
        except:
            return ""

    def _get_job_url(self, element) -> str:
        """Extract job URL from element"""
        try:
            return element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        except:
            return ""

    def _get_job_description(self, element) -> str:
        """Extract full job description"""
        try:
            # Click on job card to load description
            element.click()
            time.sleep(2)
            
            # Get description from modal or new page
            description = self._get_text(self.driver, ".jobDescriptionContent")
            return description
        except:
            return ""

    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit() 