# milestone_update

[Back to index](../README.md)

## Signature

```python
milestone_update(project='', milestone, description=None, title=None, due_date=None, state=None, expected_updated_at='', force=False, repo='', instance='')
```

Write a milestone's description, title, due date and/or state. Only the fields PASSED are written: an omitted field is left alone, and an EMPTY STRING clears it (description='' blanks the description, due_date='' removes the due date; title='' is refused). `due_date` takes 'today', 'week', '7d' or an ISO date. `state` is 'active' or 'closed'. `milestone` is the TITLE or numeric id.

`expected_updated_at` is the `updated_at` milestone_show returned. When given, the write is REFUSED (stale_milestone) if the milestone changed since that read, naming both timestamps — two sessions editing one ordering document must not silently overwrite each other. Pass it on every edit of a description somebody else may be editing too. READ BACK: after the write the milestone is fetched again and the stored description's byte length and sha256 are reported next to what was sent; a mismatch is an ERROR (readback_mismatch), never a quiet success.

The new `updated_at` is reported so the next edit can chain on it. A rename onto a title another milestone already has is REFUSED — two milestones with one title is the state milestone_create exists to prevent. state='closed' carries milestone_close's check: REFUSED while issues are still open on it unless force=True. IDEMPOTENT: when every passed field already holds that value nothing is written and the report says 'no change'.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

Writes only the fields passed ('' clears one). expected_updated_at REFUSES a write over an edit you did not see; the stored description is read back and a length/sha256 mismatch is an error. state='closed' keeps milestone_close's open-issue refusal.

## Example

```python
milestone_update('root/acme-widgets', milestone='19', description=text, expected_updated_at=shown_updated_at)
```

## Required

`milestone`
