# Example Workflow – PL/SQL Code Review with AI Assist

This is a simple example of how an Oracle / APEX team could use this
repository in their **daily development workflow**.

The goal is **not** to replace human code review, but to:
- Catch obvious issues earlier
- Standardize review questions
- Make senior reviewers faster

---

## 1. Developer writes / changes a PL/SQL package

Normal flow:

- Developer edits `invoice_pkg` in their local repo.
- Runs basic compile checks in a dev database.
- Commits changes to a feature branch, e.g. `feature/invoice-discounts`.

---

## 2. Optional: Local AI-assisted review

Before opening a pull request, the developer can run:

```bash
python scripts/ai_review_plsql.py samples/plsql_invoice_pkg.sql
