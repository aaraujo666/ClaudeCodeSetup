# mr_update

[Back to index](../README.md)

## Signature

```python
mr_update(project='', iid, title=None, description=None, draft=None, repo='', instance='')
```

Edit an OPEN merge request's title, description and draft state in place. Only the fields you pass change: None means leave it alone, and `description=''` is a real value that clears the body. An empty `title` is refused — GitLab requires one. Passing nothing is refused. `draft=True` ensures the title starts with 'Draft: '; `draft=False` strips a leading Draft:/[Draft]/(Draft) marker.

With `draft` alone the CURRENT title is the one adjusted. The marker is expressed on the title because that is how it is done on this GitLab, exactly as mr_create does. REFUSES a closing keyword (Closes, Fixes, Resolves, IMPLEMENTING, and every inflection) followed by an issue reference in the new title or description — the same check and message as mr_create, made before anything is read or written.

REFUSES a merged or closed MR, naming its state. The description is READ BACK with a second GET after the write, and the report says whether it round-tripped byte-for-byte; a mismatch names both lengths and the first differing offset, never the body. IDEMPOTENT: a second identical call finds nothing to change, reports 'no change' and makes no PUT. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

Edits an OPEN MR in place; only the fields passed change (`description=''` clears the body, a blank `title` is refused). REFUSES a closing keyword in the new title/description, exactly as mr_create does, and a merged or closed MR, naming its state. `draft=True/False` adds or strips the Draft: marker on the title. The description is READ BACK after the write and the report says whether it round-tripped byte-for-byte.

A repeat call reports 'no change' and makes no PUT.

## Example

```python
mr_update('root/gitlab-mcp', iid=9, description='…the new body…')
```

## Required

`iid`
