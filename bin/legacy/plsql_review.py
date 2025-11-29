#!/usr/bin/env python3
# python plsql_review.py prc_ex.sql --model gpt-4.1-mini --no-markdown --output-dir ./output --no-classification --no-analysis --refactor
from dotenv import load_dotenv
import argparse
import json
from hashlib import sha256
from modules.run_logger import RunLogger

from pathlib import Path
from prompts import (
    build_summary_prompt,
    build_classification_prompt,
    build_analysis_prompt,
    build_refactor_prompt,
    build_json_correction_prompt,
    ANALYSIS_JSON_TEMPLATE,
    CLASSIFICATION_JSON_TEMPLATE,
)
from validator import (
    validate_summary,
    validate_classification,
    validate_analysis,
)
from reporter import build_markdown_report
from llm_client import call_llm


load_dotenv()

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

def run_classification_step(code: str, model: str | None = None) -> dict:
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
                f"Classification JSON still invalid after correction.\n"
                f"Original error: {exc}\n"
                f"Correction error: {exc2}\n"
                f"Original output:\n{raw}\n\nCorrected output:\n{fixed_raw}"
            )
    validate_classification(data, code)
    return data

def run_analysis_step(code: str, model: str | None = None) -> dict:
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
                f"Analysis JSON still invalid after correction.\n"
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



def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI-assisted PL/SQL code reviewer (summary, classification, analysis)."
    )
    parser.add_argument(
        "--log-dir",
        help="Directory to write run logs and global index (default: ./runs)",
        default="runs",
    )
    parser.add_argument(
        "input_file",
        help="Path to PL/SQL source file (.sql, .pks, .pkb, etc.)",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to write JSON and Markdown outputs (default: ./output)",
        default="output",
    )
    parser.add_argument(
        "--model",
        help="Override the default LLM model for this run (e.g. gpt-4.1, gpt-4.1-mini)",
        default=None,
    )
    parser.add_argument(
        "--no-markdown",
        action="store_true",
        help="Skip generating the Markdown report.",
    )
    parser.add_argument(
        "--no-classification",
        action="store_true",
        help="Skip classification step (no classification JSON; report will show no issues by category).",
    )
    parser.add_argument(
        "--no-analysis",
        action="store_true",
        help="Skip analysis step (no analysis JSON; risks/assumptions will be empty).",
    )
    parser.add_argument(
        "--refactor",
        action="store_true",
        help="Generate a behavior-preserving refactored version of the code.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompts that would be sent to the model, but do not call the LLM or write outputs.",
    )



    args = parser.parse_args()

    input_path = Path(args.input_file).expanduser().resolve()
    if not input_path.is_file():
        raise SystemExit(f"Input file does not exist: {input_path}")

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    log_dir = Path(args.log_dir).expanduser().resolve()
    # we don't mkdir here yet; RunLogger.write() will ensure it exists

    # Save JSON artifacts
    base_name = input_path.stem
    summary_json_path = output_dir / f"{base_name}_summary.json"
    classification_json_path = output_dir / f"{base_name}_classification.json"
    analysis_json_path = output_dir / f"{base_name}_analysis.json"

    code = input_path.read_text(encoding="utf-8")

    # If --dry-run is enabled, print the prompts and exit before calling the LLM.
    if args.dry_run:
        model = args.model
        print(f"[DRY-RUN] PL/SQL review for: {input_path.name}")
        print(f"[DRY-RUN] Model: {model or 'DEFAULT (from LLM_MODEL or llm_client.DEFAULT_MODEL)'}")
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
        if not args.no_classification:
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
        if not args.no_analysis:
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
        if args.refactor:
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
        return


    model = args.model  # may be None → default in llm_client

    # Initialize run logger
    flags = {
        "model": model,
        "no_markdown": args.no_markdown,
        "no_classification": args.no_classification,
        "no_analysis": args.no_analysis,
        "refactor": args.refactor,
    }
    run_logger = RunLogger(
        input_file=str(input_path),
        model=model,
        input_sha256=_sha256_text(code),
        flags=flags,
    )

    empty_classification = {
        "performance": [],
        "error_handling": [],
        "logic_correctness": [],
        "maintainability": [],
        "security": [],
        "data_integrity": [],
        "uncertainty": [],
    }
    classification = empty_classification
    analysis = {"summary": "", "risks": [], "assumptions": []}

    print(f"[INFO] Running summary step on: {input_path.name} (model={model or 'DEFAULT'})")
    run_logger.log_step("summary", "started")
    summary_text = run_summary_step(code, model=model)
    run_logger.log_step("summary", "success")

    summary_json_path = output_dir / f"{base_name}_summary.json"
    summary_content = json.dumps({"summary": summary_text}, indent=2)
    summary_json_path.write_text(summary_content, encoding="utf-8")
    run_logger.add_output(
        kind="summary_json",
        path=summary_json_path,
        content=summary_content,
    )


    if not args.no_classification:
        print("[INFO] Running classification step...")
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
        print("[INFO] --no-classification flag detected; skipping classification step.")
        run_logger.log_step("classification", "skipped")


    if not args.no_analysis:
        print("[INFO] Running analysis step...")
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
        print("[INFO] --no-analysis flag detected; skipping analysis step.")
        run_logger.log_step("analysis", "skipped")

    refactored_code: str | None = None
    if args.refactor:
        print("[INFO] Running refactor step...")
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
        print("[INFO] --refactor not specified; skipping refactor step.")
        run_logger.log_step("refactor", "skipped")



    summary_json_path.write_text(
        json.dumps({"summary": summary_text}, indent=2),
        encoding="utf-8",
    )
    classification_json_path.write_text(
        json.dumps(classification, indent=2),
        encoding="utf-8",
    )
    analysis_json_path.write_text(
        json.dumps(analysis, indent=2),
        encoding="utf-8",
    )

    if not args.no_markdown:
        report_md = build_markdown_report(
            file_name=input_path.name,
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
        print("[INFO] --no-markdown flag detected; skipping Markdown report.")

    print(f"[INFO] JSON outputs written to: {output_dir}")

    runlog_path = run_logger.write(log_dir, base_name)
    print(f"[INFO] Run log written to: {runlog_path}")

    index_path = _update_global_index(log_dir, runlog_path, run_logger)
    print(f"[INFO] Global run index updated at: {index_path}")


if __name__ == "__main__":
    main()


