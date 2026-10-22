# issue_criteria_list

[Back to index](../README.md)

## Signature

```python
issue_criteria_list(project='', iid, format='text', repo='', instance='')
```

Read an issue's acceptance criteria back as DATA — one row per checkbox (index, ticked, text) plus a DIGEST of the section body, which issue_criteria_replace requires. Says explicitly when there is no section or an empty one, and counts any non-checkbox line in the section, since a replace does not carry those over. `format` is text (default), toon or json. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Example

```python
issue_criteria_list('root/gitlab-mcp', iid=42)
```

## Required

`iid`
