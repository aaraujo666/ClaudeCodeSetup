# tag_show

[Back to index](../README.md)

## Signature

```python
tag_show(project='', tag, full=False, format='text', repo='', instance='')
```

Show ONE tag in full: the commit it points at (with that commit's author, date and subject), the tag's own annotation message, and its RELEASE NOTES if it carries any. `tag` is the name, exactly as tag_list prints it. This is how a version gets verified before it is quoted — the same job commit_show does for a SHA. A tag name in a changelog that the remote has never had reads exactly like one it has.

Long messages are clipped with a size hint; full=True returns the rest. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Required

`tag`
