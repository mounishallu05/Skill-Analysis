import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from typing import List, Dict, Set
import logging
import re
from collections import Counter

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

logger = logging.getLogger(__name__)

class SkillProcessor:
    def __init__(self):
        """Initialize the skill processor with NLP models"""
        self.nlp = spacy.load('en_core_web_sm')
        self.stop_words = set(stopwords.words('english'))
        
        # Predefined list of known skills
        self.known_skills = {
            'python', 'django', 'flask', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker', 'kubernetes',
            'java', 'machine learning', 'data science', 'agile', 'devops', 'git', 'ci/cd'
        }

        # Common non-skill words to filter out
        self.non_skill_words = {'experience', 'proficient', 'skills', 'design', 'database', 'programming', 'frameworks'}

        # Expanded skill synonyms mapping
        self.skill_synonyms = {
            'python': ['python programming', 'python development', 'python experience'],
            'javascript': ['js', 'javascript programming', 'javascript development'],
            'java': ['java programming', 'java development', 'java experience'],
            'sql': ['sql programming', 'database sql', 'sql experience'],
            'aws': ['amazon web services', 'aws cloud', 'aws experience'],
            'docker': ['docker container', 'docker platform', 'docker experience'],
            'kubernetes': ['k8s', 'kubernetes orchestration', 'kubernetes experience'],
            'react': ['react.js', 'reactjs', 'react development', 'react experience'],
            'node.js': ['nodejs', 'node development', 'node experience'],
            'machine learning': ['ml', 'machine learning development', 'machine learning experience'],
            'data science': ['data analytics', 'data scientist', 'data science experience'],
            'agile': ['agile methodology', 'agile development', 'agile experience'],
            'devops': ['devops engineering', 'devops practices', 'devops experience'],
            'git': ['git version control', 'git management', 'git experience'],
            'ci/cd': ['continuous integration', 'continuous deployment', 'ci/cd experience'],
        }

    def extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extract skills from text using direct matching and regex patterns
        
        Args:
            text (str): Text to extract skills from
            
        Returns:
            List of extracted skills
        """
        if not text:
            return []
            
        # Convert text to lowercase for case-insensitive matching
        text = text.lower()
        
        # Directly match against known skills
        skills = set()
        for skill in self.known_skills:
            if skill in text:
                skills.add(skill)
        
        # Match against skill synonyms
        for standard, variants in self.skill_synonyms.items():
            for variant in variants:
                if variant in text:
                    skills.add(standard)
        
        # Use regex to capture skills in specific contexts
        patterns = [
            r'proficient in (\w+)',
            r'experience with (\w+)',
            r'knowledge of (\w+)',
            r'skilled in (\w+)',
            r'expertise in (\w+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                skill = match.group(1)
                if skill in self.known_skills:
                    skills.add(skill)
        
        return list(skills)

    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """
        Normalize skills by removing duplicates and mapping synonyms
        
        Args:
            skills (List[str]): List of skills to normalize
            
        Returns:
            List of normalized skills
        """
        normalized = set()
        
        for skill in skills:
            # Clean the skill
            skill = re.sub(r'[^\w\s]', '', skill).strip()
            
            # Check if skill is in synonyms
            found = False
            for standard, variants in self.skill_synonyms.items():
                if skill in variants or skill == standard:
                    normalized.add(standard)
                    found = True
                    break
            
            if not found:
                normalized.add(skill)
        
        return list(normalized)

    def compare_skills(self, user_skills: List[str], job_skills: List[str]) -> Dict:
        """
        Compare user skills against job requirements
        
        Args:
            user_skills (List[str]): List of user's skills
            job_skills (List[str]): List of required job skills
            
        Returns:
            Dict containing skill match analysis
        """
        user_skills_set = set(user_skills)
        job_skills_set = set(job_skills)
        
        # Find matching and missing skills
        matching_skills = user_skills_set.intersection(job_skills_set)
        missing_skills = job_skills_set - user_skills_set
        unique_skills = user_skills_set - job_skills_set
        
        # Calculate match percentage
        match_percentage = (len(matching_skills) / len(job_skills_set)) * 100 if job_skills_set else 0
        
        return {
            'matching_skills': list(matching_skills),
            'missing_skills': list(missing_skills),
            'unique_skills': list(unique_skills),
            'match_percentage': round(match_percentage, 2)
        }

    def get_skill_frequency(self, skills_list: List[List[str]]) -> Dict[str, int]:
        """
        Calculate frequency of skills across multiple job postings
        
        Args:
            skills_list (List[List[str]]): List of skills from multiple job postings
            
        Returns:
            Dict mapping skills to their frequency
        """
        all_skills = [skill for skills in skills_list for skill in skills]
        return dict(Counter(all_skills)) 