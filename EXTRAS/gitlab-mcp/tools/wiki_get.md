# wiki_get

[Back to index](../README.md)

## Signature

```python
wiki_get(project, slug, full=False, instance='')
```

Show one wiki page's raw content. `slug` is the page slug from wiki_list; a TITLE with spaces is accepted too (retried as its slug, 'Getting Started' -> 'Getting-Started'). Returns a `# slug=... chars=N` header line, a blank line, then the content verbatim.

## Required

`project`, `slug`
