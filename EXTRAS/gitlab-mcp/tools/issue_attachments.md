# issue_attachments

[Back to index](../README.md)

## Signature

```python
issue_attachments(project='', iid=0, repo='', format='text', full=False, instance='')
```

List what an issue CARRIES as attachments — the /uploads/ links in its description AND in its comments, resolved to the upload ids that can actually be fetched. The pairing read for download_attachment: the links are otherwise findable only by reading the issue text, and upload_attachment posts its markdown as a COMMENT, so most attachments are not in the description at all. A link whose file is not in this project's uploads is listed as MISSING rather than dropped — deleted, or uploaded to a different project — which is a different answer from an issue that carries nothing.

Reads take `repo=` (a checkout path) in place of `project`.
