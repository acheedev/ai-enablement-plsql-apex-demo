# scripts/ai_ci_gate.py

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

from modules import llm_client  # reuse same client


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI gatekeeper for CI logs (sqlcl, tests, etc.)."
    )
    parser.add_argument(
        "--log-file",
        required=True,
        help="Path to CI log file (e.g. ci/sqlcl.log).",
    )
    parser.add_argument(
        "--run-id",
        required=False,
        help="Run ID for traceability.",
    )
    parser.add_argument(
        "--output-dir",
        required=False,
        help="Optional dir to write ai-ci-gate.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    log_path = Path(args.log_file)
    if not log_path.exists():
        print(f"ERROR: log file not found: {log_path}", file=sys.stderr)
        return 1

    log_text = log_path.read_text(encoding="utf-8", errors="ignore")
    run_id = args.run_id or datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    # You define this in llm_client; prompt something like:
    # "You are a deployment gatekeeper. Analyze this log and answer strictly JSON:
    #  { 'deploy_ok': true/false, 'reasons': [ ... ], 'severity': 'low/medium/high' }"
    result = llm_client.review_ci_logs(
        log_text=log_text,
        run_id=run_id,
    )

    # Expected shape:
    # {
    #   "deploy_ok": true,
    #   "reasons": ["All tests passed", "No ORA- errors found"],
    #   "severity": "low"
    # }

    deploy_ok = bool(result.get("deploy_ok", False))
    reasons = result.get("reasons", [])
    severity = result.get("severity", "unknown")

    print(f"AI CI Gate result: deploy_ok={deploy_ok}, severity={severity}")
    for r in reasons:
        print(f"- {r}")

    if args.output_dir:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "ai-ci-gate.json").write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "deploy_ok": deploy_ok,
                    "severity": severity,
                    "reasons": reasons,
                    "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    # Hard gate: if deploy_ok is false, fail the job
    if not deploy_ok:
        print("AI CI Gate: BLOCKING DEPLOY", file=sys.stderr)
        return 1

    print("AI CI Gate: OK to deploy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
