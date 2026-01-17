"""
DAMAC Finance Operations - Synthetic Test Data Generator
Generates realistic test data based on DAMAC Properties' actual business model
"""

from faker import Faker
import random
import json
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

fake = Faker()

# DAMAC-specific constants
DAMAC_PROJECTS = [
    {"name": "DAMAC Hills", "type": "villa", "location": "Dubailand"},
    {"name": "DAMAC Hills 2", "type": "townhouse", "location": "Dubailand"},
    {"name": "DAMAC Lagoons", "type": "townhouse", "location": "Dubailand"},
    {"name": "DAMAC Islands", "type": "villa", "location": "Dubai Islands"},
    {"name": "Cavalli Tower", "type": "apartment", "location": "Dubai Marina"},
    {"name": "DAMAC Bay", "type": "apartment", "location": "Dubai Harbour"},
    {"name": "DAMAC Bay 2", "type": "apartment", "location": "Dubai Harbour"},
    {"name": "Safa One", "type": "apartment", "location": "Business Bay"},
    {"name": "Safa Two", "type": "apartment", "location": "Business Bay"},
    {"name": "AYKON City", "type": "apartment", "location": "Sheikh Zayed Road"},
    {"name": "Trump DAMAC Golf", "type": "villa", "location": "DAMAC Hills"},
    {"name": "Zada Tower", "type": "apartment", "location": "Business Bay"},
]

PAYMENT_PLANS = [
    {"name": "1% Monthly", "structure": {"during_construction": 60, "on_handover": 40}, "monthly": True},
    {"name": "60/40", "structure": {"during_construction": 60, "on_handover": 40}, "monthly": False},
    {"name": "80/20", "structure": {"during_construction": 80, "on_handover": 20}, "monthly": False},
    {"name": "75/25", "structure": {"during_construction": 75, "on_handover": 25}, "monthly": False},
    {"name": "50/50", "structure": {"during_construction": 50, "on_handover": 50}, "monthly": False},
]

CONSTRUCTION_VENDORS = [
    {"name": "Al Habtoor Engineering", "category": "MEP"},
    {"name": "ALEC Engineering", "category": "Main Contractor"},
    {"name": "Arabtec Construction", "category": "Civil Works"},
    {"name": "Drake & Scull", "category": "MEP"},
    {"name": "Gulf Marble Factory", "category": "Materials"},
    {"name": "Emirates Glass", "category": "Materials"},
    {"name": "Al Futtaim Carillion", "category": "Fit-out"},
    {"name": "Depa Interiors", "category": "Interiors"},
    {"name": "Schindler Gulf", "category": "Elevators"},
    {"name": "Carrier Middle East", "category": "HVAC"},
]

INVOICE_CATEGORIES = [
    "Construction Progress",
    "Material Supply",
    "MEP Works",
    "Fit-out Works",
    "Landscaping",
    "Security Systems",
    "Smart Home Installation",
    "Swimming Pool",
    "External Works",
    "Contingency",
]

UAE_BANKS = [
    "Emirates NBD",
    "Abu Dhabi Commercial Bank",
    "Dubai Islamic Bank",
    "Mashreq Bank",
    "First Abu Dhabi Bank",
    "RAKBANK",
    "Commercial Bank of Dubai",
]

# Dubai Land Department constants
DLD_FEE_PERCENT = 4.0
VAT_PERCENT = 5.0
RETENTION_PERCENT = 5.0
BROKER_COMMISSION_PERCENT = 5.0


def generate_emirates_id():
    """Generate realistic Emirates ID format: 784-YYYY-NNNNNNN-N"""
    year = random.randint(1960, 2005)
    number = random.randint(1000000, 9999999)
    check = random.randint(0, 9)
    return f"784-{year}-{number}-{check}"


