"""Main chatbot service with OpenAI integration and RAG"""
import json
from typing import List, Dict, Optional, AsyncGenerator
from openai import OpenAI
from sqlalchemy.orm import Session

from app.core import settings
from app.services.vector_store import vector_store
from app.services.recommendation_engine import RecommendationEngine
from app.models import ChatSession, UserProfile


SYSTEM_PROMPT = """You are NYVO's AI Insurance Advisor, a knowledgeable and friendly assistant helping customers in India understand and purchase insurance products.

## Your Expertise:
- Health Insurance (individual, family floater, senior citizen, critical illness)
- Term Life Insurance (pure term, return of premium, increasing cover)
- Indian insurance regulations (IRDAI guidelines)
- Insurance basics, terminology, and concepts
- Claim processes and documentation
- Policy comparison and selection

## Guidelines:

### Communication Style:
- Be warm, professional, and empathetic
- Use simple language; avoid jargon unless explaining it
- Be concise but thorough when explaining complex topics
- Ask clarifying questions when needed to give better recommendations
- Use Indian context (₹ for currency, Indian regulations, local examples)

### When Answering Questions:
- Provide accurate, up-to-date information about insurance in India
- Reference IRDAI regulations when relevant
- Explain both benefits and limitations honestly
- Clarify common misconceptions

### When Making Recommendations:
- Always ask for relevant details (age, income, family size, health conditions, budget)
- Explain WHY you're recommending specific policies
- Highlight key features, not just prices
- Mention claim settlement ratios (CSR) - they matter!
- Discuss important exclusions and waiting periods
- Suggest appropriate coverage amounts based on user's situation

### Coverage Guidelines for Term Insurance:
- Recommend 10-15x annual income as coverage
- Consider outstanding loans and future goals
- Factor in inflation for long-term planning

### Coverage Guidelines for Health Insurance:
- Minimum ₹5-10 lakhs for individuals in metro cities
- ₹10-25 lakhs for family floaters
- Consider room rent limits, sub-limits, and co-pay clauses

### Important Reminders:
- Always mention that insurance is subject to terms and conditions
- Recommend reading policy documents carefully
- Suggest consulting with NYVO advisors for complex cases
- Never make guarantees about claims or returns

## Context Information:
You have access to NYVO's content library for educational information and a database of insurance products for recommendations. Use the provided context to give accurate, helpful responses.

Current date context: Prices and policies are subject to change. Always recommend verifying current rates with NYVO."""


