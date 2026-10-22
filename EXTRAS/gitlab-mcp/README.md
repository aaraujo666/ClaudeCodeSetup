# gitlab-mcp: self-documenting help, exported

This is the help output of the gitlab-mcp server, the MCP server I use to run the issue
workflow described in [the issue workflow doc](../../docs/04-issue-workflow.md). It is
published as reference material, not as a product: it shows how a server that carries a
workflow documents itself. See [EXTRAS](../../docs/14-extras.md) for why.

The server generates this text from its registered tool metadata (`gitlab_help()` for
the overview, `gitlab_help('<tool>')` for one tool), so it cannot drift from the tool
signatures. I exported it with a script and sanitized it: hosts, project names and local
paths are replaced with generic stand-ins such as `root/acme-widgets` and the phrase
"your GitLab host".

Issue references such as `(#190)` in the text refer to the tool's own private tracker.
They are left in because they show how each rule traces back to a decision, but you
cannot follow them.

There are 100 tools. Below: the standing rules, the status loop and the conventions
every tool shares (from `gitlab_help()`), then the tools by area. Each tool links to its
own page.

## Standing rules

1. Every issue carries exactly ONE type:: and ONE status:: label (priority:: optional). issue_create ENFORCES it: type:: is required, status:: defaults to status::backlog.
2. This is GitLab CE: scoped labels are NOT auto-exclusive. Use issue_status / issue_scoped_set, which add AND remove in one call.
3. issue_close runs the WHOLE protocol — cross-reference the MR, log time, terminal status::, close, sync the wiki — and `spend` ('0' to opt out) and `repo` are BOTH REQUIRED. `mr`, like commit/spend/summary/repo, comes from the handoff.
4. Logged time is ESTIMATED SKILLED-DEV EFFORT for the work, never clock hours or session length.
5. A close is not finished until the wiki is synced, so issue_close REFUSES without a repo=. Omitted, it comes from the handoff, then the checkout registry; with none of the three, the close writes nothing.
6. status:: is a STATE MACHINE, and issue_status / issue_bulk refuse illegal moves. status::ready means 'implementable by a session with no conversation history' and is reached only through issue_ready, which checks it. status::review means A MERGE REQUEST IS OPEN, not that a branch exists — issue_handoff records mr=, and work_queue / project_status show a review row with no MR as a stray. When dispatched work is underspecified, issue_ask — never a guess.

## The loop

Review, ready, work, review. The owner decides what is ready and what is done; an agent
owns only started, stuck and finished.

| From | To | Tool | When |
|---|---|---|---|
| `backlog` | `ready` | `issue_ready` | the owner reviewed it |
| `backlog` | `in-progress` | `issue_start` | hand-started, not delegated |
| `ready` | `in-progress` | `issue_start` | agent took the DISPATCH LOCK |
| `*` | `blocked` | `issue_ask` | agent is stuck; asks, never guesses |
| `in-progress` | `review` | `issue_handoff` | agent finished; an MR is OPEN |
| `blocked` | `ready` | `issue_ready` | the owner answered |
| `blocked` | `backlog` | `issue_status` | answered; was asked at write time |
| `review` | `ready` | `issue_ready` | the owner wants rework |
| `review` | `done` | `issue_close` | the owner said close it |
| `*` | `moved` | `issue_move` | filed in the wrong project |

- AGENTS NEVER CLOSE, MERGE OR APPROVE. The owner owns ready/done; an agent owns only started / stuck / finished.
- blocked = waiting on the owner to ANSWER. review = waiting on the owner to READ.
- issue_ask writes yes/no as TWO boxes: one box cannot tell 'no' from 'not read yet', and both ticked is `contradictory`, never a coin flip.
- issue_handoff PROPOSES the spend and never logs it; issue_close is the only thing that writes time, and sources spend/summary/commit/mr/repo from it.
- in-progress is the lock, so a stranded issue is a run in flight or a run that died — work_queue reports strays and nothing auto-picks one up.

## Across every tool

