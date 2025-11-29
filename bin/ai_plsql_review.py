#!/usr/bin/env python3
"""
Directory-wide AI-powered PL/SQL review.

This script scans a directory for PL/SQL-related files, runs the same
multi-step pipeline as `plsql_review.py` (summary, classification,
analysis, optional refactor), logs each file's run, writes per-file
artifacts, and produces an aggregated summary.json + summary.md for the run.
"""

from __future__ import annotations

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

from dotenv import load_dotenv

from modules.run_logger import RunLogger
from modules.prompts import (
    build_summary_prompt,
    build_classification_prompt,
    build_analysis_prompt,
    build_refactor_prompt,
    build_json_correction_prompt,
    ANALYSIS_JSON_TEMPLATE,
    CLASSIFICATION_JSON_TEMPLATE,
)
from modules.validator import (
    validate_summary,
    validate_classification,
    validate_analysis,
)
from modules.reporter import build_markdown_report
from modules.llm_client import call_llm


load_dotenv()


# ---------------------------------------------------------------------------
# Helpers copied / adapted from the single-file plsql_review.py
# ---------------------------------------------------------------------------

def _sha256_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _update_global_index(log_dir: Path, runlog_path: Path, run_logger: RunLogger) -> Path:
    """
    Update (or create) a global index.json file in log_dir with a summary
    of this run. Returns the index.json path.
    """
    index_path = log_dir / "index.json"

    # Load existing index or start a new list
    if index_path.is_file():
        try:
            existing = json.loads(index_path.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
        except Exception:
            existing = []
    else:
        existing = []

    entry = run_logger.to_dict()
    entry["runlog_path"] = str(runlog_path)

    existing.append(entry)

    index_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    return index_path


def _correct_json(raw: str, template: str, model: str | None = None) -> str:
    """
    Use the JSON correction prompt to fix malformed JSON.
    Returns the corrected JSON text (still as a string).
    """
    system_prompt, user_prompt = build_json_correction_prompt(raw, template)
    fixed_raw = call_llm(system_prompt, user_prompt, model=model).strip()
    return fixed_raw


def run_summary_step(code: str, model: str | None = None) -> str:
    system_prompt, user_prompt = build_summary_prompt(code)
    raw = call_llm(system_prompt, user_prompt, model=model)
    validate_summary(raw, code)
    return raw.strip()


def run_classification_step(code: str, model: str | None = None) -> Dict[str, Any]:
    system_prompt, user_prompt = build_classification_prompt(code)
    raw = call_llm(system_prompt, user_prompt, model=model).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        # Attempt one correction pass
        print(f"[WARN] Classification JSON malformed, attempting correction: {exc}")
        fixed_raw = _correct_json(raw, CLASSIFICATION_JSON_TEMPLATE, model=model)
        try:
            data = json.loads(fixed_raw)
        except json.JSONDecodeError as exc2:
            raise ValueError(
                "Classification JSON still invalid after correction.\n"
                f"Original error: {exc}\n"
                f"Correction error: {exc2}\n"
                f"Original output:\n{raw}\n\nCorrected output:\n{fixed_raw}"
            )
    validate_classification(data, code)
    return data


def run_analysis_step(code: str, model: str | None = None) -> Dict[str, Any]:
    system_prompt, user_prompt = build_analysis_prompt(code)
    raw = call_llm(system_prompt, user_prompt, model=model).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        # Attempt one correction pass
        print(f"[WARN] Analysis JSON malformed, attempting correction: {exc}")
        fixed_raw = _correct_json(raw, ANALYSIS_JSON_TEMPLATE, model=model)
        try:
            data = json.loads(fixed_raw)
        except json.JSONDecodeError as exc2:
            raise ValueError(
                "Analysis JSON still invalid after correction.\n"
                f"Original error: {exc}\n"
                f"Correction error: {exc2}\n"
                f"Original output:\n{raw}\n\nCorrected output:\n{fixed_raw}"
            )
    validate_analysis(data, code)
    return data


def run_refactor_step(code: str, model: str | None = None) -> str:
    system_prompt, user_prompt = build_refactor_prompt(code)
    raw = call_llm(system_prompt, user_prompt, model=model).strip()
    if not raw:
        raise ValueError("Refactor output is empty.")
    return raw


# ---------------------------------------------------------------------------
# Directory-level orchestration
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Directory-wide AI-assisted PL/SQL code reviewer."
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Root directory to scan (e.g. 'sql').",
    )
    parser.add_argument(
        "--glob",
        default="**/*.sql",
        help="Glob pattern relative to --path for files to analyze (default: '**/*.sql').",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to write run outputs (default: ./var/output)",
        default="var/output",
    )
    parser.add_argument(
        "--log-dir",
        help="Directory to write run logs and global index (default: ./var/logs)",
        default="var/logs",
    )
    parser.add_argument(
        "--model",
        help="Override the default LLM model for this run (e.g. gpt-4.1, gpt-4.1-mini).",
        default=None,
    )
    parser.add_argument(
        "--no-markdown",
        action="store_true",
        help="Skip generating per-file Markdown reports.",
    )
    parser.add_argument(
        "--no-classification",
        action="store_true",
        help="Skip classification step.",
    )
    parser.add_argument(
        "--no-analysis",
        action="store_true",
        help="Skip analysis step.",
    )
    parser.add_argument(
        "--refactor",
        action="store_true",
        help="Generate behavior-preserving refactored code for each file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompts that would be sent to the model, but do not call the LLM or write outputs.",
    )
    parser.add_argument(
        "--run-id",
        help="Explicit run ID (default: timestamp-based).",
        default=None,
    )
    return parser.parse_args()


