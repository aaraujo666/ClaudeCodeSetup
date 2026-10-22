# issue_decide

[Back to index](../README.md)

## Signature

```python
issue_decide(project, iid, decision, heading='', instance='')
```

Record a decision that HAS been settled onto an issue — the append-only write for the escape #139 named and never gave a tool. Appends a '## DECISION' section (or '## AMENDMENT' once one is there), which is what the readiness gate reads as a decision RECORDED rather than one stated as prose, so an issue refused with `prose_decision` can be answered in place instead of rewritten.

APPEND-ONLY: the rest of the description comes back BYTE-IDENTICAL. That is the whole point — the alternative is issue_update(description=…), which replaces the description and silently eats the '<!-- asked: -->' and '<!-- next: N -->' marks of an '## Open questions' block, letting the next issue_ask reuse a question number. A settled decision is exactly what an issue carrying that block is most likely to be recording.

`heading` picks the section by name — DECISION, AMENDMENT, DECIDED or RESOLVED, the four the gate honours, and anything else is REFUSED because it would write a section the gate cannot see. Left empty it is chosen: DECISION first, AMENDMENT after. Converges — a second call recording the same text reports no change rather than appending a twin, while a genuinely new amendment goes through.

No status move: the decision makes the issue eligible for status::ready, and issue_ready still checks it.

## Convention

The append-only write for a decision that HAS been settled — the escape #139 named and never gave a tool. Appends a '## DECISION' section (or '## AMENDMENT' once one is there), which is what the ready gate reads as a decision RECORDED rather than stated as prose, so an issue refused with prose_decision is answered in place instead of rewritten. Rest of the description BYTE-IDENTICAL.

An off-list heading is REFUSED — it would write a section the gate cannot see. Converges on the same text; a new amendment goes through. No status move. An UNMADE decision is an issue_ask, not this.

## Example

```python
issue_decide('root/gitlab-mcp', 42, decision='The check lives in its own tool rather than in gitlab_audit, which touches no GitLab by design.')
```

## Required

`project`, `iid`, `decision`
