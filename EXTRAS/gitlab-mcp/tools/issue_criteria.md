# issue_criteria

[Back to index](../README.md)

## Signature

```python
issue_criteria(project, iid, criteria, instance='')
```

Write acceptance criteria onto an issue — the append-only write for the one section grooming authors, where issue_update(description=…) would replace the whole description. `criteria` is one criterion per line, each written as an unticked checkbox; a leading '-' or '- [ ] ' is tolerated. APPEND-ONLY: the rest of the description comes back BYTE-IDENTICAL, which is what makes this safe on an issue carrying an '## Open questions' block — that block's '<!-- asked: -->' and '<!-- next: N -->' marks are invisible in rendered markdown, and a description round-tripped through a paraphrase loses them silently, letting the next issue_ask reuse a question number.

Three shapes: no section, and one is appended at the end; an EMPTY section (what a template leaves behind, and what the gate reads as absent), and it is FILLED rather than joined by a second one — the gate matches the first heading it finds; a NON-EMPTY section, which is left exactly as it is and REPORTED, never merged and never overwritten. That last one is also how a second identical call converges.

No status move: the criteria make the issue eligible for status::ready, and issue_ready still checks it.

## Convention

The append-only write for the acceptance-criteria section — the one grooming authors, and the one the ready gate reads. The rest of the description comes back BYTE-IDENTICAL, which is what makes it safe where issue_update(description=…) loses the questions block's invisible round markers. An EMPTY section is FILLED, never joined by a second one the gate would not look at; a NON-EMPTY one is left alone and reported, which is also how a re-run converges.

No status move: issue_ready still checks. To REVISE criteria already there: issue_criteria_list, then issue_criteria_replace.

## Example

```python
issue_criteria('root/gitlab-mcp', 42, criteria='the section is appended, never replaced\na second identical call converges')
```

## Required

`project`, `iid`, `criteria`
