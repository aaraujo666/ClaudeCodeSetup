# tracker_import

[Back to index](../README.md)

## Signature

```python
tracker_import(path, project, dry_run=False, notes=True, links=True, attachments=True, instance='')
```

Recreate a tracker_export file's issues in a project — the half that makes the export a backup rather than a comfort. Preserves iids (an admin/owner field, so every `#79` in a commit message or wiki page still points at the same issue), labels, milestones, created_at, state, time totals and relations. CUSTOM ATTRIBUTES (#191): every key the export carries is SET on the target, each key whose value there differed is reported old -> new, and keys the export does not carry are left untouched; a re-run sets nothing.

An export written before #191 has no `custom_attributes` and touches none. dry_run=True lists the changes without writing. A refused (colliding) import writes no attribute either. REFUSES only on a COLLIDING iid — one the file wants that the destination already holds — and NAMES them (#150). A destination with its own history that collides nowhere restores fine, which is the case a real migration turns up.

That is still what makes a second identical call a no-op rather than a duplicate tracker: after a restore every iid is taken, and the refusal says so. dry_run=True REPORTS the collisions and returns the plan instead of raising, so a migration can be checked before the destination is touched. ATTACHMENTS ARE RE-UPLOADED (#158) when the export carries them (tracker_export's attachments=True): each referenced file is re-uploaded from the export's `-attachments/` directory and every /uploads/ link in the description and comments is rewritten to the new secret, PER ISSUE and all-or-nothing — one file that cannot be re-uploaded means that issue is SKIPPED and named, never created half-rewritten.

Pass attachments=False to restore the issues without re-uploading (the export's links then point at the source instance, same as an export written without attachments=True). dry_run=True reports the upload plan and the byte total, before anything is written. project_create(..., record=False) is still the clean path for a fresh destination — the initial-build record it files by default would occupy iid 1 — but it is no longer the only one.

NOTE: a project with `github.source` configured is a MOVING TARGET; github_sync re-files a deleted mirror row at a fresh iid, so deleting a mirrored issue frees its slot without unsubscribing it, and the slot can be taken again before the import reaches it. What it still CANNOT recreate, and reports: comment authorship (the original author and time are written into the body instead), SYSTEM notes — so a migrated tracker cannot answer 'when did this go to status::ready', which work_queue's stranded-age reads — closed_at, attachments an export never fetched (the report NAMES the issues carrying them so you know what to re-upload by hand), and relations pointing outside the file.

## Convention

What makes the export a backup instead of a comfort: an export nobody has restored is a hope. Targets an EMPTY project and refuses a populated one, which is also its idempotence — a second identical call cannot double the tracker. iids are PRESERVED (an admin/owner field), because every `#79` in a commit message and wiki page depends on it, and any drift is reported per issue rather than discovered later.

## Example

```python
tracker_import(path='D:/backup/gitlab/root-gitlab-mcp.json', project='root/gitlab-mcp-restored', dry_run=True)
```

## Required

`path`, `project`
