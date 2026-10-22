# schedule_update

[Back to index](../README.md)

## Signature

```python
schedule_update(project='', schedule_id, description='', ref='', cron='', cron_timezone='', active=None, variables='', remove_variables='', force=False, repo='', instance='')
```

Change a pipeline schedule. `schedule_id` is the id from schedule_list; every other argument is optional and an omitted one is LEFT ALONE — `active` is tri-state (None leaves it, True resumes, False pauses), so pausing a schedule does not require restating its cron. A new `ref` is validated exactly as schedule_create validates one: refused if it does not exist or carries no CI config, warned if it is not the default branch, and `force=True` writes past the refusal.

IDEMPOTENT — a call that would change nothing reports 'no change' and writes nothing. `variables` sets THE SCHEDULE'S OWN variables — one 'KEY=value' per line — and `remove_variables` deletes them by key (comma-separated), which is the repair path for a schedule whose flag is wrong. An OMITTED `variables` leaves every existing one alone, matching this tool's rule for every other field; a key already holding its value is skipped, so a re-run converges, and a key already gone is reported rather than treated as an error.

THE VALUES ARE NEVER PRINTED — the report names keys. The variables are written BEFORE the schedule fields: the variable decides WHICH jobs a run fires and the cron only decides when, so a schedule never starts running on a new cadence without the flag its rules key on. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

Every field is optional and an omitted one is LEFT ALONE; `active` is tri-state (None leaves it), so pausing a schedule does not mean restating its cron. A new ref is validated exactly as schedule_create validates one. `variables` / `remove_variables` write the schedule's own, BEFORE the schedule fields — a variable decides which jobs a run fires and the cron only when, so the cadence never moves ahead of the flag its rules key on.

## Example

```python
schedule_update('root/gitlab-mcp', schedule_id=5, active=False)   # pause it, cron untouched
```

## Required

`schedule_id`
