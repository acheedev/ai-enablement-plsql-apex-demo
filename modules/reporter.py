"""
Markdown report builder for PL/SQL AI reviews.
"""

from typing import Dict, Any


def _format_issue_section(title: str, items: list[str]) -> str:
    if not items:
        return f"### {title}\n\n- *(none detected)*\n"
    lines = "\n".join(f"- {item}" for item in items)
    return f"### {title}\n\n{lines}\n"


def build_markdown_report(
    file_name: str,
    summary: str,
    classification: Dict[str, Any],
    analysis: Dict[str, Any],
) -> str:
    """
    Build a human-readable Markdown report from the AI outputs.
    """
    perf = classification.get("performance", [])
    eh = classification.get("error_handling", [])
    logic = classification.get("logic_correctness", [])
    maint = classification.get("maintainability", [])
    sec = classification.get("security", [])
    di = classification.get("data_integrity", [])
    unc = classification.get("uncertainty", [])

    risks = analysis.get("risks", [])
    assumptions = analysis.get("assumptions", [])

    parts: list[str] = []

    parts.append(f"# Code Review: {file_name}\n")
    parts.append("## Summary\n")
    parts.append(summary.strip() + "\n")

    parts.append("## Issue Categories\n")
    parts.append(_format_issue_section("Performance", perf))
    parts.append(_format_issue_section("Error Handling", eh))
    parts.append(_format_issue_section("Logic Correctness", logic))
    parts.append(_format_issue_section("Maintainability", maint))
    parts.append(_format_issue_section("Security", sec))
    parts.append(_format_issue_section("Data Integrity", di))
    parts.append(_format_issue_section("Uncertainty / Open Questions", unc))

    parts.append("## Risks\n")
    if risks:
        parts.append("\n".join(f"- {r}" for r in risks) + "\n")
    else:
        parts.append("- *(none explicitly identified)*\n")

    parts.append("## Assumptions\n")
    if assumptions:
        parts.append("\n".join(f"- {a}" for a in assumptions) + "\n")
    else:
        parts.append("- *(none explicitly identified)*\n")

    # Optional: add a stub section for future refactor suggestions
    parts.append("## Refactor Suggestions (Optional / Future Work)\n")
    parts.append(
        "- This version does not yet include automated refactor output.\n"
        "- Future versions may generate a behavior-preserving refactor using a dedicated prompt.\n"
    )

    return "\n".join(parts)
