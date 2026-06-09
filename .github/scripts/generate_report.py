#!/usr/bin/env python3
"""Generate a branded PDF report for a merged pull request.

Reads `pr.json` (from `gh pr view`) and `checks.json` (from the GitHub
check-runs API) in the current directory, renders the HTML template, and writes
`report_output/PR-<number>-<slug>.pdf`.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re

from jinja2 import Template
from weasyprint import HTML


def _load(path: str, default):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def _overall_test_state(check_runs: list[dict]) -> tuple[str, str]:
    """Return (label, state) where state is pass | fail | pending | neutral."""
    if not check_runs:
        return ("No checks reported", "neutral")
    if any(r.get("status") != "completed" for r in check_runs):
        return ("In progress", "pending")
    conclusions = [r.get("conclusion") for r in check_runs]
    if all(c in ("success", "neutral", "skipped") for c in conclusions):
        return ("Passed", "pass")
    return ("Failed", "fail")


def main() -> None:
    pr = _load("pr.json", {})
    checks = _load("checks.json", {"check_runs": []})
    check_runs = checks.get("check_runs", []) if isinstance(checks, dict) else []

    test_label, test_state = _overall_test_state(check_runs)

    number = pr.get("number", "x")
    title = pr.get("title", "report")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-").lower()[:50] or "report"

    out_dir = pathlib.Path("report_output")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"PR-{number}-{slug}.pdf"

    context = {
        "repo": os.environ.get("REPO", ""),
        "pr": pr,
        "author": (pr.get("author") or {}).get("login", "—"),
        "merged_by": (pr.get("mergedBy") or {}).get("login", "—"),
        "merged_at": (pr.get("mergedAt") or "")[:10],
        "commits": pr.get("commits", []) or [],
        "files": pr.get("files", []) or [],
        "additions": pr.get("additions", 0),
        "deletions": pr.get("deletions", 0),
        "changed_files": pr.get("changedFiles", 0),
        "body": (pr.get("body") or "").strip() or "_No description provided._",
        "test_label": test_label,
        "test_state": test_state,
        "check_runs": check_runs,
        "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }

    template_path = pathlib.Path(".github/scripts/report_template.html")
    template = Template(template_path.read_text(encoding="utf-8"))
    html = template.render(**context)
    HTML(string=html).write_pdf(str(out_path))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
