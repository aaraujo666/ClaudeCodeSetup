---
type: Reference
title: Acme CI Runner
tags: [ci, acme-widgets]
status: stable
stale_after: 2027-03-01T00:00:00Z
generated: { by: claude-code/example, at: 2026-10-21T09:00:00Z }
name: reference-acme-ci-runner
description: "acme-widgets CI runs on the dedicated runner pool labelled widgets-ci (4 vCPU, 8 GB); re-check the label before relying on it, it changes with infra migrations"
metadata:
  node_type: memory
  type: reference
---

As of 2026-10-21, `acme-widgets` pipelines run on the **dedicated** runner pool with the
tag `widgets-ci`: 4 vCPU, 8 GB each, three runners, concurrency 1 per runner. A job without
that tag waits forever in `pending` because no shared runner accepts it.

This replaced the shared pool; see
[Acme CI Runner (legacy)](/reference-acme-ci-runner-legacy.md) for why it was retired.

**Why this carries `stale_after`.** Runner labels, sizes and counts change with every infra
migration. The session-start hook lists any memory past its `stale_after`; the move is to
re-check against the live CI settings, then either move the date forward (still true) or fix
the file (not true). Add `verified:` only if a human confirmed it.

Facts that age (versions, prices, addresses, who-owns-what, "currently") belong in a file
like this one, not in a project file.
