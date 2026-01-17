"""
Test DAMAC Finance AI with GPT-5 Models
"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Use latest GPT-5 models
ORCHESTRATOR_MODEL = os.getenv('OPENAI_MODEL_ORCHESTRATOR', 'gpt-5-mini')
AGENT_MODEL = os.getenv('OPENAI_MODEL_AGENTS', 'gpt-5-mini')


def classify_intent(query: str) -> dict:
    """Orchestrator: Classify query intent using GPT-5-mini"""
    response = client.chat.completions.create(
        model=ORCHESTRATOR_MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are the DAMAC Finance AI orchestrator. Classify user queries into:
- "invoice": Vendor invoices, PO, payments to vendors
- "payment": Customer payment plans, milestones, escrow
- "commission": Broker commissions, sales agent payouts
- "general": Other queries

Respond with JSON: {"intent": "...", "confidence": 0.0-1.0, "entities": {...}}

Extract entities like amounts, vendor names, project names, dates."""
            },
            {"role": "user", "content": query}
        ],
        response_format={"type": "json_object"},
        max_completion_tokens=1000  # GPT-5 needs more for reasoning + output
    )
    return json.loads(response.choices[0].message.content)


def process_invoice(query: str, entities: dict) -> dict:
    """Invoice Agent: Process vendor invoice queries"""
    response = client.chat.completions.create(
        model=AGENT_MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are DAMAC's Invoice Processing Agent.

UAE Tax Rules:
- VAT: 5% on subtotal
- Retention: 5% held for 12 months (defects liability)
- Net Payable = Subtotal + VAT - Retention

Approval Thresholds:
- Up to AED 50,000: Auto-approve
- AED 50,001 - 500,000: Project Manager
- AED 500,001 - 2,000,000: Finance Director
- Above AED 2,000,000: CFO

TRN Format: 15 digits starting with 100

Respond with JSON containing: parsed_invoice, calculations, approval_routing, validation"""
            },
            {"role": "user", "content": f"Query: {query}\nEntities: {json.dumps(entities)}"}
        ],
        response_format={"type": "json_object"},
        max_completion_tokens=2000  # More tokens for complex calculations
    )
    return json.loads(response.choices[0].message.content)


def process_payment(query: str, entities: dict) -> dict:
    """Payment Agent: Process payment plan queries"""
    response = client.chat.completions.create(
        model=AGENT_MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are DAMAC's Payment Plan Agent.

Payment Plans:
- 1% Monthly: 1% per month during construction, 40% on handover
- 60/40: 60% during construction (milestones), 40% on handover
- 80/20: 80% during construction, 20% on handover

Dubai Fees:
- DLD Fee: 4% of property value
- Admin Fee: AED 4,200
- Oqood (off-plan): AED 40/sqft

Escrow: All payments go to RERA-regulated escrow account.

Respond with JSON containing: payment_status, milestones, calculations, next_due"""
            },
            {"role": "user", "content": f"Query: {query}\nEntities: {json.dumps(entities)}"}
        ],
        response_format={"type": "json_object"},
        max_completion_tokens=4000  # Payment needs more for milestone calculations
    )
    return json.loads(response.choices[0].message.content)


def process_commission(query: str, entities: dict) -> dict:
    """Commission Agent: Calculate broker commissions"""
    response = client.chat.completions.create(
        model=AGENT_MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are DAMAC's Commission Agent.

Commission Structure:
- Standard rate: 5% of sale price
- VAT on commission: 5%

Commission Split:
- External broker: 60%
- Internal sales: 40%

RERA BRN Format: BRN-XXXXX (5 digits)

Respond with JSON containing: calculation, split, broker_validation, total_payable"""
            },
            {"role": "user", "content": f"Query: {query}\nEntities: {json.dumps(entities)}"}
        ],
        response_format={"type": "json_object"},
        max_completion_tokens=3000
    )
    return json.loads(response.choices[0].message.content)


def run_query(query: str) -> dict:
    """Full pipeline: Orchestrator -> Agent"""
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print('='*60)

    # Step 1: Classify
    print(f"\n[1] ORCHESTRATOR ({ORCHESTRATOR_MODEL}) - Classifying...")
    classification = classify_intent(query)
    print(f"    Intent: {classification.get('intent')}")
    print(f"    Confidence: {classification.get('confidence')}")
    print(f"    Entities: {classification.get('entities', {})}")

    intent = classification.get('intent', 'general')
    entities = classification.get('entities', {})

    # Step 2: Route to agent
    print(f"\n[2] {intent.upper()} AGENT ({AGENT_MODEL}) - Processing...")

    if intent == 'invoice':
        result = process_invoice(query, entities)
    elif intent == 'payment':
        result = process_payment(query, entities)
    elif intent == 'commission':
        result = process_commission(query, entities)
    else:
        result = {"message": "General query - no specific agent needed", "entities": entities}

    print(f"\n[3] RESULT:")
    print(json.dumps(result, indent=2))

    return {
        "query": query,
        "classification": classification,
        "result": result
    }


if __name__ == "__main__":
    print("="*60)
    print("DAMAC FINANCE AI - GPT-5 LIVE TEST")
    print(f"Orchestrator: {ORCHESTRATOR_MODEL}")
    print(f"Agent Model: {AGENT_MODEL}")
    print("="*60)

    # Test 1: Invoice
    run_query("Process the invoice from Al Habtoor Engineering for AED 850,000 for MEP works at DAMAC Hills 2")

    # Test 2: Payment
    run_query("What's the payment status for a customer on 60/40 plan who bought a AED 3.5M villa at DAMAC Hills?")

    # Test 3: Commission
    run_query("Calculate commission for AED 4.5 million sale at Safa One with broker ABC Realty (BRN-12345)")

    print("\n" + "="*60)
    print("ALL GPT-5 TESTS COMPLETE!")
    print("="*60)
