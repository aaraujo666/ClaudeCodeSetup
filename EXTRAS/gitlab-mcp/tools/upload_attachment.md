# upload_attachment

[Back to index](../README.md)

## Signature

```python
upload_attachment(project, path, iid=0, comment='', instance='')
```

Upload a local FILE to `project` and get back the markdown snippet that embeds it — for putting a render, screenshot, log excerpt or chart INTO an issue instead of describing it in prose. With `iid`, the snippet is posted straight into that issue as a comment (with `comment` as the accompanying text); without `iid` the file is stored and the snippet returned for you to paste, which leaves it referenced by nothing until you do.

The snippet is only valid inside the project it was uploaded to — the URL is relative and authorised per project, so pasting it into another project's issue renders as a broken link. Posting it into an issue also makes the FILENAME findable by issue_search, since the snippet is text in the issue. The file's contents stay unsearchable.

## Convention

An upload belongs to a PROJECT. Without `iid` the file is stored but attached to nothing.

## Example

```python
upload_attachment('root/gitlab-mcp', 'C:/tmp/chart.png', iid=19)
```

## Required

`project`, `path`
