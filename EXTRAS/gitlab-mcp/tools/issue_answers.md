# issue_answers

[Back to index](../README.md)

## Signature

```python
issue_answers(project='', iid, format='text', full=False, repo='', instance='')
```

Read an issue's '## Open questions' block back as DATA — the other half of issue_ask, and how a dispatcher learns whether a blocked issue can move. Returns one row per question: number, text, kind, and state. A yes/no question is `yes`, `no`, `unanswered` (neither box ticked) or `contradictory` (BOTH ticked — a contradiction, not a coin flip). A long-form one is `answered` or `unanswered`, and an answered one carries the comments posted after that question's round rather than the whole thread.

An issue with no questions block says so explicitly — that is a different answer from 'every question is answered'. Comment bodies are clipped; full=True returns them whole. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

The other half of issue_ask. BOTH boxes ticked reads as `contradictory`, not as a coin flip. A long-form question is `answered`/`unanswered` and carries the comments posted after ITS round, not the whole thread — a question with no round marker says so rather than pretending.

## Example

```python
issue_answers('root/gitlab-mcp', iid=42)
```

## Required

`iid`
