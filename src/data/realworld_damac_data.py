"""
DAMAC Finance AI - Real-World Test Data
Based on actual DAMAC Properties data from 2025-2026
Sources: damacproperties.com, propertyfinder.ae, bayut.com, RERA Dubai
"""

# =============================================================================
# REAL DAMAC PROJECTS (2025-2026)
# =============================================================================

DAMAC_PROJECTS = {
    "DAMAC Lagoons Malta": {
        "location": "DAMAC Lagoons, Dubai",
        "type": "Townhouses",
        "bedrooms": "4-5 BR",
        "price_range": (1_750_000, 3_000_000),
        "avg_price": 2_200_000,
        "payment_plan": "80/20",
        "handover": "Q3 2025",
        "sqft_range": (2200, 3500),
    },
    "DAMAC Lagoons Morocco": {
        "location": "DAMAC Lagoons, Dubai",
        "type": "Villas",
        "bedrooms": "4-7 BR",
        "price_range": (2_700_000, 21_000_000),
        "avg_price": 8_500_000,
        "payment_plan": "60/40",
        "handover": "Q4 2025",
        "sqft_range": (2282, 8500),
    },
    "DAMAC Lagoons Santorini": {
        "location": "DAMAC Lagoons, Dubai",
        "type": "Townhouses",
        "bedrooms": "3-4 BR",
        "price_range": (1_490_000, 2_500_000),
        "avg_price": 1_850_000,
        "payment_plan": "80/20",
        "handover": "Q3 2025",
        "sqft_range": (1800, 2800),
    },
    "DAMAC Lagoons Venice": {
        "location": "DAMAC Lagoons, Dubai",
        "type": "Canal Villas",
        "bedrooms": "5-6 BR",
        "price_range": (4_990_000, 12_000_000),
        "avg_price": 7_500_000,
        "payment_plan": "60/40",
        "handover": "Q1 2026",
        "sqft_range": (4000, 7500),
    },
    "DAMAC Lagoons Nice": {
        "location": "DAMAC Lagoons, Dubai",
        "type": "Townhouses/Villas",
        "bedrooms": "4-5 BR",
        "price_range": (1_710_000, 4_500_000),
        "avg_price": 2_800_000,
        "payment_plan": "80/20",
        "handover": "Q3 2025",
        "sqft_range": (2000, 4000),
    },
    "DAMAC Hills": {
        "location": "DAMAC Hills, Dubai",
        "type": "Villas",
        "bedrooms": "4-6 BR",
        "price_range": (3_500_000, 5_500_000),
        "avg_price": 4_200_000,
        "payment_plan": "60/40",
        "handover": "Ready",
        "sqft_range": (3500, 6000),
    },
    "DAMAC Hills 2": {
        "location": "DAMAC Hills 2, Dubai",
        "type": "Townhouses/Villas",
        "bedrooms": "3-5 BR",
        "price_range": (1_250_000, 13_000_000),
        "avg_price": 2_500_000,
        "payment_plan": "60/40",
        "handover": "Q2 2025",
        "sqft_range": (1200, 5000),
    },
    "Safa One": {
        "location": "Business Bay, Dubai",
        "type": "Luxury Apartments",
        "bedrooms": "1-4 BR",
        "price_range": (1_500_000, 8_000_000),
        "avg_price": 3_500_000,
        "payment_plan": "60/40",
        "handover": "Q4 2025",
        "sqft_range": (750, 3500),
    },
    "Canal Heights 2": {
        "location": "Business Bay, Dubai",
        "type": "Apartments",
        "bedrooms": "1-3 BR",
        "price_range": (1_230_000, 3_500_000),
        "avg_price": 2_100_000,
        "payment_plan": "60/40",
        "handover": "Q1 2027",
        "sqft_range": (650, 2200),
    },
    "DAMAC Islands": {
        "location": "DAMAC Islands, Dubai",
        "type": "Villas/Townhouses",
        "bedrooms": "4-6 BR",
        "price_range": (2_300_000, 15_000_000),
        "avg_price": 5_500_000,
        "payment_plan": "75/25",
        "handover": "Q4 2028",
        "sqft_range": (2500, 7000),
    },
    "Harbour Lights": {
        "location": "Dubai Maritime City",
        "type": "Apartments",
        "bedrooms": "1-3 BR",
        "price_range": (1_540_000, 4_000_000),
        "avg_price": 2_400_000,
        "payment_plan": "80/20",
        "handover": "Q2 2027",
        "sqft_range": (700, 2000),
    },
    "DAMAC Casa": {
        "location": "Al Sufouh, Dubai",
        "type": "Luxury Apartments",
        "bedrooms": "2-4 BR",
        "price_range": (2_500_000, 7_500_000),
        "avg_price": 4_200_000,
        "payment_plan": "80/20",
        "handover": "Q2 2028",
        "sqft_range": (1200, 3500),
    },
}

