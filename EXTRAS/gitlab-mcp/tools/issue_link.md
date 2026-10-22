# issue_link

[Back to index](../README.md)

## Signature

```python
issue_link(project, iid, commit='', mr='', relation='Related to', body='', close=False, instance='')
```

Cross-reference a commit and/or MR from an issue via a note (GitLab links them automatically). `close=True` adds a BARE state flip — no time logged, no status:: move — so use issue_close for finished work and keep this for linking.

## Required

`project`, `iid`
