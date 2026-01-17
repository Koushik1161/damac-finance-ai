#!/usr/bin/env python3
"""
DAMAC Finance AI - Real-World Data Test Suite
Tests using actual DAMAC Properties data from 2025
"""
import asyncio
import time
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.box import ROUNDED

from src.visualizer import COLORS, AGENT_THEME, DAMACVisualizer
from src.llm import (
    OrchestratorLLMAgent,
    InvoiceLLMAgent,
    PaymentLLMAgent,
    CommissionLLMAgent,
)
from src.data.realworld_damac_data import (
    REALWORLD_INVOICE_QUERIES,
    REALWORLD_PAYMENT_QUERIES,
    REALWORLD_COMMISSION_QUERIES,
    DAMAC_PROJECTS,
    CONTRACTORS,
    BROKERS,
    UAE_RATES,
)

console = Console()
viz = DAMACVisualizer()

# Initialize agents
orchestrator = OrchestratorLLMAgent()
invoice_agent = InvoiceLLMAgent()
payment_agent = PaymentLLMAgent()
commission_agent = CommissionLLMAgent()


async def test_single_query(query_data: dict, query_type: str) -> dict:
    """Test a single query and return results."""
    query = query_data["query"]
    start_time = time.time()

    try:
        # Step 1: Classify
        classification = await orchestrator.classify(query)
        intent = classification.get("intent", "general")
        confidence = classification.get("confidence", 0.0)
        entities = classification.get("entities", {})

        # Step 2: Route to agent
        if intent == "invoice":
            result = await invoice_agent.process(query, entities)
        elif intent == "payment":
            result = await payment_agent.process(query, entities)
        elif intent == "commission":
            result = await commission_agent.process(query, entities)
        else:
            result = {"error": "Unclassified query"}

        processing_time = int((time.time() - start_time) * 1000)

        # Validate results
        correct_intent = intent == query_type

        return {
            "query": query[:60] + "..." if len(query) > 60 else query,
            "expected_type": query_type,
            "detected_intent": intent,
            "confidence": confidence,
            "correct_intent": correct_intent,
            "processing_time_ms": processing_time,
            "result": result,
            "status": "success" if correct_intent else "mismatch",
        }

    except Exception as e:
        return {
            "query": query[:60] + "...",
            "expected_type": query_type,
            "detected_intent": "error",
            "confidence": 0.0,
            "correct_intent": False,
            "processing_time_ms": int((time.time() - start_time) * 1000),
            "result": {"error": str(e)},
            "status": "error",
        }


