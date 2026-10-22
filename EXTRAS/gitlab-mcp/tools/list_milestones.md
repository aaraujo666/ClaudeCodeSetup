# list_milestones

[Back to index](../README.md)

## Signature

```python
list_milestones(project='', state='active', format='text', repo='', instance='')
```

List a project's milestones. state is active|closed|all (default active). Returns `id iid state title (due)` per milestone. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.