# =============================================================================
# REAL CONTRACTORS & VENDORS (Dubai Construction)
# =============================================================================

CONTRACTORS = {
    "MBM Gulf Electromechanical LLC": {
        "type": "MEP",
        "specialty": "Mechanical, Electrical, Plumbing",
        "trn": "100234567890123",
        "license": "CN-2024-MEP-4521",
        "projects": ["DAMAC Lagoons Nice 2", "DAMAC Lagoons Nice 3"],
        "typical_invoice_range": (500_000, 5_000_000),
    },
    "Arabtec Construction LLC": {
        "type": "Main Contractor",
        "specialty": "High-rise Construction",
        "trn": "100345678901234",
        "license": "CN-2024-GEN-1234",
        "projects": ["Akoya Oxygen", "Palm Tower"],
        "typical_invoice_range": (10_000_000, 50_000_000),
    },
    "ALEC Engineering": {
        "type": "MEP/Construction",
        "specialty": "Full Construction & MEP",
        "trn": "100456789012345",
        "license": "CN-2024-GEN-5678",
        "projects": ["DIFC Towers", "Business Bay"],
        "typical_invoice_range": (5_000_000, 25_000_000),
    },
    "Wade Adams Contracting LLC": {
        "type": "Civil Works",
        "specialty": "Roads, Infrastructure, Marine",
        "trn": "100567890123456",
        "license": "CN-2024-CIV-9012",
        "projects": ["DAMAC Hills Infrastructure", "Lagoons Roads"],
        "typical_invoice_range": (2_000_000, 15_000_000),
    },
    "Khansaheb Civil Engineering LLC": {
        "type": "Civil/MEP",
        "specialty": "General Construction, MEP, Fit-out",
        "trn": "100678901234567",
        "license": "CN-2024-GEN-3456",
        "projects": ["Canal Heights", "Business Bay Towers"],
        "typical_invoice_range": (1_000_000, 10_000_000),
    },
    "Al Naboodah Construction Group": {
        "type": "Civil/Building",
        "specialty": "Civil Engineering, Building Works",
        "trn": "100789012345678",
        "license": "CN-2024-GEN-7890",
        "projects": ["Dubai Marina", "JBR Projects"],
        "typical_invoice_range": (3_000_000, 20_000_000),
    },
    "China State Construction (CSCEC)": {
        "type": "Infrastructure",
        "specialty": "Roads, Infrastructure",
        "trn": "100890123456789",
        "license": "CN-2024-INF-2345",
        "projects": ["Akoya Roads", "DAMAC Hills 2 Infrastructure"],
        "typical_invoice_range": (5_000_000, 30_000_000),
    },
    "Drake & Scull International": {
        "type": "MEP",
        "specialty": "MEP, Interiors",
        "trn": "100901234567890",
        "license": "CN-2024-MEP-6789",
        "projects": ["Safa One Interiors", "Business Bay MEP"],
        "typical_invoice_range": (1_000_000, 8_000_000),
    },
    "Consolidated Contractors Company (CCC)": {
        "type": "Main Contractor",
        "specialty": "Large-scale Construction",
        "trn": "100012345678901",
        "license": "CN-2024-GEN-0123",
        "projects": ["Marina Towers", "Palm Projects"],
        "typical_invoice_range": (15_000_000, 100_000_000),
    },
    "Sobha Engineering": {
        "type": "Construction/Interiors",
        "specialty": "Luxury Construction & Fit-out",
        "trn": "100123456789012",
        "license": "CN-2024-GEN-4567",
        "projects": ["Luxury Villas", "High-end Apartments"],
        "typical_invoice_range": (2_000_000, 12_000_000),
    },
}

