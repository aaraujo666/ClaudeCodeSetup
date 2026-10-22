---
type: User
title: User Profile
tags: [profile]
status: stable
generated: { by: claude-code/example, at: 2026-10-21T09:00:00Z }
name: user-profile
description: "Sam Rivera (a fictional user): backend developer on acme-widgets, 12 years of Python, prefers direct answers with numbers"
metadata:
  node_type: memory
  type: user
---

Sam Rivera is a backend developer who owns the `acme-widgets` service
([acme-widgets](/project-acme-widgets.md)). Twelve years of Python, some Go, comfortable
with Postgres internals, newer to Kubernetes.

**Working style.** Wants the conclusion first, then the evidence. Numbers over adjectives:
"p95 went from 480 ms to 190 ms", not "much faster". Short bullets beat paragraphs. Dislikes
being agreed with to be polite; would rather be told a plan is wrong.

**What to assume.** Knows the codebase better than you do on day one; do not explain Python
basics. Does not know the CI internals ([Acme CI Runner](/reference-acme-ci-runner.md)), so
explain those when they matter.

This is a sample file. Replace it with facts about yourself, the user the model is working
for, so each new session starts with the right tone and level.
