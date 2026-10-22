# ci_variable_check

[Back to index](../README.md)

## Signature

```python
ci_variable_check(project='', key, sha256='', group='', scope='', environment_scope='*', format='text', repo='', instance='')
```

Is the stored CI/CD variable `key` the value you think it is? Pass the SHA-256 of that value (64 hex characters) as `sha256` and get back `match` or `no match`, the stored value's LENGTH, and its masked/protected flags — so a credential can be checked without the raw value ever travelling. **Neither the value nor its hash is returned, and the `sha256` you pass is not echoed back** — it is a hash of a secret.

A key that is not there is its own answer ('missing'), never `no match`; a failed read is an error, never `no match`. Target: `project` (or `repo`), `group` (an id or path), or `scope='instance'` — one of them; naming two is refused. `environment_scope` (default '*') picks between variables sharing a key; instance variables have none.

## Convention

Compares the stored value to a SHA-256 you pass and answers match / no match plus length and flags — never the value, never a hash. A missing key is its own answer, not 'no match'. Project, `group=` or `scope='instance'`.

## Example

```python
ci_variable_check(group='acme', key='DEPLOY_TOKEN', sha256='<sha256sum of the value>')
```

## Required

`key`