- Reads take format=text|toon|json — the default is unchanged, and TOON is accepted on batch inputs too (detected from content, no flag).
- Long output is clipped with a size hint and a `full` escape hatch.
- List reads carry counts by status/type/priority, each stating its denominator.
- A zero result is stated explicitly and echoes the query, including the resolved date window.
- Errors carry `code:` and `hint:` lines under the message.
- instance='<name>' addresses another configured GitLab (~/.config/gitlab-mcp/instances.json); omitted, it is the one this server is registered against. list_projects(instance='*') sweeps them all and labels each row — a project ref is ambiguous without its instance.

## Tool index

### issues

| Tool | Summary |
|---|---|
| [issue_create](tools/issue_create.md) | Create one or more issues in `project`. |
| [issue_update](tools/issue_update.md) | Update an issue's fields/labels. |
| [issue_start](tools/issue_start.md) | Start work on an issue: move it to status::in-progress and, with `estimate`, set its time estimate — one call for what is otherwise issue_status plus issue_estimate. |
| [issue_status](tools/issue_status.md) | Move an issue to a workflow status in ONE call — the correct way to change status on this CE instance, which has no scoped-label auto-exclusion. |
| [issue_scoped_set](tools/issue_scoped_set.md) | Set any scoped labels on an issue in ONE call, each displacing the labels sharing its prefix. |
| [issue_move](tools/issue_move.md) | Move an issue to another project, preserving its discussion and its logged time — over GitLab's own `POST /issues/:iid/move`. |
| [issue_bulk](tools/issue_bulk.md) | Apply the SAME label change to a list of issues in one call — the release-prep path, where moving a batch one issue_status call at a time is how one of them gets missed. |
| [issue_close](tools/issue_close.md) | Close an issue THE WHOLE WAY: optional commit/MR cross-reference note -> log spent time -> move status:: to a terminal value -> close -> sync the wiki. |
| [issue_reopen](tools/issue_reopen.md) | Reopen a closed issue. |
| [issue_comment](tools/issue_comment.md) | Add a comment (note) to an issue. |
| [issue_link](tools/issue_link.md) | Cross-reference a commit and/or MR from an issue via a note (GitLab links them automatically). |
| [issue_relate](tools/issue_relate.md) | Link one issue to others (issue-to-issue relation). |

### workflow

| Tool | Summary |
|---|---|
| [work_queue](tools/work_queue.md) | The dispatch queue: what is READY to pick up, in the order to pick it up, and what is STRANDED in status::in-progress. |
| [issue_ready](tools/issue_ready.md) | Promote an issue into status::ready — the ONLY blessed way in, because `ready` is the label a dispatcher acts on with no human in the loop. |
| [issue_criteria](tools/issue_criteria.md) | Write acceptance criteria onto an issue — the append-only write for the one section grooming authors, where issue_update(description=…) would replace the whole description. |
| [issue_criteria_list](tools/issue_criteria_list.md) | Read an issue's acceptance criteria back as DATA — one row per checkbox (index, ticked, text) plus a DIGEST of the section body, which issue_criteria_replace requires. |
| [issue_criteria_replace](tools/issue_criteria_replace.md) | REPLACE an issue's acceptance criteria with a full new set — the way to REVISE criteria that already exist, which issue_criteria (append-only) never does. |
| [issue_decide](tools/issue_decide.md) | Record a decision that HAS been settled onto an issue — the append-only write for the escape #139 named and never gave a tool. |
| [issue_ask](tools/issue_ask.md) | Record questions on an issue and BLOCK it, in one call — what an agent does when dispatched work turns out to be underspecified, instead of guessing. |
| [issue_answer](tools/issue_answer.md) | Answer an issue's open questions — the write that was missing from the ask/answer loop, and the only one that does not need the GitLab UI. |
| [issue_answers](tools/issue_answers.md) | Read an issue's '## Open questions' block back as DATA — the other half of issue_ask, and how a dispatcher learns whether a blocked issue can move. |
| [issue_handoff](tools/issue_handoff.md) | End a round of work: post ONE structured '## Handoff' comment and move the issue to status::review. |

### reads