def generate_property_unit():
    """Generate a DAMAC property unit"""
    project = random.choice(DAMAC_PROJECTS)

    if project["type"] == "apartment":
        unit_types = ["Studio", "1BR", "2BR", "3BR", "Penthouse"]
        unit_type = random.choice(unit_types)
        floor = random.randint(1, 50)
        unit_number = f"{floor}{random.randint(1, 12):02d}"
        area_sqft = {
            "Studio": random.randint(400, 600),
            "1BR": random.randint(700, 1000),
            "2BR": random.randint(1100, 1500),
            "3BR": random.randint(1600, 2500),
            "Penthouse": random.randint(3000, 8000),
        }[unit_type]
        price_per_sqft = random.randint(1500, 4000)
    else:
        unit_types = ["3BR Villa", "4BR Villa", "5BR Villa", "6BR Villa", "Mansion"]
        unit_type = random.choice(unit_types)
        unit_number = f"{random.choice(['A', 'B', 'C', 'D', 'E'])}{random.randint(1, 500)}"
        area_sqft = random.randint(2500, 15000)
        price_per_sqft = random.randint(800, 2000)

    total_price = area_sqft * price_per_sqft

    return {
        "unit_id": f"DAMAC-{project['name'][:3].upper()}-{unit_number}",
        "project_name": project["name"],
        "project_type": project["type"],
        "location": project["location"],
        "unit_type": unit_type,
        "unit_number": unit_number,
        "area_sqft": area_sqft,
        "price_aed": round(total_price, -3),  # Round to nearest 1000
        "price_per_sqft": price_per_sqft,
    }


def generate_customer():
    """Generate a DAMAC customer profile"""
    nationalities = [
        ("UAE", 15), ("India", 20), ("Pakistan", 10), ("UK", 12),
        ("Russia", 8), ("China", 10), ("Saudi Arabia", 8), ("Egypt", 5),
        ("Lebanon", 4), ("Jordan", 3), ("Germany", 3), ("France", 2)
    ]
    nationality = random.choices(
        [n[0] for n in nationalities],
        weights=[n[1] for n in nationalities]
    )[0]

    return {
        "customer_id": f"CUST-{uuid.uuid4().hex[:8].upper()}",
        "name": fake.name(),
        "email": fake.email(),
        "phone": f"+971 {random.randint(50, 58)} {random.randint(100, 999)} {random.randint(1000, 9999)}",
        "nationality": nationality,
        "emirates_id": generate_emirates_id() if nationality == "UAE" else None,
        "passport_number": fake.passport_number() if nationality != "UAE" else None,
        "address": fake.address(),
        "kyc_status": random.choice(["verified", "pending", "under_review"]),
        "customer_type": random.choice(["individual", "corporate"]),
        "bank_name": random.choice(UAE_BANKS),
        "account_number": fake.iban(),
    }


def generate_sales_transaction():
    """Generate a complete property sales transaction"""
    customer = generate_customer()
    property_unit = generate_property_unit()
    payment_plan = random.choice(PAYMENT_PLANS)

    booking_date = fake.date_between(start_date='-2y', end_date='today')
    spa_date = booking_date + timedelta(days=random.randint(7, 30))
    expected_handover = spa_date + timedelta(days=random.randint(365, 1095))

    # Calculate fees
    property_price = property_unit["price_aed"]
    dld_fee = property_price * (DLD_FEE_PERCENT / 100)
    admin_fee = 4200  # Standard DAMAC admin fee
    oqood_fee = 40 * property_unit["area_sqft"]  # AED 40 per sqft for off-plan

    # Payment schedule based on plan
    construction_amount = property_price * (payment_plan["structure"]["during_construction"] / 100)
    handover_amount = property_price * (payment_plan["structure"]["on_handover"] / 100)

    return {
        "transaction_id": f"TXN-{uuid.uuid4().hex[:10].upper()}",
        "customer": customer,
        "property": property_unit,
        "payment_plan": payment_plan["name"],
        "dates": {
            "booking_date": booking_date.isoformat(),
            "spa_date": spa_date.isoformat(),
            "expected_handover": expected_handover.isoformat(),
        },
        "financials": {
            "property_price_aed": property_price,
            "dld_fee_aed": round(dld_fee, 2),
            "admin_fee_aed": admin_fee,
            "oqood_fee_aed": oqood_fee,
            "total_due_aed": property_price + dld_fee + admin_fee + oqood_fee,
            "construction_payments_aed": round(construction_amount, 2),
            "handover_payment_aed": round(handover_amount, 2),
        },
        "status": random.choice([
            "booked", "spa_signed", "under_construction",
            "ready_for_handover", "handed_over", "snagging"
        ]),
        "sales_agent": fake.name(),
        "broker": random.choice([None, fake.company()]),
        "broker_commission_aed": round(property_price * (BROKER_COMMISSION_PERCENT / 100), 2) if random.random() > 0.3 else 0,
    }


