# 14. Extras: reference material from the real tools

The other docs describe the setup. This one points at material pulled straight from the
tools I actually run, published so you can read the real thing instead of my summary of
it. It lives in the `EXTRAS/` folder at the top of the repository, outside `docs/`,
because it is generated reference rather than prose.

At the moment there is one section.

## gitlab-mcp: the full help output

[EXTRAS/gitlab-mcp/README.md](../EXTRAS/gitlab-mcp/README.md) holds the help output of
the tracker server described in [doc 04](04-issue-workflow.md) and
[doc 09](09-mcp-servers.md): the overview that `gitlab_help()` returns, an index of every
tool grouped by area, and one page per tool with the text `gitlab_help('<tool>')`
returns. It covers about a hundred tools.

I sanitized it before publishing. Hosts, private project names and local paths are
replaced with generic stand-ins. The `(#190)`-style issue numbers are left in; they point
at the server's own private tracker, so you cannot follow them, but they show that each
rule traces back to a recorded decision.

## Why publish help text

Doc 09 describes the `help()` catalogue pattern in a few paragraphs. The paragraphs say
what the pattern is. The export shows what it looks like when a server has a hundred
tools and a workflow with real rules in it.

The pattern has three parts:

- **It is generated from the registered tool metadata.** The overview is built by walking
  the tool registry, and each tool's signature comes from its published schema. Nobody
  maintains a second copy by hand, so the help cannot drift from the code. A test fails
  if a registered tool is missing from the groups, and an ungrouped tool shows up
  loudly instead of silently not existing.
- **There is an overview and a per-tool detail.** `help()` is the map: tools by area,
  the standing rules, the status loop, and the conventions every tool shares.
  `help('tool')` is the territory: the description, the signature, the convention that
  governs the tool, and a worked example with real argument values.
- **An agent calls it before guessing.** The server's `instructions` string says to call
  `help()` first. The conventions are expensive to look up in a repository mid-task and
  cheap to read from inside a call, so an agent that is unsure about an argument asks
  the server instead of inventing one. A misspelled tool name returns a "did you mean"
  hint rather than a stack trace.

Read a few pages with that in mind. Start with `issue_close`, which states its five
steps and the required `spend` argument, then a read-only tool such as `issue_list`, and
compare how much of the page is signature and how much is convention. The convention is
the part a model cannot recover from the signature alone.

## A note on the wiki

My copy of this repository is mirrored to a wiki from the `docs/` folder. The links from
this page to `../EXTRAS/` resolve on GitHub but not on the wiki, because `EXTRAS/` is
outside the mirrored folder. I accept that; the wiki copy of this page is a pointer, and
the content is in the repository.

Next: [Glossary](glossary.md)
