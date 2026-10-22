# labels_ensure

[Back to index](../README.md)

## Signature

```python
labels_ensure(group='', project='', all_root=False, reconcile=False, instance='')
```

Idempotently create the canonical scoped-label scheme (type::/status::/priority::) on one or more scopes. `group` is a comma-separated list of group ids; `project` a comma-separated list of ids or 'namespace/path'; all_root=True targets every LIVE project under the root/ user namespace — archived projects are read-only in GitLab, so they are skipped and reported rather than 403ing the rollout (an explicitly named `project` is still attempted).

A label that EXISTS but whose colour or description disagrees with the scheme is reported as DIVERGENT rather than counted as skipped, and is only rewritten when reconcile=True — off by default, because a description edited deliberately on one project must not be overwritten by a wildcard rollout. Run this once when onboarding a new project.

## Convention

Idempotent. `all_root` skips archived projects (they are read-only) and reports them. A label that exists with the WRONG colour/description is DIVERGENT, not skipped, and is rewritten only with reconcile=True.