def generate_vendor_invoice():
    """Generate a construction vendor invoice"""
    vendor = random.choice(CONSTRUCTION_VENDORS)
    project = random.choice(DAMAC_PROJECTS)

    invoice_date = fake.date_between(start_date='-6m', end_date='today')
    due_date = invoice_date + timedelta(days=random.choice([30, 45, 60]))

    # Generate line items
    num_items = random.randint(1, 5)
    items = []
    subtotal = 0

    for i in range(num_items):
        quantity = random.randint(1, 100)
        unit_price = random.randint(1000, 50000)
        amount = quantity * unit_price
        subtotal += amount

        items.append({
            "line_number": i + 1,
            "description": f"{random.choice(INVOICE_CATEGORIES)} - {fake.bs()}",
            "quantity": quantity,
            "unit": random.choice(["sqm", "units", "hours", "lots", "sets"]),
            "unit_price_aed": unit_price,
            "amount_aed": amount,
        })

    vat_amount = subtotal * (VAT_PERCENT / 100)
    retention = subtotal * (RETENTION_PERCENT / 100)
    total = subtotal + vat_amount
    net_payable = total - retention

    return {
        "invoice_id": f"INV-{uuid.uuid4().hex[:8].upper()}",
        "vendor": {
            "name": vendor["name"],
            "category": vendor["category"],
            "trn": f"100{random.randint(100000000, 999999999)}",  # UAE TRN format
            "address": fake.address(),
            "bank_name": random.choice(UAE_BANKS),
            "iban": fake.iban(),
        },
        "project": {
            "name": project["name"],
            "location": project["location"],
            "cost_center": f"CC-{project['name'][:3].upper()}-{random.randint(100, 999)}",
        },
        "dates": {
            "invoice_date": invoice_date.isoformat(),
            "due_date": due_date.isoformat(),
            "received_date": (invoice_date + timedelta(days=random.randint(1, 5))).isoformat(),
        },
        "line_items": items,
        "financials": {
            "subtotal_aed": round(subtotal, 2),
            "vat_percent": VAT_PERCENT,
            "vat_amount_aed": round(vat_amount, 2),
            "total_aed": round(total, 2),
            "retention_percent": RETENTION_PERCENT,
            "retention_aed": round(retention, 2),
            "net_payable_aed": round(net_payable, 2),
        },
        "payment_terms": f"Net {(due_date - invoice_date).days}",
        "currency": "AED",
        "status": random.choice(["pending_approval", "approved", "partially_paid", "paid", "disputed", "on_hold"]),
        "approval_workflow": {
            "site_engineer": random.choice([None, {"name": fake.name(), "date": invoice_date.isoformat(), "status": "approved"}]),
            "project_manager": random.choice([None, {"name": fake.name(), "date": invoice_date.isoformat(), "status": "approved"}]),
            "finance_manager": random.choice([None, {"name": fake.name(), "date": invoice_date.isoformat(), "status": "pending"}]),
        },
        "po_number": f"PO-{random.randint(10000, 99999)}",
        "contract_reference": f"CONT-{project['name'][:3].upper()}-{random.randint(1000, 9999)}",
    }


