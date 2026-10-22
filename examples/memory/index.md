---
okf_version: "0.2"
---

# General

* [User Profile](user-profile.md) - Sam Rivera (a fictional user): backend developer on acme-widgets, 12 years of Python, prefers direct answers with numbers

# How to work with Sam

* [Verify Before Asserting](feedback-verify-before-asserting.md) - Check the repo or the live system before stating a fact or asking Sam a question; never answer from memory when the answer is one command away

# Projects

* [acme-widgets](project-acme-widgets.md) - acme-widgets is a Python 3.12 + Postgres service, deployed from main by CI; Sam owns it; staging mirrors production schema

# Reference

* [Acme CI Runner](reference-acme-ci-runner.md) - acme-widgets CI runs on the dedicated runner pool labelled widgets-ci (4 vCPU, 8 GB); re-check the label before relying on it, it changes with infra migrations
* [widgetctl Exit-Zero Trap](reference-widgetctl-exit-zero-trap.md) - TRAP: widgetctl deploy exits 0 even when the rollout failed; read the final status line (ROLLED OUT / ROLLED BACK) instead of trusting the exit code
* [Acme CI Runner (legacy)](reference-acme-ci-runner-legacy.md) - DEPRECATED: acme-widgets used the shared runner pool until 2026-09; superseded by the dedicated pool in reference-acme-ci-runner
