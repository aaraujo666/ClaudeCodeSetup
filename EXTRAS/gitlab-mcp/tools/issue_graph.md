# issue_graph

[Back to index](../README.md)

## Signature

```python
issue_graph(project='', root='', state='opened', format='text', full=False, repo='', instance='')
```

The issue RELATION graph, walked and rendered — what `issue_relate` writes and nothing read back. `project` is a project ref or '*'; `root` narrows it to the component around one issue ('94', '#94' or 'root/acme-widgets#12', which needs no `project` at all). Each connected component is drawn as a tree with every node's ref, stage and title. Cross-project links resolve and render with their project prefix — those are the dependencies this exists for, since CE has no epics to hold them.

Neighbours OUTSIDE the scope are walked too, which is what makes a component spanning four projects come back whole. DIRECTION IS NEVER INVENTED. On CE every link is `relates_to` and symmetric — the directed types are Premium and this instance refuses to create one — so a link says two issues are connected, not which waits on which. Where the payload does report a directed link_type it is used and the row says so; otherwise the two findings are read from the STATUS and the report says that in words: `->` orients an edge by which end is further along, `--` means both ends sit at the same stage and the order is arbitrary.

TWO FINDINGS. `waiting on work that is not started` — an open issue linked to one in status::backlog or status::ready, which is the dependency that stalls a dispatch. `linked to a CLOSED issue` — the dependency is satisfied and the link still reads as live, which is the case most worth seeing because nobody is told when a blocker closes. One row per link, never per ordered pair.

CYCLES are marked, not walked: the render builds a spanning tree per component and every edge that closes a loop is shown as `already shown` where it would have re-descended. Note that an undirected link cannot express a DEPENDENCY cycle — a loop here is a loop in the links. THREE ZEROS, deliberately different. `root=` naming an issue that does not exist is an error with a code; an issue that exists and carries no relations is a stated zero naming issue_relate; and a scope where nothing is linked at all is a third answer again.

COST: one request per node reached, bounded at 150 (full=True lifts it). `root=` walks outward from one issue and is cheap; the sweep is one request per issue in scope plus one per neighbour it drags in. A walk that hits the bound reports the nodes it did not expand rather than presenting a cut component as a whole one. `state` is opened|closed|all (default opened) and seeds the sweep only — a walk reaches a closed neighbour either way.

`repo` (path to a checkout) supplies `project`. `format=text|toon|json|mermaid`; mermaid comes back fenced, so it pastes into an issue description or a wiki page unedited.

## Convention

The read `issue_relate` never had. DIRECTION IS NEVER INVENTED: on CE every link is relates_to and SYMMETRIC, so a link says two issues are connected and not which waits on which — the two findings are read from the STATUS and the report says so (`->` oriented by stage, `--` for a tie, `(directed link)` where the relation itself said). A cycle is MARKED where it closes, never walked.

Three different zeros: a root that does not exist, a root with no relations, and a scope where nothing is linked. format='mermaid' comes back fenced, so it pastes into an issue or a wiki page unedited.

## Example

```python
issue_graph(root='root/acme-widgets#12')   # the component around one issue, across every project it reaches
```
