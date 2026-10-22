# project_create

[Back to index](../README.md)

## Signature

```python
project_create(name, path='', description='', visibility='private', namespace='', initialize_with_readme=False, apply_labels=True, record=True, record_spend='', repo='', scaffold='none', decision_check='', instance='')
```

Create a new GitLab project. `name` is required; `path` (the URL slug) defaults to a slugified name. `namespace` (id or path, e.g. a group) defaults to the token user's namespace (root). `visibility` is private|internal|public (default private). Set initialize_with_readme=True to seed a first commit (leave False to push an existing local repo). apply_labels=True (default) rolls out the canonical type::/status::/priority:: scheme onto the new project.

Returns the new id, path_with_namespace, and clone URL. record=True (default) also files the standing INITIAL-BUILD RECORD: a type::chore issue describing the work the project arrived with, closed through the full protocol so the project's history and time_report start from the real number. `record_spend` is that build's estimated SKILLED-DEV EFFORT ('4h', '2d') — omitted, the issue is still filed and closed, and the report says loudly that no time was logged rather than inventing a plausible default.

`repo` (a checkout of the new project) is REQUIRED for the record, whose close syncs the wiki like any other (#131) — without one the record is SKIPPED and the report says how to file it. scaffold='none' (default) | 'python-mcp' | 'mod' | 'docs' also SEEDS THE REPOSITORY through the Repository Files API — no clone: a .gitlab-tools.json naming the new project, a README stub, a docs/ page for the wiki, and a kind-appropriate .gitignore, then `project_protect` on the default branch.

It NEVER overwrites: a file already there is reported as `no change`, and the report names every file one line each. 'none' leaves today's behaviour byte-identical. `decision_check` is REQUIRED: 'on' or 'off' — whether this project opts in to the semantic decision check (#190), which sends each issue's title and description to TypeSafe's Jev from issue_ready / issue_create / issue_update.

Omitted or anything else is REFUSED (bad_argument) before the project is created, the way issue_close refuses an empty `spend` — every new project gets asked. 'on' sets the custom attribute typesafe_decision_check=on after the create; 'off' sets nothing. A failed attribute write is reported as FAILED with the project left created and the project_attribute_set call that repairs it.

## Convention

`decision_check` is REQUIRED ('on' | 'off') and refused before the create POST when missing — every new project is asked whether its issue text may go to TypeSafe for the semantic decision check. 'on' sets the custom attribute typesafe_decision_check=on after the create; a failed write is FAILED with the repairing project_attribute_set named.

## Example

```python
project_create('My MCP', scaffold='python-mcp', record_spend='4h', repo='C:/path/to/checkout', decision_check='off')
```

## Required

`name`
