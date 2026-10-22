# issue_spend

[Back to index](../README.md)

## Signature

```python
issue_spend(project, iid, duration, summary='', summary_overflow='refuse', instance='')
```

Log spent time on an issue (additive). duration like '45m' or '1h30m'; negative subtracts. `summary` (<=255 chars, a GitLab hard limit) records what was done; a longer one is refused locally, before anything is written — or, with `summary_overflow='comment'`, logged cut with the WHOLE text posted as a comment on the issue, so an over-long summary costs no re-wording.

## Convention

ADDITIVE and NOT idempotent — GitLab exposes no timelog list, so a duplicate cannot be detected. The report states the prior total so a double-log is visible rather than silent. A summary over 255 characters is refused before anything is written; summary_overflow='comment' logs a cut one and posts the whole text as a comment instead, so it costs no re-wording.

## Required

`project`, `iid`, `duration`
