---
type: Reference
title: widgetctl Exit-Zero Trap
tags: [trap, deploy, acme-widgets]
status: stable
generated: { by: claude-code/example, at: 2026-10-21T09:00:00Z }
name: reference-widgetctl-exit-zero-trap
description: "TRAP: widgetctl deploy exits 0 even when the rollout failed; read the final status line (ROLLED OUT / ROLLED BACK) instead of trusting the exit code"
metadata:
  node_type: memory
  type: reference
---

`widgetctl deploy <env>` returns exit code 0 when it *submitted* the rollout, not when the
rollout *succeeded*. A failed health check shows up only on the last line of output:

- `status: ROLLED OUT` — the new version is serving.
- `status: ROLLED BACK` — the health check failed and the previous version is serving.

**Consequence.** A script or an agent that checks `$?` reports success on a rolled-back
deploy. Always parse the status line, and say which one you saw.

**Why it is a memory.** The failure is silent and was hit twice in one week before the cause
was found. A TRAP file names the symptom, the cause and the check in the first two lines so a
future session finds it by the symptom ("deploy said OK but the old version is live").

Related: [acme-widgets](/project-acme-widgets.md).
