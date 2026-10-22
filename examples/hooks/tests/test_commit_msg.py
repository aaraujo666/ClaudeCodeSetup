"""Tests for examples/git/commit-msg: it must refuse AI co-author trailers and closing
keywords next to an issue reference, and accept ordinary messages and `re #N`.

    python -m pytest examples/hooks/tests/test_commit_msg.py -q
"""
import os
import shutil
import subprocess

import pytest

HOOK = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    "git", "commit-msg")
_GIT_SH = r"C:\Program Files\Git\bin\sh.exe"
SH = _GIT_SH if os.path.exists(_GIT_SH) else shutil.which("sh")


@pytest.fixture
def repo(tmp_path):
    """A repo whose remote is on a forge that acts on closing keywords."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "remote", "add", "origin",
                    "https://gitlab.example.com/team/proj.git"], check=True)
    return tmp_path


def check(repo, message, env_extra=None):
    msg = repo / "MSG"
    msg.write_text(message, encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k not in ("ALLOW_CLOSING_KEYWORD", "CLOSING_REMOTES")}
    env.update(env_extra or {})
    r = subprocess.run([SH, HOOK, str(msg)], cwd=repo, capture_output=True, text=True, env=env, timeout=30)
    return r.returncode, r.stderr


ACCEPT = [
    "Add retry to the uploader",
    "Add retry to the uploader\n\nre #45",
    "Refs #45: tighten the timeout",
    "Update CLAUDE.md with the new rules",
    "Mention that the fix landed earlier (see issue 45)",
    "# a git comment line: closes #9\nReal subject",
    "Prefix handling\n\nThe prefixes #1 and #2 are sorted",
]

REJECT_KEYWORD = [
    "Close #45",
    "closes #45",
    "Fixes #45",
    "fixed: #45",
    "Resolves #45",
    "resolving #45",
    "implementing #45",
    "Add retry\n\nImplements #45 in full",
    "Add retry\n\nthis closes  #45",
]

REJECT_AI = [
    "Add retry\n\nCo-Authored-By: Claude <noreply@anthropic.com>",
    "Add retry\n\nco-authored-by: Claude Sonnet 5.5 <noreply@anthropic.com>",
    "Add retry\n\nCo-Authored-By: GitHub Copilot <copilot@example.com>",
    "Add retry\n\nGenerated with [Claude Code](https://claude.com/claude-code)",
]


@pytest.mark.parametrize("message", ACCEPT)
def test_accepts(repo, message):
    code, err = check(repo, message)
    assert code == 0, err


@pytest.mark.parametrize("message", REJECT_KEYWORD)
def test_rejects_closing_keywords_and_suggests_re(repo, message):
    code, err = check(repo, message)
    assert code == 1
    assert 're #N' in err


@pytest.mark.parametrize("message", REJECT_AI)
def test_rejects_ai_attribution(repo, message):
    code, err = check(repo, message)
    assert code == 1
    assert "REFUSED" in err and "co-author" in err.lower()


def test_closing_keyword_override(repo):
    code, _ = check(repo, "Fixes #45", {"ALLOW_CLOSING_KEYWORD": "1"})
    assert code == 0


def test_ai_trailer_has_no_override(repo):
    code, _ = check(repo, "x\n\nCo-Authored-By: Claude <noreply@anthropic.com>", {"ALLOW_CLOSING_KEYWORD": "1"})
    assert code == 1


def test_closing_keyword_ignored_when_remote_does_not_act_on_it(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "remote", "add", "origin",
                    "https://bitbucket.example.org/team/proj.git"], check=True)
    code, _ = check(tmp_path, "Fixes #45")
    assert code == 0


def test_custom_remote_pattern(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "remote", "add", "origin",
                    "https://git.corp.example/team/proj.git"], check=True)
    code, _ = check(tmp_path, "Fixes #45", {"CLOSING_REMOTES": "git\\.corp\\.example"})
    assert code == 1
