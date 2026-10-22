# schedule_delete

[Back to index](../README.md)

## Signature

```python
schedule_delete(project='', schedule_id, repo='', instance='')
```

Delete a pipeline schedule. `schedule_id` is the id from schedule_list. IDEMPOTENT: an id that is already gone reports 'no change' rather than a 404, so a repeated delete does not look like a fault. The schedule is read first so the report can name WHAT was deleted — an id alone is not something anyone can check afterwards. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Required

`schedule_id`
