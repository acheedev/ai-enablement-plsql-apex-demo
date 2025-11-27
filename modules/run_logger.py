"""
run_logger.py

Lightweight run-level logging / audit for the PL/SQL review tool.

- Captures input file, model, flags, and input hash.
- Logs each step (summary, classification, analysis, refactor).
- Records output files and their hashes.
- Writes a single JSON run log per execution.

Intended to be simple, explicit, and easy to read in Git or CI.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional


def _sha256_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class RunLogger:
    input_file: str
    model: Optional[str]
    input_sha256: str
    flags: Dict[str, Any]
    started_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z"
    )
    steps: List[Dict[str, Any]] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)

    def log_step(self, name: str, status: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a step in the workflow.

        name:   e.g. "summary", "classification", "analysis", "refactor"
        status: e.g. "started", "success", "skipped", "failed"
        extra:  arbitrary metadata (error message, correction used, etc.)
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "name": name,
            "status": status,
        }
        if extra:
            event["extra"] = extra
        self.steps.append(event)

    def add_output(
        self,
        kind: str,
        path: Path,
        content: Optional[str] = None,
    ) -> None:
        """
        Register an output artifact.

        kind:   logical type (e.g. "summary_json", "classification_json", "analysis_json",
                "markdown_report", "refactor_sql")
        path:   file path
        content:optional raw content (if you already have it); if None we hash from disk.
        """
        if content is not None:
            digest = _sha256_text(content)
        else:
            digest = _sha256_file(path)

        self.outputs.append(
            {
                "kind": kind,
                "path": str(path),
                "sha256": digest,
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "started_at": self.started_at,
            "input_file": self.input_file,
            "model": self.model or "DEFAULT",
            "input_sha256": self.input_sha256,
            "flags": self.flags,
            "steps": self.steps,
            "outputs": self.outputs,
        }

    def write(self, log_dir: Path, base_name: str) -> Path:
        """
        Write the run log JSON into the log directory as <base_name>_runlog.json.
        Returns the path.
        """
        data = self.to_dict()
        log_dir.mkdir(parents=True, exist_ok=True)
        out_path = log_dir / f"{base_name}_runlog.json"
        out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return out_path
