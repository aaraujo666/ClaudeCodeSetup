# labels_list

[Back to index](../README.md)

## Signature

```python
labels_list(group='', project='', format='text', repo='', instance='')
```

List the scheme's labels on one scope (pass `group` id OR `project` id/path), showing which are present/divergent/missing plus any other labels not in the scheme. DIVERGENT means the label exists but its colour or description disagrees with the scheme; the row names which. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` — or a `group` — wins.
