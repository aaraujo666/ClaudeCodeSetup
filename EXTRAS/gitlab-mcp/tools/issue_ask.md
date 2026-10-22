# issue_ask

[Back to index](../README.md)

## Signature

```python
issue_ask(project, iid, questions, force=False, allow_new=False, instance='')
```

Record questions on an issue and BLOCK it, in one call — what an agent does when dispatched work turns out to be underspecified, instead of guessing. `questions` is one question per line; each is written as a yes/no checkbox pair so it can be answered by ticking a box in the GitLab UI, and a line prefixed 'open:' becomes a single 'Answered below' box for a question that needs a paragraph (the answer then arrives as a comment).

A leading '-' bullet is tolerated. APPEND-ONLY: the questions join a single '## Open questions' section and the rest of the description is returned verbatim — existing ticks, hand edits and reworded questions all survive. Question numbers continue from the highest ever used and are NEVER reused, so a comment answering 'Q3' cannot come to mean a different Q3. The move to status::blocked happens in the same call: the two acts never come apart, and the questions ARE the block's stated reason, so nothing else has to be passed.

Legal from backlog and ready as well as in-progress, and needs no force for it (#109) — an issue's AUTHOR asks on work nobody started, which is when questions are normally written; grooming asks only on a RELATED issue its round destabilized, never on the one it is grooming. Read the answers back with issue_answers.

## Convention

Questions go in the DESCRIPTION as checkboxes, so they can be answered by ticking a box in the UI and read back as data. APPEND-ONLY — existing ticks and hand edits survive every later round — and numbers are never reused. The move to status::blocked happens in the same call; the questions are written FIRST, so a failed move leaves the message intact.

## Example

```python
issue_ask('root/gitlab-mcp', 42, questions='Should the poll interval be configurable per block?\nopen: What should happen when the partner grid has no mod loaded?')
```

## Required

`project`, `iid`, `questions`