| Tool | Summary |
|---|---|
| [issue_list](tools/issue_list.md) | List issues. |
| [issue_show](tools/issue_show.md) | Show one issue in full: title, state, labels, related issues, description, and every non-system comment. |
| [issue_search](tools/issue_search.md) | Full-text search over issues — the 'has this already been filed?' read. |
| [project_status](tools/project_status.md) | Where a project stands right now: how much is open, what is in flight, what is mislabelled and what has gone quiet — the read a session opens with. |
| [workspace_status](tools/workspace_status.md) | The health of the PROJECTS, not of the tracker — one row per project across the whole instance, so a fact like 'eighteen projects have no CI' is visible as a fact rather than as eighteen separate observations. |
| [time_report](tools/time_report.md) | Roll up logged time over a date window — the 'what did I close today, and how long did it take' read. |
| [issue_digest](tools/issue_digest.md) | What CHANGED since a date, grouped by project — the read a session opens with after a gap, and the one neither time_report (hours, closed issues only) nor project_status (a snapshot with no memory) answers. |
| [issue_graph](tools/issue_graph.md) | The issue RELATION graph, walked and rendered — what `issue_relate` writes and nothing read back. |
| [list_projects](tools/list_projects.md) | List projects as `id path_with_namespace N open`. |
| [list_milestones](tools/list_milestones.md) | List a project's milestones. |

### repository

