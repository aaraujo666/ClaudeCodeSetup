# ci_variable_set

[Back to index](../README.md)

## Signature

```python
ci_variable_set(project='', key, value, masked=False, protected=False, raw=False, environment_scope='*', variable_type='env_var', description='', group='', repo='', instance='')
```

Create or update a project (or, with `group=`, a group) CI/CD variable — the write half of the CI surface. `key` is letters/digits/underscores; `value` is the secret. `masked=True` hides it in job logs, `protected=True` restricts it to protected branches and tags, `raw=True` stops GitLab expanding `$OTHER` references inside it, `variable_type` is 'env_var' or 'file', and `environment_scope` defaults to '*' (a variable is keyed on KEY **and** scope, so 'PATH' can exist for '*' and again for 'production').

MASKING IS VALIDATED BEFORE THE WRITE. GitLab accepts `masked=true` on a value it cannot actually mask in some versions, and the runner then prints the token in full — so a value that is under 8 characters, carries whitespace or a line break, or uses characters outside the maskable alphabet (A-Z a-z 0-9 + / = @ : . ~) is REFUSED with every reason named and NOTHING WRITTEN. The value is never quoted back, not even to say which character is the problem — those are counted.

IDEMPOTENT: an existing key is UPDATED rather than 400ing on the duplicate, and a call whose value and flags already match reports 'no change' and writes nothing. THE VALUE NEVER APPEARS IN THE REPORT — a change says which fields moved, by name, and no more. `group` (an id or path) targets a group's variables instead of a project's; naming both is refused and nothing is written.

A group's environment scope is a Premium feature — on CE every group variable is '*'. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

VALIDATES MASKING BEFORE THE WRITE. GitLab accepts masked=true on a value it cannot mask in some versions and the runner then prints the token in full, so a value under 8 characters, carrying whitespace, or outside the maskable alphabet is REFUSED with every reason named and nothing written. Idempotent: an existing key is UPDATED, not 400ed as a duplicate, and an identical call reports 'no change'.

THE VALUE IS NEVER PRINTED — a change names the FIELDS that moved, and not even a masking refusal quotes the offending characters. `group=` writes a GROUP variable instead (naming a project too is refused).

## Example

```python
ci_variable_set('root/gitlab-mcp', key='GITHUB_TOKEN', value='<a classic PAT>', masked=True, protected=True)
```

## Required

`key`, `value`
