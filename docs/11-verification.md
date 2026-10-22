# 11. Verification: verify, do not assert

"Done" from a model means "I stopped". It does not mean the thing works, the file
arrived, or the number is right. This setup makes verification part of the workflow
instead of a courtesy.

## Verify before asking, verify before asserting

The hard rule: **before asking me something, go and look for the answer. Before stating
something as fact, check it.** Asking is the last resort.

Two failure modes this kills:

- *The lazy question.* "Which file is the config in?" when a search would have found it.
  Each question costs me a context switch.
- *The confident guess.* Stating how a system behaves from memory of how similar systems
  behave. The memory store carries explicit traps for exactly this: the command that
  exits 0 and does nothing, the status that says "running" for an unhealthy VM.

### Never "you may be right"

When I push back on something, the wrong response is a hedge: "you may be right, it's
possible that...". That avoids the work and shifts the burden back to me. The right
response is to go and measure, then state what is true. If I am right, say so and say
what the evidence was. If I am wrong, say so and show the evidence. Either way I get a
fact instead of a social gesture.

## Measure, then state

Several of the most useful findings in this setup came from measuring a belief:

- "A cheap model saves tokens." It did not, on a small pile. Measured: 376k tokens with
  the cheap model against 227k reading directly, on 14 issues. Break-even came out at
  about 45 to 60 issues. See [Jev](06-jev-decision-model.md).
- "Splitting work across subagents costs more." Only for a single issue. Break-even at
  two.
- "The log line says reverted." The log line was written by the script that failed to
  revert. Inspect the resource, not the log. (The memory entry for this is a TRAP about a
  container CPU cap that survives a command that reports success.)
- A token count that looked 39% too high had been counted three times, because each
  streamed response appears in the transcript several times. Dedupe by request id before
  you believe a baseline.

The habit: when a number or a claim will drive a decision, write down how it was
produced, and prefer a second independent way to produce it.

## Deliveries are verified by hash

When a change is delivered somewhere (a built artifact copied to a test host, a tarball
unpacked on a server), the check is a content hash of the delivered file compared with
the local one:

```bash
sha256sum build/acme-widgets-1.4.2.tar.gz
ssh deploy-host "sha256sum /srv/releases/acme-widgets-1.4.2.tar.gz"
```

Not "I copied it, so it is there". Not poking at the running application to see if it
seems different. A hash answers the actual question: is the thing on that machine the
thing I built? Deliver a `.sha256` file alongside the archive so the receiver can check
too.

## The Word-document render loop

A Word document is not verified by the script that generated it. It is verified by
looking at the pages. The loop:

1. Generate the `.docx` (pandoc from markdown, or a library).
2. Convert to PDF with a headless office suite.
3. Convert the PDF pages to images.
4. Have the model *look at the images* and check layout, tables, headings and cropped
   screenshots against what the text says.

```bash
soffice --headless --convert-to pdf report.docx
pdftoppm -jpeg -r 90 report.pdf page
# page-01.jpg, page-02.jpg, ...
```

Anything I will send to another person goes through this before I see it. Screenshots in
a document are cropped to the region the text describes, not pasted full screen.

## Compile check before every deploy

For code that is deployed somewhere hard to debug (a game mod loaded by a running game, a
script pushed to a device), a compile check runs before every deploy. It is a script, it
is fast, and the deploy tool calls it. A syntax error found locally costs seconds; found
in the target, it costs a restart cycle and a confusing log.

A general form: **whatever the target will do to your artifact, do a cheaper version of it
first.**

## Tests gate releases

New functionality spawns test cases in the tracker. A release is gated by a check that
asks:

- Are there open issues on the milestone?
- Are there test cases not passed?
- Are there closed issues with no logged time?
- Are there issues missing a `type::` or `status::` label?
- Is CI on the release ref green?
- Are there committed credentials?

The check is a tool, not a checklist in someone's head. A gate you run from memory is a
gate you skip when you are in a hurry, which is when you need it.

## Verification in the agent contracts

Every implementation agent's prompt says: do not report success without having run the
check. The report format has a *Verified* section and a *Not verified* section, and the
handoff comment on an issue carries both, so the reader knows exactly what was and was
not exercised:

```markdown
### Verified
- [x] pytest: 214 passed

### Not verified
- [ ] the live round trip against staging
```

An honest "not verified" line is worth more than a confident summary.

## When a check disagrees with the agent

The check wins. If the test fails and the agent says it should pass, the test is right
until proven otherwise. If a hash differs, the file differs. If the screen reader says the
installer is at a different prompt than expected, it is. The whole point of an independent
check is that it is not asked what it thinks.

Next: [12 Walkthrough](12-walkthrough.md)
