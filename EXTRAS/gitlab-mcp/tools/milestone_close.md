# milestone_close

[Back to index](../README.md)

## Signature

```python
milestone_close(project='', milestone, reopen=False, force=False, full=False, repo='', instance='')
```

Retire a milestone — the other end of milestone_create, and the step that makes list_milestones(state='active') mean "still in flight" rather than "every milestone ever". `milestone` is its TITLE ('v1.4', 'M1 – Foundations') or numeric id, so a title nobody has is NAMED rather than returned as a 404. `reopen=True` re-activates one instead (GitLab's state_event='activate') — closing the wrong milestone should not need curl either.

REFUSES while issues are still OPEN on it, naming them, because that close is silent otherwise: the issues stay assigned and simply vanish from the active view, and nobody looks at a milestone they can no longer see. `force=True` closes anyway and says how many were left on it. The check does not apply to `reopen`, which can only ever make those issues more visible. IDEMPOTENT: a milestone already in the state being asked for reports 'no change' and writes nothing, the same way milestone_create handles a duplicate title.

`full=True` lists every open issue rather than the first 10. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

The other end of milestone_create, and what makes list_milestones(state='active') mean 'still in flight'. REFUSES while issues are still open on it, naming them (force=True closes anyway) — that close is silent otherwise: the issues stay assigned and vanish from the active view. reopen=True re-activates one.

## Example

```python
milestone_close('root/acme-docs', milestone='M1 – Foundations')
```

## Required

`milestone`
