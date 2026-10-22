# project_protect

[Back to index](../README.md)

## Signature

```python
project_protect(project='', branch='', push='maintainer', merge='maintainer', allow_force=False, repo='', instance='')
```

Protect a branch — the write half of the settings surface, and the one that makes branch_delete's protected refusal mean something. `branch` defaults to the project's DEFAULT BRANCH, read from the API rather than guessed between main and master. `push` and `merge` take a WORD (noone, developer, maintainer, admin), not GitLab's 0/30/40/60, and both default to 'maintainer'. `allow_force` defaults to False, which is the whole point: an unprotected trunk can be force-pushed, and every git convention in this workspace assumes history is stable.

IDEMPOTENT: a rule that already matches reports 'no change' and writes nothing. A rule that differs is UPDATED, and how depends on what moved — `allow_force` alone goes through PATCH and is atomic, while an ACCESS LEVEL change is a DELETE and a POST, because on CE the levels cannot be patched. The branch is unprotected between those two calls, the report says so, and a failed re-protect is reported as UNPROTECTED NOW with the call that repairs it — never as a failed update.

A branch already covered only by a WILDCARD rule (`*`, `release/*`) gets its own exact-name rule, and the report names the wildcard that also covers it. The exact rule is what GitLab resolves first, and it is the one a later change here acts on. THERE IS NO UNPROTECT. branch_delete refuses a protected branch with no force and sends you to Settings > Repository precisely because protection is a decision somebody made; a tool that could lift it from here would turn that refusal into two calls and no decision.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.
