# wiki_list

[Back to index](../README.md)

## Signature

```python
wiki_list(project, format='text', instance='')
```

List a project's wiki pages as `slug format chars title` (the slug is what `wiki_get` takes; the title is what a sync's filename stem became). Read-only — the counterpart to wiki_sync, for checking what is actually published. `format` is text (default), toon or json. Note the collision: the ARGUMENT selects the rendering, while each row's `format` column is the wiki page's own markup (markdown, rdoc, …) — GitLab's field name, kept rather than renamed.

## Required

`project`
