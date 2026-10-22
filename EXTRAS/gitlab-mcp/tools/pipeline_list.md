# pipeline_list

[Back to index](../README.md)

## Signature

```python
pipeline_list(project='', ref='', status='', since='', limit=20, durations=False, format='text', repo='', sha='', instance='')
```

List a project's CI pipelines — the 'did it run, and did it pass' read. Returns `id ref sha status source created` per pipeline, newest first, with a tally by status. `ref` filters to one branch or tag; `status` to one of created, waiting_for_resource, preparing, pending, running, success, failed, canceled, canceling, skipped, manual, scheduled (validated locally). `since` takes 'today', 'yesterday', 'week', 'month', '7d' or an ISO date — the same LOCAL half-open vocabulary as the reporting reads, echoed back resolved.

`sha` filters to the pipelines of one commit (full SHA). `limit` caps the rows (default 20). `durations=True` adds a duration column, at the cost of ONE EXTRA REQUEST PER PIPELINE: the list payload does not carry it, and pipeline_show has it for free on a single pipeline. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

`since` is applied to created_at locally: the endpoint only filters on updated_after, which a re-run moves. durations=True costs one extra request PER pipeline.

## Example

```python
pipeline_list('root/gitlab-mcp', ref='master', since='week')
```
