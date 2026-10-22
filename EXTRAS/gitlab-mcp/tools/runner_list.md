# runner_list

[Back to index](../README.md)

## Signature

```python
runner_list(scope='instance', project='', group='', details=True, limit=20, format='text', repo='', instance='')
```

List the CI runners: `id description type online last-contact tags`. `scope` is 'instance' (every runner on the instance — needs an admin token), 'project' (the runners available to `project`) or 'group' (to `group`, an id or path). ONLINE comes from GitLab's own `online` field, deliberately. `contacted_at` is NOT a heartbeat — GitLab throttles that write, so an idle but perfectly healthy runner can sit 30+ minutes stale; a listing that derived liveness from it would be confidently wrong.

It is shown as last contact, and means only that. `details=False` skips the per-runner request that fetches tags and last contact (the list payload carries neither), leaving the id/description/online columns. `repo` supplies `project` from a checkout's .gitlab-tools.json.

## Convention

ONLINE is GitLab's own field. `contacted_at` is NOT a heartbeat — GitLab throttles the write, so an idle healthy runner sits 30+ minutes stale; never read staleness as down.

## Example

```python
runner_list(scope='instance')
```
