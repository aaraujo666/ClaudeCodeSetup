# project_attribute_list

[Back to index](../README.md)

## Signature

```python
project_attribute_list(project='', key='', value='', format='text', repo='', instance='')
```

List a project's CUSTOM ATTRIBUTES — the key/value pairs GitLab stores on a project and shows nowhere (CE has no UI for them, only the API). #190's per-project opt-in (`typesafe_decision_check = on`) is one. Returns every key and value; `key` narrows to one. `project='*'` returns ONE ROW PER PROJECT that carries any attribute. With `key` AND `value` it uses GitLab's own `?custom_attributes[key]=value` filter — one request, and the projects it excluded are not counted, so no denominator is claimed.

With `key` alone (or nothing) every project is listed and read, since the filter cannot match a key without a value; the count then states how many projects were read. ADMIN-ONLY: GitLab refuses custom attributes to a non-admin token, and that refusal is reported as one — naming the token — never as 'no attributes'. `repo` (path to a checkout) supplies `project` from that repo's .gitlab-tools.json; an explicit `project` wins.
