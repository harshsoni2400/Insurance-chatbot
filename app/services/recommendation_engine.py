"""Policy recommendation engine based on user requirements"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import InsurancePolicy, InsuranceProvider, UserProfile, InsuranceType


class RecommendationEngine:
    """Engine for generating personalized insurance policy recommendations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_health_insurance_recommendations(
        self,
        age: int,
        coverage_needed: float,
        budget_monthly: Optional[float] = None,
        family_size: int = 1,
        pre_existing_conditions: Optional[List[str]] = None,
        city: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Get health insurance recommendations based on user requirements"""
        
        query = self.db.query(InsurancePolicy).join(InsuranceProvider).filter(
            InsurancePolicy.insurance_type == InsuranceType.HEALTH,
            InsurancePolicy.is_active == True,
            InsurancePolicy.min_age <= age,
            InsurancePolicy.max_age >= age,
            InsurancePolicy.max_coverage >= coverage_needed
        )
        
        policies = query.all()
        
        # Score and rank policies
        scored_policies = []
        for policy in policies:
            score = self._calculate_health_score(
                policy, age, coverage_needed, budget_monthly, 
                family_size, pre_existing_conditions, city
            )
            scored_policies.append((policy, score))
        
        # Sort by score descending
        scored_policies.sort(key=lambda x: x[1], reverse=True)
        
        # Return top recommendations
        recommendations = []
        for policy, score in scored_policies[:limit]:
            recommendations.append(self._format_policy_recommendation(policy, score))
        
        return recommendations
    
    def get_term_insurance_recommendations(
        self,
        age: int,
        coverage_needed: float,
        annual_income: Optional[float] = None,
        smoker: bool = False,
        policy_term: Optional[int] = None,
        budget_monthly: Optional[float] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Get term insurance recommendations based on user requirements"""
        
        query = self.db.query(InsurancePolicy).join(InsuranceProvider).filter(
            InsurancePolicy.insurance_type == InsuranceType.TERM_LIFE,
            InsurancePolicy.is_active == True,
            InsurancePolicy.min_age <= age,
            InsurancePolicy.max_age >= age,
            InsurancePolicy.max_coverage >= coverage_needed
        )
        
        policies = query.all()
        
        # Score and rank policies
        scored_policies = []
        for policy in policies:
            score = self._calculate_term_score(
                policy, age, coverage_needed, annual_income,
                smoker, policy_term, budget_monthly
            )
            scored_policies.append((policy, score))
        
        # Sort by score descending
        scored_policies.sort(key=lambda x: x[1], reverse=True)
        
        # Return top recommendations
        recommendations = []
        for policy, score in scored_policies[:limit]:
            recommendations.append(self._format_policy_recommendation(policy, score))
        
        return recommendations
    
    def _calculate_health_score(
        self,
        policy: InsurancePolicy,
        age: int,
        coverage_needed: float,
        budget_monthly: Optional[float],
        family_size: int,
        pre_existing_conditions: Optional[List[str]],
        city: Optional[str]
    ) -> float:
        """Calculate match score for health insurance policy"""
        score = 50.0  # Base score
        
        # Provider claim settlement ratio (very important for health)
        if policy.provider and policy.provider.claim_settlement_ratio:
            csr = policy.provider.claim_settlement_ratio
            if csr >= 95:
                score += 20
            elif csr >= 90:
                score += 15
            elif csr >= 85:
                score += 10
        
        # NYVO rating
        if policy.nyvo_rating:
            score += policy.nyvo_rating * 3
        
        # Coverage match
        if policy.max_coverage and coverage_needed:
            coverage_ratio = policy.max_coverage / coverage_needed
            if 1 <= coverage_ratio <= 2:
                score += 10
            elif coverage_ratio > 2:
                score += 5
        
        # Budget consideration
        if budget_monthly and policy.base_premium:
            monthly_premium = policy.base_premium / 12
            if monthly_premium <= budget_monthly:
                score += 10
            elif monthly_premium <= budget_monthly * 1.2:
                score += 5
        
        # Waiting period (lower is better)
        if policy.waiting_period_days:
            if policy.waiting_period_days <= 30:
                score += 5
            elif policy.waiting_period_days <= 90:
                score += 3
        
        # Pre-existing condition handling
        if pre_existing_conditions and policy.coverage_details:
            pec_coverage = policy.coverage_details.get('pre_existing_coverage', {})
            if pec_coverage.get('covered_after_waiting'):
                score += 8
        
        # Featured policy bonus
        if policy.is_featured:
            score += 5
        
        return min(score, 100)  # Cap at 100
    
    def _calculate_term_score(
        self,
        policy: InsurancePolicy,
        age: int,
        coverage_needed: float,
        annual_income: Optional[float],
        smoker: bool,
        policy_term: Optional[int],
        budget_monthly: Optional[float]
    ) -> float:
        """Calculate match score for term insurance policy"""
        score = 50.0  # Base score
        
        # Provider claim settlement ratio (critical for term)
        if policy.provider and policy.provider.claim_settlement_ratio:
            csr = policy.provider.claim_settlement_ratio
            if csr >= 98:
                score += 25
            elif csr >= 95:
                score += 20
            elif csr >= 90:
                score += 10
        
        # NYVO rating
        if policy.nyvo_rating:
            score += policy.nyvo_rating * 3
        
        # Coverage adequacy (10-15x annual income recommended)
        if annual_income and coverage_needed:
            recommended_coverage = annual_income * 12
            if coverage_needed >= recommended_coverage * 0.8:
                score += 10
        
        # Budget consideration
        if budget_monthly and policy.base_premium:
            monthly_premium = policy.base_premium / 12
            if monthly_premium <= budget_monthly:
                score += 10
        
        # Riders availability
        if policy.riders_available:
            riders = policy.riders_available
            valuable_riders = ['critical_illness', 'accidental_death', 'waiver_of_premium']
            for rider in valuable_riders:
                if rider in [r.get('type', '').lower() for r in riders if isinstance(r, dict)]:
                    score += 3
        
        # Featured policy bonus
        if policy.is_featured:
            score += 5
        
        return min(score, 100)  # Cap at 100
    
    def _format_policy_recommendation(self, policy: InsurancePolicy, score: float) -> Dict:
        """Format policy as recommendation response"""
        return {
            "policy_id": policy.id,
            "name": policy.name,
            "provider": policy.provider.name if policy.provider else "Unknown",
            "provider_logo": policy.provider.logo_url if policy.provider else None,
            "insurance_type": policy.insurance_type.value,
            "match_score": round(score, 1),
            "coverage_range": {
                "min": policy.min_coverage,
                "max": policy.max_coverage
            },
            "base_premium": policy.base_premium,
            "premium_frequency": policy.premium_frequency,
            "key_features": policy.key_features or [],
            "riders_available": policy.riders_available or [],
            "claim_settlement_ratio": policy.provider.claim_settlement_ratio if policy.provider else None,
            "nyvo_rating": policy.nyvo_rating,
            "customer_rating": policy.customer_rating,
            "waiting_period_days": policy.waiting_period_days,
            "description": policy.description
        }
    
    def get_policy_details(self, policy_id: int) -> Optional[Dict]:
        """Get detailed information about a specific policy"""
        policy = self.db.query(InsurancePolicy).filter(
            InsurancePolicy.id == policy_id
        ).first()
        
        if not policy:
            return None
        
        return {
            "policy_id": policy.id,
            "name": policy.name,
            "provider": {
                "name": policy.provider.name if policy.provider else "Unknown",
                "logo": policy.provider.logo_url if policy.provider else None,
                "claim_settlement_ratio": policy.provider.claim_settlement_ratio if policy.provider else None,
                "website": policy.provider.website if policy.provider else None,
                "support": policy.provider.customer_support if policy.provider else None
            },
            "insurance_type": policy.insurance_type.value,
            "description": policy.description,
            "coverage": {
                "min": policy.min_coverage,
                "max": policy.max_coverage,
                "details": policy.coverage_details
            },
            "eligibility": {
                "min_age": policy.min_age,
                "max_age": policy.max_age,
                "min_income": policy.min_income
            },
            "premium": {
                "base": policy.base_premium,
                "frequency": policy.premium_frequency,
                "factors": policy.premium_factors
            },
            "policy_terms": policy.policy_term_options,
            "waiting_period_days": policy.waiting_period_days,
            "free_look_period_days": policy.free_look_period_days,
            "key_features": policy.key_features,
            "riders": policy.riders_available,
            "exclusions": policy.exclusions,
            "claim_process": policy.claim_process,
            "documents_required": policy.documents_required,
            "ratings": {
                "nyvo": policy.nyvo_rating,
                "customer": policy.customer_rating
            }
        }
    
    def compare_policies(self, policy_ids: List[int]) -> List[Dict]:
        """Compare multiple policies side by side"""
        policies = self.db.query(InsurancePolicy).filter(
            InsurancePolicy.id.in_(policy_ids)
        ).all()
        
        return [self.get_policy_details(p.id) for p in policies]
