---
type: Reference
title: Acme CI Runner (legacy)
tags: [ci, acme-widgets]
status: deprecated
generated: { by: claude-code/example, at: 2026-10-21T09:10:00Z }
name: reference-acme-ci-runner-legacy
description: "DEPRECATED: acme-widgets used the shared runner pool until 2026-09; superseded by the dedicated pool in reference-acme-ci-runner"
metadata:
  node_type: memory
  type: reference
---

**Superseded by [Acme CI Runner](/reference-acme-ci-runner.md).** Kept as history, not as
guidance: if this file disagrees with the current one, the current one wins.

Until 2026-09, `acme-widgets` pipelines ran on the shared pool tagged `shared`. Builds queued
behind other teams (median wait 7 minutes) and the 2 GB limit killed the integration suite
about once a week, which is why the project moved to a dedicated pool.

A fact is superseded by setting `status: deprecated` and linking to its replacement, not by
deleting the file. The `[deprecated]` marker on its `MEMORY.md` line tells a future session
to treat it as history.
