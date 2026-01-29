"""Database models for NYVO Insurance products and policies"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, JSON, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
import os
from pathlib import Path

from app.core import settings

# Ensure data directory exists for SQLite
if "sqlite" in settings.database_url:
    db_path = settings.database_url.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        Path(db_dir).mkdir(parents=True, exist_ok=True)

# Database setup
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class InsuranceType(enum.Enum):
    HEALTH = "health"
    TERM_LIFE = "term_life"
    WHOLE_LIFE = "whole_life"
    ULIP = "ulip"
    MOTOR = "motor"
    TRAVEL = "travel"


class InsuranceProvider(Base):
    """Insurance company/provider details"""
    __tablename__ = "insurance_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    short_name = Column(String(50))
    logo_url = Column(String(500))
    claim_settlement_ratio = Column(Float)  # Percentage
    irdai_registration = Column(String(50))
    website = Column(String(200))
    customer_support = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    policies = relationship("InsurancePolicy", back_populates="provider")


class InsurancePolicy(Base):
    """Insurance policy/product details"""
    __tablename__ = "insurance_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("insurance_providers.id"), nullable=False)
    
    # Basic Info
    name = Column(String(300), nullable=False)
    insurance_type = Column(SQLEnum(InsuranceType), nullable=False)
    description = Column(Text)
    
    # Coverage Details
    min_coverage = Column(Float)  # In INR
    max_coverage = Column(Float)
    coverage_details = Column(JSON)  # Detailed coverage breakdown
    
    # Eligibility
    min_age = Column(Integer)
    max_age = Column(Integer)
    min_income = Column(Float)  # Annual income in INR
    
    # Premium Info
    base_premium = Column(Float)  # Starting premium
    premium_frequency = Column(String(50))  # monthly, quarterly, yearly
    premium_factors = Column(JSON)  # Factors affecting premium
    
    # Policy Details
    policy_term_options = Column(JSON)  # Available term lengths
    waiting_period_days = Column(Integer)
    free_look_period_days = Column(Integer, default=15)
    
    # Features
    key_features = Column(JSON)
    riders_available = Column(JSON)
    exclusions = Column(JSON)
    
    # Claim Process
    claim_process = Column(Text)
    documents_required = Column(JSON)
    
    # Ratings & Reviews
    nyvo_rating = Column(Float)  # NYVO's internal rating
    customer_rating = Column(Float)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    provider = relationship("InsuranceProvider", back_populates="policies")


class UserProfile(Base):
    """User profile for personalized recommendations"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    
    # Demographics
    age = Column(Integer)
    gender = Column(String(20))
    city = Column(String(100))
    occupation = Column(String(100))
    
    # Financial
    annual_income = Column(Float)
    existing_coverage = Column(Float)
    
    # Health (for health insurance)
    pre_existing_conditions = Column(JSON)
    smoker = Column(Boolean)
    
    # Family
    marital_status = Column(String(20))
    dependents = Column(Integer)
    family_members = Column(JSON)  # For family floater plans
    
    # Preferences
    budget_monthly = Column(Float)
    coverage_needed = Column(Float)
    preferred_insurers = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatSession(Base):
    """Chat session history"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    user_message = Column(Text)
    assistant_response = Column(Text)
    context_used = Column(JSON)  # Sources used for the response
    recommendations = Column(JSON)  # Policy IDs recommended
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
