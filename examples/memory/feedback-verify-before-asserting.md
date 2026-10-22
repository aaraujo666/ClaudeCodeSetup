---
type: Feedback
title: Verify Before Asserting
tags: [working-rules]
status: stable
verified: { by: human:sam, at: 2026-10-21T09:05:00Z }
generated: { by: claude-code/example, at: 2026-10-21T09:00:00Z }
name: feedback-verify-before-asserting
description: "Check the repo or the live system before stating a fact or asking Sam a question; never answer from memory when the answer is one command away"
metadata:
  node_type: memory
  type: feedback
---

Before stating a fact about the code or the environment, or asking Sam a question, look for
the answer: read the file, run the command, check the config. Ask only when the answer is
genuinely not recoverable from the machine.

**Why:** Sam has been burned by confident answers that were true of an older version of the
service. A wrong assertion costs a debugging session; a lazy question costs Sam a context
switch to look up something Claude could have read. Both come out worse than a one-line
check.

**How to apply:** when about to write "the service uses X" or "which database is it?", run
the grep or open the config first and cite what was found (`path:line`). When the check
turns up nothing, say what was checked and then ask. When a memory says a fact is stale
(see the markers in `MEMORY.md`), re-check it before repeating it.
