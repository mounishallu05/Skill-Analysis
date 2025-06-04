from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import uvicorn
import logging
from typing import Optional, List, Dict
import os
from datetime import datetime

from .scrapers.linkedin_scraper import LinkedInScraper
from .scrapers.job_scraper import JobScraper
from .processors.pdf_parser import PDFParser
from .processors.skill_processor import SkillProcessor
from .database.database import get_db, init_db
from .database.models import Profile, Skill, JobPosting, JobRequirement
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LinkedIn Skill Analysis Bot",
    description="Analyze LinkedIn profiles and identify skill gaps",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:8000",  # FastAPI development server
        "https://your-netlify-app.netlify.app",  # Replace with your Netlify domain
        "https://your-vercel-app.vercel.app",    # Replace with your Vercel domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Create data directory if it doesn't exist
Path("data/uploads").mkdir(parents=True, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()

@app.get("/")
async def root():
    """Root endpoint returning API status"""
    return {
        "status": "active",
        "message": "LinkedIn Skill Analysis Bot API is running"
    }

@app.post("/analyze/profile")
async def analyze_profile(
    profile_url: Optional[str] = None,
    pdf_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Analyze a LinkedIn profile either from URL or uploaded PDF
    """
    if not profile_url and not pdf_file:
        raise HTTPException(
            status_code=400,
            detail="Either profile_url or pdf_file must be provided"
        )
    
    try:
        profile_data = None
        
        if profile_url:
            # Scrape profile from URL
            scraper = LinkedInScraper()
            try:
                if scraper.login():
                    profile_data = scraper.scrape_profile(profile_url)
            finally:
                scraper.close()
                
        elif pdf_file:
            # Save uploaded file
            file_path = f"data/uploads/{pdf_file.filename}"
            with open(file_path, "wb") as f:
                f.write(await pdf_file.read())
            
            # Parse PDF
            parser = PDFParser()
            profile_data = parser.parse_profile_pdf(file_path)
            
            # Clean up
            os.remove(file_path)
        
        if not profile_data:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract profile data"
            )
        
        # Process skills
        skill_processor = SkillProcessor()
        profile_data['skills'] = skill_processor.extract_skills_from_text(
            profile_data.get('about', '') + ' ' + 
            ' '.join([exp.get('description', '') for exp in profile_data.get('experience', [])])
        )
        
        # Save to database
        profile = Profile(
            name=profile_data['name'],
            headline=profile_data['headline'],
            location=profile_data['location'],
            about=profile_data['about']
        )
        db.add(profile)
        db.commit()
        
        # Save skills
        for skill_name in profile_data['skills']:
            skill = db.query(Skill).filter_by(name=skill_name).first()
            if not skill:
                skill = Skill(name=skill_name)
                db.add(skill)
                db.commit()
            profile.skills.append(skill)
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Profile analysis completed",
            "data": profile_data
        }
        
    except Exception as e:
        logger.error(f"Error analyzing profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing profile: {str(e)}"
        )

@app.get("/skills/trends")
async def get_skill_trends(
    job_title: str,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get skill trends for a specific job title
    """
    try:
        # Scrape job postings
        job_scraper = JobScraper()
        indeed_jobs = job_scraper.scrape_indeed_jobs(job_title, location)
        glassdoor_jobs = job_scraper.scrape_glassdoor_jobs(job_title, location)
        job_scraper.close()
        
        # Combine and process job data
        all_jobs = indeed_jobs + glassdoor_jobs
        skill_processor = SkillProcessor()
        
        # Extract skills from all job descriptions
        job_skills = []
        for job in all_jobs:
            skills = skill_processor.extract_skills_from_text(job['description'])
            job_skills.append(skills)
            
            # Save job posting
            job_posting = JobPosting(
                title=job['title'],
                company=job['company'],
                location=job['location'],
                description=job['description'],
                url=job['url'],
                posted_date=datetime.now()  # Use actual posted date if available
            )
            db.add(job_posting)
            db.commit()
            
            # Save job requirements
            for skill_name in skills:
                skill = db.query(Skill).filter_by(name=skill_name).first()
                if not skill:
                    skill = Skill(name=skill_name)
                    db.add(skill)
                    db.commit()
                
                requirement = JobRequirement(
                    job_posting_id=job_posting.id,
                    skill_id=skill.id,
                    importance_score=1.0  # Could be calculated based on position in description
                )
                db.add(requirement)
            
            db.commit()
        
        # Calculate skill frequencies
        skill_frequencies = skill_processor.get_skill_frequency(job_skills)
        
        return {
            "status": "success",
            "job_title": job_title,
            "location": location,
            "total_jobs": len(all_jobs),
            "skill_trends": [
                {
                    "skill": skill,
                    "frequency": count,
                    "percentage": round((count / len(all_jobs)) * 100, 2)
                }
                for skill, count in skill_frequencies.items()
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting skill trends: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting skill trends: {str(e)}"
        )

@app.get("/skills/compare")
async def compare_skills(
    profile_url: Optional[str] = None,
    pdf_file: Optional[UploadFile] = File(None),
    job_title: str = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Compare profile skills against job requirements
    """
    if not profile_url and not pdf_file:
        raise HTTPException(
            status_code=400,
            detail="Either profile_url or pdf_file must be provided"
        )
    
    if not job_title:
        raise HTTPException(
            status_code=400,
            detail="job_title is required"
        )
    
    try:
        # Get profile skills
        profile_data = None
        if profile_url:
            scraper = LinkedInScraper()
            try:
                if scraper.login():
                    profile_data = scraper.scrape_profile(profile_url)
            finally:
                scraper.close()
        elif pdf_file:
            file_path = f"data/uploads/{pdf_file.filename}"
            with open(file_path, "wb") as f:
                f.write(await pdf_file.read())
            
            parser = PDFParser()
            profile_data = parser.parse_profile_pdf(file_path)
            os.remove(file_path)
        
        if not profile_data:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract profile data"
            )
        
        # Get job requirements
        job_scraper = JobScraper()
        indeed_jobs = job_scraper.scrape_indeed_jobs(job_title, location)
        glassdoor_jobs = job_scraper.scrape_glassdoor_jobs(job_title, location)
        job_scraper.close()
        
        # Process skills
        skill_processor = SkillProcessor()
        profile_skills = skill_processor.extract_skills_from_text(
            profile_data.get('about', '') + ' ' + 
            ' '.join([exp.get('description', '') for exp in profile_data.get('experience', [])])
        )
        
        job_skills = []
        for job in indeed_jobs + glassdoor_jobs:
            skills = skill_processor.extract_skills_from_text(job['description'])
            job_skills.extend(skills)
        
        # Compare skills
        comparison = skill_processor.compare_skills(profile_skills, list(set(job_skills)))
        
        return {
            "status": "success",
            "profile": {
                "name": profile_data['name'],
                "headline": profile_data['headline']
            },
            "job_title": job_title,
            "location": location,
            "comparison": comparison
        }
        
    except Exception as e:
        logger.error(f"Error comparing skills: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing skills: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 