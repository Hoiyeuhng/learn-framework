# Learning workspace

Before teaching or changing files, read and follow the shared rules in
@framework/AGENTS.md and the local preferences in @preferences.md.
These paths are relative to this file. Codex must read both files explicitly;
Claude Code can load them through the imports in this file.

This repository owns all `topics/` paths and learning PRs. The framework is a
pinned Git submodule. Keep it unchanged during lessons. Use a separate framework
worktree and PR for shared improvements. Never copy private records into it.

If `framework/AGENTS.md` is missing, run `git submodule update --init --recursive`
from this workspace before continuing. Do this in each new linked worktree.