class ChatbotService:
    """Main chatbot service orchestrating RAG and recommendations"""
    
    def __init__(self, db: Session):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.db = db
        self.recommendation_engine = RecommendationEngine(db)
    
    def _get_relevant_context(self, query: str, n_results: int = 5) -> str:
        """Retrieve relevant context from vector store"""
        results = vector_store.search(query, n_results=n_results)
        
        if not results["documents"]:
            return ""
        
        context_parts = []
        for doc, meta in zip(results["documents"], results["metadatas"]):
            source = meta.get("file_name", "NYVO Content")
            category = meta.get("category", "general")
            context_parts.append(f"[Source: {source} | Category: {category}]\n{doc}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def _detect_intent(self, message: str) -> Dict:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        intent = {
            "type": "general_query",
            "insurance_type": None,
            "needs_recommendation": False,
            "needs_comparison": False,
            "asking_about_policy": False
        }
        
        # Detect insurance type
        if any(word in message_lower for word in ["health", "medical", "hospitalization", "mediclaim"]):
            intent["insurance_type"] = "health"
        elif any(word in message_lower for word in ["term", "life", "death benefit"]):
            intent["insurance_type"] = "term_life"
        elif any(word in message_lower for word in ["car", "motor", "vehicle", "bike"]):
            intent["insurance_type"] = "motor"
        
        # Detect if recommendation needed
        if any(phrase in message_lower for phrase in [
            "recommend", "suggest", "best policy", "which policy", 
            "what should i buy", "help me choose", "find me", "looking for"
        ]):
            intent["needs_recommendation"] = True
        
        # Detect comparison intent
        if any(word in message_lower for word in ["compare", "comparison", "versus", "vs", "difference between"]):
            intent["needs_comparison"] = True
        
        # Detect policy-specific questions
        if any(phrase in message_lower for phrase in [
            "claim process", "how to claim", "documents required",
            "exclusion", "waiting period", "premium", "coverage"
        ]):
            intent["asking_about_policy"] = True
        
        return intent
    
    def _extract_user_details(self, message: str, conversation_history: List[Dict]) -> Dict:
        """Extract user details from conversation for recommendations"""
        # This would ideally use NER or a separate LLM call
        # Simplified extraction for now
        details = {
            "age": None,
            "coverage_needed": None,
            "budget_monthly": None,
            "family_size": 1,
            "annual_income": None,
            "smoker": False
        }
        
        # Simple pattern matching (production would use NER)
        import re
        
        all_text = message + " " + " ".join([m.get("content", "") for m in conversation_history])
        
        # Age extraction
        age_match = re.search(r'(\d{2})\s*(?:years?|yrs?)?\s*old|age[:\s]+(\d{2})', all_text.lower())
        if age_match:
            details["age"] = int(age_match.group(1) or age_match.group(2))
        
        # Coverage extraction (in lakhs)
        coverage_match = re.search(r'(\d+)\s*(?:lakhs?|lacs?|L)\s*(?:coverage|cover|sum assured)?', all_text, re.IGNORECASE)
        if coverage_match:
            details["coverage_needed"] = float(coverage_match.group(1)) * 100000
        
        # Budget extraction
        budget_match = re.search(r'budget[:\s]+(?:₹|rs\.?|inr)?\s*(\d+[,\d]*)', all_text, re.IGNORECASE)
        if budget_match:
            details["budget_monthly"] = float(budget_match.group(1).replace(",", ""))
        
        # Family size
        family_match = re.search(r'family\s+(?:of\s+)?(\d+)|(\d+)\s*(?:members?|people)', all_text, re.IGNORECASE)
        if family_match:
            details["family_size"] = int(family_match.group(1) or family_match.group(2))
        
        # Income extraction (in lakhs per annum)
        income_match = re.search(r'(?:income|salary|earn)[:\s]+(?:₹|rs\.?|inr)?\s*(\d+)\s*(?:lakhs?|lacs?|L)?\s*(?:per\s+(?:annum|year)|pa|p\.a\.)?', all_text, re.IGNORECASE)
        if income_match:
            income_val = float(income_match.group(1))
            if income_val < 100:  # Likely in lakhs
                details["annual_income"] = income_val * 100000
            else:
                details["annual_income"] = income_val
        
        # Smoker status
        if any(word in all_text.lower() for word in ["smoker", "smoking", "smoke", "tobacco"]):
            if "non-smoker" in all_text.lower() or "non smoker" in all_text.lower():
                details["smoker"] = False
            else:
                details["smoker"] = True
        
        return details
    
    def _build_messages(
        self,
        user_message: str,
        conversation_history: List[Dict],
        context: str,
        recommendations: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """Build message list for OpenAI API"""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history (limited to last 10 exchanges)
        for msg in conversation_history[-20:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Build user message with context
        user_content = user_message
        
        if context:
            user_content = f"""User Question: {user_message}

---
Relevant Information from NYVO Knowledge Base:
{context}
---

Please answer the user's question using the above context when relevant."""
        
        if recommendations:
            rec_text = "\n\nRecommended Policies from NYVO Database:\n"
            for i, rec in enumerate(recommendations, 1):
                rec_text += f"""
{i}. {rec['name']} by {rec['provider']}
   - Match Score: {rec['match_score']}%
   - Coverage: ₹{rec['coverage_range']['min']/100000:.0f}L - ₹{rec['coverage_range']['max']/100000:.0f}L
   - Base Premium: ₹{rec['base_premium']:,.0f}/{rec['premium_frequency']}
   - Claim Settlement Ratio: {rec['claim_settlement_ratio']}%
   - Key Features: {', '.join(rec['key_features'][:3]) if rec['key_features'] else 'N/A'}
"""
            user_content += rec_text + "\nPlease present these recommendations to the user in a helpful way, explaining why each might be suitable."
        
        messages.append({"role": "user", "content": user_content})
        
        return messages
    
    def chat(
        self,
        user_message: str,
        session_id: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """Process a chat message and generate response"""
        conversation_history = conversation_history or []
        
        # Detect intent
        intent = self._detect_intent(user_message)
        
        # Get relevant context from knowledge base
        context = self._get_relevant_context(user_message)
        
        # Get recommendations if needed
        recommendations = None
        if intent["needs_recommendation"] and intent["insurance_type"]:
            user_details = self._extract_user_details(user_message, conversation_history)
            
            if intent["insurance_type"] == "health":
                if user_details["age"]:
                    recommendations = self.recommendation_engine.get_health_insurance_recommendations(
                        age=user_details["age"],
                        coverage_needed=user_details["coverage_needed"] or 500000,
                        budget_monthly=user_details["budget_monthly"],
                        family_size=user_details["family_size"]
                    )
            elif intent["insurance_type"] == "term_life":
                if user_details["age"]:
                    recommendations = self.recommendation_engine.get_term_insurance_recommendations(
                        age=user_details["age"],
                        coverage_needed=user_details["coverage_needed"] or 5000000,
                        annual_income=user_details["annual_income"],
                        smoker=user_details["smoker"],
                        budget_monthly=user_details["budget_monthly"]
                    )
        
        # Build messages for OpenAI
        messages = self._build_messages(
            user_message, conversation_history, context, recommendations
        )
        
        # Generate response
        response = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        assistant_message = response.choices[0].message.content
        
        # Save to chat history
        chat_record = ChatSession(
            session_id=session_id,
            user_message=user_message,
            assistant_response=assistant_message,
            context_used={"intent": intent, "context_retrieved": bool(context)},
            recommendations=[r["policy_id"] for r in recommendations] if recommendations else None
        )
        self.db.add(chat_record)
        self.db.commit()
        
        return {
            "response": assistant_message,
            "intent": intent,
            "recommendations": recommendations,
            "context_used": bool(context)
        }
    
    async def chat_stream(
        self,
        user_message: str,
        session_id: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat response for real-time output"""
        conversation_history = conversation_history or []
        
        intent = self._detect_intent(user_message)
        context = self._get_relevant_context(user_message)
        
        # Get recommendations if needed (same logic as chat)
        recommendations = None
        if intent["needs_recommendation"] and intent["insurance_type"]:
            user_details = self._extract_user_details(user_message, conversation_history)
            
            if intent["insurance_type"] == "health" and user_details["age"]:
                recommendations = self.recommendation_engine.get_health_insurance_recommendations(
                    age=user_details["age"],
                    coverage_needed=user_details["coverage_needed"] or 500000,
                    budget_monthly=user_details["budget_monthly"],
                    family_size=user_details["family_size"]
                )
            elif intent["insurance_type"] == "term_life" and user_details["age"]:
                recommendations = self.recommendation_engine.get_term_insurance_recommendations(
                    age=user_details["age"],
                    coverage_needed=user_details["coverage_needed"] or 5000000,
                    annual_income=user_details["annual_income"],
                    smoker=user_details["smoker"],
                    budget_monthly=user_details["budget_monthly"]
                )
        
        messages = self._build_messages(
            user_message, conversation_history, context, recommendations
        )
        
        stream = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
            stream=True
        )
        
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content
        
        # Save to chat history after streaming completes
        chat_record = ChatSession(
            session_id=session_id,
            user_message=user_message,
            assistant_response=full_response,
            context_used={"intent": intent, "context_retrieved": bool(context)},
            recommendations=[r["policy_id"] for r in recommendations] if recommendations else None
        )
        self.db.add(chat_record)
        self.db.commit()
