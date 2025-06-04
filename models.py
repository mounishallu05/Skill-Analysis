from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Association table for many-to-many relationship between profiles and skills
profile_skills = Table(
    'profile_skills',
    Base.metadata,
    Column('profile_id', Integer, ForeignKey('profiles.id')),
    Column('skill_id', Integer, ForeignKey('skills.id'))
)

class Profile(Base):
    """Model for storing LinkedIn profile information"""
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True)
    linkedin_id = Column(String, unique=True)
    name = Column(String)
    headline = Column(String)
    location = Column(String)
    about = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skills = relationship('Skill', secondary=profile_skills, back_populates='profiles')
    experiences = relationship('Experience', back_populates='profile')

class Skill(Base):
    """Model for storing normalized skills"""
    __tablename__ = 'skills'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    category = Column(String)  # e.g., 'programming', 'soft_skills', 'tools'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    profiles = relationship('Profile', secondary=profile_skills, back_populates='skills')
    job_requirements = relationship('JobRequirement', back_populates='skill')

class Experience(Base):
    """Model for storing work experience"""
    __tablename__ = 'experiences'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    title = Column(String)
    company = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    profile = relationship('Profile', back_populates='experiences')

class JobPosting(Base):
    """Model for storing job posting information"""
    __tablename__ = 'job_postings'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)
    description = Column(String)
    url = Column(String, unique=True)
    posted_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    requirements = relationship('JobRequirement', back_populates='job_posting')

class JobRequirement(Base):
    """Model for storing job requirements"""
    __tablename__ = 'job_requirements'

    id = Column(Integer, primary_key=True)
    job_posting_id = Column(Integer, ForeignKey('job_postings.id'))
    skill_id = Column(Integer, ForeignKey('skills.id'))
    importance_score = Column(Float)  # Score indicating how important the skill is
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job_posting = relationship('JobPosting', back_populates='requirements')
    skill = relationship('Skill', back_populates='job_requirements')

class SkillTrend(Base):
    """Model for storing skill trends over time"""
    __tablename__ = 'skill_trends'

    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey('skills.id'))
    job_title = Column(String)
    frequency = Column(Integer)  # Number of job postings requiring this skill
    date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    skill = relationship('Skill') 