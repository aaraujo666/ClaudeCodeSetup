# project_attribute_set

[Back to index](../README.md)

## Signature

```python
project_attribute_set(project, key, value, instance='')
```

Set one project CUSTOM ATTRIBUTE — the write behind #190's per-project opt-in (`project_attribute_set('root/X', 'typesafe_decision_check', 'on')`). CONVERGES: the current value is read first, so a second identical call reports 'no change' and writes nothing, and changing a value reports old -> new. An empty `value` is refused — that is project_attribute_delete. ADMIN-ONLY: a non-admin token is refused by GitLab and the report names the token, not the project.

## Required

`project`, `key`, `value`
