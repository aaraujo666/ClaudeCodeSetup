# issue_time

[Back to index](../README.md)

## Signature

```python
issue_time(project='', iid, format='text', repo='', instance='')
```

Show an issue's time estimate and total spent (read). `format` is text (default), toon or json — the machine formats carry a `time` record with both the human durations and the raw SECONDS, which is the form worth summing. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Required

`iid`
