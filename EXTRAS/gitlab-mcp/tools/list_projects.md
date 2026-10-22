# list_projects

[Back to index](../README.md)

## Signature

```python
list_projects(search='', membership=True, format='text', instance='')
```

List projects as `id path_with_namespace N open`. `search` filters by name/path; membership=True (default) limits to projects the token's user belongs to. Use this to discover the `project` argument the other tools take. instance='*' sweeps EVERY configured GitLab and prefixes each row with the instance it came from — the one tool that does, since a project ref is only unambiguous once you know which instance it is on.

## Example

```python
list_projects(instance='*')   # every configured GitLab, each row labelled with the instance it is on
```