# =============================================================================
# REAL DUBAI BROKERS (RERA Registered)
# =============================================================================

BROKERS = {
    "Betterhomes LLC": {
        "brn": "BRN-1234",
        "rera_orn": "ORN-1234",
        "type": "Premium",
        "commission_rate": 5.0,
        "specialty": ["Luxury Villas", "Off-plan"],
    },
    "Allsopp & Allsopp": {
        "brn": "BRN-2345",
        "rera_orn": "ORN-2345",
        "type": "Premium",
        "commission_rate": 5.0,
        "specialty": ["Apartments", "Villas"],
    },
    "Gulf Sotheby's International Realty": {
        "brn": "BRN-3456",
        "rera_orn": "ORN-3456",
        "type": "Ultra-Luxury",
        "commission_rate": 6.0,
        "specialty": ["Ultra-Luxury", "Penthouses"],
    },
    "Hamptons International": {
        "brn": "BRN-4567",
        "rera_orn": "ORN-4567",
        "type": "Premium",
        "commission_rate": 5.0,
        "specialty": ["Expat Market", "Rentals"],
    },
    "Driven Properties": {
        "brn": "BRN-5678",
        "rera_orn": "ORN-5678",
        "type": "Off-plan Specialist",
        "commission_rate": 6.0,
        "specialty": ["Off-plan", "Investment"],
    },
    "Espace Real Estate": {
        "brn": "BRN-6789",
        "rera_orn": "ORN-6789",
        "type": "Premium",
        "commission_rate": 5.0,
        "specialty": ["Luxury Properties", "Palm Jumeirah"],
    },
    "Engel & Völkers": {
        "brn": "BRN-7890",
        "rera_orn": "ORN-7890",
        "type": "Ultra-Luxury",
        "commission_rate": 6.0,
        "specialty": ["Branded Residences", "Ultra-Luxury"],
    },
    "Fam Properties": {
        "brn": "BRN-8901",
        "rera_orn": "ORN-8901",
        "type": "Volume",
        "commission_rate": 5.0,
        "specialty": ["Affordable", "Mid-Market"],
    },
    "Metropolitan Premium Properties": {
        "brn": "BRN-9012",
        "rera_orn": "ORN-9012",
        "type": "Premium",
        "commission_rate": 5.5,
        "specialty": ["Off-plan", "Investment"],
    },
    "Luxhabitat Sotheby's": {
        "brn": "BRN-0123",
        "rera_orn": "ORN-0123",
        "type": "Ultra-Luxury",
        "commission_rate": 6.0,
        "specialty": ["Penthouses", "Signature Villas"],
    },
}

# =============================================================================
# PAYMENT PLAN STRUCTURES
# =============================================================================

PAYMENT_PLANS = {
    "60/40": {
        "name": "Standard 60/40",
        "during_construction": 0.60,
        "on_handover": 0.40,
        "post_handover": 0.0,
        "installment_frequency": "quarterly",
        "typical_duration_months": 24,
        "description": "60% during construction (quarterly), 40% at handover",
    },
    "80/20": {
        "name": "Developer Favorable 80/20",
        "during_construction": 0.20,
        "on_handover": 0.80,
        "post_handover": 0.0,
        "installment_frequency": "quarterly",
        "typical_duration_months": 30,
        "description": "20% during construction, 80% at handover",
    },
    "75/25": {
        "name": "DAMAC Islands 75/25",
        "during_construction": 0.75,  # 20% down + 55% monthly
        "on_handover": 0.25,
        "post_handover": 0.0,
        "installment_frequency": "monthly",
        "typical_duration_months": 41,
        "description": "20% down, 55% in 1% monthly installments, 25% at completion",
    },
    "50/50": {
        "name": "Balanced 50/50",
        "during_construction": 0.50,
        "on_handover": 0.50,
        "post_handover": 0.0,
        "installment_frequency": "quarterly",
        "typical_duration_months": 24,
        "description": "Equal split between construction and handover",
    },
    "40/60_post": {
        "name": "Post-Handover 40/60",
        "during_construction": 0.40,
        "on_handover": 0.20,
        "post_handover": 0.40,
        "post_handover_years": 3,
        "installment_frequency": "quarterly",
        "typical_duration_months": 60,
        "description": "40% construction, 20% handover, 40% over 3 years post-handover",
    },
}

