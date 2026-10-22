# tracker_export

[Back to index](../README.md)

## Signature

```python
tracker_export(path, project='', notes=True, links=True, attachments=False, format='text', full=False, repo='', instance='')
```

Export a project's WHOLE issue tracker to JSON on disk — descriptions, labels, time totals, comments (system notes included) and issue relations, at state='all', plus the project's CUSTOM ATTRIBUTES (#191) under `custom_attributes` — a map, `{}` when there are none, and an admin-only read that fails the export rather than writing an empty map. `project='*'` exports EVERY project the token can see, one file per project, INCLUDING projects with no issues (an attribute-only project is still backed up); `path` is a directory (or a .json file for a single project).

ATTACHMENTS ARE OPT-IN (#95): `attachments=True` fetches every referenced /uploads/ file into a `<name>-attachments/` directory beside the JSON and records it per issue; without it the links are carried and the files are not, and the file and the report both say which. Time is TOTALS: GitLab's REST API exposes no per-entry timelog list, and that history survives only in the system notes. tracker_import reads these files back; the pair round-trips on issue count, labels and time totals.

Re-running overwrites a file it wrote before, and refuses one belonging to a different project or instance.

## Convention

The tracker is the record of WHY things were done, and it is not reproducible from the code — this is the only thing that gets it off the VM. Two omissions, both stated in the file and the report rather than left to be inferred: ATTACHMENTS are not exported (#95), and time is TOTALS, since GitLab exposes no per-entry timelog list — that history survives only in the system notes, which is why those are exported too.

## Example

```python
tracker_export(path='D:/backup/gitlab', project='*')   # one JSON file per project
```

## Required

`path`
