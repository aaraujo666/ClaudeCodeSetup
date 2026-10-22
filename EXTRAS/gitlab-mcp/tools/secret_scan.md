# secret_scan

[Back to index](../README.md)

## Signature

```python
secret_scan(project='', ref='', history=False, commits=100, max_files=300, full=False, format='text', repo='', instance='')
```

Scan a project's committed files for CREDENTIALS — GitLab PATs (glpat-), AWS keys, PEM private key blocks, PRIVATE-TOKEN headers, and password assignments — plus the literals known to be in circulation on this LAN, which are matched by SHA-256 HASH from ~/.config/gitlab-mcp/known-secrets.json and are not stored in this tool. `project='*'` sweeps every project the token can see.

THE MATCHED VALUE IS NEVER ECHOED. A finding is `file:line rule where commit age (N chars)` — the length distinguishes a real value from a placeholder, and a length is not a secret. By default it reads the WORKING TREE at `ref` (default: the default branch) through the Repository Files API — one request per file, capped by `max_files` (300), and a PARTIAL scan says so rather than reading as a clean one. history=True adds the opt-in second pass over the last `commits` (100) commits' diffs, scanning ADDED lines only: that is the half that matters, since removing a line does not remove the secret from the history, but it costs a request per commit.

An assignment whose value is an environment lookup, a variable or a placeholder is NOT counted, and the number declined is reported — a rule that fires on every correct `password = os.environ[...]` is a rule people learn to skim past. An inline `secret-scan: ignore` on the line stands the scan down for it. Ends on PASS or `[FAIL] N finding(s)`, so a shell `&&` reads it. A clean scan is stated explicitly, and 'nothing matched' is worded differently from 'there was nothing to scan' — an empty report otherwise reads exactly like one that failed to run.

`repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.

## Convention

NEVER echoes a matched value — a report that quotes the credential is a second copy of it. The known LAN literals are matched by SHA-256 hash from ~/.config/gitlab-mcp/known-secrets.json and are not stored in the tool; no file is a note, not an error. HEAD is the default and history=True is the opt-in second pass — removing a line does not remove the secret. release_check blocks on it, and a scan that could not RUN blocks too: 'not checked' is not 'clean'.

## Example

```python
secret_scan('*')   # every project at HEAD; history=True for the pass that matters
```