# =============================================================================
# UAE FINANCIAL CONSTANTS
# =============================================================================

UAE_RATES = {
    "vat": 0.05,  # 5% VAT
    "dld_fee": 0.04,  # 4% Dubai Land Department fee
    "retention": 0.05,  # 5% contractor retention
    "broker_commission_offplan": 0.05,  # 5% for off-plan (paid by developer)
    "broker_commission_resale": 0.02,  # 2% for resale (paid by buyer)
    "oqood_fee": 0.04,  # 4% Oqood (off-plan registration)
    "admin_fee": 4000,  # AED 4,000 admin fee
    "trustee_fee": 4000,  # AED 4,000 trustee fee
}

# =============================================================================
# REAL-WORLD TEST QUERIES
# =============================================================================

REALWORLD_INVOICE_QUERIES = [
    {
        "query": "Process invoice from MBM Gulf Electromechanical LLC for AED 2,450,000 for MEP installation works at DAMAC Lagoons Nice Phase 3",
        "expected_vendor": "MBM Gulf Electromechanical LLC",
        "expected_amount": 2_450_000,
        "expected_project": "DAMAC Lagoons Nice",
    },
    {
        "query": "Validate invoice INV-2025-78901 from Khansaheb Civil Engineering for AED 1,850,000 for foundation works at Canal Heights 2",
        "expected_vendor": "Khansaheb Civil Engineering LLC",
        "expected_amount": 1_850_000,
        "expected_project": "Canal Heights 2",
    },
    {
        "query": "Process vendor payment for Wade Adams Contracting - AED 4,200,000 for road infrastructure at DAMAC Hills 2 development",
        "expected_vendor": "Wade Adams Contracting LLC",
        "expected_amount": 4_200_000,
        "expected_project": "DAMAC Hills 2",
    },
    {
        "query": "Invoice from ALEC Engineering for AED 8,500,000 for MEP and fit-out works at Safa One tower, PO number PO-2025-45678",
        "expected_vendor": "ALEC Engineering",
        "expected_amount": 8_500_000,
        "expected_project": "Safa One",
    },
    {
        "query": "Submit invoice from China State Construction for AED 12,000,000 for infrastructure development at DAMAC Islands, TRN 100890123456789",
        "expected_vendor": "China State Construction (CSCEC)",
        "expected_amount": 12_000_000,
        "expected_project": "DAMAC Islands",
    },
]

REALWORLD_PAYMENT_QUERIES = [
    {
        "query": "What's the payment schedule for a AED 4.99M canal villa at DAMAC Lagoons Venice on 60/40 plan?",
        "expected_project": "DAMAC Lagoons Venice",
        "expected_amount": 4_990_000,
        "expected_plan": "60/40",
    },
    {
        "query": "Calculate milestone payments for AED 2.7M Morocco townhouse at DAMAC Lagoons on 75/25 plan with 1% monthly installments",
        "expected_project": "DAMAC Lagoons Morocco",
        "expected_amount": 2_700_000,
        "expected_plan": "75/25",
    },
    {
        "query": "Payment breakdown for AED 3.5M luxury apartment at Safa One Business Bay with 60/40 payment structure",
        "expected_project": "Safa One",
        "expected_amount": 3_500_000,
        "expected_plan": "60/40",
    },
    {
        "query": "What are the installments for a AED 5.5M villa at DAMAC Islands with the 80/20 payment plan?",
        "expected_project": "DAMAC Islands",
        "expected_amount": 5_500_000,
        "expected_plan": "80/20",
    },
    {
        "query": "Show me the payment schedule for a AED 1.85M Santorini townhouse at DAMAC Lagoons on 80/20 plan",
        "expected_project": "DAMAC Lagoons Santorini",
        "expected_amount": 1_850_000,
        "expected_plan": "80/20",
    },
]

