# pipeline_show

[Back to index](../README.md)

## Signature

```python
pipeline_show(project='', pipeline_id, full=False, format='text', repo='', instance='')
```

Show ONE pipeline in full: its ref, SHA, status, source, who triggered it, duration and web URL — then EVERY JOB under it with its stage, status, duration and THE RUNNER THAT RAN IT. That last column is the point. No listing carries it: /pipelines has no jobs, and the runner lives on the individual job — so 'which runner executed this' cannot be answered without joining two endpoints, which is what this does.

A job with no runner (skipped, created, still queued) shows '-', and that is information: it means nothing ever picked the job up. Long job lists are clipped with a count — full=True for the rest. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

The only read that says WHICH RUNNER ran a job: /pipelines has no jobs and the runner lives on the individual job, so the answer needs two endpoints joined. A job with no runner ('-') was never picked up by one.

## Example

```python
pipeline_show('root/gitlab-mcp', pipeline_id=28)
```

## Required

`pipeline_id`
