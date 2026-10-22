# download_attachment

[Back to index](../README.md)

## Signature

```python
download_attachment(project='', iid=0, url='', dest='', upload_id=0, repo='', format='text', full=False, instance='')
```

Download an issue's attachments to local files, so `Read` can open a render or a screenshot a previous session attached. `iid` fetches every attachment on that issue into `dest` (a directory); `url` fetches ONE — the /uploads/… link out of the issue text, or the whole markdown snippet — and `dest` may then be a file path. `upload_id` names an upload outright, which is the way past a duplicate filename.

It never fetches the /uploads/ path itself: that is served outside the API, ignores PRIVATE-TOKEN, and answers the SIGN-IN PAGE with an HTTP 200 — so a naive fetch writes an HTML login form to disk and calls it a render. The bytes come from the API's upload endpoint instead. Idempotent: a file already on disk with the same bytes is reported `unchanged` and not rewritten. A link whose file is not in this project's uploads is reported MISSING, which is distinct from an issue that carries no attachments at all.
