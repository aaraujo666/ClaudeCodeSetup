# issue_estimate

[Back to index](../README.md)

## Signature

```python
issue_estimate(project, iid, duration, instance='')
```

Set the time estimate on an issue. duration like '2h' or '1d'. This SETS the estimate (unlike issue_spend, which adds), so a repeat is idempotent. When the estimate is being set because work is starting, use issue_start — one call does this and the status move.

## Required

`project`, `iid`, `duration`
