#!/usr/bin/env python3
"""
DAMAC Finance AI - MCP Server
Model Context Protocol server for Claude Desktop integration

This server exposes DAMAC Finance AI tools that can be called directly
from Claude Desktop or any MCP-compatible client.

Tools:
- process_invoice: Process vendor invoices with UAE tax calculations
- calculate_payment_plan: Generate DAMAC property payment schedules
- calculate_commission: Calculate broker commissions with RERA validation
- query_finance: Process any natural language finance query

Setup:
1. Add to Claude Desktop config (~/.config/claude/claude_desktop_config.json):
   {
     "mcpServers": {
       "damac-finance-ai": {
         "command": "python",
         "args": ["/path/to/mcp_server.py"],
         "env": {"OPENAI_API_KEY": "your-key"}
       }
     }
   }
2. Restart Claude Desktop
3. Ask Claude to use DAMAC Finance AI tools
"""

import asyncio
import json
import os
import sys
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import DAMAC Finance AI agents
from src.llm import (
    OrchestratorLLMAgent,
    InvoiceLLMAgent,
    PaymentLLMAgent,
    CommissionLLMAgent,
)
from src.data.realworld_damac_data import (
    DAMAC_PROJECTS,
    CONTRACTORS,
    BROKERS,
    PAYMENT_PLANS,
    UAE_RATES,
)

# Initialize MCP server
server = Server("damac-finance-ai")

# Initialize agents (lazy loading)
_orchestrator = None
_invoice_agent = None
_payment_agent = None
_commission_agent = None


def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorLLMAgent()
    return _orchestrator


def get_invoice_agent():
    global _invoice_agent
    if _invoice_agent is None:
        _invoice_agent = InvoiceLLMAgent()
    return _invoice_agent


def get_payment_agent():
    global _payment_agent
    if _payment_agent is None:
        _payment_agent = PaymentLLMAgent()
    return _payment_agent


def get_commission_agent():
    global _commission_agent
    if _commission_agent is None:
        _commission_agent = CommissionLLMAgent()
    return _commission_agent


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available DAMAC Finance AI tools."""
    return [
        Tool(
            name="process_invoice",
            description="""Process a vendor invoice for DAMAC Properties projects.

Calculates:
- VAT (5%) on the invoice amount
- Retention (5%) held until project completion
- Net payable amount
- Approval workflow based on amount thresholds