def discover_files(root: Path, pattern: str) -> List[Path]:
    return sorted(p for p in root.glob(pattern) if p.is_file())


def _flatten_issues_from_classification(classification: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    for category, items in classification.items():
        # items is expected to be a list of issue dicts
        if not isinstance(items, list):
            continue
        for issue in items:
            if not isinstance(issue, dict):
                issue_dict = {"message": str(issue)}
            else:
                issue_dict = dict(issue)  # shallow copy
            issue_dict.setdefault("category", category)
            # Normalize severity
            sev = (issue_dict.get("severity") or "medium").lower()
            if sev not in {"low", "medium", "high", "critical"}:
                sev = "medium"
            issue_dict["severity"] = sev
            # Provide a code if missing
            issue_dict.setdefault("code", category.upper())
            issues.append(issue_dict)

    return issues


def _compute_risk_score(classification: Dict[str, Any], analysis: Dict[str, Any]) -> int:
    """
    Heuristic risk scoring based on number and severity of issues.
    Returns a score between 0 and 100.
    """
    severity_weights = {"low": 5, "medium": 10, "high": 20, "critical": 30}
    score = 0

    for issue in _flatten_issues_from_classification(classification):
        sev = issue.get("severity", "medium")
        score += severity_weights.get(sev, 10)

    # Light bump if there are any risks in analysis
    risks = analysis.get("risks") or []
    if isinstance(risks, list):
        score += 5 * len(risks)

    # Cap at 100
    return max(0, min(100, score))


def _derive_checklist_items(classification: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
    checklist: List[str] = []

    # From analysis risks/assumptions
    for bucket_name in ("risks", "assumptions"):
        bucket = analysis.get(bucket_name) or []
        if not isinstance(bucket, list):
            continue
        for item in bucket:
            if isinstance(item, dict):
                text = (
                    item.get("mitigation")
                    or item.get("recommendation")
                    or item.get("message")
                    or item.get("description")
                    or ""
                )
            else:
                text = str(item)
            text = text.strip()
            if not text:
                continue
            label = f"Review: {text}"
            if label not in checklist:
                checklist.append(label)

    # From classification "uncertainty" bucket if present
    unc = classification.get("uncertainty") or []
    if isinstance(unc, list):
        for item in unc:
            if isinstance(item, dict):
                text = item.get("message") or item.get("description") or ""
            else:
                text = str(item)
            text = text.strip()
            if not text:
                continue
            label = f"Clarify: {text}"
            if label not in checklist:
                checklist.append(label)

    return checklist


def _derive_refactor_suggestions(classification: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
    suggestions: List[str] = []

    # First, see if analysis has an explicit "suggestions" or similar field
    for key in ("suggestions", "refactor_suggestions", "improvements"):
        val = analysis.get(key)
        if isinstance(val, list):
            for item in val:
                text = str(item).strip()
                if text and text not in suggestions:
                    suggestions.append(text)

    # Fall back to classification issues with recommendations
    for issue in _flatten_issues_from_classification(classification):
        text = (
            issue.get("recommendation")
            or issue.get("suggestion")
            or ""
        )
        text = text.strip()
        if text and text not in suggestions:
            suggestions.append(text)

    return suggestions


def process_file(
    path: Path,
    output_dir: Path,
    log_dir: Path,
    model: str | None,
    flags: Dict[str, Any],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Run the full multi-step pipeline on a single PL/SQL file and return a
    normalized result dict used by the aggregated summary.
    """
    rel_name = path.name
    base_name = path.stem

    code = path.read_text(encoding="utf-8")

    if dry_run:
        print(f"[DRY-RUN] PL/SQL review for: {rel_name}")
        print(f"[DRY-RUN] Model: {model or 'DEFAULT (llm_client)'}")
        print()

        # Summary prompt
        system_prompt, user_prompt = build_summary_prompt(code)
        print("=" * 80)
        print("[DRY-RUN] SUMMARY STEP — system prompt")
        print("-" * 80)
        print(system_prompt)
        print()
        print("[DRY-RUN] SUMMARY STEP — user prompt")
        print("-" * 80)
        print(user_prompt)
        print()

        # Classification prompt (if not disabled)
        if not flags.get("no_classification"):
            system_prompt, user_prompt = build_classification_prompt(code)
            print("=" * 80)
            print("[DRY-RUN] CLASSIFICATION STEP — system prompt")
            print("-" * 80)
            print(system_prompt)
            print()
            print("[DRY-RUN] CLASSIFICATION STEP — user prompt")
            print("-" * 80)
            print(user_prompt)
            print()

        # Analysis prompt (if not disabled)
        if not flags.get("no_analysis"):
            system_prompt, user_prompt = build_analysis_prompt(code)
            print("=" * 80)
            print("[DRY-RUN] ANALYSIS STEP — system prompt")
            print("-" * 80)
            print(system_prompt)
            print()
            print("[DRY-RUN] ANALYSIS STEP — user prompt")
            print("-" * 80)
            print(user_prompt)
            print()

        # Refactor prompt (if requested)
        if flags.get("refactor"):
            system_prompt, user_prompt = build_refactor_prompt(code)
            print("=" * 80)
            print("[DRY-RUN] REFACTOR STEP — system prompt")
            print("-" * 80)
            print(system_prompt)
            print()
            print("[DRY-RUN] REFACTOR STEP — user prompt")
            print("-" * 80)
            print(user_prompt)
            print()

        print("=" * 80)
        print("[DRY-RUN] No LLM calls were made. No files were written.")
        # For a dry-run, return a stub entry
        return {
            "path": str(path),
            "risk_score": 0,
            "summary": "",
            "issues": [],
            "refactor_suggestions": [],
            "checklist_items": [],
        }

    # Real run
    run_logger = RunLogger(
        input_file=str(path),
        model=model,
        input_sha256=_sha256_text(code),
        flags=flags,
    )

    # Ensure per-run output dirs exist
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    empty_classification = {
        "performance": [],
        "error_handling": [],
        "logic_correctness": [],
        "maintainability": [],
        "security": [],
        "data_integrity": [],
        "uncertainty": [],
    }
    classification: Dict[str, Any] = dict(empty_classification)
    analysis: Dict[str, Any] = {"summary": "", "risks": [], "assumptions": []}

    print(f"[INFO] Running summary step on: {rel_name} (model={model or 'DEFAULT'})")
    run_logger.log_step("summary", "started")
    summary_text = run_summary_step(code, model=model)
    run_logger.log_step("summary", "success")

    # Write per-file summary JSON
    summary_json_path = output_dir / f"{base_name}_summary.json"
    summary_content = json.dumps({"summary": summary_text}, indent=2)
    summary_json_path.write_text(summary_content, encoding="utf-8")
    run_logger.add_output(
        kind="summary_json",
        path=summary_json_path,
        content=summary_content,
    )

    # Classification
    if not flags.get("no_classification"):
        print(f"[INFO] Running classification step on: {rel_name}")
        run_logger.log_step("classification", "started")
        classification = run_classification_step(code, model=model)
        run_logger.log_step("classification", "success")

        classification_json_path = output_dir / f"{base_name}_classification.json"
        classification_content = json.dumps(classification, indent=2)
        classification_json_path.write_text(
            classification_content,
            encoding="utf-8",
        )
        run_logger.add_output(
            kind="classification_json",
            path=classification_json_path,
            content=classification_content,
        )
    else:
        print(f"[INFO] --no-classification flag; skipping classification for {rel_name}")
        run_logger.log_step("classification", "skipped")

    # Analysis
    if not flags.get("no_analysis"):
        print(f"[INFO] Running analysis step on: {rel_name}")
        run_logger.log_step("analysis", "started")
        analysis = run_analysis_step(code, model=model)
        run_logger.log_step("analysis", "success")

        analysis_json_path = output_dir / f"{base_name}_analysis.json"
        analysis_content = json.dumps(analysis, indent=2)
        analysis_json_path.write_text(
            analysis_content,
            encoding="utf-8",
        )
        run_logger.add_output(
            kind="analysis_json",
            path=analysis_json_path,
            content=analysis_content,
        )
    else:
        print(f"[INFO] --no-analysis flag; skipping analysis for {rel_name}")
        run_logger.log_step("analysis", "skipped")

    # Optional refactor step
    if flags.get("refactor"):
        print(f"[INFO] Running refactor step on: {rel_name}")
        run_logger.log_step("refactor", "started")
        refactored_code = run_refactor_step(code, model=model)
        refactor_path = output_dir / f"{base_name}_refactor.sql"
        refactor_path.write_text(refactored_code, encoding="utf-8")
        run_logger.add_output(
            kind="refactor_sql",
            path=refactor_path,
            content=refactored_code,
        )
        run_logger.log_step("refactor", "success")
        print(f"[INFO] Refactored code written to: {refactor_path}")
    else:
        print(f"[INFO] --refactor not set; skipping refactor for {rel_name}")
        run_logger.log_step("refactor", "skipped")

    # Markdown report per file
    if not flags.get("no_markdown"):
        report_md = build_markdown_report(
            file_name=rel_name,
            summary=summary_text,
            classification=classification,
            analysis=analysis,
        )
        report_path = output_dir / f"{base_name}_review.md"
        report_path.write_text(report_md, encoding="utf-8")
        run_logger.add_output(
            kind="markdown_report",
            path=report_path,
            content=report_md,
        )
        print(f"[INFO] Markdown report written to: {report_path}")
    else:
        print(f"[INFO] --no-markdown; skipping Markdown report for {rel_name}")

    # Persist run log
    runlog_path = run_logger.write(log_dir, base_name)
    _update_global_index(log_dir, runlog_path, run_logger)

    # Derive aggregated fields
    issues = _flatten_issues_from_classification(classification)
    risk_score = _compute_risk_score(classification, analysis)
    checklist_items = _derive_checklist_items(classification, analysis)
    refactor_suggestions = _derive_refactor_suggestions(classification, analysis)

    return {
        "path": str(path),
        "risk_score": risk_score,
        "summary": summary_text,
        "issues": issues,
        "refactor_suggestions": refactor_suggestions,
        "checklist_items": checklist_items,
    }


def aggregate_results(run_id: str, file_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    scanned_files = len(file_results)
    if scanned_files == 0:
        overall_risk = 0
    else:
        overall_risk = round(
            sum(fr.get("risk_score", 0) for fr in file_results) / scanned_files
        )

    red_flags: List[Dict[str, Any]] = []
    checklist: List[str] = []

    for fr in file_results:
        for issue in fr.get("issues", []):
            sev = (issue.get("severity") or "").lower()
            if sev in {"high", "critical"}:
                red_flags.append(
                    {
                        "file": fr.get("path"),
                        "severity": issue.get("severity"),
                        "code": issue.get("code"),
                        "message": issue.get("message"),
                    }
                )
        for item in fr.get("checklist_items", []):
            if item not in checklist:
                checklist.append(item)

    return {
        "run_id": run_id,
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "scanned_files": scanned_files,
        "overall_risk_score": overall_risk,
        "red_flags": red_flags,
        "files": file_results,
        "checklist": checklist,
    }


def write_summary_json(out_dir: Path, summary: Dict[str, Any]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "summary.json"
    target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return target


def write_summary_md(out_dir: Path, summary: Dict[str, Any]) -> Path:
    lines: List[str] = []
    lines.append("# AI PL/SQL Review Report")
    lines.append("")
    lines.append(f"- Run ID: `{summary['run_id']}`")
    lines.append(f"- Files scanned: **{summary['scanned_files']}**")
    lines.append(f"- Overall risk score: **{summary['overall_risk_score']}** / 100")
    lines.append("")

    if summary["red_flags"]:
        lines.append("## Red Flags (High/Critical)")
        lines.append("")
        for rf in summary["red_flags"]:
            lines.append(
                f"- **{rf['severity'].upper()}** in `{rf['file']}` "
                f"({rf.get('code', 'UNSPECIFIED')}): {rf['message']}"
            )
        lines.append("")

    if summary["checklist"]:
        lines.append("## Review Checklist")
        lines.append("")
        for item in summary["checklist"]:
            lines.append(f"- [ ] {item}")
        lines.append("")

    if summary["files"]:
        lines.append("## Per-File Highlights")
        lines.append("")
        for fr in summary["files"]:
            lines.append(f"### `{fr['path']}`")
            lines.append("")
            if fr.get("summary"):
                lines.append(f"**Summary:** {fr['summary']}")
                lines.append("")
            if fr.get("issues"):
                lines.append("**Issues:**")
                for issue in fr["issues"]:
                    lines.append(
                        f"- {issue.get('severity', '').upper()} "
                        f"{issue.get('code', '')}: {issue.get('message', '')}"
                    )
                lines.append("")
            if fr.get("refactor_suggestions"):
                lines.append("**Refactor Suggestions:**")
                for sug in fr["refactor_suggestions"]:
                    lines.append(f"- {sug}")
                lines.append("")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "summary.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def main() -> int:
    args = parse_args()

    root = Path(args.path).expanduser().resolve()
    if not root.exists():
        print(f"ERROR: root path does not exist: {root}", file=sys.stderr)
        return 1

    output_root = Path(args.output_dir).expanduser().resolve()
    log_root = Path(args.log_dir).expanduser().resolve()

    run_id = args.run_id or datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    # Run-level subdirs
    run_output_dir = output_root / run_id
    run_log_dir = log_root / run_id

    files = discover_files(root, args.glob)
    if not files:
        print(f"[INFO] No files found under {root} matching pattern {args.glob}")
        return 0

    print(f"[INFO] Discovered {len(files)} file(s) under {root} with pattern {args.glob}")

    model = args.model or None
    flags: Dict[str, Any] = {
        "model": model,
        "no_markdown": args.no_markdown,
        "no_classification": args.no_classification,
        "no_analysis": args.no_analysis,
        "refactor": args.refactor,
    }

    results: List[Dict[str, Any]] = []

    for path in files:
        print(f"[INFO] === Processing {path} ===")
        try:
            # Each file writes its own per-file artifacts under run_output_dir
            file_result = process_file(
                path=path,
                output_dir=run_output_dir,
                log_dir=run_log_dir,
                model=model,
                flags=flags,
                dry_run=args.dry_run,
            )
            results.append(file_result)
        except Exception as exc:
            print(f"[ERROR] Failed processing {path}: {exc}", file=sys.stderr)
            # Continue to next file; CI should still see partial results

    summary = aggregate_results(run_id, results)

    write_summary_json(run_output_dir, summary)
    write_summary_md(run_output_dir, summary)

    print(f"[INFO] Run {run_id} complete. Outputs in: {run_output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
