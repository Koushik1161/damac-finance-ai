#!/usr/bin/env python3
"""
DAMAC Finance AI - Visual Workflow Runner
Claude Code-inspired terminal visualization
"""
import asyncio
import time
import sys
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.box import ROUNDED, SIMPLE
from rich.live import Live

from src.visualizer import (
    DAMACVisualizer,
    COLORS,
    GRADIENT,
    AGENT_THEME,
    gradient_text,
)
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

# Real-world DAMAC queries (based on actual 2025 data)
SAMPLE_QUERIES = {
    "1": {
        "name": "Invoice - MEP Works",
        "icon": "📄",
        "color": AGENT_THEME["invoice"]["primary"],
        "query": "Process invoice from MBM Gulf Electromechanical LLC for AED 2,450,000 for MEP installation at DAMAC Lagoons Nice Phase 3",
    },
    "2": {
        "name": "Payment - Venice Villa",
        "icon": "💳",
        "color": AGENT_THEME["payment"]["primary"],
        "query": "What's the payment schedule for a AED 4.99M canal villa at DAMAC Lagoons Venice on 60/40 plan?",
    },
    "3": {
        "name": "Commission - Sotheby's",
        "icon": "💰",
        "color": AGENT_THEME["commission"]["primary"],
        "query": "Calculate commission for AED 8.5M Morocco villa at DAMAC Lagoons with Gulf Sotheby's (BRN-3456) at 6% rate",
    },
}


async def process_query_visual(query: str):
    """Process a query with visual workflow display."""
    start_time = time.time()

    # Step 1: Show query
    viz.print_query_box(query)

    # Step 2: Orchestrator classification with animated spinner
    with Progress(
        SpinnerColumn(spinner_name="dots", style=AGENT_THEME['orchestrator']['primary']),
        TextColumn(f"[bold {AGENT_THEME['orchestrator']['primary']}]ORCHESTRATOR[/]"),
        TextColumn(f"[{COLORS['muted']}]analyzing...[/]"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("", total=None)
        classification = await orchestrator.classify(query)

    # Step 3: Show orchestrator results
    intent = classification.get("intent", "general")
    confidence = classification.get("confidence", 0.0)
    entities = classification.get("entities", {})

    viz.print_orchestrator_result(intent, confidence, entities)

    # Step 4: Route to specialized agent
    theme = AGENT_THEME.get(intent, AGENT_THEME["general"])

    with Progress(
        SpinnerColumn(spinner_name="dots", style=theme['primary']),
        TextColumn(f"[bold {theme['primary']}]{theme['icon']} {intent.upper()} AGENT[/]"),
        TextColumn(f"[{COLORS['muted']}]processing...[/]"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("", total=None)

        if intent == "invoice":
            result = await invoice_agent.process(query, entities)
        elif intent == "payment":
            result = await payment_agent.process(query, entities)
        elif intent == "commission":
            result = await commission_agent.process(query, entities)
        else:
            result = {
                "message": "I can help with invoices, payment plans, and commissions.",
                "suggestion": "Try one of the example queries.",
                "examples": [
                    "Process invoice from [vendor] for AED [amount]",
                    "What's the payment plan for AED [amount] property?",
                    "Calculate commission for AED [amount] sale",
                ]
            }

    # Step 5: Display results
    viz.print_results(intent, result)

    # Step 6: Show processing time
    processing_time = int((time.time() - start_time) * 1000)
    viz.print_processing_time(processing_time, "gpt-5-mini")

    return {"intent": intent, "result": result, "processing_time_ms": processing_time}


def show_menu():
    """Show elegant demo selection menu."""
    console.print()

    # Menu items
    menu_content = Text()

    for key, demo in SAMPLE_QUERIES.items():
        menu_content.append(f"\n  [{demo['color']}]{key}[/]  ")
        menu_content.append(f"{demo['icon']} ", style="default")
        menu_content.append(f"{demo['name']}\n", style=f"bold {demo['color']}")
        menu_content.append(f"      {demo['query'][:55]}...\n", style=COLORS["dim"])

    menu_content.append(f"\n  [{COLORS['text']}]4[/]  ")
    menu_content.append("✎ ", style="default")
    menu_content.append("Custom Query\n", style=f"bold {COLORS['text']}")

    menu_content.append(f"\n  [{COLORS['error']}]q[/]  ")
    menu_content.append("Exit\n", style=COLORS["muted"])

    console.print(Panel(
        menu_content,
        title=f"[{COLORS['primary']}]SELECT DEMO[/]",
        title_align="left",
        border_style=COLORS["primary"],
        box=ROUNDED,
        padding=(1, 2),
    ))


async def interactive_mode():
    """Run interactive query mode."""
    # Print banner
    viz.print_banner()
    viz.print_tagline()

    while True:
        show_menu()

        choice = Prompt.ask(
            f"\n  [{COLORS['primary']}]›[/] Choice",
            choices=["1", "2", "3", "4", "q"],
            default="1",
        )

        if choice == "q":
            console.print()
            console.print(Align.center(
                Text("Thank you for using DAMAC Finance AI", style=COLORS["dim"])
            ))
            console.print()
            break

        viz.print_separator()

        if choice == "4":
            query = Prompt.ask(f"\n  [{COLORS['primary']}]›[/] Enter query")
            if not query.strip():
                continue
        else:
            query = SAMPLE_QUERIES[choice]["query"]

        try:
            await process_query_visual(query)
        except Exception as e:
            viz.print_error(str(e))

        console.print()
        cont = Prompt.ask(
            f"  [{COLORS['dim']}]Press Enter to continue, 'q' to quit[/]",
            default="",
        )
        if cont.lower() == 'q':
            console.print()
            console.print(Align.center(
                Text("Thank you for using DAMAC Finance AI", style=COLORS["dim"])
            ))
            console.print()
            break


async def single_query_mode(query: str):
    """Process a single query and exit."""
    viz.print_banner()
    viz.print_tagline()
    viz.print_separator()
    await process_query_visual(query)


async def demo_all():
    """Run all demos sequentially."""
    viz.print_banner()
    viz.print_tagline()

    for key, demo in SAMPLE_QUERIES.items():
        console.print()
        demo_header = Text()
        demo_header.append(f"  {demo['icon']} ", style="default")
        demo_header.append(f"DEMO {key}: {demo['name'].upper()}", style=f"bold {demo['color']}")

        console.print(Panel(
            Align.center(demo_header),
            border_style=demo['color'],
            box=ROUNDED,
        ))

        await process_query_visual(demo["query"])
        viz.print_separator()

    # Final summary
    console.print(Panel(
        Align.center(Text("ALL DEMOS COMPLETE", style=f"bold {COLORS['success']}")),
        border_style=COLORS["success"],
        box=ROUNDED,
        padding=(1, 2),
    ))


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            asyncio.run(demo_all())
        else:
            query = " ".join(sys.argv[1:])
            asyncio.run(single_query_mode(query))
    else:
        asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()
