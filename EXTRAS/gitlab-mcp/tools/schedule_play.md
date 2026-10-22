# schedule_play

[Back to index](../README.md)

## Signature

```python
schedule_play(project='', schedule_id, repo='', instance='')
```

Run a pipeline schedule NOW, without waiting for its cron — the 'does this thing actually work' call, and the way a schedule gets tested on the day it is created rather than discovered broken a week later. NOT IDEMPOTENT, and it cannot be: every call starts another pipeline. That is stated in the report rather than papered over. The schedule is read first, so a PAUSED one is named — GitLab plays a paused schedule quite happily, and a pipeline that ran once by hand is the least useful evidence that a paused schedule is working.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

NOT IDEMPOTENT and cannot be — every call starts another pipeline, and the report says so. A PAUSED schedule is named: GitLab plays one happily, and a pipeline run once by hand is the least useful evidence that a paused schedule works.

## Example

```python
schedule_play('root/gitlab-mcp', schedule_id=5)
```

## Required

`schedule_id`
