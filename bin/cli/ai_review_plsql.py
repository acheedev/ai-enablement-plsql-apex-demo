#!/usr/bin/env python3
"""
ai_review_plsql.py

Reads a PL/SQL file and sends it to an AI model using the
"PL/SQL Code Review – AI Assistant" prompt pattern.

This is demo code: focus is on workflow, not production hardening.
"""

import os
import sys
from pathlib import Path

import openai  # or the relevant client library

PROMPT_FILE = Path("prompts/01-code-review-plsql.md")

def load_prompt() -> str:
    return PROMPT_FILE.read_text(encoding="utf-8")

def load_source(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

def main():
    if len(sys.argv) != 2:
        print("Usage: ai_review_plsql.py path/to/package.sql", file=sys.stderr)
        sys.exit(1)

    source_path = sys.argv[1]

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set in environment.", file=sys.stderr)
        sys.exit(1)

    openai.api_key = api_key

    prompt_template = load_prompt()
    plsql_code = load_source(source_path)

    # Simple concatenation; in real usage you'd use the new client API with
    # messages=[...] and model="gpt-4.1" or similar.
    user_content = f"{prompt_template}\n\n---\n\nHere is the PL/SQL code:\n\n```plsql\n{plsql_code}\n```"

    response = openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a senior Oracle PL/SQL reviewer."},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
    )

    print(response["choices"][0]["message"]["content"])

if __name__ == "__main__":
    main()
