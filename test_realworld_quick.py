#!/usr/bin/env python3
"""
DAMAC Finance AI - Quick Real-World Test (3 queries)
For faster testing - one query per type
"""
import asyncio
import time
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED

from src.visualizer import COLORS, AGENT_THEME, DAMACVisualizer
from src.llm import (
    OrchestratorLLMAgent,
    InvoiceLLMAgent,
    PaymentLLMAgent,
    CommissionLLMAgent,
)

console = Console()
viz = DAMACVisualizer()

# Initialize agents
orchestrator = OrchestratorLLMAgent()
invoice_agent = InvoiceLLMAgent()
payment_agent = PaymentLLMAgent()
commission_agent = CommissionLLMAgent()

# Quick test - one query per type
QUICK_TEST_QUERIES = [
    {
        "type": "invoice",
        "query": "Process invoice from MBM Gulf Electromechanical LLC for AED 2,450,000 for MEP installation at DAMAC Lagoons Nice Phase 3",
    },
    {
        "type": "payment",
        "query": "What's the payment schedule for a AED 4.99M canal villa at DAMAC Lagoons Venice on 60/40 plan?",
    },
    {
        "type": "commission",
        "query": "Calculate commission for AED 8.5M Morocco villa at DAMAC Lagoons with Gulf Sotheby's (BRN-3456) at 6% rate",
    },
]


async def run_quick_test():
    """Run quick 3-query test."""
    viz.print_banner()
    console.print()
    console.print(Panel(
        Text("QUICK REAL-WORLD TEST (3 queries)", style=f"bold {COLORS['primary']}", justify="center"),
        subtitle="Testing with actual DAMAC data",
        border_style=COLORS["primary"],
        box=ROUNDED,
    ))
    console.print()

    results = []
    total_time = 0

    for i, test in enumerate(QUICK_TEST_QUERIES, 1):
        query = test["query"]
        expected = test["type"]

        theme = AGENT_THEME.get(expected, AGENT_THEME["general"])
        console.print(f"[{COLORS['dim']}]Test {i}/3:[/] [{theme['primary']}]{expected.upper()}[/]")
        console.print(f"[{COLORS['muted']}]Query: {query[:70]}...[/]")

        start = time.time()

        try:
            # Classify
            console.print(f"  [dim]→ Classifying...[/]", end="")
            classification = await orchestrator.classify(query)
            intent = classification.get("intent", "general")
            confidence = classification.get("confidence", 0.0)
            entities = classification.get("entities", {})
            console.print(f" [green]✓[/] {intent} ({confidence:.0%})")

            # Process
            console.print(f"  [dim]→ Processing with {intent} agent...[/]", end="")
            if intent == "invoice":
                result = await invoice_agent.process(query, entities)
            elif intent == "payment":
                result = await payment_agent.process(query, entities)
            elif intent == "commission":
                result = await commission_agent.process(query, entities)
            else:
                result = {"error": "Unknown intent"}

            elapsed = int((time.time() - start) * 1000)
            total_time += elapsed
            console.print(f" [green]✓[/] {elapsed}ms")

            correct = intent == expected
            status = "✓ PASS" if correct else "✗ FAIL"
            status_style = COLORS["success"] if correct else COLORS["error"]

            results.append({
                "expected": expected,
                "detected": intent,
                "confidence": confidence,
                "correct": correct,
                "time_ms": elapsed,
            })

            console.print(f"  [{status_style}]{status}[/]")
            console.print()

        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            total_time += elapsed
            console.print(f" [red]✗ ERROR: {e}[/]")
            results.append({
                "expected": expected,
                "detected": "error",
                "confidence": 0,
                "correct": False,
                "time_ms": elapsed,
            })
            console.print()

    # Summary
    correct_count = sum(1 for r in results if r["correct"])
    accuracy = correct_count / len(results)
    avg_time = total_time / len(results)
    avg_confidence = sum(r["confidence"] for r in results) / len(results)

    console.print(Panel(
        f"[bold]Accuracy:[/] {accuracy:.0%} ({correct_count}/3)\n"
        f"[bold]Avg Time:[/] {avg_time:.0f}ms\n"
        f"[bold]Avg Confidence:[/] {avg_confidence:.0%}",
        title=f"[{COLORS['primary']}]RESULTS[/]",
        border_style=COLORS["success"] if accuracy == 1.0 else COLORS["warning"],
        box=ROUNDED,
    ))

    return results


if __name__ == "__main__":
    asyncio.run(run_quick_test())
