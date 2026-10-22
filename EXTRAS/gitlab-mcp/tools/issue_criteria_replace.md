# issue_criteria_replace

[Back to index](../README.md)

## Signature

```python
issue_criteria_replace(project, iid, criteria, digest, instance='')
```

REPLACE an issue's acceptance criteria with a full new set — the way to REVISE criteria that already exist, which issue_criteria (append-only) never does. `criteria` is one criterion per line; `digest` is REQUIRED and comes from issue_criteria_list. A digest that no longer matches the section means somebody edited it since that read, and the call is REFUSED (stale_digest), writing nothing.

Allowed only on status::backlog and status::blocked. Refused (criteria_locked) on ready, in-progress and review — work was promoted, locked or proposed against the current definition of done — with a hint naming the legal route back. A CLOSED issue is refused. One PUT. Only the section body changes: the rest of the description comes back BYTE-IDENTICAL, questions-block markers included.

A criterion identical to one already TICKED keeps its tick; every other one is written unticked, and the report names each ticked criterion the new set removed. No section: one is created; an empty one: filled, exactly as issue_criteria does. A second identical call reports no change and writes nothing. No status move — issue_ready re-checks.

## Convention

The way to REVISE criteria, never a comment the gate cannot read. Needs the digest issue_criteria_list returned — stale_digest if the section moved since. Only on backlog / blocked: criteria_locked elsewhere, hint naming the legal route. Ticks survive on unchanged criteria; a removed tick is reported.

## Example

```python
issue_criteria_replace('root/gitlab-mcp', 42, criteria='the whole new set\none per line', digest='3f9a1c0b7d2e')
```

## Required

`project`, `iid`, `criteria`, `digest`
