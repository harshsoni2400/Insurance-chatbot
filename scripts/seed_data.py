#!/usr/bin/env python3
"""Seed database with sample insurance providers and policies"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import (
    init_db, SessionLocal, InsuranceProvider, InsurancePolicy, InsuranceType
)


def seed_providers():
    """Seed insurance providers"""
    providers = [
        {
            "name": "HDFC Life Insurance",
            "short_name": "HDFC Life",
            "claim_settlement_ratio": 98.5,
            "irdai_registration": "101",
            "website": "https://www.hdfclife.com",
            "customer_support": "1860-267-9999"
        },
        {
            "name": "ICICI Prudential Life Insurance",
            "short_name": "ICICI Pru",
            "claim_settlement_ratio": 97.8,
            "irdai_registration": "105",
            "website": "https://www.iciciprulife.com",
            "customer_support": "1860-266-7766"
        },
        {
            "name": "Max Life Insurance",
            "short_name": "Max Life",
            "claim_settlement_ratio": 99.2,
            "irdai_registration": "104",
            "website": "https://www.maxlifeinsurance.com",
            "customer_support": "1860-120-5577"
        },
        {
            "name": "Star Health Insurance",
            "short_name": "Star Health",
            "claim_settlement_ratio": 87.5,
            "irdai_registration": "129",
            "website": "https://www.starhealth.in",
            "customer_support": "1800-425-2255"
        },
        {
            "name": "HDFC ERGO Health Insurance",
            "short_name": "HDFC ERGO",
            "claim_settlement_ratio": 89.2,
            "irdai_registration": "146",
            "website": "https://www.hdfcergo.com",
            "customer_support": "1800-2666-400"
        },
        {
            "name": "Niva Bupa Health Insurance",
            "short_name": "Niva Bupa",
            "claim_settlement_ratio": 91.0,
            "irdai_registration": "145",
            "website": "https://www.nivabupa.com",
            "customer_support": "1800-102-4462"
        },
        {
            "name": "Tata AIA Life Insurance",
            "short_name": "Tata AIA",
            "claim_settlement_ratio": 98.0,
            "irdai_registration": "110",
            "website": "https://www.tataaia.com",
            "customer_support": "1800-267-9966"
        },
        {
            "name": "LIC of India",
            "short_name": "LIC",
            "claim_settlement_ratio": 98.7,
            "irdai_registration": "512",
            "website": "https://www.licindia.in",
            "customer_support": "022-68276827"
        }
    ]
    return providers


def seed_term_policies(db, providers_map):
    """Seed term insurance policies"""
    term_policies = [
        {
            "provider": "HDFC Life",
            "name": "HDFC Life Click 2 Protect Super",
            "description": "Comprehensive term plan with multiple payout options and in-built terminal illness benefit.",
            "min_coverage": 2500000,
            "max_coverage": 500000000,
            "min_age": 18,
            "max_age": 65,
            "min_income": 300000,
            "base_premium": 8500,
            "premium_frequency": "yearly",
            "policy_term_options": [10, 15, 20, 25, 30, 35, 40],
            "waiting_period_days": 0,
            "key_features": [
                "Option to increase cover at key life stages",
                "Terminal illness benefit included",
                "Multiple payout options: Lump sum, Income, Increasing Income",
                "Return of Premium option available"
            ],
            "riders_available": [
                {"type": "critical_illness", "name": "Critical Illness Plus", "premium_factor": 1.3},
                {"type": "accidental_death", "name": "Accidental Death Benefit", "premium_factor": 1.1},
                {"type": "waiver_of_premium", "name": "Waiver of Premium", "premium_factor": 1.05}
            ],
            "exclusions": ["Suicide within 12 months", "Death due to hazardous activities"],
            "nyvo_rating": 4.5,
            "customer_rating": 4.3,
            "is_featured": True
        },
        {
            "provider": "ICICI Pru",
            "name": "ICICI Pru iProtect Smart",
            "description": "Smart term plan with guaranteed cover option and special exit value on survival.",
            "min_coverage": 5000000,
            "max_coverage": 500000000,
            "min_age": 18,
            "max_age": 60,
            "min_income": 400000,
            "base_premium": 7800,
            "premium_frequency": "yearly",
            "policy_term_options": [15, 20, 25, 30, 35, 40],
            "waiting_period_days": 0,
            "key_features": [
                "Special exit value on survival",
                "Whole life cover option",
                "10% increase in cover every year for first 5 years",
                "Premium break allowed"
            ],
            "riders_available": [
                {"type": "critical_illness", "name": "Critical Illness Rider", "premium_factor": 1.25},
                {"type": "accidental_death", "name": "Accident Care", "premium_factor": 1.08}
            ],
            "exclusions": ["Suicide within 12 months", "Death under influence of drugs/alcohol"],
            "nyvo_rating": 4.4,
            "customer_rating": 4.2,
            "is_featured": True
        },
        {
            "provider": "Max Life",
            "name": "Max Life Smart Secure Plus",
            "description": "Industry's first term plan with changing life cover option.",
            "min_coverage": 5000000,
            "max_coverage": 1000000000,
            "min_age": 18,
            "max_age": 60,
            "min_income": 500000,
            "base_premium": 8200,
            "premium_frequency": "yearly",
            "policy_term_options": [10, 15, 20, 25, 30, 35],
            "waiting_period_days": 0,
            "key_features": [
                "Changing life cover - increase/decrease as needed",
                "Cover against 64 critical illnesses",
                "Joint life cover option",
                "Special women's premium rates"
            ],
            "riders_available": [
                {"type": "critical_illness", "name": "Max Life Critical Illness", "premium_factor": 1.35},
                {"type": "waiver_of_premium", "name": "Premium Waiver", "premium_factor": 1.06}
            ],
            "exclusions": ["Suicide within 12 months"],
            "nyvo_rating": 4.7,
            "customer_rating": 4.5,
            "is_featured": True
        },
        {
            "provider": "Tata AIA",
            "name": "Tata AIA Sampoorna Raksha Promise",
            "description": "Complete family protection with unique flexibility features.",
            "min_coverage": 2500000,
            "max_coverage": 500000000,
            "min_age": 18,
            "max_age": 65,
            "min_income": 300000,
            "base_premium": 7500,
            "premium_frequency": "yearly",
            "policy_term_options": [10, 15, 20, 25, 30],
            "waiting_period_days": 0,
            "key_features": [
                "Whole life option available",
                "Return of premium variant",
                "Lump sum + Monthly Income payout",
                "No extra charge for women"
            ],
            "riders_available": [
                {"type": "critical_illness", "name": "Critical Care", "premium_factor": 1.28},
                {"type": "accidental_death", "name": "Accident Death", "premium_factor": 1.1}
            ],
            "exclusions": ["Suicide within 12 months", "Participation in adventure sports without disclosure"],
            "nyvo_rating": 4.3,
            "customer_rating": 4.1,
            "is_featured": False
        },
        {
            "provider": "LIC",
            "name": "LIC Tech Term",
            "description": "Online term plan from India's most trusted insurer.",
            "min_coverage": 5000000,
            "max_coverage": 100000000,
            "min_age": 18,
            "max_age": 65,
            "min_income": 300000,
            "base_premium": 9000,
            "premium_frequency": "yearly",
            "policy_term_options": [10, 15, 20, 25, 30, 35, 40],
            "waiting_period_days": 0,
            "key_features": [
                "Backed by LIC's claim settlement track record",
                "Competitive premiums for online purchase",
                "Multiple premium payment options",
                "Grace period of 30 days"
            ],
            "riders_available": [
                {"type": "accidental_death", "name": "AD Rider", "premium_factor": 1.1}
            ],
            "exclusions": ["Suicide within 12 months"],
            "nyvo_rating": 4.2,
            "customer_rating": 4.4,
            "is_featured": False
        }
    ]
    
    for policy_data in term_policies:
        provider_name = policy_data.pop("provider")
        provider = providers_map.get(provider_name)
        if provider:
            policy = InsurancePolicy(
                provider_id=provider.id,
                insurance_type=InsuranceType.TERM_LIFE,
                **policy_data
            )
            db.add(policy)


def seed_health_policies(db, providers_map):
    """Seed health insurance policies"""
    health_policies = [
        {
            "provider": "Star Health",
            "name": "Star Health Comprehensive",
            "description": "Comprehensive health coverage with wide hospital network and quick claim settlement.",
            "min_coverage": 500000,
            "max_coverage": 10000000,
            "min_age": 18,
            "max_age": 65,
            "base_premium": 12000,
            "premium_frequency": "yearly",
            "waiting_period_days": 30,
            "coverage_details": {
                "room_rent": "No limit",
                "pre_hospitalization": 60,
                "post_hospitalization": 90,
                "daycare_procedures": True,
                "ambulance_cover": 3000,
                "pre_existing_coverage": {"covered_after_waiting": True, "waiting_years": 3}
            },
            "key_features": [
                "No room rent capping",
                "100% No claim bonus",
                "Covers modern treatments - robotic surgery, gene therapy",
                "Annual health checkup included"
            ],
            "riders_available": [
                {"type": "critical_illness", "name": "Critical Care", "premium_factor": 1.2},
                {"type": "maternity", "name": "Maternity Cover", "premium_factor": 1.4}
            ],
            "exclusions": ["Cosmetic surgery", "Self-inflicted injuries", "Dental treatments unless accident"],
            "nyvo_rating": 4.4,
            "customer_rating": 4.2,
            "is_featured": True
        },
        {
            "provider": "HDFC ERGO",
            "name": "HDFC ERGO Optima Secure",
            "description": "Health insurance with no-claim bonus super saver and restore benefit.",
            "min_coverage": 300000,
            "max_coverage": 5000000,
            "min_age": 18,
            "max_age": 65,
            "base_premium": 10500,
            "premium_frequency": "yearly",
            "waiting_period_days": 30,
            "coverage_details": {
                "room_rent": "Single AC private room",
                "pre_hospitalization": 60,
                "post_hospitalization": 180,
                "daycare_procedures": True,
                "ambulance_cover": 2500,
                "pre_existing_coverage": {"covered_after_waiting": True, "waiting_years": 4}
            },
            "key_features": [
                "100% sum restore benefit",
                "50% cumulative bonus per year (up to 100%)",
                "Global coverage optional",
                "No disease-wise sub-limits"
            ],
            "riders_available": [
                {"type": "critical_illness", "name": "Critical Illness", "premium_factor": 1.25}
            ],
            "exclusions": ["Cosmetic surgery", "Sterility", "Sleep disorders"],
            "nyvo_rating": 4.3,
            "customer_rating": 4.0,
            "is_featured": True
        },
        {
            "provider": "Niva Bupa",
            "name": "Niva Bupa ReAssure 2.0",
            "description": "Smart health plan with infinite care benefit and 100% No Claim Bonus protection.",
            "min_coverage": 300000,
            "max_coverage": 10000000,
            "min_age": 18,
            "max_age": 65,
            "base_premium": 11000,
            "premium_frequency": "yearly",
            "waiting_period_days": 30,
            "coverage_details": {
                "room_rent": "Up to 1% of sum insured per day",
                "pre_hospitalization": 60,
                "post_hospitalization": 180,
                "daycare_procedures": True,
                "ambulance_cover": 3000,
                "pre_existing_coverage": {"covered_after_waiting": True, "waiting_years": 3}
            },
            "key_features": [
                "Infinite care benefit - unlimited restoration",
                "No Claim Bonus protection",
                "Same day claim settlement for cashless",
                "24x7 doctor on call"
            ],
            "riders_available": [
                {"type": "maternity", "name": "Maternity Care", "premium_factor": 1.5},
                {"type": "super_ncb", "name": "Super NCB", "premium_factor": 1.15}
            ],
            "exclusions": ["Cosmetic surgery", "Experimental treatments", "Self-inflicted injuries"],
            "nyvo_rating": 4.5,
            "customer_rating": 4.3,
            "is_featured": True
        },
        {
            "provider": "Star Health",
            "name": "Star Family Health Optima",
            "description": "Family floater plan with automatic restoration of sum insured.",
            "min_coverage": 500000,
            "max_coverage": 25000000,
            "min_age": 18,
            "max_age": 65,
            "base_premium": 15000,
            "premium_frequency": "yearly",
            "waiting_period_days": 30,
            "coverage_details": {
                "room_rent": "No limit",
                "pre_hospitalization": 60,
                "post_hospitalization": 90,
                "daycare_procedures": True,
                "ambulance_cover": 2500,
                "pre_existing_coverage": {"covered_after_waiting": True, "waiting_years": 4}
            },
            "key_features": [
                "Floater benefit for entire family",
                "Automatic 100% restoration",
                "Covers children from 16 days",
                "Organ donor expenses covered"
            ],
            "riders_available": [],
            "exclusions": ["Cosmetic surgery", "Sterility treatment", "AIDS"],
            "nyvo_rating": 4.6,
            "customer_rating": 4.4,
            "is_featured": False
        }
    ]
    
    for policy_data in health_policies:
        provider_name = policy_data.pop("provider")
        provider = providers_map.get(provider_name)
        if provider:
            policy = InsurancePolicy(
                provider_id=provider.id,
                insurance_type=InsuranceType.HEALTH,
                **policy_data
            )
            db.add(policy)


def main():
    """Main seed function"""
    print("Initializing database...")
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing = db.query(InsuranceProvider).first()
        if existing:
            print("Database already seeded. Skipping...")
            return
        
        # Seed providers
        print("Seeding insurance providers...")
        providers_map = {}
        for provider_data in seed_providers():
            provider = InsuranceProvider(**provider_data)
            db.add(provider)
            db.flush()
            providers_map[provider.short_name] = provider
        
        # Seed term policies
        print("Seeding term insurance policies...")
        seed_term_policies(db, providers_map)
        
        # Seed health policies
        print("Seeding health insurance policies...")
        seed_health_policies(db, providers_map)
        
        db.commit()
        print("✅ Database seeded successfully!")
        print(f"   - {len(providers_map)} providers added")
        print(f"   - Policies added for term and health insurance")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