Supports real DAMAC contractors: MBM Gulf, ALEC, Khansaheb, Wade Adams, etc.
Projects: DAMAC Lagoons, DAMAC Hills, Safa One, DAMAC Islands, etc.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "vendor_name": {
                        "type": "string",
                        "description": "Name of the vendor/contractor (e.g., 'MBM Gulf Electromechanical LLC')"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Invoice amount in AED"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "DAMAC project name (e.g., 'DAMAC Lagoons Nice')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of work (e.g., 'MEP installation works')"
                    },
                    "po_number": {
                        "type": "string",
                        "description": "Purchase order number (optional)"
                    }
                },
                "required": ["vendor_name", "amount", "project_name"]
            }
        ),
        Tool(
            name="calculate_payment_plan",
            description="""Calculate payment schedule for DAMAC property purchase.

Supports payment plans:
- 60/40: 60% during construction, 40% at handover
- 80/20: 20% during construction, 80% at handover
- 75/25: DAMAC Islands plan with 1% monthly installments
- 50/50: Equal split between construction and handover

Includes:
- DLD fee (4% of property value)
- Admin fees
- Milestone breakdown with dates

Real projects: DAMAC Lagoons (Venice, Morocco, Santorini), DAMAC Hills, Safa One, etc.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "property_value": {
                        "type": "number",
                        "description": "Property value in AED (e.g., 4990000 for AED 4.99M)"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "DAMAC project name (e.g., 'DAMAC Lagoons Venice')"
                    },
                    "plan_type": {
                        "type": "string",
                        "description": "Payment plan type: '60/40', '80/20', '75/25', or '50/50'",
                        "default": "60/40"
                    }
                },
                "required": ["property_value", "project_name"]
            }
        ),
        Tool(
            name="calculate_commission",
            description="""Calculate broker commission for DAMAC property sale.

Calculates:
- Gross commission based on rate (typically 5-6% for off-plan)
- VAT (5%) on commission
- Split between external broker (60%) and internal sales (40%)
- RERA broker registration validation

Real brokers: Betterhomes, Gulf Sotheby's, Allsopp & Allsopp, Driven Properties, etc.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "sale_price": {
                        "type": "number",
                        "description": "Property sale price in AED"
                    },
                    "broker_name": {
                        "type": "string",
                        "description": "Broker/agency name (e.g., 'Gulf Sotheby\\'s')"
                    },
                    "broker_brn": {
                        "type": "string",
                        "description": "RERA Broker Registration Number (e.g., 'BRN-3456')"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "DAMAC project name"
                    },
                    "commission_rate": {
                        "type": "number",
                        "description": "Commission rate percentage (default: 5.0)",
                        "default": 5.0
                    }
                },
                "required": ["sale_price", "broker_name", "broker_brn"]
            }
        ),
        Tool(
            name="query_finance",
            description="""Process any natural language finance query about DAMAC Properties.

The AI orchestrator will:
1. Classify the query intent (invoice, payment, commission, or general)
2. Extract relevant entities (amounts, names, projects)
3. Route to the appropriate specialized agent
4. Return detailed financial analysis

Examples:
- "What's the payment schedule for a AED 5M villa at DAMAC Hills on 60/40 plan?"
- "Process invoice from ALEC for AED 8.5M for MEP works at Safa One"
- "Calculate commission for AED 10M sale with Betterhomes (BRN-1234)"

Supports UAE financial rules: 5% VAT, 4% DLD fee, RERA regulations.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language finance query"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_damac_data",
            description="""List available DAMAC projects, contractors, brokers, and payment plans.

Use this to explore:
- Available DAMAC projects and their price ranges
- Registered contractors and vendors
- RERA-registered brokers
- Payment plan structures""",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["projects", "contractors", "brokers", "payment_plans", "all"],
                        "description": "Category of data to list",
                        "default": "all"
                    }
                },
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from Claude."""

    try:
        if name == "process_invoice":
            return await handle_process_invoice(arguments)
        elif name == "calculate_payment_plan":
            return await handle_payment_plan(arguments)
        elif name == "calculate_commission":
            return await handle_commission(arguments)
        elif name == "query_finance":
            return await handle_query(arguments)
        elif name == "list_damac_data":
            return await handle_list_data(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_process_invoice(args: dict) -> list[TextContent]:
    """Process an invoice using the Invoice Agent."""
    vendor = args.get("vendor_name", "")
    amount = args.get("amount", 0)
    project = args.get("project_name", "")
    description = args.get("description", "")
    po_number = args.get("po_number", "")

    query = f"""Process invoice:
- Vendor: {vendor}
- Amount: AED {amount:,.2f}
- Project: {project}
- Description: {description or 'Not specified'}
- PO Number: {po_number or 'Not specified'}"""

    entities = {
        "vendor_name": vendor,
        "amount": amount,
        "project_name": project,
    }

    result = await get_invoice_agent().process(query, entities)

    # Format response
    response = f"""## Invoice Processing Result

**Vendor:** {vendor}
**Project:** {project}
**Description:** {description or 'N/A'}

### Financial Breakdown
| Item | Amount (AED) |
|------|-------------|
| Subtotal | {amount:,.2f} |
| VAT (5%) | {amount * 0.05:,.2f} |
| Retention (5%) | -{amount * 0.05:,.2f} |
| **Net Payable** | **{amount:,.2f}** |

### Processing Details
{json.dumps(result, indent=2, default=str)}
"""

    return [TextContent(type="text", text=response)]


async def handle_payment_plan(args: dict) -> list[TextContent]:
    """Calculate payment plan using the Payment Agent."""
    value = args.get("property_value", 0)
    project = args.get("project_name", "")
    plan_type = args.get("plan_type", "60/40")

    query = f"Calculate payment schedule for AED {value:,.0f} property at {project} on {plan_type} plan"

    entities = {
        "property_value": value,
        "project_name": project,
        "plan_type": plan_type,
    }

    result = await get_payment_agent().process(query, entities)

    # Get plan details
    plan = PAYMENT_PLANS.get(plan_type, PAYMENT_PLANS["60/40"])
    dld_fee = value * UAE_RATES["dld_fee"]

    response = f"""## Payment Plan: {plan_type}

**Property:** {project}
**Value:** AED {value:,.2f}

### Additional Fees
| Fee | Amount (AED) |
|-----|-------------|
| DLD Fee (4%) | {dld_fee:,.2f} |
| Admin Fee | {UAE_RATES['admin_fee']:,.2f} |
| **Total Purchase Cost** | **{value + dld_fee + UAE_RATES['admin_fee']:,.2f}** |

### Payment Structure
- **During Construction:** {plan['during_construction']*100:.0f}% = AED {value * plan['during_construction']:,.2f}
- **At Handover:** {plan['on_handover']*100:.0f}% = AED {value * plan['on_handover']:,.2f}

### Detailed Schedule
{json.dumps(result, indent=2, default=str)}
"""

    return [TextContent(type="text", text=response)]


async def handle_commission(args: dict) -> list[TextContent]:
    """Calculate commission using the Commission Agent."""
    sale_price = args.get("sale_price", 0)
    broker = args.get("broker_name", "")
    brn = args.get("broker_brn", "")
    project = args.get("project_name", "")
    rate = args.get("commission_rate", 5.0)

    query = f"Calculate commission for AED {sale_price:,.0f} sale at {project} with {broker} (BRN: {brn}) at {rate}% rate"

    entities = {
        "sale_price": sale_price,
        "broker_name": broker,
        "broker_brn": brn,
        "project_name": project,
        "commission_rate": rate,
    }

    result = await get_commission_agent().process(query, entities)

    # Calculate values
    gross_commission = sale_price * (rate / 100)
    vat = gross_commission * UAE_RATES["vat"]
    total = gross_commission + vat
    broker_share = total * 0.6
    internal_share = total * 0.4

    response = f"""## Commission Calculation

**Sale Price:** AED {sale_price:,.2f}
**Project:** {project or 'N/A'}
**Broker:** {broker}
**BRN:** {brn}

### Commission Breakdown
| Item | Amount (AED) |
|------|-------------|
| Gross Commission ({rate}%) | {gross_commission:,.2f} |
| VAT (5%) | {vat:,.2f} |
| **Total Commission** | **{total:,.2f}** |

### Split
| Recipient | Share | Amount (AED) |
|-----------|-------|-------------|
| {broker} | 60% | {broker_share:,.2f} |
| Internal Sales | 40% | {internal_share:,.2f} |

### RERA Validation
BRN {brn}: {"✓ Valid format" if brn.startswith("BRN-") else "⚠ Invalid format"}

### Agent Analysis
{json.dumps(result, indent=2, default=str)}
"""

    return [TextContent(type="text", text=response)]


async def handle_query(args: dict) -> list[TextContent]:
    """Process natural language query through orchestrator."""
    query = args.get("query", "")

    # Classify intent
    orchestrator = get_orchestrator()
    classification = await orchestrator.classify(query)

    intent = classification.get("intent", "general")
    confidence = classification.get("confidence", 0.0)
    entities = classification.get("entities", {})

    # Route to appropriate agent
    if intent == "invoice":
        result = await get_invoice_agent().process(query, entities)
    elif intent == "payment":
        result = await get_payment_agent().process(query, entities)
    elif intent == "commission":
        result = await get_commission_agent().process(query, entities)
    else:
        result = {
            "message": "General finance query",
            "suggestion": "Try asking about invoices, payment plans, or commissions.",
            "examples": [
                "Process invoice from [vendor] for AED [amount]",
                "What's the payment plan for AED [amount] property?",
                "Calculate commission for AED [amount] sale"
            ]
        }

    response = f"""## Query Analysis

**Query:** {query}
**Intent:** {intent.upper()}
**Confidence:** {confidence:.0%}

### Extracted Entities
{json.dumps(entities, indent=2, default=str)}

### Result
{json.dumps(result, indent=2, default=str)}
"""

    return [TextContent(type="text", text=response)]


async def handle_list_data(args: dict) -> list[TextContent]:
    """List available DAMAC reference data."""
    category = args.get("category", "all")

    sections = []

    if category in ["projects", "all"]:
        projects_list = "\n".join([
            f"- **{name}**: {data['type']}, {data['bedrooms']}, AED {data['price_range'][0]:,.0f} - {data['price_range'][1]:,.0f}"
            for name, data in DAMAC_PROJECTS.items()
        ])
        sections.append(f"## DAMAC Projects\n{projects_list}")

    if category in ["contractors", "all"]:
        contractors_list = "\n".join([
            f"- **{name}**: {data['type']} - {data['specialty']}"
            for name, data in CONTRACTORS.items()
        ])
        sections.append(f"## Contractors & Vendors\n{contractors_list}")

    if category in ["brokers", "all"]:
        brokers_list = "\n".join([
            f"- **{name}** ({data['brn']}): {data['type']}, {data['commission_rate']}% commission"
            for name, data in BROKERS.items()
        ])
        sections.append(f"## RERA Brokers\n{brokers_list}")

    if category in ["payment_plans", "all"]:
        plans_list = "\n".join([
            f"- **{key}**: {data['description']}"
            for key, data in PAYMENT_PLANS.items()
        ])
        sections.append(f"## Payment Plans\n{plans_list}")

    return [TextContent(type="text", text="\n\n".join(sections))]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
