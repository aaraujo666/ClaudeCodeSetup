# project_retire

[Back to index](../README.md)

## Signature

```python
project_retire(project, successor='', hazard='', dry_run=True, full=False, format='text', instance='')
```

Retire a repository — the nine-step checklist as one call (#86). `hazard` is REQUIRED and `successor` is the project that replaces it (omit it for a project with no successor; the report says so rather than leaving a blank). DRY RUN BY DEFAULT. dry_run=True writes nothing and prints exactly what it would do; dry_run=False performs step 6 (revoke every project access token, deploy token, deploy key and webhook) and then step 7 (set the archived flag).

ARCHIVING IS THE LAST WRITE, and this refuses to do it early. An archived project is READ-ONLY, so steps 1-6 become impossible once the flag is set — the archive therefore runs after the revocations and only if every one of them succeeded. An inventory that could not be READ stops it too: a credential class nobody could list is not a clean project, it is an unchecked one. STEPS 5 AND 9 ARE REPORTED, never performed: every project on the instance is searched for references (repository files, and issue titles/descriptions), hits in CI configs and cron/systemd units are called out as SCHEDULED invocations, and the project's own files are excluded.

What the sweep cannot see — ~/.claude memory notes, CLAUDE.md files, anything off this GitLab — is named in the checklist rather than left implied. The remaining steps print as a checklist with `successor` and `hazard` substituted in, including the archive notice ready to paste. An ALREADY-ARCHIVED project is reported and does not error: the sweep and the checklist still run, and any credential still live on it is reported with the unarchive-revoke-re-archive recovery.

`project` is REQUIRED and there is no `repo=` shortcut, unlike the reads: this is the write whose mistake cannot be walked back, and letting a checkout's config name the project would let a session standing in the wrong directory archive the wrong one. The written checklist is docs/RETIREMENT.md, which reaches the wiki through wiki_sync.

## Required

`project`
