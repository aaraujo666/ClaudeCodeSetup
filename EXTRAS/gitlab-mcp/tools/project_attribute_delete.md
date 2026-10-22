# project_attribute_delete

[Back to index](../README.md)

## Signature

```python
project_attribute_delete(project, key, instance='')
```

Delete one project CUSTOM ATTRIBUTE. CONVERGES: deleting a key that is not there reports that it was absent and SUCCEEDS — the state asked for already holds — rather than failing on GitLab's 404. The deleted value is named in the report, so it can be put back. ADMIN-ONLY, like the rest of the custom-attribute API.

## Required

`project`, `key`
