# issue_show

[Back to index](../README.md)

## Signature

```python
issue_show(project='', iid, full=False, comments=10, system=False, format='text', repo='', instance='')
```

Show one issue in full: title, state, labels, related issues, description, and every non-system comment. The on-demand interrogation path for backlog/status. `comments=0` means no cap (every comment, chronological); `system=True` interleaves GitLab's system notes (label/state changes, mentions), each marked `system`. `format` is text (default), toon or json — the machine formats carry the issue as a head record, its description, and its comments as rows, unclipped.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

Clips the description and shows the newest comments only; full=True for everything; comments=0 shows every comment, chronological; system=True interleaves the system notes.

## Required

`iid`
