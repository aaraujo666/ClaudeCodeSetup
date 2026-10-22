"""The work-content markers, in one place.

Imported by block-work-to-third-party.py (the hook) and by anything that sends text to
a third-party AI on its own and has to withhold work content BEFORE it leaves the box
(for example a script that pre-sorts tickets with an outside model). A second copy of
these patterns would drift, and the copy that drifts is the one that leaks.

Lives under ~/.claude so that reading it never taints a session: the hook exempts
output from Claude's own config.

=== CONFIG ===========================================================================
Everything employer- or client-specific is in this block. Replace the placeholders with
your own domains, checkout path and company name.
"""
import re

# Path to the client-work checkout root, Windows or Git Bash separators. Placeholder:
# ~/source/WORK. Never spell the real path out anywhere that gets read back as tool
# output: a Write/Edit input naming it taints the session.
WORK_PATH_NAME = r"WORK"

# Strong identifiers: specific enough that a hit in tool output really is work data.
# Hostnames of your employer's systems, your work e-mail domain, work-only tool names.
STRONG_PATTERN = (
    r"work\.example\.com|@work\.example\.com|tracker\.example\.net|"
    r"\bEXAMPLE-OPS\b|\bwork-vm\w*"
)

# Bare words that mark a request as work. Broader than STRONG because it is only used on
# what is about to LEAVE the box, where a false positive is cheap. Company name here.
WORK_WORDS_PATTERN = r"\bExampleCorp\b|\bExampleConsulting\b"
# === END CONFIG ======================================================================

WORK_PATH = re.compile(r"[\\/]source[\\/]+" + WORK_PATH_NAME + r"([\\/]|$|[\"' ])", re.I)
STRONG = re.compile(STRONG_PATTERN, re.I)

# Everything that marks a request as work, strong identifiers plus the checkout path.
WORK = re.compile(STRONG.pattern + r"|" + WORK_PATH.pattern, re.I)
WORK_WORDS = re.compile(WORK_WORDS_PATTERN)


def work_marker(text):
    """The first work marker in `text`, or None: the same test the hook's gate applies."""
    m = WORK.search(text or "") or WORK_WORDS.search(text or "")
    return m.group(0) if m else None
