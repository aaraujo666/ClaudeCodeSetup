# wiki_sync

[Back to index](../README.md)

## Signature

```python
wiki_sync(project='', dir='', title='', prune=None, index=True, repo='', dry_run=False, instance='')
```

Mirror a docs directory to `project`'s wiki. `dir` is an ABSOLUTE path; each .txt (Steam BBCode -> Markdown) or .md (passthrough) file becomes one page (title = filename stem); files starting with '_' are skipped. Order comes from a '_wiki_order.txt' in the dir if present, else alphabetical. index=True (default) also writes a 'home' table-of-contents + '_sidebar'. prune=True deletes wiki pages with no backing source file (home/_sidebar never pruned).

Idempotent — safe to re-run every release. dry_run=True writes NOTHING and reports the diff instead: create/update/same per page, plus orphans. PREFER `repo` (path to the repo checkout): project/dir/title/prune then come from its .gitlab-tools.json, which is what the repo actually declares — arguments you pass still win, so pass none of them unless you mean to override. `prune` is unset by default (null), NOT false: pass it only to override a declared value.

## Convention

Idempotent — safe every release. dry_run=True writes nothing and reports the diff instead.

## Example

```python
wiki_sync(repo='C:/path/to/checkout', dry_run=True)
```
