# issue_list

[Back to index](../README.md)

## Signature

```python
issue_list(project='', state='opened', labels='', closed_after='', closed_before='', created_after='', updated_after='', with_time=False, limit=200, format='text', repo='', milestone='', iids='', bodies=False, instance='')
```

List issues. `project` is a project ref, or '*' for EVERY project the token can see (instance-wide, project-qualified refs in the output). state is opened|closed|all (default opened); `labels` is an optional comma-separated filter. Date windows: `closed_after` / `closed_before` / `created_after` / `updated_after` each take 'today', 'yesterday', 'week', 'month', '7d', or an ISO date/datetime.

Boundaries are LOCAL time and windows are half-open — closed_after='today' is 'since local midnight', and closed_after='2026-08-14' + closed_before='2026-08-15' is exactly that day. GitLab has no closed_after of its own, so the window is applied to `closed_at` here (over-fetching on updated_after, which is sound: closing an issue updates it). Passing a close window with the default state switches it to closed. with_time=True adds each issue's logged time and a total — free, from the list payload, rather than one issue_time call per row.

Paging is handled internally. Returns one line per issue: #iid state [spend] title [labels] (milestone). `milestone` filters by milestone TITLE or numeric id ('none' = issues on no milestone). A milestone the project does not have is REFUSED by name, never answered with an empty list. With project='*' a title filters instance-wide and an id is refused, since ids are per-project.

Without the filter, each row names its milestone. `iids` is issue_bulk's syntax — '12,14-16' — and lists exactly those issues in one request; a requested iid that does not exist is named by number. bodies=True adds each issue's full description, in text and in the machine formats — one call in place of an issue_show per issue. Every filter combines with the others, and the echoed filters name the ones applied.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json, so a session standing in the working copy need not know the ref; an explicit `project` wins.

## Convention

project='*' reads every project. Date windows are LOCAL and half-open. Capped at `limit` rows; a cut result says so. milestone= takes a title or id ('none' = no milestone; an unknown one is refused by name); iids='12,14-16' reads a known set, naming any that do not exist; bodies=True adds each description.

## Example

```python
issue_list('*', state='closed', closed_after='today', with_time=True)
```
