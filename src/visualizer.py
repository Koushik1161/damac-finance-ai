"""
DAMAC Finance AI - Terminal Visualizer
Claude Code inspired aesthetic with gradients and modern block art
"""
import time
import sys
from typing import Optional, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.box import ROUNDED, DOUBLE, HEAVY, SIMPLE, MINIMAL
from rich.style import Style
from rich.padding import Padding
from rich.rule import Rule


# ═══════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE - Inspired by modern CLI tools
# ═══════════════════════════════════════════════════════════════════════════════

GRADIENT = {
    "cyan": "#00D9FF",
    "teal": "#00C9B7",
    "mint": "#00E5A0",
    "coral": "#FF6B6B",
    "orange": "#FF9F43",
    "purple": "#A55EEA",
    "pink": "#FF6B9D",
    "gold": "#FFD93D",
}

COLORS = {
    "primary": "#00D9FF",       # Bright cyan
    "secondary": "#FF6B6B",     # Coral
    "accent": "#00E5A0",        # Mint green
    "success": "#00E676",       # Green
    "warning": "#FFD93D",       # Gold
    "error": "#FF5252",         # Red
    "muted": "#6B7280",         # Gray
    "dim": "#4B5563",           # Dark gray
    "text": "#E5E7EB",          # Light gray
    "white": "#FFFFFF",
}

AGENT_THEME = {
    "invoice": {"primary": "#FF9F43", "secondary": "#FFD93D", "icon": "📄"},
    "payment": {"primary": "#A55EEA", "secondary": "#FF6B9D", "icon": "💳"},
    "commission": {"primary": "#00C9B7", "secondary": "#00E5A0", "icon": "💰"},
    "orchestrator": {"primary": "#00D9FF", "secondary": "#00C9B7", "icon": "🧠"},
    "general": {"primary": "#6B7280", "secondary": "#9CA3AF", "icon": "💬"},
}


# ═══════════════════════════════════════════════════════════════════════════════
# ASCII ART - Hand-crafted DAMAC logo with block characters
# ═══════════════════════════════════════════════════════════════════════════════

DAMAC_LOGO = """
██████╗   █████╗  ███╗   ███╗  █████╗   ██████╗
██╔══██╗ ██╔══██╗ ████╗ ████║ ██╔══██╗ ██╔════╝
██║  ██║ ███████║ ██╔████╔██║ ███████║ ██║
██║  ██║ ██╔══██║ ██║╚██╔╝██║ ██╔══██║ ██║
██████╔╝ ██║  ██║ ██║ ╚═╝ ██║ ██║  ██║ ╚██████╗
╚═════╝  ╚═╝  ╚═╝ ╚═╝     ╚═╝ ╚═╝  ╚═╝  ╚═════╝
"""

DAMAC_LOGO_SMALL = """
▄▀▀▄ ▄▀▀▄ █▀▄▀█ ▄▀▀▄ ▄▀▀▀
█  █ █▀▀█ █ █ █ █▀▀█ █
▀▀▀  ▀  ▀ ▀   ▀ ▀  ▀  ▀▀▀
"""

FINANCE_AI_TEXT = "F I N A N C E   A I"


def gradient_text(text: str, colors: list[str]) -> Text:
    """Apply gradient colors across text."""
    result = Text()
    if not text or not colors:
        return Text(text)

    lines = text.split('\n')
    num_colors = len(colors)

    for i, line in enumerate(lines):
        color_idx = int((i / max(len(lines) - 1, 1)) * (num_colors - 1))
        color = colors[min(color_idx, num_colors - 1)]
        result.append(line + '\n', style=f"bold {color}")

    return result


def horizontal_gradient_text(text: str, colors: list[str]) -> Text:
    """Apply horizontal gradient across text."""
    result = Text()
    if not text or not colors:
        return Text(text)

    text_len = len(text.replace('\n', ''))
    char_count = 0
    num_colors = len(colors)

    for char in text:
        if char == '\n':
            result.append('\n')
        else:
            color_idx = int((char_count / max(text_len - 1, 1)) * (num_colors - 1))
            color = colors[min(color_idx, num_colors - 1)]
            result.append(char, style=f"bold {color}")
            char_count += 1

    return result


