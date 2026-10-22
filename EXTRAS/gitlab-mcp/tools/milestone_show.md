# milestone_show

[Back to index](../README.md)

## Signature

```python
milestone_show(project='', milestone, format='text', repo='', instance='')
```

Show one milestone in full: id, iid, title, state, start and due dates, updated_at, and the WHOLE description — never clipped, because a milestone description is used as a working document (root/acme-widgets M1 keeps its entire implementation order there, ~36 KB) and a clipped read handed to milestone_update would silently truncate it. `milestone` is its TITLE or numeric id, resolved the way milestone_close resolves one.

The description's UTF-8 byte length and sha256 are reported alongside it, and `updated_at` is the value to pass milestone_update as `expected_updated_at`, so an edit made by another session in between is refused rather than overwritten. `format` is text (default), toon or json. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

The WHOLE description, never clipped, with its byte length, sha256 and updated_at — the read milestone_update's expected_updated_at comes from.

## Example

```python
milestone_show('root/acme-widgets', milestone='19')
```

## Required

`milestone`
