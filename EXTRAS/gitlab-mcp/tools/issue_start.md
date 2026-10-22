# issue_start

[Back to index](../README.md)

## Signature

```python
issue_start(project, iid, estimate='', allow_new=False, instance='')
```

Start work on an issue: move it to status::in-progress and, with `estimate`, set its time estimate — one call for what is otherwise issue_status plus issue_estimate. The status move is the same one-request add-and-remove as issue_status (this is CE: adding status::in-progress does not remove status::backlog), and `estimate` is a GitLab duration ('2h', '1d', '1h30m') checked locally before anything is written.

A CLOSED issue is REOPENED first rather than refused — a closed issue carrying status::in-progress is the state this whole scheme exists to prevent — and the report says so on its own line. Idempotent: a second identical call reports 'no change' on the status and 'unchanged' on the estimate. Setting an estimate over a DIFFERENT one replaces it (GitLab's estimate is a set, not a total) and the report names the value it displaced.

Steps run in order and stop at the first failure.

## Convention

The bookend to issue_close: status move + estimate in one call. A CLOSED issue is REOPENED first — closed-and-in-progress is the state the scheme exists to prevent. The estimate SETS, so a repeat is idempotent and a different value is reported as a replacement.

## Example

```python
issue_start('root/gitlab-mcp', 42, estimate='2h')
```

## Required

`project`, `iid`