def generate_payment_receipt():
    """Generate a customer payment receipt"""
    transaction = generate_sales_transaction()

    payment_date = fake.date_between(start_date='-1y', end_date='today')

    payment_methods = [
        ("Bank Transfer", 50),
        ("Cheque", 25),
        ("Credit Card", 15),
        ("Manager's Cheque", 10),
    ]
    payment_method = random.choices(
        [p[0] for p in payment_methods],
        weights=[p[1] for p in payment_methods]
    )[0]

    # Payment could be milestone payment, booking, or installment
    payment_types = [
        ("Booking Amount", transaction["property"]["price_aed"] * 0.10),
        ("DLD Fee", transaction["financials"]["dld_fee_aed"]),
        ("Admin Fee", transaction["financials"]["admin_fee_aed"]),
        ("Construction Milestone", transaction["property"]["price_aed"] * random.uniform(0.05, 0.20)),
        ("Handover Payment", transaction["financials"]["handover_payment_aed"]),
        ("Monthly Installment", transaction["property"]["price_aed"] * 0.01),
    ]
    payment_type, amount = random.choice(payment_types)

    return {
        "receipt_id": f"RCP-{uuid.uuid4().hex[:8].upper()}",
        "transaction_id": transaction["transaction_id"],
        "customer": {
            "customer_id": transaction["customer"]["customer_id"],
            "name": transaction["customer"]["name"],
        },
        "property": {
            "unit_id": transaction["property"]["unit_id"],
            "project_name": transaction["property"]["project_name"],
        },
        "payment": {
            "date": payment_date.isoformat(),
            "type": payment_type,
            "method": payment_method,
            "amount_aed": round(amount, 2),
            "reference": f"REF-{random.randint(100000, 999999)}",
        },
        "bank_details": {
            "bank_name": random.choice(UAE_BANKS),
            "cheque_number": f"{random.randint(100000, 999999)}" if "Cheque" in payment_method else None,
        },
        "escrow_account": f"RERA-ESC-{random.randint(10000, 99999)}",
        "status": random.choice(["cleared", "pending_clearance", "bounced"]),
    }


def generate_commission_calculation():
    """Generate broker commission calculation"""
    transaction = generate_sales_transaction()

    if not transaction["broker"]:
        transaction["broker"] = fake.company()
        transaction["broker_commission_aed"] = round(
            transaction["property"]["price_aed"] * (BROKER_COMMISSION_PERCENT / 100), 2
        )

    commission_amount = transaction["broker_commission_aed"]
    vat_on_commission = commission_amount * (VAT_PERCENT / 100)

    # Commission split
    external_broker_share = commission_amount * 0.6  # 60% to external broker
    internal_sales_share = commission_amount * 0.4   # 40% to internal sales

    return {
        "commission_id": f"COM-{uuid.uuid4().hex[:8].upper()}",
        "transaction_id": transaction["transaction_id"],
        "property": {
            "unit_id": transaction["property"]["unit_id"],
            "project_name": transaction["property"]["project_name"],
            "sale_price_aed": transaction["property"]["price_aed"],
        },
        "broker": {
            "name": transaction["broker"],
            "trn": f"100{random.randint(100000000, 999999999)}",
            "rera_number": f"BRN-{random.randint(10000, 99999)}",
        },
        "commission": {
            "rate_percent": BROKER_COMMISSION_PERCENT,
            "gross_amount_aed": commission_amount,
            "vat_amount_aed": round(vat_on_commission, 2),
            "total_with_vat_aed": round(commission_amount + vat_on_commission, 2),
        },
        "split": {
            "external_broker_aed": round(external_broker_share, 2),
            "internal_sales_aed": round(internal_sales_share, 2),
        },
        "payment_status": random.choice(["pending", "approved", "paid", "on_hold"]),
        "sales_agent": transaction["sales_agent"],
        "approval_date": fake.date_between(start_date='-3m', end_date='today').isoformat(),
    }


