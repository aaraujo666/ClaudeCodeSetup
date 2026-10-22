# 09. MCP servers: write your own, with the rules inside

A generic MCP server exposes an API. A domain server exposes *your workflow*, with your
rules built into the tool surface so that the wrong move is not available. I run one per
domain I work in.

## The servers

**Homelab VM provisioning.** Creates and clones VirtualBox VMs on a hypervisor over SSH,
attaches installer media, and drives headless installers by *reading the screen*: it can
capture the VM's display, wait for specific text to appear, send keystrokes, and wait for
first boot. A `wait_for_screen` tool replaces sleeping, which is slow and blind. At the
end it registers the new host in an inventory. About 30 tools.

**The git-hosting tracker.** Issues, labels, milestones, merge requests, pipelines, CI
variables, wiki sync, time reports. About 90 tools, with the whole workflow in
[doc 04](04-issue-workflow.md) built in: illegal status moves refused, closing keywords
refused in merge request text, close requires time and a checkout to sync the wiki from.

**The decision model.** A wrapper around Jev that keeps item contents out of the
conversation. See [doc 06](06-jev-decision-model.md).

**A game-modding toolkit.** For Space Engineers mods: compile-check a mod's C# scripts,
validate definition files, build and render models, fetch the newest game log or
screenshot, snapshot and reset a test world, watch the log for the load result, pixel-diff
two renders. About 70 tools, all things I used to do by hand and by memory.

**A read-only work mailbox.** Mail triage, search, read and thread tools, calendar agenda
and free-time lookup, and a draft tool that saves to Drafts. There is no send verb and no
delete verb. Anything that mutates is gated behind an environment flag that is off by
default. This is deliberate, and it is the cleanest example of the principle:

> The safest permission is a capability that does not exist.

A hook that blocks "send" can be misconfigured, bypassed or forgotten. A server that has no
send tool cannot send. When you design a server, ask for each verb whether the model needs
it, and leave out the ones it does not.

## Design rules that carried across servers

The tracker server states these as its tool contract; they generalise.

1. **Accept loose input, return consistent output.** Every row-shaped read offers
   `format=text|json`, defaulting to the same text it always returned.
2. **Truncate large text, with a size hint and an escape hatch.** No unbounded output. A
   clipped response says how much was withheld and which argument returns the rest. Clip
   from the *useful* end: for a long thread, keep the newest comments.
3. **Aggregate so the caller does not round-trip.** The obvious follow-up is answered in
   the first response, with counts that state their denominator.
4. **Say "0 results" out loud, and distinguish its causes.** "Nothing matched" (the query
   ran and excluded everything), "there are none to query" (the scope is empty) and
   `error: ...` (the query failed) are three different answers and must never be rendered
   as one another. A failed fetch rendered as an empty list is the bug that bites hardest.
5. **Idempotent mutations, structured errors, no prompts, fail loud on unknown
   arguments.** Re-running converges and says "no change". Errors carry a stable code and
   a hint naming the next move. A misspelled argument fails rather than being ignored,
   because a silently dropped flag reports success for work that never happened.
6. **A concise reference on demand.** See the next section.

## The `help()` catalogue pattern

Every server has a `help()` tool, and `help("tool_name")` for one tool. It is generated
from the registered tool metadata so it cannot drift from the signatures. The model looks
up what is available instead of guessing, and the server's `instructions` string tells it
to call `help()` first.

Two traps:

- **Check that every tool is in the catalogue** with a test that fails if a registered
  tool is missing from the help groups. The catalogue only works if it is complete.
- **A tool-name that does not exist cannot be guessed correctly.** If a session reaches
  for a raw call because no tool covers the case, that is a missing tool, not a model
  failure. Write the tool.

## `restart_self`

Every server has a `restart_self` tool that makes the process exit so the client
restarts it. After editing an *existing* tool, the process only needs killing. A
*newly added* tool needs a new session, because the client holds the tool list it was sent
at startup and a restart does not resend it. Knowing which is which saves a confusing
half hour.

## A minimal Python skeleton

Using the MCP Python SDK (check the SDK's current docs; its server API has changed
between major versions, and the example below uses the `mcp.server.MCPServer` class from
the 2.x line):

```python
"""acme-tools: a minimal domain MCP server."""
import os
import sys

from mcp.server import MCPServer

mcp = MCPServer(
    "acme-tools",
    instructions=(
        "Tools for the acme-widgets build system. Call help() for the catalogue. "
        "Read-only unless a tool says otherwise."
    ),
)

# One place that lists every tool, so help() can never drift from reality.
CATALOGUE = {
    "build_status": "Latest build result for a branch. Read-only.",
    "queue_build": "Queue a build for a branch. Idempotent: a second call reports no change.",
}


@mcp.tool()
def help(tool: str = "") -> str:
    """Catalogue of tools, or detail on one."""
    if tool:
        return CATALOGUE.get(tool, f"error: unknown tool {tool!r}; call help() for the list")
    return "\n".join(f"{name}: {line}" for name, line in sorted(CATALOGUE.items()))


@mcp.tool()
def build_status(branch: str) -> str:
    """Latest build result for a branch. Read-only."""
    result = lookup_build(branch)            # your code
    if result is None:
        # Say "none" out loud, and say which kind of none.
        return f"there are no builds for branch {branch!r}"
    return f"{branch}: {result.state} ({result.duration_s}s)"


@mcp.tool()
def queue_build(branch: str) -> str:
    """Queue a build. A second identical call converges and reports no change."""
    if already_queued(branch):               # your code
        return f"no change: {branch} is already queued"
    enqueue(branch)                          # your code
    return f"queued {branch}"


@mcp.tool()
def restart_self() -> str:
    """Exit so the client restarts this server after an edit to an existing tool."""
    os._exit(0)


if __name__ == "__main__":
    mcp.run()                                 # stdio transport
```

Register it in your client's MCP configuration as a stdio command
(`python /path/to/server.py`), then allowlist the server as a whole in your permission
settings so its calls do not prompt. Prefer allowlisting a server you wrote over
allowlisting a shell pattern: shell strings vary on every call and prompt each time.

## Testing a server

- A registry test: every registered tool is classified (read or mutation) and appears in
  the help groups. A tool added without both fails the build.
- A convergence test per mutation: call it twice, assert the second reports no change.
- Offline tests by default; live tests behind a marker, and a live run that executed
  nothing because the host was unreachable should exit with a distinct code that means "no
  evidence", not 0.

Next: [10 Infrastructure rules](10-infrastructure-rules.md)