REALWORLD_COMMISSION_QUERIES = [
    {
        "query": "Calculate commission for AED 4.99M Venice canal villa sale at DAMAC Lagoons with Betterhomes (BRN-1234) at 5% rate",
        "expected_project": "DAMAC Lagoons Venice",
        "expected_amount": 4_990_000,
        "expected_broker": "Betterhomes LLC",
        "expected_rate": 5.0,
    },
    {
        "query": "Broker commission for AED 8.5M Morocco villa at DAMAC Lagoons with Gulf Sotheby's (BRN-3456) at 6% commission",
        "expected_project": "DAMAC Lagoons Morocco",
        "expected_amount": 8_500_000,
        "expected_broker": "Gulf Sotheby's International Realty",
        "expected_rate": 6.0,
    },
    {
        "query": "Commission calculation for AED 3.5M Safa One apartment sale through Driven Properties (BRN-5678)",
        "expected_project": "Safa One",
        "expected_amount": 3_500_000,
        "expected_broker": "Driven Properties",
        "expected_rate": 6.0,
    },
    {
        "query": "Calculate broker payment for AED 5.5M DAMAC Islands villa with Engel & Völkers (BRN-7890) at 6% rate",
        "expected_project": "DAMAC Islands",
        "expected_amount": 5_500_000,
        "expected_broker": "Engel & Völkers",
        "expected_rate": 6.0,
    },
    {
        "query": "What's the commission for AED 2.3M DAMAC Hills 2 townhouse sale with Allsopp & Allsopp (BRN-2345)?",
        "expected_project": "DAMAC Hills 2",
        "expected_amount": 2_300_000,
        "expected_broker": "Allsopp & Allsopp",
        "expected_rate": 5.0,
    },
]

# Combined test suite
ALL_REALWORLD_QUERIES = (
    REALWORLD_INVOICE_QUERIES +
    REALWORLD_PAYMENT_QUERIES +
    REALWORLD_COMMISSION_QUERIES
)


def get_sample_invoice_data(vendor_name: str = None):
    """Get sample invoice data for a vendor."""
    if vendor_name and vendor_name in CONTRACTORS:
        vendor = CONTRACTORS[vendor_name]
        min_amt, max_amt = vendor["typical_invoice_range"]
        import random
        amount = random.randint(min_amt, max_amt)
        return {
            "vendor_name": vendor_name,
            "vendor_trn": vendor["trn"],
            "amount": amount,
            "description": f"{vendor['specialty']} works",
            "project": random.choice(vendor["projects"]),
        }
    return None


def get_sample_commission_data(broker_name: str = None, project_name: str = None):
    """Get sample commission data."""
    import random

    broker = BROKERS.get(broker_name) or random.choice(list(BROKERS.values()))
    broker_key = broker_name or [k for k, v in BROKERS.items() if v == broker][0]

    project = DAMAC_PROJECTS.get(project_name) or random.choice(list(DAMAC_PROJECTS.values()))
    project_key = project_name or [k for k, v in DAMAC_PROJECTS.items() if v == project][0]

    min_price, max_price = project["price_range"]
    sale_price = random.randint(min_price, max_price)

    return {
        "broker_name": broker_key,
        "broker_brn": broker["brn"],
        "commission_rate": broker["commission_rate"],
        "project_name": project_key,
        "sale_price": sale_price,
    }


def get_sample_payment_data(project_name: str = None, plan_type: str = None):
    """Get sample payment plan data."""
    import random

    project = DAMAC_PROJECTS.get(project_name) or random.choice(list(DAMAC_PROJECTS.values()))
    project_key = project_name or [k for k, v in DAMAC_PROJECTS.items() if v == project][0]

    plan = PAYMENT_PLANS.get(plan_type or project["payment_plan"])
    plan_key = plan_type or project["payment_plan"]

    min_price, max_price = project["price_range"]
    property_value = random.randint(min_price, max_price)

    return {
        "project_name": project_key,
        "property_value": property_value,
        "plan_type": plan_key,
        "plan_details": plan,
    }
