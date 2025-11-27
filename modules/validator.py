"""
Validation helpers for LLM outputs.
These are intentionally conservative; tighten as needed.
"""

from typing import Any, Dict


def validate_summary(summary: str, code: str) -> None:
    """
    Basic checks for the summary step.
    You can extend this with:
      - sentence count checks
      - simple heuristics to detect obvious hallucinations
    """
    if not summary or not summary.strip():
        raise ValueError("Summary is empty.")

    # Very lightweight sanity checks:
    if "CREATE TABLE" in summary or "INSERT INTO" in summary:
        # Summary should describe behavior, not start dumping SQL.
        # Not fatal, but suspicious; you can upgrade this to an error if you like.
        pass


def _ensure_keys(obj: Dict[str, Any], required_keys: list[str], context: str) -> None:
    for key in required_keys:
        if key not in obj:
            raise ValueError(f"{context}: missing required key '{key}'.")


def validate_classification(data: Dict[str, Any], code: str) -> None:
    required_categories = [
        "performance",
        "error_handling",
        "logic_correctness",
        "maintainability",
        "security",
        "data_integrity",
        "uncertainty",
    ]
    _ensure_keys(data, required_categories, "Classification")

    for key in required_categories:
        if not isinstance(data[key], list):
            raise ValueError(f"Classification: '{key}' should be a list, got {type(data[key])}.")

    # Optionally: check that items are short strings
    for key, issues in data.items():
        for issue in issues:
            if not isinstance(issue, str):
                raise ValueError(f"Classification: entry in '{key}' is not a string: {issue!r}")


def validate_analysis(data: Dict[str, Any], code: str) -> None:
    required = ["summary", "risks", "assumptions"]
    _ensure_keys(data, required, "Analysis")

    if not isinstance(data["summary"], str):
        raise ValueError("Analysis: 'summary' must be a string.")

    if not isinstance(data["risks"], list) or not all(
        isinstance(r, str) for r in data["risks"]
    ):
        raise ValueError("Analysis: 'risks' must be a list of strings.")

    if not isinstance(data["assumptions"], list) or not all(
        isinstance(a, str) for a in data["assumptions"]
    ):
        raise ValueError("Analysis: 'assumptions' must be a list of strings.")

    # You can optionally add regex-based guards here
    # to detect obviously invented table/column names, etc.
