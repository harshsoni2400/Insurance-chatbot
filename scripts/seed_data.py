#!/usr/bin/env python3
"""Seed database with insurance data from Excel file"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from app.models import (
    init_db, SessionLocal, InsuranceProvider, InsurancePolicy, InsuranceType
)


def seed_from_excel():
    """Seed database from Master Database Excel file"""
    excel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'nyvo-content', 'Master Database_V21.xlsx')
    
    if not os.path.exists(excel_path):
        print(f"Excel file not found at {excel_path}, using default data...")
        return seed_default_data()
    
    print(f"Reading data from {excel_path}...")
    xl = pd.ExcelFile(excel_path)
    
    # Read Company Database
    companies_df = pd.read_excel(xl, sheet_name='Company Database')
    
    # Read Policy Database
    policies_df = pd.read_excel(xl, sheet_name='Base Policy Database')
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing = db.query(InsuranceProvider).first()
        if existing:
            print("Database already seeded. Skipping...")
            return
        
        # Seed providers from Company Database
        print("Seeding insurance providers...")
        providers_map = {}
        
        for _, row in companies_df.iterrows():
            provider = InsuranceProvider(
                name=str(row['Name of the Insurance Company']),
                short_name=str(row['Display name']),
                claim_settlement_ratio=float(row['Claim ratio avg']) * 100 if pd.notna(row['Claim ratio avg']) else None,
                irdai_registration=str(row.get('S.no', '')),
                website=None,
                customer_support=None
            )
            db.add(provider)
            db.flush()
            providers_map[row['Display name']] = provider
        
        # Seed policies from Base Policy Database
        print("Seeding insurance policies...")
        
        # Get policy columns (skip first 4 columns which are metadata)
        policy_columns = policies_df.columns[4:].tolist()
        
        # Map policy names to providers
        policy_provider_map = {
            'Activ One Next': 'Aditya Birla Health Insurance ',
            'Activ One – MAX': 'Aditya Birla Health Insurance ',
            'Activ One VYTL': 'Aditya Birla Health Insurance ',
            'Activ One – MAX+': 'Aditya Birla Health Insurance ',
            'Ultimate Care': 'Care Health Insurance ',
            'Care Supreme': 'Care Health Insurance ',
            'Optima Secure': 'HDFC ERGO General Insurance',
        }
        
        for policy_name in policy_columns:
            provider_name = policy_provider_map.get(policy_name)
            provider = None
            
            # Find provider
            for pname, prov in providers_map.items():
                if provider_name and provider_name.strip() in pname:
                    provider = prov
                    break
            
            if not provider:
                # Try to get from first row of policy column
                first_row = policies_df[policies_df['Main Heading'] == 'Company'][policy_name].values
                if len(first_row) > 0:
                    company_name = str(first_row[0])
                    for pname, prov in providers_map.items():
                        if company_name in pname or pname in company_name:
                            provider = prov
                            break
            
            if not provider:
                print(f"  Skipping {policy_name} - no provider found")
                continue
            
            # Build features from the Excel data
            features = []
            coverage_details = {}
            
            for _, row in policies_df.iterrows():
                if pd.isna(row['Main Heading']) or pd.isna(row.get(policy_name)):
                    continue
                
                heading = str(row['Main Heading'])
                feature_name = str(row['Features']) if pd.notna(row['Features']) else ''
                value = str(row[policy_name])
                
                if value and value != 'nan':
                    if heading == 'Overview':
                        features.append(value)
                    elif feature_name:
                        coverage_details[feature_name] = value
                        if 'Yes' in value or 'Covered' in value:
                            features.append(f"{feature_name}: {value}")
            
            policy = InsurancePolicy(
                provider_id=provider.id,
                insurance_type=InsuranceType.HEALTH,
                name=policy_name,
                description=features[0] if features else f"{policy_name} Health Insurance Plan",
                min_coverage=300000,
                max_coverage=10000000,
                min_age=18,
                max_age=65,
                base_premium=10000,
                premium_frequency="yearly",
                waiting_period_days=30,
                coverage_details=coverage_details,
                key_features=features[:10],
                riders_available=[],
                exclusions=[],
                nyvo_rating=4.5,
                customer_rating=4.3,
                is_featured=True
            )
            db.add(policy)
            print(f"  Added: {policy_name} ({provider.short_name})")
        
        db.commit()
        print(f"\n✅ Database seeded successfully!")
        print(f"   - {len(providers_map)} providers added")
        print(f"   - Multiple health insurance policies added")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def seed_default_data():
    """Fallback: seed with default hardcoded data"""
    print("Using default seed data...")
    
    providers = [
        {"name": "HDFC ERGO Health Insurance", "short_name": "HDFC ERGO", "claim_settlement_ratio": 89.2},
        {"name": "Star Health Insurance", "short_name": "Star Health", "claim_settlement_ratio": 86.1},
        {"name": "Care Health Insurance", "short_name": "Care Health", "claim_settlement_ratio": 94.2},
        {"name": "Niva Bupa Health Insurance", "short_name": "Niva Bupa", "claim_settlement_ratio": 91.9},
        {"name": "Aditya Birla Health Insurance", "short_name": "ABHI", "claim_settlement_ratio": 95.8},
    ]
    
    db = SessionLocal()
    try:
        existing = db.query(InsuranceProvider).first()
        if existing:
            print("Database already seeded. Skipping...")
            return
            
        for p in providers:
            provider = InsuranceProvider(**p)
            db.add(provider)
        
        db.commit()
        print("✅ Default data seeded!")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main seed function"""
    print("Initializing database...")
    init_db()
    seed_from_excel()


if __name__ == "__main__":
    main()
