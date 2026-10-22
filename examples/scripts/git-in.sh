#!/usr/bin/env bash
# Run a git command in a given repo WITHOUT cd, so the harness sees a stable
# command prefix (`bash ~/.claude/scripts/git-in.sh ...`) that can be
# permission-allowlisted - a leading `cd <dir> && git ...` can't be, and the Bash
# tool's cwd resets between calls anyway.
#
# Usage: bash git-in.sh <repo-dir> <git args...>
#   e.g. bash ~/.claude/scripts/git-in.sh ~/source/repos/foo status -s
#
# Allowlist it once in settings.json with: "Bash(bash ~/.claude/scripts/git-in.sh:*)"
# block-cd-git.sh then refuses the `cd ... && git` form and points here.
dir="$1"; shift
exec git -C "$dir" "$@"
