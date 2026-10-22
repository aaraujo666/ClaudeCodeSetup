# gitlab_help

[Back to index](../README.md)

## Signature

```python
gitlab_help(topic='')
```

Concise reference for this server's own tools. No argument: one line per tool grouped by area, plus the standing rules that decide whether a call is correct (one type::/one status:: per issue, CE has no scoped-label exclusion, issue_close is a five-step protocol with a required `spend`, time means estimated skilled-dev effort, a close syncs the wiki). With a tool name: its signature with defaults, its description, the convention governing it, and a worked example.

Generated from the registered tool metadata, so it cannot drift from the signatures. Call this before guessing at an argument, and instead of reading docs/CONVENTIONS.md mid-task.
