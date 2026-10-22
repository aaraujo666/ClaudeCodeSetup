# pipeline_run

[Back to index](../README.md)

## Signature

```python
pipeline_run(project='', ref, variables='', repo='', instance='')
```

Start a pipeline on a branch or tag NOW — the way to run CI against a ref without pushing to it. `ref` is required. `variables` is one 'KEY=value' per line and sets variables for THIS pipeline only; the report names the KEYS that were passed and never the values. NOT IDEMPOTENT, and it cannot be: every call starts another pipeline. The report names the new pipeline's id, so pipeline_show(pipeline_id=N) can follow it.

A ref with no CI config is refused by GitLab and the refusal is passed through. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

NOT IDEMPOTENT — every call starts another pipeline. `variables` is one KEY=value per line; the report names the KEYS and never the values.

## Example

```python
pipeline_run('root/gitlab-mcp', ref='master', variables='RUN_LIVE=1')
```

## Required

`ref`
