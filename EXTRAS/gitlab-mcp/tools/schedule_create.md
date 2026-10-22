# schedule_create

[Back to index](../README.md)

## Signature

```python
schedule_create(project='', description, ref, cron, cron_timezone='UTC', active=True, variables='', force=False, repo='', instance='')
```

Create a pipeline schedule — the write that makes a repeating job actually repeat. `description` names it, `ref` is the branch or tag it runs from, `cron` is a five-field line ('0 3 * * *') or a macro ('@daily'), `cron_timezone` defaults to UTC, and `active=False` creates it paused. THE REF IS VALIDATED, and this is the point of the tool. A schedule whose ref does not exist, or which carries no CI config file, is REFUSED — that schedule fails silently on a cadence nobody is watching, which is exactly how #129's mirror schedule was lost when its feature branch died at the merge.

A ref that is not the DEFAULT branch is a warning, not a refusal: it is legitimate as often as it is a mistake, and the report says which branch it should probably be. `force=True` writes anyway and labels what it went past. IDEMPOTENT: a schedule with the same `description` is reported and reused rather than duplicated — GitLab creates a second one happily, and two nightly mirrors that both fire is a state nobody notices until the log is doubled.

Any field that DIFFERS is named, with schedule_update as the way to change it. `variables` sets THE SCHEDULE'S OWN variables — one 'KEY=value' per line. They are the only thing that tells two schedules on one project apart from inside .gitlab-ci.yml: GitLab exposes no predefined variable naming which schedule fired a pipeline, so `rules:` can only key on a variable the schedule sets.

Not to be confused with ci_variable_set, which writes PROJECT variables that apply to every pipeline. THE VALUES ARE NEVER PRINTED — the report names keys. GitLab's create endpoint does not accept them inline, so they are written immediately after the schedule; if that second write fails the schedule EXISTS WITHOUT THEM and the report says so loudly, because a schedule missing the variable its rules key on runs the wrong jobs rather than none.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

VALIDATES THE REF, which is the point. A ref that does not exist, or carries no CI config file, is refused: that schedule fails silently on a cadence nobody is watching, which is how #129's mirror schedule was lost when its feature branch died at the merge. A ref that is not the DEFAULT branch is a warning, not a refusal. Idempotent on the description — two nightly mirrors that both fire is a state nobody notices until the log is doubled.

`variables` sets THE SCHEDULE'S OWN — the only thing .gitlab-ci.yml rules can use to tell two schedules apart, since GitLab names no schedule in a pipeline's variables. Written as a SECOND request (the create endpoint takes none inline), and a failure there leaves the schedule existing without them, which the report shouts about.

## Example

```python
schedule_create('root/gitlab-mcp', description='live suite', ref='master', cron='0 5 * * *', variables='RUN_LIVE=1')
```

## Required

`description`, `ref`, `cron`
