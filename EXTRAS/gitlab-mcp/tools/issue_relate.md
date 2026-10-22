# issue_relate

[Back to index](../README.md)

## Signature

```python
issue_relate(project, iid, to, link_type='relates_to', instance='')
```

Link one issue to others (issue-to-issue relation). `to` is a comma-separated list of targets, each '12', '#12' or 'root/OtherProject#12' — a QUALIFIED target links ACROSS projects, which is the shape most dependencies here have since CE has no epics to hold them; a bare iid still means this project. link_type is relates_to (everywhere) or blocks/is_blocked_by (DIRECTED, and Premium-only — on Free/CE the create is refused and the report says so in words rather than passing back a bare 400).

Note that `enterprise` in /version is a build flag and not a licence, so an unlicensed -ee instance reports it true and still cannot make a directed link. Read the relations back with issue_graph.

## Required

`project`, `iid`, `to`
