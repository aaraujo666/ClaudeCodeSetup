# schedule_list

[Back to index](../README.md)

## Signature

```python
schedule_list(project='', limit=20, full=False, variables=False, format='text', repo='', instance='')
```

List a project's pipeline schedules: `id description ref cron tz active next run owner`. The read that answers 'is anything actually running on a cadence, and from where' — and the one that makes a PAUSED schedule visible, since a paused schedule and a missing one look identical from the outside. Tallied by active, with its denominator. `limit` caps the rows (default 20); full=True lifts the cap.

`variables=True` adds each schedule's variable KEYS — never their values — at the cost of ONE EXTRA REQUEST PER SCHEDULE: the list payload does not carry them and only the per-schedule read does, the same trade `pipeline_list` makes for `durations`. Worth asking for when a scheduled job is running the wrong work, since a schedule that lost the variable its rules key on looks identical to one that never had it.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

`variables=True` adds each schedule's variable KEYS (never values) at ONE EXTRA REQUEST PER SCHEDULE — the listing payload does not carry them. Worth it when a scheduled job runs the wrong work: a schedule that lost its flag looks exactly like one that never had it.

## Example

```python
schedule_list('root/gitlab-mcp', variables=True)
```