async def run_test_suite():
    """Run the complete real-world test suite."""
    viz.print_banner()
    console.print()
    console.print(Panel(
        Text("REAL-WORLD DATA TEST SUITE", style=f"bold {COLORS['primary']}", justify="center"),
        subtitle="Based on actual DAMAC Properties 2025 data",
        border_style=COLORS["primary"],
        box=ROUNDED,
    ))
    console.print()

    # Show data summary
    data_table = Table(title="Test Data Summary", box=ROUNDED, border_style=COLORS["dim"])
    data_table.add_column("Category", style=COLORS["text"])
    data_table.add_column("Count", style=COLORS["primary"], justify="right")
    data_table.add_column("Source", style=COLORS["muted"])

    data_table.add_row("DAMAC Projects", str(len(DAMAC_PROJECTS)), "damacproperties.com")
    data_table.add_row("Contractors/Vendors", str(len(CONTRACTORS)), "Dubai construction firms")
    data_table.add_row("RERA Brokers", str(len(BROKERS)), "propertyfinder.ae")
    data_table.add_row("Invoice Queries", str(len(REALWORLD_INVOICE_QUERIES)), "Real scenarios")
    data_table.add_row("Payment Queries", str(len(REALWORLD_PAYMENT_QUERIES)), "Real scenarios")
    data_table.add_row("Commission Queries", str(len(REALWORLD_COMMISSION_QUERIES)), "Real scenarios")

    console.print(data_table)
    console.print()

    results = []
    total_queries = (
        len(REALWORLD_INVOICE_QUERIES) +
        len(REALWORLD_PAYMENT_QUERIES) +
        len(REALWORLD_COMMISSION_QUERIES)
    )

    # Run tests with progress bar
    with Progress(
        SpinnerColumn(spinner_name="dots", style=COLORS["primary"]),
        TextColumn("[bold]{task.description}[/]"),
        BarColumn(complete_style=COLORS["success"], finished_style=COLORS["success"]),
        TextColumn("[{task.completed}/{task.total}]"),
        console=console,
    ) as progress:
        task = progress.add_task("Running tests...", total=total_queries)

        # Test Invoice Queries
        for query_data in REALWORLD_INVOICE_QUERIES:
            result = await test_single_query(query_data, "invoice")
            results.append(result)
            progress.advance(task)

        # Test Payment Queries
        for query_data in REALWORLD_PAYMENT_QUERIES:
            result = await test_single_query(query_data, "payment")
            results.append(result)
            progress.advance(task)

        # Test Commission Queries
        for query_data in REALWORLD_COMMISSION_QUERIES:
            result = await test_single_query(query_data, "commission")
            results.append(result)
            progress.advance(task)

    console.print()

    # Results table
    results_table = Table(
        title="Test Results",
        box=ROUNDED,
        border_style=COLORS["primary"],
        show_lines=True,
    )
    results_table.add_column("#", style=COLORS["muted"], width=3)
    results_table.add_column("Query", style=COLORS["text"], max_width=45)
    results_table.add_column("Expected", style=COLORS["dim"], width=10)
    results_table.add_column("Detected", width=10)
    results_table.add_column("Conf.", justify="right", width=6)
    results_table.add_column("Time", justify="right", width=7)
    results_table.add_column("Status", width=8)

    for i, r in enumerate(results, 1):
        # Color based on intent type
        intent_colors = {
            "invoice": AGENT_THEME["invoice"]["primary"],
            "payment": AGENT_THEME["payment"]["primary"],
            "commission": AGENT_THEME["commission"]["primary"],
        }

        detected_color = intent_colors.get(r["detected_intent"], COLORS["error"])
        status_color = COLORS["success"] if r["correct_intent"] else COLORS["error"]
        status_icon = "✓" if r["correct_intent"] else "✗"

        results_table.add_row(
            str(i),
            r["query"],
            r["expected_type"],
            Text(r["detected_intent"], style=detected_color),
            f"{r['confidence']:.0%}",
            f"{r['processing_time_ms']}ms",
            Text(f"{status_icon} {r['status']}", style=status_color),
        )

    console.print(results_table)
    console.print()

    # Summary statistics
    correct = sum(1 for r in results if r["correct_intent"])
    total = len(results)
    accuracy = correct / total if total > 0 else 0

    avg_time = sum(r["processing_time_ms"] for r in results) / total if total > 0 else 0
    avg_confidence = sum(r["confidence"] for r in results) / total if total > 0 else 0

    # Per-category stats
    invoice_results = [r for r in results if r["expected_type"] == "invoice"]
    payment_results = [r for r in results if r["expected_type"] == "payment"]
    commission_results = [r for r in results if r["expected_type"] == "commission"]

    invoice_correct = sum(1 for r in invoice_results if r["correct_intent"])
    payment_correct = sum(1 for r in payment_results if r["correct_intent"])
    commission_correct = sum(1 for r in commission_results if r["correct_intent"])

    # Summary panel
    summary = Table.grid(padding=(0, 2))
    summary.add_column(justify="right")
    summary.add_column(justify="left")

    summary.add_row(
        Text("Overall Accuracy:", style=COLORS["text"]),
        Text(f"{accuracy:.1%} ({correct}/{total})",
             style=COLORS["success"] if accuracy >= 0.9 else COLORS["warning"])
    )
    summary.add_row(
        Text("Avg. Confidence:", style=COLORS["text"]),
        Text(f"{avg_confidence:.1%}", style=COLORS["primary"])
    )
    summary.add_row(
        Text("Avg. Response Time:", style=COLORS["text"]),
        Text(f"{avg_time:.0f}ms", style=COLORS["primary"])
    )
    summary.add_row("", "")
    summary.add_row(
        Text("Invoice Accuracy:", style=AGENT_THEME["invoice"]["primary"]),
        Text(f"{invoice_correct}/{len(invoice_results)}")
    )
    summary.add_row(
        Text("Payment Accuracy:", style=AGENT_THEME["payment"]["primary"]),
        Text(f"{payment_correct}/{len(payment_results)}")
    )
    summary.add_row(
        Text("Commission Accuracy:", style=AGENT_THEME["commission"]["primary"]),
        Text(f"{commission_correct}/{len(commission_results)}")
    )

    console.print(Panel(
        summary,
        title=f"[{COLORS['primary']}]TEST SUMMARY[/]",
        border_style=COLORS["success"] if accuracy >= 0.9 else COLORS["warning"],
        box=ROUNDED,
        padding=(1, 2),
    ))

    # Detailed results for review
    console.print()
    console.print(f"[{COLORS['dim']}]Detailed results saved to: test_results.json[/]")

    with open("test_results.json", "w") as f:
        json.dump({
            "summary": {
                "total_tests": total,
                "correct": correct,
                "accuracy": accuracy,
                "avg_confidence": avg_confidence,
                "avg_processing_time_ms": avg_time,
                "by_category": {
                    "invoice": {"total": len(invoice_results), "correct": invoice_correct},
                    "payment": {"total": len(payment_results), "correct": payment_correct},
                    "commission": {"total": len(commission_results), "correct": commission_correct},
                }
            },
            "results": results,
        }, f, indent=2, default=str)

    return accuracy


