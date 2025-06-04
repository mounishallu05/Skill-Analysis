from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import logging
import time
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self):
        """Initialize the LinkedIn scraper with Selenium WebDriver"""
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Set up the Selenium WebDriver with appropriate options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Add user agent to avoid detection
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
        """Login to LinkedIn using credentials from environment variables"""
        try:
            self.driver.get('https://www.linkedin.com/login')
            
            # Wait for login form
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            # Enter credentials
            username_field.send_keys(os.getenv('LINKEDIN_USERNAME'))
            password_field.send_keys(os.getenv('LINKEDIN_PASSWORD'))
            
            # Click login button
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            # Wait for login to complete
            time.sleep(3)
            
            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def scrape_profile(self, profile_url: str) -> Dict:
        """
        Scrape a LinkedIn profile and extract relevant information
        
        Args:
            profile_url (str): URL of the LinkedIn profile to scrape
            
        Returns:
            Dict containing profile information including skills
        """
        try:
            self.driver.get(profile_url)
            time.sleep(3)  # Allow page to load
            
            # Extract basic information
            profile_data = {
                'name': self._get_text('h1'),
                'headline': self._get_text('.text-body-medium'),
                'location': self._get_text('.text-body-small'),
                'about': self._get_text('.display-flex .pv-shared-text-with-see-more'),
                'skills': self._get_skills(),
                'experience': self._get_experience()
            }
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error scraping profile: {str(e)}")
            raise

    def _get_text(self, selector: str) -> str:
        """Helper method to safely extract text from an element"""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element.text.strip()
        except:
            return ""

    def _get_skills(self) -> List[str]:
        """Extract skills from the profile"""
        skills = []
        try:
            # Click on "Show all skills" if present
            show_more = self.driver.find_elements(By.CSS_SELECTOR, "button.inline-show-more-text__button")
            if show_more:
                show_more[0].click()
                time.sleep(1)
            
            # Get all skill elements
            skill_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".pv-skill-category-entity__name-text"
            )
            
            skills = [skill.text.strip() for skill in skill_elements]
            
        except Exception as e:
            logger.error(f"Error extracting skills: {str(e)}")
        
        return skills

    def _get_experience(self) -> List[Dict]:
        """Extract work experience from the profile"""
        experience = []
        try:
            # Click on "Show all experience" if present
            show_more = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "button.inline-show-more-text__button"
            )
            if show_more:
                show_more[0].click()
                time.sleep(1)
            
            # Get experience elements
            exp_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".pv-entity__position-group-pager"
            )
            
            for exp in exp_elements:
                exp_data = {
                    'title': self._get_text('.pv-entity__summary-info h3'),
                    'company': self._get_text('.pv-entity__secondary-title'),
                    'duration': self._get_text('.pv-entity__date-range span:nth-child(2)'),
                    'description': self._get_text('.pv-entity__description')
                }
                experience.append(exp_data)
                
        except Exception as e:
            logger.error(f"Error extracting experience: {str(e)}")
        
        return experience

    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit() 