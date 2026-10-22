# project_status

[Back to index](../README.md)

## Signature

```python
project_status(project='', stale='14d', full=False, format='text', repo='', instance='')
```

Where a project stands right now: how much is open, what is in flight, what is mislabelled and what has gone quiet — the read a session opens with. `project` is a project ref or '*' for every project the token can see, which adds a per-project table; grouping follows the scope, so there is nothing to choose. Returns open counts tallied by status::/type::/priority:: (each with its denominator), then four sections: ISSUES IN PROGRESS with their estimate and logged time, ISSUES IN REVIEW with the MERGE REQUEST each is waiting on and that MR's state, ISSUES MISSING a type:: or status:: label — which the tallies can only count, never name — and STALE issues untouched since the `stale` boundary, oldest first.

An empty section is omitted; a project with nothing to report says so rather than returning a bare header. A review row reading `no MR` is a STRAY: status::review means a merge request is open, not that a branch exists. `?` means the lookup did not run, which is a different answer. The MRs come from one listing per project holding a review row (a second only when a row is unmatched, to tell 'merged and never closed' from 'never had one') — never one request per row.

`stale` takes '14d' (the default), 'week', 'month', or an ISO date, resolved as a LOCAL boundary and echoed back resolved; stale='' turns the section off. Caveat worth knowing: GitLab's `updated_at` moves on ANY activity, so a comment or a label change resets the clock — 'untouched' means no activity, not no progress. A NAMED project's header states its DEFAULT BRANCH, read from the API — one constant extra request, and the answer half this toolchain otherwise guesses between main and master.

A '?' there means the read failed, not that the project has no trunk. Under '*' it is omitted: saying it would cost one request per project. One request per 100 open issues: every section reads the same sweep. Under '*' there is one more, asking which projects are ARCHIVED — an archived project is read-only and by definition untouched, so its issues are marked (archived) and kept out of the stale section rather than filling it.

A project with no open issues at all cannot appear under '*' — use list_projects, which counts every project including the quiet ones. instance='*' sweeps EVERY configured GitLab into one report and prefixes each ref and project with the instance it came from ('other:root/acme-widgets#3') — a project ref is only unambiguous once you know which instance it is on, and two GitLabs can both hold a root/ namespace.

An instance that could not be read is a NOTE on the report rather than the end of it, so a sweep that came back short says which half is missing instead of reading as a quiet backlog. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins. Under instance='*' the checkout fallback is not consulted — a checkout names a project on its OWN instance.

## Convention

The read to OPEN a session with. `updated_at` moves on any activity, so 'stale' means no activity, not no progress. A project with zero open issues cannot appear under '*' — list_projects counts the quiet ones.

## Example

```python
project_status('*', stale='week')
```
