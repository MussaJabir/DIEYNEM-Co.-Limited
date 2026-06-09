# Reports branch

This branch is **machine-managed**. It holds auto-generated PDF reports — one per
merged pull request — produced by the `PR Report` GitHub Action.

- Each merged PR adds `reports/PR-<number>-<title>.pdf`.
- Files are committed by `github-actions[bot]`.
- **Do not edit or commit here manually**, and do not merge this branch into `main`/`develop`.

Reports are also available as workflow artifacts on each PR's Actions run.
