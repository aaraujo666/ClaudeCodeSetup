# issue_create

[Back to index](../README.md)

## Signature

```python
issue_create(project='', title='', labels='', description='', issues_json='', template='', dedup=True, dedup_scope='open', allow_new=False, repo='', instance='')
```

Create one or more issues in `project`. For a single issue pass title/labels/description; for a batch pass `issues_json` (a JSON array of {title, labels, description} objects) instead. `labels` is comma-separated (e.g. 'type::feature,status::backlog'). dedup=True (default) skips any title that EXACTLY matches an existing one; dedup_scope is 'open' (default — matches only open issues, so a recurring chore can be re-filed) or 'all' (also matches CLOSED issues, which is what catches a topic that was already dealt with).

Titles that merely RESEMBLE an existing issue are reported alongside the created issue and never skipped — a near match is for you to judge. EVERY issue gets exactly one type:: and one status:: label, enforced here rather than reported by release_check months later: `type::` is REQUIRED (feature|bug|story|chore — only you know which, and a guessed one is worse than an absent one), `status::` defaults to status::backlog, and two of either is refused.

Labels are validated against the scheme and the project's label set BEFORE anything is created — GitLab would otherwise silently create a typo'd label; allow_new=True bypasses THAT check, not the one-type-one-status rule. An UNMADE DECISION is REFUSED: a description carrying a decision-shaped heading ('## What has to be decided', '## What has to be settled', '## The tradeoff', '## Open decisions') — or an acceptance criterion that is an ALTERNATIVE to another, opening with Or / Alternatively or forking on 'either …, or' — with no '## Open questions' block is rejected before anything is created, because issue_ready reads only that block and a decision written as prose is invisible to it.

There is no force — the escapes are the CONTENT: ask it with issue_ask, or, if it is already settled, head that section DECISION / AMENDMENT / DECIDED / RESOLVED in uppercase. A HAND-WRITTEN questions block is likewise REFUSED: a '## Open questions' heading whose questions are not their own '### Qn — text' headings renders identically to a human but is invisible to issue_answers and issue_ready — write it with issue_ask instead.

`template='bug'` fills the body from the project's own '.gitlab/issue_templates/bug.md' (feature|bug|story|chore are what project_create(scaffold=…) seeds; a project may carry others). With no `description` the template is used verbatim; with one, it is PREPENDED and your text is kept byte for byte — unless the description already carries the template's '##' headings, in which case it is left alone and the result line says the template was skipped.

A template that is not on the project is an error (code: template_not_found) for the WHOLE batch before anything is created, never a silent skip. Templates are never ENFORCED and cannot certify an issue: their acceptance-criteria section ships empty, so issue_ready still refuses. A per-item "template" key inside issues_json displaces the argument for that item. `repo` (path to the repo checkout) supplies `project` and prepends `issues.default_labels` from its .gitlab-tools.json.

Returns a per-issue result line and a summary. On a project that opted in (custom attribute typesafe_decision_check=on) each CREATED issue is also read by TypeSafe's Jev for an unmade decision (`semantic_decision`, #190) — ADVISORY, reported after the summary with its probability and cost, never a refusal; silent when not opted in.

## Convention

dedup skips an EXACT title match (dedup_scope open|all). A title that merely resembles an existing one is reported, never skipped. type:: is REQUIRED and status:: defaults to status::backlog — the one-type-one-status rule is enforced at creation, and allow_new does not bypass it. `template=` is the opposite kind of rule and deliberately so: it fills the BODY from the project's .gitlab/issue_templates/<name>.md and is NEVER enforced — a template that refused an issue would stop issues being filed.

The four the scaffold seeds (feature, bug, story, chore) ship with an EMPTY acceptance-criteria section, so a templated issue is still refused by issue_ready until somebody fills it in.

## Example

```python
issue_create('root/gitlab-mcp', title='Fix X', labels='type::bug,status::backlog', template='bug')
```