class DAMACVisualizer:
    """Modern terminal visualizer with Claude Code-inspired aesthetics."""

    def __init__(self):
        self.console = Console()
        self.width = min(self.console.width, 90)

    def clear(self):
        """Clear terminal screen."""
        self.console.clear()

    def print_banner(self):
        """Print stunning DAMAC Finance AI banner with gradient."""
        self.console.print()

        # Gradient logo
        logo_colors = [GRADIENT["cyan"], GRADIENT["teal"], GRADIENT["mint"]]
        logo_text = gradient_text(DAMAC_LOGO.strip(), logo_colors)

        # Subtitle with different gradient
        subtitle = Text()
        subtitle.append("\n")
        for i, char in enumerate(FINANCE_AI_TEXT):
            # Gradient from coral to orange
            ratio = i / len(FINANCE_AI_TEXT)
            if ratio < 0.5:
                color = GRADIENT["coral"]
            else:
                color = GRADIENT["orange"]
            subtitle.append(char, style=f"bold {color}")

        subtitle.append("\n\n", style="default")
        subtitle.append("Powered by ", style=COLORS["dim"])
        subtitle.append("GPT-5", style=f"bold {COLORS['primary']}")
        subtitle.append(" Multi-Agent System", style=COLORS["dim"])

        # Combined content
        content = Text()
        content.append_text(logo_text)
        content.append_text(subtitle)

        self.console.print(Align.center(content))
        self.console.print()

    def print_mini_banner(self):
        """Print compact banner."""
        logo_colors = [GRADIENT["cyan"], GRADIENT["teal"]]
        logo_text = gradient_text(DAMAC_LOGO_SMALL.strip(), logo_colors)

        self.console.print()
        self.console.print(Align.center(logo_text))
        self.console.print(Align.center(
            Text(FINANCE_AI_TEXT, style=f"bold {GRADIENT['coral']}")
        ))
        self.console.print()

    def print_tagline(self):
        """Print feature tagline."""
        features = [
            ("UAE Tax Rules", GRADIENT["orange"]),
            ("Payment Plans", GRADIENT["purple"]),
            ("Broker Commissions", GRADIENT["mint"]),
        ]

        tagline = Text()
        for i, (feature, color) in enumerate(features):
            if i > 0:
                tagline.append("  •  ", style=COLORS["dim"])
            tagline.append(feature, style=f"{color}")

        self.console.print(Align.center(tagline))
        self.console.print()

    def print_separator(self, char: str = "─", style: str = None):
        """Print elegant separator line."""
        style = style or COLORS["dim"]
        self.console.print()
        self.console.print(Rule(style=style))
        self.console.print()

    def print_query_box(self, query: str):
        """Display user query in elegant box."""
        self.console.print()

        # Query panel with gradient border effect
        query_text = Text()
        query_text.append('"', style=COLORS["dim"])
        query_text.append(query, style=f"italic {COLORS['text']}")
        query_text.append('"', style=COLORS["dim"])

        self.console.print(Panel(
            Align.center(query_text),
            title=f"[{COLORS['primary']}]⌘ QUERY[/]",
            title_align="left",
            border_style=COLORS["primary"],
            box=ROUNDED,
            padding=(1, 3),
        ))
        self._print_flow_arrow()

    def _print_flow_arrow(self, color: str = None):
        """Print connecting flow arrow."""
        color = color or COLORS["dim"]
        arrow = Text()
        arrow.append("        │\n", style=color)
        arrow.append("        ▼", style=color)
        self.console.print(Align.center(arrow))

    def print_orchestrator_processing(self):
        """Show orchestrator processing indicator."""
        from rich.live import Live
        from rich.spinner import Spinner

        spinner_text = Text()
        spinner_text.append("  ORCHESTRATOR  ", style=f"bold {AGENT_THEME['orchestrator']['primary']}")
        spinner_text.append("analyzing query...", style=COLORS["muted"])

        return Live(
            Panel(
                Align.center(spinner_text),
                border_style=AGENT_THEME['orchestrator']['primary'],
                box=ROUNDED,
                padding=(0, 2),
            ),
            console=self.console,
            refresh_per_second=10,
            transient=True,
        )

    def print_orchestrator_result(self, intent: str, confidence: float, entities: dict):
        """Display orchestrator classification with style."""
        theme = AGENT_THEME.get(intent, AGENT_THEME["general"])

        # Header
        header = Text()
        header.append(f"{theme['icon']} ", style="default")
        header.append("ORCHESTRATOR", style=f"bold {theme['primary']}")
        header.append("  ›  ", style=COLORS["dim"])
        header.append(intent.upper(), style=f"bold {theme['secondary']}")
        header.append(f"  ({confidence:.0%})", style=COLORS["muted"])

        # Entities
        entity_lines = []
        for key, value in entities.items():
            if value and key not in ['intent', 'confidence']:
                if isinstance(value, dict):
                    value = value.get('value', str(value))
                display_key = key.replace('_', ' ').title()
                entity_lines.append(f"  [dim]›[/dim] {display_key}: [{theme['primary']}]{value}[/]")

        entities_text = "\n".join(entity_lines[:5]) if entity_lines else f"  [{COLORS['dim']}]No entities extracted[/]"

        content = f"{header}\n\n[{COLORS['muted']}]Extracted:[/]\n{entities_text}"

        self.console.print(Panel(
            content,
            border_style=theme['primary'],
            box=ROUNDED,
            padding=(1, 2),
        ))
        self._print_flow_arrow(theme['primary'])

    def print_agent_processing(self, agent_name: str):
        """Show agent processing indicator."""
        from rich.live import Live

        theme = AGENT_THEME.get(agent_name, AGENT_THEME["general"])

        text = Text()
        text.append(f"  {theme['icon']} {agent_name.upper()} AGENT  ", style=f"bold {theme['primary']}")
        text.append("processing...", style=COLORS["muted"])

        return Live(
            Panel(
                Align.center(text),
                border_style=theme['primary'],
                box=ROUNDED,
                padding=(0, 2),
            ),
            console=self.console,
            refresh_per_second=10,
            transient=True,
        )

    def print_invoice_results(self, result: dict):
        """Display invoice results with modern styling."""
        theme = AGENT_THEME["invoice"]
        calculations = result.get('calculations', {})
        approval = result.get('approval', {})
        validation = result.get('validation', {})

        # Calculations table
        calc_table = Table(
            show_header=False,
            box=None,
            padding=(0, 2),
            collapse_padding=True,
        )
        calc_table.add_column("Label", style=COLORS["text"])
        calc_table.add_column("Value", justify="right", style=f"bold {theme['primary']}")

        calc_table.add_row("Subtotal", f"AED {calculations.get('subtotal', 0):,.2f}")
        calc_table.add_row(f"VAT ({calculations.get('vat_rate', 5)}%)", f"AED {calculations.get('vat_amount', 0):,.2f}")
        calc_table.add_row(f"Retention ({calculations.get('retention_rate', 5)}%)", f"- AED {calculations.get('retention_amount', 0):,.2f}")
        calc_table.add_row("─" * 20, "─" * 18)
        calc_table.add_row(
            Text("Net Payable", style="bold white"),
            Text(f"AED {calculations.get('net_payable', 0):,.2f}", style=f"bold {theme['secondary']}")
        )

        # Approval status
        approval_level = approval.get('level', 'unknown').replace('_', ' ').upper()
        is_valid = validation.get('is_valid', True)
        status_icon = "✓" if is_valid else "✗"
        status_color = COLORS["success"] if is_valid else COLORS["error"]

        approval_text = Text()
        approval_text.append("\n")
        approval_text.append("Approval: ", style=COLORS["muted"])
        approval_text.append(f"{approval_level}\n", style=f"bold {GRADIENT['gold']}")
        approval_text.append("Status: ", style=COLORS["muted"])
        approval_text.append(f"{status_icon} ", style=status_color)
        approval_text.append("Valid" if is_valid else "Issues Found", style=status_color)

        self.console.print(Panel(
            Columns([calc_table, approval_text], expand=True),
            title=f"[{theme['primary']}]{theme['icon']} INVOICE RESULT[/]",
            title_align="left",
            border_style=theme['primary'],
            box=ROUNDED,
            padding=(1, 2),
        ))

    def print_payment_results(self, result: dict):
        """Display payment results with modern styling."""
        theme = AGENT_THEME["payment"]
        payment_status = result.get('payment_status', {})
        milestones = result.get('milestones', [])
        fees = result.get('fees', {})

        # Plan info
        plan_info = Text()
        plan_info.append("Plan: ", style=COLORS["muted"])
        plan_info.append(f"{payment_status.get('plan_type', 'N/A')}\n", style=f"bold {theme['primary']}")
        plan_info.append("Value: ", style=COLORS["muted"])
        plan_info.append(f"AED {payment_status.get('property_value', 0):,.2f}\n", style=f"bold {theme['secondary']}")
        plan_info.append("Split: ", style=COLORS["muted"])
        plan_info.append(f"{payment_status.get('construction_share', 0):.0f}% / {payment_status.get('handover_share', 0):.0f}%", style=COLORS["text"])

        # Fees
        fees_text = Text()
        fees_text.append("\n")
        fees_text.append("DLD Fee: ", style=COLORS["muted"])
        fees_text.append(f"AED {fees.get('dld_fee', 0):,.2f}\n", style=theme['primary'])
        fees_text.append("Admin: ", style=COLORS["muted"])
        fees_text.append(f"AED {fees.get('admin_fee', 4200):,.2f}", style=theme['primary'])

        self.console.print(Panel(
            Columns([plan_info, fees_text], expand=True),
            title=f"[{theme['primary']}]{theme['icon']} PAYMENT PLAN[/]",
            title_align="left",
            border_style=theme['primary'],
            box=ROUNDED,
            padding=(1, 2),
        ))

        # Milestones table if available
        if milestones:
            mile_table = Table(
                show_header=True,
                header_style=f"bold {theme['primary']}",
                box=SIMPLE,
                padding=(0, 1),
            )
            mile_table.add_column("Milestone", style=COLORS["text"])
            mile_table.add_column("%", justify="center", style=COLORS["muted"])
            mile_table.add_column("Amount", justify="right", style=theme['primary'])
            mile_table.add_column("Status", justify="center")

            for m in milestones[:5]:
                status = m.get('status', 'pending')
                if status == 'paid':
                    status_display = Text("PAID", style=COLORS["success"])
                elif status == 'due':
                    status_display = Text("DUE", style=COLORS["error"])
                else:
                    status_display = Text("PENDING", style=COLORS["warning"])

                mile_table.add_row(
                    m.get('name', 'N/A')[:30],
                    f"{m.get('percentage', 0)}%",
                    f"AED {m.get('amount', 0):,.0f}",
                    status_display
                )

            self.console.print(Panel(
                mile_table,
                border_style=theme['primary'],
                box=ROUNDED,
                padding=(1, 1),
            ))

    def print_commission_results(self, result: dict):
        """Display commission results with modern styling."""
        theme = AGENT_THEME["commission"]
        calculation = result.get('calculation', {})
        split = result.get('split', {})
        broker_validation = result.get('broker_validation', {})

        # Main calculation
        calc_text = Text()
        calc_text.append("Sale Price: ", style=COLORS["muted"])
        calc_text.append(f"AED {calculation.get('sale_price', 0):,.2f}\n", style=COLORS["text"])
        calc_text.append(f"Commission ({calculation.get('commission_rate', 5)}%): ", style=COLORS["muted"])
        calc_text.append(f"AED {calculation.get('gross_commission', 0):,.2f}\n", style=f"bold {theme['primary']}")
        calc_text.append(f"+ VAT ({calculation.get('vat_rate', 5)}%): ", style=COLORS["muted"])
        calc_text.append(f"AED {calculation.get('vat_amount', 0):,.2f}\n", style=theme['primary'])
        calc_text.append("─" * 28 + "\n", style=COLORS["dim"])
        calc_text.append("Total: ", style="bold white")
        calc_text.append(f"AED {calculation.get('total_with_vat', 0):,.2f}", style=f"bold {theme['secondary']}")

        self.console.print(Panel(
            calc_text,
            title=f"[{theme['primary']}]{theme['icon']} COMMISSION[/]",
            title_align="left",
            border_style=theme['primary'],
            box=ROUNDED,
            padding=(1, 2),
        ))

        # Split table
        ext_broker = split.get('external_broker', {})
        int_sales = split.get('internal_sales', {})

        split_table = Table(
            show_header=True,
            header_style=f"bold {theme['primary']}",
            box=SIMPLE,
            padding=(0, 1),
        )
        split_table.add_column("Recipient", style=COLORS["text"])
        split_table.add_column("Share", justify="center", style=COLORS["muted"])
        split_table.add_column("Total", justify="right", style=f"bold {theme['primary']}")

        broker_name = ext_broker.get('name', 'External Broker')[:20]
        split_table.add_row(
            broker_name,
            f"{ext_broker.get('percentage', 60)}%",
            f"AED {ext_broker.get('total', 0):,.2f}"
        )
        split_table.add_row(
            "Internal Sales",
            f"{int_sales.get('percentage', 40)}%",
            f"AED {int_sales.get('total', 0):,.2f}"
        )

        # Broker validation
        brn = broker_validation.get('brn', 'N/A')
        brn_status = broker_validation.get('status', 'unknown')
        if brn_status == 'valid':
            status_icon, status_color = "✓", COLORS["success"]
        elif brn_status == 'needs_verification':
            status_icon, status_color = "?", COLORS["warning"]
        else:
            status_icon, status_color = "✗", COLORS["error"]

        brn_text = Text()
        brn_text.append(f"\nBRN: ", style=COLORS["muted"])
        brn_text.append(f"{brn} ", style=COLORS["text"])
        brn_text.append(f"{status_icon}", style=status_color)

        self.console.print(Panel(
            Columns([split_table, brn_text], expand=True),
            title=f"[{theme['primary']}]SPLIT & VALIDATION[/]",
            title_align="left",
            border_style=theme['primary'],
            box=ROUNDED,
            padding=(1, 2),
        ))

    def print_general_result(self, result: dict):
        """Display general query results."""
        theme = AGENT_THEME["general"]
        message = result.get('message', 'Query processed')
        examples = result.get('examples', [])

        content = Text()
        content.append(f"{message}\n\n", style=COLORS["text"])

        if examples:
            content.append("Try:\n", style=COLORS["muted"])
            for ex in examples:
                content.append(f"  › {ex}\n", style=COLORS["dim"])

        self.console.print(Panel(
            content,
            title=f"[{theme['primary']}]{theme['icon']} RESPONSE[/]",
            title_align="left",
            border_style=theme['primary'],
            box=ROUNDED,
            padding=(1, 2),
        ))

    def print_results(self, intent: str, result: dict):
        """Route to appropriate result display."""
        self._print_flow_arrow(AGENT_THEME.get(intent, AGENT_THEME["general"])['primary'])

        if intent == "invoice":
            self.print_invoice_results(result)
        elif intent == "payment":
            self.print_payment_results(result)
        elif intent == "commission":
            self.print_commission_results(result)
        else:
            self.print_general_result(result)

    def print_processing_time(self, time_ms: int, model: str):
        """Display processing time footer."""
        self.console.print()
        footer = Text()
        footer.append("Processed in ", style=COLORS["dim"])
        footer.append(f"{time_ms:,}ms", style=COLORS["muted"])
        footer.append(" using ", style=COLORS["dim"])
        footer.append(model, style=COLORS["primary"])
        self.console.print(Align.center(footer))
        self.console.print()

    def print_error(self, error: str):
        """Display error message."""
        self.console.print(Panel(
            Text(error, style=COLORS["error"]),
            title=f"[{COLORS['error']}]✗ ERROR[/]",
            title_align="left",
            border_style=COLORS["error"],
            box=ROUNDED,
            padding=(1, 2),
        ))

    def print_success(self, message: str):
        """Display success message."""
        self.console.print(Panel(
            Text(message, style=COLORS["success"]),
            title=f"[{COLORS['success']}]✓ SUCCESS[/]",
            title_align="left",
            border_style=COLORS["success"],
            box=ROUNDED,
            padding=(1, 2),
        ))
