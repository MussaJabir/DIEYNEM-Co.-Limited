#!/usr/bin/env python3
"""Generate a client-friendly branded progress report PDF for a pull request.

Reads `pr.json` (from `gh pr view`) and `checks.json` (from the GitHub
check-runs API) in the current directory, renders the HTML template, and writes
`report_output/PR-<number>-<slug>.pdf`.

The report is written for a non-technical reader (the client/boss): it leads with
plain-language Summary and "What's included" content taken from the PR
description, plus simple status and at-a-glance figures — not git internals.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re

import markdown as md
from jinja2 import Template
from weasyprint import HTML

# Maps the internal test state to a stat-value colour class in the template.
TEST_STATE_CLASS = {"pass": "ok", "fail": "fail", "pending": "warn", "neutral": ""}


def _load(path: str, default):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def _overall_test_state(check_runs: list[dict]) -> tuple[str, str]:
    """Return (label, state) where state is pass | fail | pending | neutral."""
    if not check_runs:
        return ("Not reported", "neutral")
    if any(r.get("status") != "completed" for r in check_runs):
        return ("In progress", "pending")
    conclusions = [r.get("conclusion") for r in check_runs]
    if all(c in ("success", "neutral", "skipped") for c in conclusions):
        return ("Passed", "pass")
    return ("Attention", "fail")


def _sections(body: str) -> dict[str, str]:
    """Split a markdown body into {lowercased heading: content} by '## ' headings."""
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in body.splitlines():
        match = re.match(r"^\s*##\s+(.*)", line)
        if match:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = match.group(1).strip().lower()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def _md(text: str) -> str:
    return md.markdown(text, extensions=["extra", "sane_lists"]) if text else ""


def main() -> None:
    pr = _load("pr.json", {})
    checks = _load("checks.json", {"check_runs": []})
    check_runs = checks.get("check_runs", []) if isinstance(checks, dict) else []
    test_label, test_state = _overall_test_state(check_runs)

    body = (pr.get("body") or "").strip()
    sec = _sections(body)
    summary_src = sec.get("summary") or (body.split("\n\n")[0] if body else "")
    highlights_src = sec.get("changes") or sec.get("highlights") or sec.get("what's included") or ""

    number = pr.get("number", "x")
    title = pr.get("title", "Project update")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-").lower()[:50] or "report"

    out_dir = pathlib.Path("report_output")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"PR-{number}-{slug}.pdf"

    context = {
        "title": title,
        "number": number,
        "merged_at": (pr.get("mergedAt") or "")[:10] or "",
        "summary_html": _md(summary_src),
        "highlights_html": _md(highlights_src),
        "has_highlights": bool(highlights_src),
        "changed_files": pr.get("changedFiles", 0),
        "commit_count": len(pr.get("commits", []) or []),
        "test_label": test_label,
        "test_state": test_state,
        "test_state_class": TEST_STATE_CLASS.get(test_state, ""),
        "repo": os.environ.get("REPO", ""),
        "generated": dt.datetime.now(dt.UTC).strftime("%d %B %Y"),
    }

    template_path = pathlib.Path(".github/scripts/report_template.html")
    template = Template(template_path.read_text(encoding="utf-8"))
    HTML(string=template.render(**context)).write_pdf(str(out_path))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
