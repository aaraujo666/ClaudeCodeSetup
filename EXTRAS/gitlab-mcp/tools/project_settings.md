# project_settings

[Back to index](../README.md)

## Signature

```python
project_settings(project='', branch='', format='text', repo='', instance='')
```

Read a project's merge-request-adjacent SETTINGS as one table: the default branch, whether it is protected and by which rule, whether force-push is allowed on it, who may push and merge, the merge method, the squash option, whether the source branch is deleted on merge, the two merge preconditions (green pipeline, resolved discussions), and the required-approval count. The layer under branch_list and mr_create, and until now a browser trip into Settings > Repository.

THREE STATES, KEPT APART. A value is a setting that was read; `unavailable` means the field is not on this GitLab's EDITION, which is a different fact from `no` or `0` — required approvals and code-owner approval are EE, and CE reports them as unavailable rather than as zero. `?` means THAT READ FAILED, and the failures are named under the table. Nothing here gates on `/version`'s `enterprise` flag: that is a build flag, not a licence, so a field's presence is the only evidence there is.

PROTECTION IS MATCHED BY WILDCARD, the way GitLab matches it — a rule named `*` protects the trunk, and an exact-name rule wins over a wildcard where both apply. The row names the rule doing the protecting, since `protected by *` and `protected by master` are different settings to change. Rules covering other refs are listed under the table. An UNPROTECTED trunk reports force push as `yes (unprotected)` — because it is.

The project's CUSTOM ATTRIBUTES (#191) — which GitLab shows nowhere — follow as their own section (`none` when there are none, `?` when the admin-only read was refused), and ride under `custom_attributes` in toon/json; project_attribute_set / project_attribute_delete change them. `branch` reads the protection of a branch other than the default one. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.
