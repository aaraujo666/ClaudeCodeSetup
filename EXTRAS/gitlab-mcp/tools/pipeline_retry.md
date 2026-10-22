# pipeline_retry

[Back to index](../README.md)

## Signature

```python
pipeline_retry(project='', pipeline_id=0, job_id=0, repo='', instance='')
```

Retry failed CI work. Pass exactly ONE of `pipeline_id` and `job_id`. `pipeline_id` retries that pipeline's failed jobs IN PLACE — the pipeline keeps its id, so that is the id to follow (pipeline_show). `job_id` retries one job, and GitLab answers with a NEW job under a NEW id: the report names both, and the new id is the one to follow (job_log). A job that is still in flight or already succeeded is refused, with its state named — there is nothing to retry.

NOT IDEMPOTENT: every accepted call queues more work. A running pipeline is not pre-refused; GitLab's own answer is passed through. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

Exactly one of pipeline_id / job_id. A pipeline retry keeps its id; a JOB retry returns a NEW job id, and the report says which to follow. A running or successful job is refused.

## Example

```python
pipeline_retry('root/gitlab-mcp', job_id=97)
```
