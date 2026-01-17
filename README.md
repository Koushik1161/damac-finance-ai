# DAMAC Finance AI

> Multi-Agent AI System for Real Estate Finance Operations | GPT-5 Powered | MCP Server

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-1.0-purple.svg)](https://modelcontextprotocol.io/)
[![Test Accuracy](https://img.shields.io/badge/accuracy-93.3%25-brightgreen.svg)](#test-results)

Production-grade AI system for automating finance workflows in luxury real estate development. Built for DAMAC Properties with UAE-specific business rules.

## Key Features

- **Multi-Agent Architecture**: Orchestrator + specialized agents for invoices, payments, commissions
- **93.3% Accuracy**: Tested on real-world DAMAC data (15 queries, 95-98% confidence)
- **MCP Server**: Claude Desktop integration via Model Context Protocol
- **UAE Compliance**: 5% VAT, 4% DLD fees, RERA escrow, Emirates ID handling
- **Enterprise Security**: Prompt injection defense, PII masking, audit logging

## Architecture

```
┌─────────────────────┐
│   Claude Desktop    │──────┐
│   (MCP Client)      │      │
└─────────────────────┘      │
                             │
┌─────────────────────┐      │    ┌──────────────────────────────┐
│   REST API          │──────┼───▶│      DAMAC Finance AI        │
│   (FastAPI)         │      │    │                              │
└─────────────────────┘      │    │  ┌────────────────────────┐  │
                             │    │  │     Orchestrator       │  │
┌─────────────────────┐      │    │  │   (Intent Routing)     │  │
│   Terminal CLI      │──────┘    │  └───────────┬────────────┘  │
│   (Rich UI)         │           │              │               │
└─────────────────────┘           │    ┌─────────┼─────────┐     │
                                  │    ▼         ▼         ▼     │
                                  │ ┌──────┐ ┌──────┐ ┌──────┐   │
                                  │ │Invoice│ │Payment│ │Commis│   │
                                  │ │Agent │ │Agent │ │Agent │   │
                                  │ └──────┘ └──────┘ └──────┘   │
                                  └──────────────────────────────┘
```

## Quick Start

### Option 1: MCP Server (Claude Desktop)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Claude Desktop** (`~/.config/claude/claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "damac-finance-ai": {
         "command": "python",
         "args": ["/path/to/damac-finance-ai/mcp_server.py"],
         "env": {
           "OPENAI_API_KEY": "your-api-key"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop** and ask:
   > "Calculate commission for AED 8.5M villa sale with Gulf Sotheby's at 6% rate"

### Option 2: REST API

```bash
# Setup
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Run API
uvicorn src.api.main:app --reload

# Test
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Process invoice from MBM Gulf for AED 2.45M for MEP works"}'
```

### Option 3: Terminal UI

```bash
# Interactive mode
python run_visual.py

# Run all demos
python run_visual.py --demo
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `process_invoice` | Process vendor invoices with VAT/retention calculations |
| `calculate_payment_plan` | Generate payment schedules (60/40, 80/20, 75/25) |
| `calculate_commission` | Calculate broker commissions with RERA validation |
| `query_finance` | Natural language finance queries |
| `list_damac_data` | Browse projects, contractors, brokers, plans |

## Test Results

Tested with real-world DAMAC Properties data (January 2025):

| Category | Accuracy | Confidence |
|----------|----------|------------|
| **Invoice Processing** | 5/5 (100%) | 95-98% |
| **Payment Plans** | 4/5 (80%) | 95% |
| **Commission Calc** | 5/5 (100%) | 95-98% |
| **Overall** | **14/15 (93.3%)** | **89.3%** |

### Real Data Sources
- **12 DAMAC Projects**: Lagoons, Hills, Safa One, Islands (damacproperties.com)
- **10 Contractors**: MBM Gulf, ALEC, Khansaheb, Wade Adams
- **10 RERA Brokers**: Betterhomes, Gulf Sotheby's, Allsopp & Allsopp

## Example Queries

```python
# Invoice Processing
"Process invoice from MBM Gulf Electromechanical for AED 2,450,000
 for MEP installation at DAMAC Lagoons Nice Phase 3"

# Payment Plan
"What's the payment schedule for a AED 4.99M canal villa
 at DAMAC Lagoons Venice on 60/40 plan?"

# Commission
"Calculate commission for AED 8.5M Morocco villa at DAMAC Lagoons
 with Gulf Sotheby's (BRN-3456) at 6% rate"
```

## UAE Business Rules

| Rule | Rate | Applied To |
|------|------|------------|
| VAT | 5% | Invoices, Commissions |
| DLD Fee | 4% | Property Transactions |
| Retention | 5% | Construction Invoices |
| Broker Commission | 5-6% | Off-plan Sales |
| Oqood Fee | 4% | Off-plan Registration |

## Project Structure

```
damac-finance-ai/
├── mcp_server.py           # MCP server for Claude Desktop
├── run_visual.py           # Terminal UI runner
├── src/
│   ├── llm/
│   │   ├── client.py       # GPT-5 client wrapper
│   │   └── agents.py       # LLM agent implementations
│   ├── api/
│   │   ├── main.py         # FastAPI application
│   │   └── routes.py       # API endpoints
│   ├── security/
│   │   ├── prompt_guard.py # Injection defense
│   │   └── pii_handler.py  # PII masking
│   ├── data/
│   │   └── realworld_damac_data.py  # Real DAMAC data
│   └── visualizer.py       # Rich terminal UI
├── test_realworld.py       # Real-world data tests
└── requirements.txt
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | GPT-5-mini (OpenAI) |
| Agent Framework | Custom + PydanticAI |
| API | FastAPI |
| MCP | Model Context Protocol |
| Terminal UI | Rich |
| Observability | Langfuse + Azure Monitor |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/query` | POST | Natural language query |
| `/api/v1/invoices/process` | POST | Process invoice |
| `/api/v1/payments/query` | POST | Payment plan query |
| `/api/v1/commissions/calculate` | POST | Calculate commission |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |

## Security Features

- **Prompt Injection Defense**: Blocks instruction override, role manipulation
- **PII Protection**: Masks Emirates ID, IBAN, credit cards
- **Audit Logging**: Immutable audit trail for compliance
- **Rate Limiting**: Request throttling per client

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
OPENAI_MODEL_ORCHESTRATOR=gpt-4o-mini
OPENAI_MODEL_AGENTS=gpt-4o-mini
APP_ENV=development
LOG_LEVEL=INFO
```

## Running Tests

```bash
# Quick test (3 queries)
python test_realworld_quick.py

# Full test suite (15 queries)
python test_realworld.py

# LLM agent tests
python test_llm_agents.py
```

## License

MIT

## Author

Portfolio project demonstrating multi-agent AI systems for enterprise finance operations.

---

**Built for DAMAC Group AI Manager - Agentic AI Position**
