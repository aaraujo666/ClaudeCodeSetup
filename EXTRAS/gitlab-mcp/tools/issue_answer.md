# issue_answer

[Back to index](../README.md)

## Signature

```python
issue_answer(project, iid, answers, instance='')
```

Answer an issue's open questions — the write that was missing from the ask/answer loop, and the only one that does not need the GitLab UI. `answers` is one per line: 'Q1: yes' or 'Q1: no' for a yes/no question, 'Q2: <the paragraph>' for a long-form one. A line that does NOT open with a question number continues the answer above it, so a multi-line answer works. A yes/no answer ticks its box.

A long-form answer POSTS THE TEXT AS A COMMENT and then ticks 'Answered below' — the prose goes down first, so a tick never outlives the answer it claims. The description is otherwise returned byte-identical: one '[ ]' becomes '[x]' and the invisible round markers survive, which is what makes this safe where issue_update(description=…) is not. A question written BY HAND — a '### Qn — text' heading with no checkbox and no '<!-- asked: -->' marker, which issue_answers reads and issue_ready blocks on — is ADOPTED on first answer: the missing box and marker are spliced into that question alone, then ticked, in the same call.

Nothing else moves (every other question, an asked: stamp already there, the '<!-- next: N -->' mark and the whole description outside the block all come back byte-identical), and the report names the row it adopted, because that row gained a line rather than a character. An adopted question is long-form: a heading with no boxes carries nothing that could say it was yes/no. Two or more boxes somebody reworded by hand are still REFUSED — which of them the answer means is a question only a human can settle, in the UI.

It TICKS and SPLICES, never unticks: an already-answered question is REPORTED and skipped, never overwritten, so a re-run converges. The status is not moved — answering the last question makes the issue eligible for issue_ready, which still checks it.

## Convention

The write that closes the loop: the ONLY step in it that used to need the GitLab UI. A yes/no answer ticks its box; a long-form one POSTS THE PROSE AS A COMMENT and then ticks, in that order, so a tick never outlives the answer it claims. It TICKS, NEVER UNTICKS — an already-answered question is reported and skipped, so a re-run converges — and the description is otherwise byte-identical, which is what makes this safe where issue_update(description=…) loses the invisible round markers.

No status move: issue_ready still checks.

## Example

```python
issue_answer('root/gitlab-mcp', 42, answers='Q1: yes\nQ2: it falls back to the vanilla behaviour and logs once')
```

## Required

`project`, `iid`, `answers`