def generate_escrow_transaction():
    """Generate RERA-compliant escrow transaction"""
    transaction = generate_sales_transaction()

    return {
        "escrow_id": f"ESC-{uuid.uuid4().hex[:8].upper()}",
        "rera_escrow_account": f"RERA-{random.randint(10000, 99999)}",
        "project": {
            "name": transaction["property"]["project_name"],
            "rera_registration": f"RERA-PRJ-{random.randint(1000, 9999)}",
        },
        "transaction_type": random.choice([
            "customer_payment_in",
            "contractor_payment_out",
            "dld_fee_payment",
            "commission_payment",
        ]),
        "amount_aed": round(random.uniform(50000, 5000000), 2),
        "date": fake.date_between(start_date='-6m', end_date='today').isoformat(),
        "reference": f"TRF-{random.randint(100000, 999999)}",
        "narration": fake.sentence(),
        "balance_after_aed": round(random.uniform(10000000, 500000000), 2),
        "verified_by": fake.name(),
    }


def generate_test_dataset(
    num_transactions: int = 50,
    num_invoices: int = 100,
    num_receipts: int = 200,
    num_commissions: int = 30,
    num_escrow: int = 150
):
    """Generate complete test dataset"""

    print(f"Generating DAMAC test dataset...")
    print(f"  - {num_transactions} sales transactions")
    print(f"  - {num_invoices} vendor invoices")
    print(f"  - {num_receipts} payment receipts")
    print(f"  - {num_commissions} commission calculations")
    print(f"  - {num_escrow} escrow transactions")

    dataset = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "generator": "DAMAC Finance Test Data Generator",
            "version": "1.0.0",
            "counts": {
                "sales_transactions": num_transactions,
                "vendor_invoices": num_invoices,
                "payment_receipts": num_receipts,
                "commission_calculations": num_commissions,
                "escrow_transactions": num_escrow,
            }
        },
        "sales_transactions": [generate_sales_transaction() for _ in range(num_transactions)],
        "vendor_invoices": [generate_vendor_invoice() for _ in range(num_invoices)],
        "payment_receipts": [generate_payment_receipt() for _ in range(num_receipts)],
        "commission_calculations": [generate_commission_calculation() for _ in range(num_commissions)],
        "escrow_transactions": [generate_escrow_transaction() for _ in range(num_escrow)],
    }

    return dataset


def save_dataset(dataset: dict, output_dir: str = "./test_data"):
    """Save dataset to JSON files"""
    import os

    os.makedirs(output_dir, exist_ok=True)

    # Save complete dataset
    with open(f"{output_dir}/damac_complete_dataset.json", "w") as f:
        json.dump(dataset, f, indent=2, default=str)

    # Save individual collections
    for key in ["sales_transactions", "vendor_invoices", "payment_receipts",
                "commission_calculations", "escrow_transactions"]:
        with open(f"{output_dir}/damac_{key}.json", "w") as f:
            json.dump(dataset[key], f, indent=2, default=str)

    print(f"\nDataset saved to {output_dir}/")
    print(f"  - damac_complete_dataset.json (all data)")
    print(f"  - damac_sales_transactions.json")
    print(f"  - damac_vendor_invoices.json")
    print(f"  - damac_payment_receipts.json")
    print(f"  - damac_commission_calculations.json")
    print(f"  - damac_escrow_transactions.json")


if __name__ == "__main__":
    # Generate and save test dataset
    dataset = generate_test_dataset()
    save_dataset(dataset)

    # Print sample data
    print("\n" + "="*60)
    print("SAMPLE DATA PREVIEW")
    print("="*60)

    print("\n--- Sample Sales Transaction ---")
    print(json.dumps(dataset["sales_transactions"][0], indent=2, default=str))

    print("\n--- Sample Vendor Invoice ---")
    print(json.dumps(dataset["vendor_invoices"][0], indent=2, default=str))
