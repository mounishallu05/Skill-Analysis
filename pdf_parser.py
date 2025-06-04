import PyPDF2
import logging
from typing import Dict, List, Optional
import re
from pathlib import Path
from ..utils.helpers import clean_text, parse_date
from .skill_processor import SkillProcessor

logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self):
        """Initialize the PDF parser with skill processor"""
        self.skill_processor = SkillProcessor()

    def parse_profile_pdf(self, pdf_path: str) -> Dict:
        """
        Parse LinkedIn profile PDF and extract information
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            Dict containing profile information
        """
        try:
            # Read PDF file
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            
            # Extract profile information
            profile_data = {
                'name': self._extract_name(text),
                'headline': self._extract_headline(text),
                'location': self._extract_location(text),
                'about': self._extract_about(text),
                'skills': self._extract_skills(text),
                'experience': self._extract_experience(text),
                'education': self._extract_education(text)
            }
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise

    def _extract_name(self, text: str) -> str:
        """Extract name from profile text"""
        # Usually the first line of the PDF
        lines = text.split('\n')
        if lines:
            return clean_text(lines[0])
        return ""

    def _extract_headline(self, text: str) -> str:
        """Extract headline from profile text"""
        # Usually follows the name
        lines = text.split('\n')
        if len(lines) > 1:
            return clean_text(lines[1])
        return ""

    def _extract_location(self, text: str) -> str:
        """Extract location from profile text"""
        # Look for location pattern
        location_pattern = r"([A-Za-z\s]+,\s*[A-Za-z\s]+)"
        match = re.search(location_pattern, text)
        if match:
            return clean_text(match.group(1))
        return ""

    def _extract_about(self, text: str) -> str:
        """Extract about section from profile text"""
        # Look for "About" section
        about_pattern = r"About\s*(.*?)(?=Experience|Education|Skills|$)"
        match = re.search(about_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return clean_text(match.group(1))
        return ""

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from profile text"""
        # Look for "Skills" section
        skills_pattern = r"Skills\s*(.*?)(?=Experience|Education|$)"
        match = re.search(skills_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            skills_text = match.group(1)
            # Extract skills using skill processor
            return self.skill_processor.extract_skills_from_text(skills_text)
        return []

    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience from profile text"""
        experience = []
        try:
            # Look for "Experience" section
            exp_pattern = r"Experience\s*(.*?)(?=Education|Skills|$)"
            match = re.search(exp_pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                exp_text = match.group(1)
                
                # Split into individual experiences
                exp_blocks = re.split(r'\n(?=[A-Z][a-z]+\s+\d{4}\s*[-–]\s*(?:Present|\d{4}))', exp_text)
                
                for block in exp_blocks:
                    if not block.strip():
                        continue
                        
                    # Extract experience details
                    exp_data = {
                        'title': self._extract_job_title(block),
                        'company': self._extract_company(block),
                        'duration': self._extract_duration(block),
                        'description': self._extract_job_description(block)
                    }
                    
                    experience.append(exp_data)
                    
        except Exception as e:
            logger.error(f"Error extracting experience: {str(e)}")
            
        return experience

    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education from profile text"""
        education = []
        try:
            # Look for "Education" section
            edu_pattern = r"Education\s*(.*?)(?=Experience|Skills|$)"
            match = re.search(edu_pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                edu_text = match.group(1)
                
                # Split into individual education entries
                edu_blocks = re.split(r'\n(?=[A-Z][a-z]+\s+\d{4}\s*[-–]\s*(?:Present|\d{4}))', edu_text)
                
                for block in edu_blocks:
                    if not block.strip():
                        continue
                        
                    # Extract education details
                    edu_data = {
                        'school': self._extract_school(block),
                        'degree': self._extract_degree(block),
                        'duration': self._extract_duration(block),
                        'description': self._extract_education_description(block)
                    }
                    
                    education.append(edu_data)
                    
        except Exception as e:
            logger.error(f"Error extracting education: {str(e)}")
            
        return education

    def _extract_job_title(self, text: str) -> str:
        """Extract job title from experience block"""
        # Usually the first line
        lines = text.split('\n')
        if lines:
            return clean_text(lines[0])
        return ""

    def _extract_company(self, text: str) -> str:
        """Extract company name from experience block"""
        # Usually follows the job title
        lines = text.split('\n')
        if len(lines) > 1:
            return clean_text(lines[1])
        return ""

    def _extract_duration(self, text: str) -> str:
        """Extract duration from text block"""
        # Look for date pattern
        duration_pattern = r'(\d{4}\s*[-–]\s*(?:Present|\d{4}))'
        match = re.search(duration_pattern, text)
        if match:
            return clean_text(match.group(1))
        return ""

    def _extract_job_description(self, text: str) -> str:
        """Extract job description from experience block"""
        # Everything after the duration
        lines = text.split('\n')
        if len(lines) > 2:
            return clean_text('\n'.join(lines[2:]))
        return ""

    def _extract_school(self, text: str) -> str:
        """Extract school name from education block"""
        # Usually the first line
        lines = text.split('\n')
        if lines:
            return clean_text(lines[0])
        return ""

    def _extract_degree(self, text: str) -> str:
        """Extract degree from education block"""
        # Usually follows the school name
        lines = text.split('\n')
        if len(lines) > 1:
            return clean_text(lines[1])
        return ""

    def _extract_education_description(self, text: str) -> str:
        """Extract education description from education block"""
        # Everything after the duration
        lines = text.split('\n')
        if len(lines) > 2:
            return clean_text('\n'.join(lines[2:]))
        return "" 