# workspace_status

[Back to index](../README.md)

## Signature

```python
workspace_status(search='', membership=True, quiet='90d', full=False, format='text', instance='')
```

The health of the PROJECTS, not of the tracker — one row per project across the whole instance, so a fact like 'eighteen projects have no CI' is visible as a fact rather than as eighteen separate observations. `project_status('*')` answers the other question: where the BACKLOG stands. Each row carries the last COMMIT date and its age (not last_activity_at, which an issue comment moves), the default branch, whether that branch is PROTECTED (`prot`), whether a CI config is present and what its newest pipeline on that branch did, whether a README and a LICENSE are present, open and closed issue counts, the archived flag and the repository size.

Then tallies with their denominators: projects with no CI, no README, no LICENSE, no pipeline history, a pipeline that is not green, an UNPROTECTED default branch, and nothing committed since the `quiet` boundary. `prot` is matched the way GitLab matches protection — a rule named `*` protects the trunk — through the same helper project_settings and project_protect use. project_settings reads one project's protection in full (who may push and merge, whether force-push is allowed); project_protect sets it.

`decision check` is #190's per-project opt-in, the custom attribute `typesafe_decision_check`: `on` / `off`, read for the WHOLE sweep with ONE `?custom_attributes[...]=on` request. That API is admin-only, so if the request fails every row reads `?` (never `off`) and a note says why. project_attribute_set turns it on. ARCHIVED projects are rows, marked `(archived)` — not excluded.

That is the opposite of project_status, which keeps an archive out of its stale section on purpose; here a read-only project with no README is still worth seeing. A cell reading `?` means THAT READ FAILED and is a different answer from `no`; the failures are named under the table, and the row is still listed. A `-` means there was nothing to read — an empty repository. A project is never dropped from the listing for failing one of its reads.

`quiet` takes '90d' (the default), 'month', 'week' or an ISO date, resolved as a LOCAL boundary and echoed back resolved; quiet='' turns that tally off. `search` filters by name/path and membership=True (default) limits to projects the token's user belongs to — the same two filters as list_projects. COST: one paged listing plus two instance-wide issue tallies over REST, then the per-project reads (the project payload, the repository root, the newest commit, the newest pipeline, the protected-branch rules) as a GraphQL sweep — ONE query for all of them plus one per distinct default-branch name, where REST costs five requests per project.

Measured on this instance at 27 projects: 149 REST requests before, 14 REST plus 3 GraphQL after. GITLAB_GRAPHQL=0 pins it back to REST, and a query this instance's schema refuses falls back to REST with a note rather than failing. An empty repository pays for none of the repository reads either way. Bounded at 60 projects per call — full=True lifts it, and the number withheld is always reported rather than silently cut.

## Convention

The other half of project_status: that one reads the TRACKER, this one reads the PROJECTS — CI, README, LICENSE, last commit, last pipeline, size. `?` in a cell means that read FAILED and is not `no`; a project is never dropped for failing one. ARCHIVED projects are rows, not exclusions. Up to four requests per project.

## Example

```python
workspace_status()   # every project: CI, README, LICENSE, last commit, size
```
