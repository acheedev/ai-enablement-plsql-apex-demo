# scripts/ai_plsql_review.py

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

from modules import llm_client  # your existing client
# from modules import validator  # if you want to sanity check LLM output

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI-powered PL/SQL review over a directory."
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Root directory to scan (e.g. 'sql')",
    )
    parser.add_argument(
        "--glob",
        default="**/*.sql",
        help="Glob pattern relative to --path for files to analyze.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write JSON/Markdown outputs into.",
    )
    parser.add_argument(
        "--log-dir",
        required=False,
        help="Directory to write run logs / debug info.",
    )
    parser.add_argument(
        "--run-id",
        required=False,
        help="Run ID for traceability; if omitted, a timestamp-based ID is used.",
    )
    return parser.parse_args()


def discover_files(root: Path, pattern: str) -> list[Path]:
    return sorted(root.glob(pattern))


def analyze_file(path: Path) -> dict:
    """
    Call your existing LLM analysis here.

    EXPECTED RETURN SHAPE (example):

    {
      "risk_score": 75,
      "summary": "High-level what this unit does...",
      "issues": [
        {
          "severity": "high",
          "code": "SQL_INJECTION_RISK",
          "message": "...",
          "line": 120
        }
      ],
      "refactor_suggestions": [
        "Use bind variables ...",
        "Introduce package API ..."
      ],
      "checklist_items": [
        "Verify NULL handling on FOO.",
        "Confirm commit boundary is acceptable."
      ]
    }
    """
    content = path.read_text(encoding="utf-8", errors="ignore")

    # TODO: hook into your existing llm_client logic
    # Something like:
    #
    # result = llm_client.analyze_plsql(
    #     filename=str(path),
    #     content=content,
    # )
    #
    # For now, stub something so you can test the pipeline shape.
    result = llm_client.analyze_plsql(
        filename=str(path),
        content=content,
    )

    result["path"] = str(path)
    return result


def aggregate_results(run_id: str, file_results: list[dict]) -> dict:
    scanned_files = len(file_results)
    if scanned_files == 0:
        overall_risk = 0
    else:
        overall_risk = round(
            sum(fr.get("risk_score", 0) for fr in file_results) / scanned_files
        )

    red_flags = []
    checklist = []

    for fr in file_results:
        for issue in fr.get("issues", []):
            if issue.get("severity", "").lower() in {"high", "critical"}:
                flagged = {
                    "file": fr.get("path"),
                    "severity": issue.get("severity"),
                    "code": issue.get("code"),
                    "message": issue.get("message"),
                }
                red_flags.append(flagged)
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


def write_summary_json(out_dir: Path, summary: dict) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "summary.json"
    target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return target


def write_summary_md(out_dir: Path, summary: dict) -> Path:
    lines: list[str] = []
    lines.append(f"# AI PL/SQL Review Report")
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

    root = Path(args.path).resolve()
    output_root = Path(args.output_dir).resolve()
    log_dir = Path(args.log_dir).resolve() if args.log_dir else None

    if not root.exists():
        print(f"ERROR: root path does not exist: {root}", file=sys.stderr)
        return 1

    run_id = args.run_id or datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    files = discover_files(root, args.glob)
    print(f"Discovered {len(files)} file(s) under {root} with pattern {args.glob}")

    results: list[dict] = []
    for path in files:
        print(f"Analyzing {path} ...")
        try:
            fr = analyze_file(path)
            results.append(fr)
        except Exception as e:  # fail-safe; don’t blow the whole run on one file
            print(f"ERROR analyzing {path}: {e}", file=sys.stderr)

    summary = aggregate_results(run_id, results)

    run_out_dir = output_root / run_id
    write_summary_json(run_out_dir, summary)
    write_summary_md(run_out_dir, summary)

    print(f"Run {run_id} complete. Outputs in: {run_out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
