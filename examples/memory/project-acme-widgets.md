---
type: Project
title: acme-widgets
tags: [acme-widgets, backend]
status: stable
generated: { by: claude-code/example, at: 2026-10-21T09:00:00Z }
name: project-acme-widgets
description: "acme-widgets is a Python 3.12 + Postgres service, deployed from main by CI; Sam owns it; staging mirrors production schema"
metadata:
  node_type: memory
  type: project
---

`acme-widgets` is the widget catalogue and ordering service. A fictional example of a
project memory: what it is, where it lives, how it ships, and the decisions that are not
obvious from the code.

- **Stack.** Python 3.12, FastAPI, Postgres 16. Tests with pytest; lint with ruff. The full
  check is `make check` (tests and lint together, never one without the other).
- **Shipping.** Every merge to `main` deploys to staging; a tag deploys to production. Both
  run on the dedicated runner pool ([Acme CI Runner](/reference-acme-ci-runner.md)).
- **Deploys** go through `widgetctl`, which has a sharp edge:
  [widgetctl Exit-Zero Trap](/reference-widgetctl-exit-zero-trap.md).
- **Decision (2026-09-02).** Money is stored as integer cents, never floats. A float column
  was tried in the prototype and removed after a rounding bug in the invoice totals.
- **Owner.** Sam ([User Profile](/user-profile.md)). Review requests go to Sam first.

Put the facts a new session needs on day one here, and move anything that ages into a
`Reference` file with a `stale_after`.