async def run_visual_demo():
    """Run visual demo with real-world queries."""
    viz.print_banner()
    viz.print_tagline()

    demos = [
        {
            "name": "INVOICE - MBM Gulf MEP Works",
            "icon": "📄",
            "color": AGENT_THEME["invoice"]["primary"],
            "query": "Process invoice from MBM Gulf Electromechanical LLC for AED 2,450,000 for MEP installation at DAMAC Lagoons Nice Phase 3",
        },
        {
            "name": "PAYMENT - Venice Canal Villa",
            "icon": "💳",
            "color": AGENT_THEME["payment"]["primary"],
            "query": "What's the payment schedule for a AED 4.99M canal villa at DAMAC Lagoons Venice on 60/40 plan?",
        },
        {
            "name": "COMMISSION - Gulf Sotheby's Luxury Sale",
            "icon": "💰",
            "color": AGENT_THEME["commission"]["primary"],
            "query": "Calculate commission for AED 8.5M Morocco villa at DAMAC Lagoons with Gulf Sotheby's (BRN-3456) at 6% rate",
        },
    ]

    from run_visual import process_query_visual

    for i, demo in enumerate(demos, 1):
        console.print()
        header = Text()
        header.append(f"  {demo['icon']} ", style="default")
        header.append(f"DEMO {i}: {demo['name']}", style=f"bold {demo['color']}")

        console.print(Panel(
            header,
            border_style=demo["color"],
            box=ROUNDED,
        ))

        await process_query_visual(demo["query"])
        viz.print_separator()

    console.print(Panel(
        Text("REAL-WORLD DEMO COMPLETE", style=f"bold {COLORS['success']}", justify="center"),
        border_style=COLORS["success"],
        box=ROUNDED,
    ))


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        asyncio.run(run_visual_demo())
    else:
        asyncio.run(run_test_suite())


if __name__ == "__main__":
    main()
