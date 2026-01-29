"""API routes for NYVO Insurance Advisor Chatbot"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json

from app.models import get_db, UserProfile
from app.services import vector_store, content_ingestion
from app.services.chatbot import ChatbotService
from app.services.recommendation_engine import RecommendationEngine
from app.api.schemas import (
    ChatRequest, ChatResponse,
    HealthInsuranceRequest, TermInsuranceRequest, RecommendationResponse,
    PolicyDetailRequest, PolicyCompareRequest,
    UserProfileCreate, UserProfileResponse,
    IngestionResponse, ContentStatsResponse
)

router = APIRouter()


# ============== Chat Endpoints ==============

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint for insurance advisor conversations.
    
    Handles:
    - General insurance questions (health, term, regulations)
    - Policy recommendations based on user needs
    - Guidance on buying insurance
    """
    chatbot = ChatbotService(db)
    
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in (request.conversation_history or [])
    ]
    
    result = chatbot.chat(
        user_message=request.message,
        session_id=request.session_id,
        conversation_history=conversation_history
    )
    
    return ChatResponse(
        response=result["response"],
        session_id=request.session_id,
        intent=result["intent"],
        recommendations=result["recommendations"],
        context_used=result["context_used"]
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Streaming chat endpoint for real-time responses.
    Returns Server-Sent Events (SSE) for progressive display.
    """
    chatbot = ChatbotService(db)
    
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in (request.conversation_history or [])
    ]
    
    async def generate():
        async for chunk in chatbot.chat_stream(
            user_message=request.message,
            session_id=request.session_id,
            conversation_history=conversation_history
        ):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


# ============== Recommendation Endpoints ==============

@router.post("/recommend/health", response_model=RecommendationResponse)
async def get_health_recommendations(
    request: HealthInsuranceRequest,
    db: Session = Depends(get_db)
):
    """
    Get personalized health insurance recommendations.
    
    Parameters:
    - age: User's age (18-100)
    - coverage_needed: Desired sum insured in INR
    - budget_monthly: Optional monthly budget
    - family_size: Number of people to cover
    - pre_existing_conditions: List of conditions if any
    - city: City of residence
    """
    engine = RecommendationEngine(db)
    
    recommendations = engine.get_health_insurance_recommendations(
        age=request.age,
        coverage_needed=request.coverage_needed,
        budget_monthly=request.budget_monthly,
        family_size=request.family_size,
        pre_existing_conditions=request.pre_existing_conditions,
        city=request.city
    )
    
    return RecommendationResponse(
        recommendations=recommendations,
        total_count=len(recommendations)
    )


@router.post("/recommend/term", response_model=RecommendationResponse)
async def get_term_recommendations(
    request: TermInsuranceRequest,
    db: Session = Depends(get_db)
):
    """
    Get personalized term insurance recommendations.
    
    Parameters:
    - age: User's age (18-65)
    - coverage_needed: Desired sum assured in INR
    - annual_income: Annual income for coverage calculation
    - smoker: Smoking status
    - policy_term: Preferred policy duration
    - budget_monthly: Optional monthly budget
    """
    engine = RecommendationEngine(db)
    
    recommendations = engine.get_term_insurance_recommendations(
        age=request.age,
        coverage_needed=request.coverage_needed,
        annual_income=request.annual_income,
        smoker=request.smoker,
        policy_term=request.policy_term,
        budget_monthly=request.budget_monthly
    )
    
    return RecommendationResponse(
        recommendations=recommendations,
        total_count=len(recommendations)
    )


# ============== Policy Endpoints ==============

@router.get("/policy/{policy_id}")
async def get_policy_details(policy_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific policy."""
    engine = RecommendationEngine(db)
    details = engine.get_policy_details(policy_id)
    
    if not details:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return details


@router.post("/policy/compare")
async def compare_policies(
    request: PolicyCompareRequest,
    db: Session = Depends(get_db)
):
    """Compare multiple policies side by side."""
    engine = RecommendationEngine(db)
    comparison = engine.compare_policies(request.policy_ids)
    
    if not comparison:
        raise HTTPException(status_code=404, detail="No policies found")
    
    return {"policies": comparison, "count": len(comparison)}


# ============== User Profile Endpoints ==============

@router.post("/profile", response_model=UserProfileResponse)
async def create_or_update_profile(
    request: UserProfileCreate,
    db: Session = Depends(get_db)
):
    """Create or update user profile for personalized recommendations."""
    existing = db.query(UserProfile).filter(
        UserProfile.session_id == request.session_id
    ).first()
    
    if existing:
        for field, value in request.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    
    profile = UserProfile(**request.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/profile/{session_id}", response_model=UserProfileResponse)
async def get_profile(session_id: str, db: Session = Depends(get_db)):
    """Get user profile by session ID."""
    profile = db.query(UserProfile).filter(
        UserProfile.session_id == session_id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile


# ============== Content Management Endpoints ==============

@router.post("/content/ingest", response_model=IngestionResponse)
async def ingest_content():
    """
    Ingest NYVO content library into vector store.
    Call this after adding new content files.
    """
    result = content_ingestion.ingest_content_library()
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return IngestionResponse(**result)


@router.get("/content/stats", response_model=ContentStatsResponse)
async def get_content_stats():
    """Get statistics about indexed content."""
    return vector_store.get_collection_stats()


@router.delete("/content/clear")
async def clear_content():
    """Clear all indexed content. Use with caution."""
    vector_store.clear_collection()
    return {"status": "success", "message": "Content cleared"}


# ============== Health Check ==============

@router.get("/health")
async def health_check():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "service": "NYVO Insurance Advisor",
        "version": "1.0.0"
    }