| Tool | Summary |
|---|---|
| [repo_file](tools/repo_file.md) | Read ONE file from a project's repository at a ref, without cloning — the 'what is actually on the remote' read. |
| [commit_list](tools/commit_list.md) | List recent commits on a ref, without cloning. |
| [commit_show](tools/commit_show.md) | Show ONE commit in full: its full SHA, author, date, message, and line stats. |
| [project_events](tools/project_events.md) | List a project's activity feed (its events): who did what, to which issue, merge request or ref, and when. |
| [repo_list](tools/repo_list.md) | List the CHECKOUT REGISTRY: every project ref that a local checkout declares, the path it maps to, and the roots that were scanned to find them. |
| [branch_list](tools/branch_list.md) | List a project's BRANCHES, without cloning: name, last commit date and author, how far each has diverged from the default branch, and whether it is protected or already merged. |
| [branch_create](tools/branch_create.md) | Create a branch on the remote from a ref, without a checkout. |
| [branch_delete](tools/branch_delete.md) | Delete a branch on the remote. |
| [tag_list](tools/tag_list.md) | List a project's TAGS, newest first: name, the commit each points at, its date, whether the tag is annotated, whether it carries RELEASE NOTES, and whether it is protected. |
| [tag_show](tools/tag_show.md) | Show ONE tag in full: the commit it points at (with that commit's author, date and subject), the tag's own annotation message, and its RELEASE NOTES if it carries any. |
| [project_settings](tools/project_settings.md) | Read a project's merge-request-adjacent SETTINGS as one table: the default branch, whether it is protected and by which rule, whether force-push is allowed on it, who may push and merge, the merge method, the squash option, whether the source branch is deleted on merge, the two merge preconditions (green pipeline, resolved discussions), and the required-approval count. |
| [project_protect](tools/project_protect.md) | Protect a branch — the write half of the settings surface, and the one that makes branch_delete's protected refusal mean something. |
| [project_attribute_list](tools/project_attribute_list.md) | List a project's CUSTOM ATTRIBUTES — the key/value pairs GitLab stores on a project and shows nowhere (CE has no UI for them, only the API). |
| [project_attribute_set](tools/project_attribute_set.md) | Set one project CUSTOM ATTRIBUTE — the write behind #190's per-project opt-in (`project_attribute_set('root/X', 'typesafe_decision_check', 'on')`). |
| [project_attribute_delete](tools/project_attribute_delete.md) | Delete one project CUSTOM ATTRIBUTE. |

### ci

| Tool | Summary |
|---|---|
| [pipeline_list](tools/pipeline_list.md) | List a project's CI pipelines — the 'did it run, and did it pass' read. |
| [pipeline_show](tools/pipeline_show.md) | Show ONE pipeline in full: its ref, SHA, status, source, who triggered it, duration and web URL — then EVERY JOB under it with its stage, status, duration and THE RUNNER THAT RAN IT. |
| [pipeline_wait](tools/pipeline_wait.md) | BLOCK until a pipeline finishes, then report it — replaces a hand-written sleep/curl poll loop. |
| [job_log](tools/job_log.md) | Read a CI job's TRACE — the log that says WHY it failed. |
| [runner_list](tools/runner_list.md) | List the CI runners: `id description type online last-contact tags`. |
| [ci_variable_set](tools/ci_variable_set.md) | Create or update a project (or, with `group=`, a group) CI/CD variable — the write half of the CI surface. |
| [ci_variable_list](tools/ci_variable_list.md) | List a project's CI/CD variables: `key type scope masked protected raw`. |
| [ci_variable_delete](tools/ci_variable_delete.md) | Delete a project CI/CD variable. |
| [ci_variable_check](tools/ci_variable_check.md) | Is the stored CI/CD variable `key` the value you think it is? Pass the SHA-256 of that value (64 hex characters) as `sha256` and get back `match` or `no match`, the stored value's LENGTH, and its masked/protected flags — so a credential can be checked without the raw value ever travelling. |
| [schedule_create](tools/schedule_create.md) | Create a pipeline schedule — the write that makes a repeating job actually repeat. |
| [schedule_list](tools/schedule_list.md) | List a project's pipeline schedules: `id description ref cron tz active next run owner`. |
| [schedule_update](tools/schedule_update.md) | Change a pipeline schedule. |
| [schedule_play](tools/schedule_play.md) | Run a pipeline schedule NOW, without waiting for its cron — the 'does this thing actually work' call, and the way a schedule gets tested on the day it is created rather than discovered broken a week later. |
| [schedule_delete](tools/schedule_delete.md) | Delete a pipeline schedule. |
| [pipeline_run](tools/pipeline_run.md) | Start a pipeline on a branch or tag NOW — the way to run CI against a ref without pushing to it. |
| [pipeline_retry](tools/pipeline_retry.md) | Retry failed CI work. |

### merge requests

| Tool | Summary |
|---|---|
| [mr_list](tools/mr_list.md) | List a project's merge requests — the 'what is proposed, against what' read. |
| [mr_show](tools/mr_show.md) | Show ONE merge request in full: title, state, source -> target, author, description, its detailed merge status, WHO HAS APPROVED IT, the count of UNRESOLVED discussion threads, its commits, and THE FILES IT CHANGED with +/- on each. |
| [mr_create](tools/mr_create.md) | Open a merge request — the write half of the MR surface, and what `status::review` actually means. |
| [mr_update](tools/mr_update.md) | Edit an OPEN merge request's title, description and draft state in place. |
| [mr_approve](tools/mr_approve.md) | Approve a merge request — or withdraw an approval with `withdraw=True`. |
| [mr_merge](tools/mr_merge.md) | Merge a reviewed branch — the GATE, and the last step of the review half of the workflow. |

### release

| Tool | Summary |
|---|---|
| [release_check](tools/release_check.md) | Gate a release on the standing rules, as a tool rather than a habit. |
| [close_audit](tools/close_audit.md) | Find CLOSES THAT BYPASSED THE PROTOCOL, across every project at once (#156). |
| [secret_scan](tools/secret_scan.md) | Scan a project's committed files for CREDENTIALS — GitLab PATs (glpat-), AWS keys, PEM private key blocks, PRIVATE-TOKEN headers, and password assignments — plus the literals known to be in circulation on this LAN, which are matched by SHA-256 HASH from ~/.config/gitlab-mcp/known-secrets.json and are not stored in this tool. |
| [milestone_create](tools/milestone_create.md) | Create a milestone — the release a batch of issues gets assigned to. |
| [issue_milestone](tools/issue_milestone.md) | Assign a BATCH of issues to a milestone — the release-prep companion to issue_bulk, and the same argument shape: `iids` is comma-separated numbers and ranges ('12,14-16', or a mix). |
| [changelog_generate](tools/changelog_generate.md) | Generate a changelog from the tracker: the closed issues in a milestone and/or a close-date window, grouped by `type::` into Added / Changed / Fixed, one bullet each from the issue title with its `(#N)` reference. |
| [release_create](tools/release_create.md) | Cut a release: create the tag (if it does not exist) and publish release notes against it. |
| [milestone_close](tools/milestone_close.md) | Retire a milestone — the other end of milestone_create, and the step that makes list_milestones(state='active') mean "still in flight" rather than "every milestone ever". |
| [milestone_show](tools/milestone_show.md) | Show one milestone in full: id, iid, title, state, start and due dates, updated_at, and the WHOLE description — never clipped, because a milestone description is used as a working document (root/acme-widgets M1 keeps its entire implementation order there, ~36 KB) and a clipped read handed to milestone_update would silently truncate it. |
| [milestone_update](tools/milestone_update.md) | Write a milestone's description, title, due date and/or state. |

### time

| Tool | Summary |
|---|---|
| [issue_spend](tools/issue_spend.md) | Log spent time on an issue (additive). |
| [issue_estimate](tools/issue_estimate.md) | Set the time estimate on an issue. |
| [issue_time](tools/issue_time.md) | Show an issue's time estimate and total spent (read). |

### labels

| Tool | Summary |
|---|---|
| [labels_ensure](tools/labels_ensure.md) | Idempotently create the canonical scoped-label scheme (type::/status::/priority::) on one or more scopes. |
| [labels_list](tools/labels_list.md) | List the scheme's labels on one scope (pass `group` id OR `project` id/path), showing which are present/divergent/missing plus any other labels not in the scheme. |

### wiki & tracker

| Tool | Summary |
|---|---|
| [wiki_sync](tools/wiki_sync.md) | Mirror a docs directory to `project`'s wiki. |
| [wiki_list](tools/wiki_list.md) | List a project's wiki pages as `slug format chars title` (the slug is what `wiki_get` takes; the title is what a sync's filename stem became). |
| [wiki_get](tools/wiki_get.md) | Show one wiki page's raw content. |
| [tracker_sync](tools/tracker_sync.md) | Mirror a checkbox test tracker (TESTING-*.md) into a GitLab issue: each case becomes a live task-list checkbox (drives the progress bar) plus an expandable <details> plan. |

### backup

| Tool | Summary |
|---|---|
| [tracker_export](tools/tracker_export.md) | Export a project's WHOLE issue tracker to JSON on disk — descriptions, labels, time totals, comments (system notes included) and issue relations, at state='all', plus the project's CUSTOM ATTRIBUTES (#191) under `custom_attributes` — a map, `{}` when there are none, and an admin-only read that fails the export rather than writing an empty map. |
| [tracker_import](tools/tracker_import.md) | Recreate a tracker_export file's issues in a project — the half that makes the export a backup rather than a comfort. |

### mirror

| Tool | Summary |
|---|---|
| [github_sync](tools/github_sync.md) | Mirror a GitHub repo's issues into a GitLab project — one-way, idempotent, safe to re-run. |

### attachments

| Tool | Summary |
|---|---|
| [upload_attachment](tools/upload_attachment.md) | Upload a local FILE to `project` and get back the markdown snippet that embeds it — for putting a render, screenshot, log excerpt or chart INTO an issue instead of describing it in prose. |
| [issue_attachments](tools/issue_attachments.md) | List what an issue CARRIES as attachments — the /uploads/ links in its description AND in its comments, resolved to the upload ids that can actually be fetched. |
| [download_attachment](tools/download_attachment.md) | Download an issue's attachments to local files, so `Read` can open a render or a screenshot a previous session attached. |

### admin

| Tool | Summary |
|---|---|
| [project_create](tools/project_create.md) | Create a new GitLab project. |
| [project_retire](tools/project_retire.md) | Retire a repository — the nine-step checklist as one call (#86). |
| [gitlab_health](tools/gitlab_health.md) | Is the GitLab instance up, and if not, how is it down? Answers the question that an opaque tool failure mid-workflow does not: 'restarting, retry in ~60s' vs 'the host is down' vs 'your token is rejected'. |
| [gitlab_audit](tools/gitlab_audit.md) | Read the AUDIT TRAIL: one record per mutating tool call this server has made — timestamp, tool, instance, project, the iids it touched, the arguments it was given (credentials redacted) and how it ended. |
| [restart_self](tools/restart_self.md) | Terminate this gitlab-mcp SERVER PROCESS — not the GitLab instance at your GitLab host, which this never touches — so the client respawns it on the next tool call, picking up edits to the server's own source. |
| [gitlab_help](tools/gitlab_help.md) | Concise reference for this server's own tools. |
