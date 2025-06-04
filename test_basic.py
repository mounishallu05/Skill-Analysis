import os
os.environ['DATABASE_URL'] = 'sqlite:///data/test/test.db'
import unittest
import os
from pathlib import Path
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.scrapers.job_scraper import JobScraper
from src.processors.pdf_parser import PDFParser
from src.processors.skill_processor import SkillProcessor
from src.database.database import init_db, drop_db, get_db
from src.database.models import Profile, Skill, JobPosting
from unittest.mock import patch

class TestLinkedInSkillAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Create test data directory
        Path("data/test").mkdir(parents=True, exist_ok=True)
        
        print("Setting up test environment...")
        # Initialize test database
        init_db()
        
        # Initialize components
        cls.skill_processor = SkillProcessor()
        cls.pdf_parser = PDFParser()

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Drop test database
        drop_db()

    def test_skill_processor(self):
        """Test skill extraction and normalization"""
        # Test text with various skills
        text = """
        Python programming experience with Django and Flask frameworks.
        Proficient in JavaScript, React, and Node.js.
        Strong SQL and database design skills.
        Experience with AWS, Docker, and Kubernetes.
        """
        
        skills = self.skill_processor.extract_skills_from_text(text)
        print(f"Extracted skills: {skills}")
        
        # Check if expected skills are extracted
        expected_skills = {'python', 'django', 'flask', 'javascript', 'react', 
                         'node.js', 'sql', 'aws', 'docker', 'kubernetes'}
        
        self.assertTrue(all(skill in skills for skill in expected_skills))

    def test_skill_comparison(self):
        """Test skill comparison functionality"""
        user_skills = ['python', 'javascript', 'sql', 'aws']
        job_skills = ['python', 'java', 'sql', 'docker', 'kubernetes']
        
        comparison = self.skill_processor.compare_skills(user_skills, job_skills)
        
        # Check comparison results
        self.assertEqual(len(comparison['matching_skills']), 2)  # python, sql
        self.assertEqual(len(comparison['missing_skills']), 3)  # java, docker, kubernetes
        self.assertEqual(len(comparison['unique_skills']), 2)  # javascript, aws
        self.assertEqual(comparison['match_percentage'], 40.0)  # 2/5 * 100

    def test_job_scraper(self):
        """Test job scraping functionality"""
        with patch('src.scrapers.job_scraper.JobScraper.scrape_indeed_jobs') as mock_scrape:
            mock_scrape.return_value = [{
                'title': 'Python Developer',
                'company': 'Test Company',
                'location': 'San Francisco',
                'description': 'Looking for Python, Django, Flask skills.',
                'posted_date': 'Today',
                'url': 'http://example.com',
                'skills': ['python', 'django', 'flask']
            }]
            job_scraper = JobScraper()
            indeed_jobs = job_scraper.scrape_indeed_jobs(
                job_title="Python Developer",
                location="San Francisco",
                max_pages=1
            )
            self.assertGreater(len(indeed_jobs), 0)
            job = indeed_jobs[0]
            self.assertIn('title', job)
            self.assertIn('company', job)
            self.assertIn('location', job)
            self.assertIn('description', job)
            self.assertIn('skills', job)
            job_scraper.close()

    def test_pdf_parser(self):
        """Test PDF parsing functionality"""
        # Create a sample PDF file for testing
        # Note: In a real test, you would need an actual LinkedIn profile PDF
        test_pdf_path = "data/test/sample_profile.pdf"
        
        if os.path.exists(test_pdf_path):
            profile_data = self.pdf_parser.parse_profile_pdf(test_pdf_path)
            
            # Check profile data structure
            self.assertIn('name', profile_data)
            self.assertIn('headline', profile_data)
            self.assertIn('location', profile_data)
            self.assertIn('about', profile_data)
            self.assertIn('skills', profile_data)
            self.assertIn('experience', profile_data)
            self.assertIn('education', profile_data)

    def test_database_operations(self):
        """Test database operations"""
        # Ensure tables exist
        init_db()
        # Get database session
        db = next(get_db())
        try:
            # Test profile creation
            profile = Profile(
                name="Test User",
                headline="Software Engineer",
                location="San Francisco",
                about="Test profile"
            )
            db.add(profile)
            db.commit()
            # Test skill creation and association
            skill = Skill(name="python")
            db.add(skill)
            db.commit()
            profile.skills.append(skill)
            db.commit()
            # Verify profile and skill
            saved_profile = db.query(Profile).filter_by(name="Test User").first()
            self.assertIsNotNone(saved_profile)
            self.assertEqual(len(saved_profile.skills), 1)
            self.assertEqual(saved_profile.skills[0].name, "python")
        finally:
            db.close()

if __name__ == '__main__':
    unittest.main() 