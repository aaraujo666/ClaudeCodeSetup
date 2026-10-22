# issue_scoped_set

[Back to index](../README.md)

## Signature

```python
issue_scoped_set(project, iid, labels, allow_new=False, instance='')
```

Set any scoped labels on an issue in ONE call, each displacing the labels sharing its prefix. `labels` is a comma-separated list of fully-qualified scoped labels, e.g. 'type::bug,priority::high,status::in-progress'. Same guarantees as issue_status (single request, no duplicate prefixes, scheme validation, allow_new=True to bypass). Use issue_status for the common status-only move; use this to fix a type/priority or change several at once.

Deliberately does NOT enforce the legal status:: transitions — this is the repair path, and a repair tool that can only reach reachable states is not a repair tool. Use issue_status for an ordinary status move; it checks.

## Required

`project`, `iid`, `labels`
