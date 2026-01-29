"""Pydantic schemas for API request/response validation"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


# Chat Schemas
class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message", min_length=1, max_length=2000)
    session_id: str = Field(..., description="Unique session identifier")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=[], 
        description="Previous conversation messages"
    )


class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant's response")
    session_id: str
    intent: Dict = Field(default={}, description="Detected intent from user message")
    recommendations: Optional[List[Dict]] = Field(
        default=None, 
        description="Policy recommendations if applicable"
    )
    context_used: bool = Field(default=False, description="Whether knowledge base was used")


# Recommendation Schemas
class HealthInsuranceRequest(BaseModel):
    age: int = Field(..., ge=18, le=100, description="User's age")
    coverage_needed: float = Field(..., gt=0, description="Desired coverage amount in INR")
    budget_monthly: Optional[float] = Field(default=None, description="Monthly budget in INR")
    family_size: int = Field(default=1, ge=1, description="Number of family members to cover")
    pre_existing_conditions: Optional[List[str]] = Field(
        default=None, 
        description="List of pre-existing conditions"
    )
    city: Optional[str] = Field(default=None, description="City of residence")


class TermInsuranceRequest(BaseModel):
    age: int = Field(..., ge=18, le=65, description="User's age")
    coverage_needed: float = Field(..., gt=0, description="Desired coverage amount in INR")
    annual_income: Optional[float] = Field(default=None, description="Annual income in INR")
    smoker: bool = Field(default=False, description="Whether the user smokes")
    policy_term: Optional[int] = Field(default=None, description="Desired policy term in years")
    budget_monthly: Optional[float] = Field(default=None, description="Monthly budget in INR")


class PolicyRecommendation(BaseModel):
    policy_id: int
    name: str
    provider: str
    provider_logo: Optional[str]
    insurance_type: str
    match_score: float
    coverage_range: Dict[str, float]
    base_premium: float
    premium_frequency: str
    key_features: List
    riders_available: List
    claim_settlement_ratio: Optional[float]
    nyvo_rating: Optional[float]
    customer_rating: Optional[float]
    waiting_period_days: Optional[int]
    description: Optional[str]


class RecommendationResponse(BaseModel):
    recommendations: List[PolicyRecommendation]
    total_count: int


# Policy Schemas
class PolicyDetailRequest(BaseModel):
    policy_id: int


class PolicyCompareRequest(BaseModel):
    policy_ids: List[int] = Field(..., min_length=2, max_length=5)


# User Profile Schemas
class UserProfileCreate(BaseModel):
    session_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    occupation: Optional[str] = None
    annual_income: Optional[float] = None
    existing_coverage: Optional[float] = None
    pre_existing_conditions: Optional[List[str]] = None
    smoker: Optional[bool] = None
    marital_status: Optional[str] = None
    dependents: Optional[int] = None
    family_members: Optional[List[Dict]] = None
    budget_monthly: Optional[float] = None
    coverage_needed: Optional[float] = None


class UserProfileResponse(BaseModel):
    id: int
    session_id: str
    age: Optional[int]
    gender: Optional[str]
    city: Optional[str]
    occupation: Optional[str]
    annual_income: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Content Ingestion Schemas
class IngestionResponse(BaseModel):
    status: str
    files_processed: int
    chunks_created: int


class ContentStatsResponse(BaseModel):
    name: str
    count: int
