# issue_ready

[Back to index](../README.md)

## Signature

```python
issue_ready(project, iid, force=False, allow_new=False, check=False, instance='')
```

Promote an issue into status::ready — the ONLY blessed way in, because `ready` is the label a dispatcher acts on with no human in the loop. Moves backlog / blocked / review -> ready, and REFUSES when the promise cannot be true: the issue carries type::story (a decision, not delegable work), the '## Open questions' block holds an unanswered question, a yes/no question has BOTH boxes ticked, the description states an unmade decision as PROSE ('## What has to be decided', '## What has to be settled', '## The tradeoff') or as an either/or acceptance criterion ('- [ ] Or, …', '… either X, or Y') instead of asking it, or the description has no acceptance-criteria section.

Each refusal carries its own code and a hint naming the next move, and ALL of them are reported at once rather than one round trip at a time. The prose-decision refusal is the one that catches an issue written BEFORE the check existed — issue_create and issue_update refuse it at the point of writing, and this refuses it on promotion. Its escapes are content-shaped, not a flag: an '## Open questions' block anywhere clears it, and so does a heading recording the decision as DECISION / AMENDMENT / DECIDED / RESOLVED (uppercase).

The label is checked, not trusted: an issue somebody already flipped to status::ready by hand is validated too, and refused if it does not hold up. Idempotent — an already-ready issue that passes reports 'no change' and writes nothing. force=True skips the CONTENT checks only; it never skips the label mechanics, and never skips the transition check (use issue_status(force=True) to repair an issue stuck in a wrong state).

A CLOSED issue is refused, not reopened. check=True is the DRY RUN: it answers 'would this be promoted, and if not why' and writes NOTHING — same guards, same checks, same codes, no label move. It exists so grooming can judge a backlog against the definition of ready without promoting anything on its own initiative, and so that judgement runs the same code the gate does rather than a second copy of the rules that is free to drift. check with force=True is refused: force skips the very checks check reports.

SEMANTIC DECISION CHECK (#190), ADVISORY: on a project whose custom attribute `typesafe_decision_check` is exactly `on`, the title and the description (fully answered '## Open questions' blocks removed) are sent to TypeSafe's Jev (jev-1.13.0), which answers how likely the text leaves a choice between approaches open. p >= 0.65 is reported as a likely unmade decision, 0.35 < p < 0.65 as unsure for a human read, lower as nothing; each with code `semantic_decision`, the probability and the cost.

It NEVER refuses and never blocks a promotion, in check mode or not. Off, one line says `semantic_decision: not enabled for <project>`. A missing key, timeout or bad answer SKIPS it and says so — never a silent 'clean'. DEPENDS-ON CHECK (#197), ADVISORY, same opt-in: every OTHER open issue of the project the description mentions as #N but neither '## Depends on' nor an inline '**Depends on:**' marker lists is put to Jev (one question each, one request per issue) — does the text say that issue must be merged first? p >= 0.8 is reported as `depends_on_missing: #N mentions #M as needed first`, with the cost; add it under '## Depends on' if true.

No such mention, no call. The same work-marker screen as the grooming pre-sort applies: a marker in the issue or a candidate's title withholds it. It NEVER refuses, never edits the issue, and a failed read or call is a SKIPPED line, never a refusal.

## Convention

The ONLY blessed way into status::ready, because `ready` is what a dispatcher acts on with no human in the loop. Refuses a story, an unanswered or contradictory question, or a description with no acceptance criteria — ALL the reasons at once, not one round trip each. Validates an issue somebody already flipped by hand: the label is checked, not trusted. force=True skips the CONTENT checks only.

On a project whose custom attribute typesafe_decision_check is `on`, Jev also reads the issue for an unmade decision the shape checks cannot see (`semantic_decision`, #190) — ADVISORY, with its probability and cost, never a refusal; off, it prints one `not enabled` line. issue_create / issue_update run the same check silently-when-off.

## Example

```python
issue_ready('root/gitlab-mcp', 42)
```

## Required

`project`, `iid`
