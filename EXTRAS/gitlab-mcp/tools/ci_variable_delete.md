# ci_variable_delete

[Back to index](../README.md)

## Signature

```python
ci_variable_delete(project='', key, environment_scope='*', group='', repo='', instance='')
```

Delete a project CI/CD variable. `key` and `environment_scope` (default '*') together identify it — a variable is keyed on both, so deleting 'PATH' without naming the scope could otherwise take the wrong one. IDEMPOTENT: a key that is not there reports 'no change' rather than a 404. A delete run twice is an ordinary thing to do after a failed first attempt, and the second run should not look like a fault.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Example

```python
ci_variable_delete('root/gitlab-mcp', key='MIRROR_SOURCE')
```

## Required

`key`
