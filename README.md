# learn-framework

A reusable learning workflow for Codex and Claude Code. Keep the framework in a
public repository. Keep goals, notes, answers, and progress in your own private
learning repository.

The tutor builds from known concepts, uses small examples, and saves enough state
to resume in another session or tool. Learning branches use dedicated Git
worktrees and AI-managed draft PRs. You decide when to merge.

## Acknowledgments

Inspired by [amosblomqvist/learn](https://github.com/amosblomqvist/learn).
Credit to its author for sharing the original AI learning system and teaching
workflow. This project adapts those ideas for Codex and Claude Code, with shared
rules, private learning records, and Git worktree and PR support.

## Start a private learning workspace

Create a private repository on GitHub, then clone it. From its root, run:

```sh
git submodule add https://github.com/Hoiyeuhng/learn-framework.git framework
./framework/bin/learn setup
./framework/bin/learn doctor
```

Commit the generated entry points and submodule pointer in your private repo.
Open Codex or Claude Code from that workspace. For example:

> I want to understand this component well enough to review changes to it.
> Help me define the scope and assess the needed knowledge.

Setup creates only missing files. It refuses to overwrite existing files.
For an existing learning repo, see [migration](docs/workspaces.md).

## What lives where

```text
private-learning-repo/
  AGENTS.md          # Small loader, not a second set of teaching rules
  CLAUDE.md          # Imports AGENTS.md
  preferences.md     # Personal preferences
  framework/         # Git submodule: this public repository
  topics/<topic>/
    plan.md          # Scope, dependencies, and evidence
    notes.md         # Compact notes on what was taught
    misses.md        # Actual errors and review history
    state.md         # Resume point and learning PR
    lesson.md        # Optional current lesson display
```

[AGENTS.md](AGENTS.md) is the single source of shared teaching rules. Topic
scaffolds are in [templates/topic](templates/topic). The workspace loader tells
Codex to read the shared file explicitly. Claude loads the same file through
[imports](https://code.claude.com/docs/en/memory#import-additional-files).
See the official [Codex instructions guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
for instruction discovery. These are instructions for an AI agent, not an
independent background service or guaranteed policy enforcement.

## Tools

Install the tools for the features you want. Use your preferred package manager
or the tools' official installers. Homebrew is optional.

| Need | Tools |
| --- | --- |
| Learning and records | Git, Codex or Claude Code |
| Workspace helpers | Python 3.9 or newer; standard library only |
| Automatic PRs | GitHub CLI (`gh`), authentication, and repository write access |
| Optional lesson display | presenterm and a terminal with image support |
| Optional math display | Pandoc and Typst |
| Optional Mermaid display | Node.js/npm, Mermaid CLI, and Chrome/Chromium |
| Optional side-by-side layout | tmux |

No API key, Python package install, or renderer is needed for text-only learning.
Use your existing AI tool and account.

```sh
./framework/bin/learn doctor
./framework/bin/learn doctor --render
./framework/bin/learn present your-topic
```

Display setup, a smoke test, and fixes for blank equations are in
[the display guide](docs/display.md). The tools do not change your tmux panes.

## Daily use

- Start: “I want to learn X so I can do Y.”
- Resume: “Continue topic X. Read its records first.”
- Review: “Quiz me on the unresolved errors in topic X.”
- Change topics: “Pause X and start Y.”
- Finish: “Save my progress.”

The agent creates or restores a dedicated worktree. It opens a draft PR after
saving initial records, then updates that PR at checkpoints. A paused topic keeps
its worktree and PR. A completed round becomes ready for your review.

In every new clone or worktree, initialize the pinned framework:

```sh
git submodule update --init --recursive
```

Upgrade the framework in a separate maintenance PR. Normal lessons use the
recorded commit. See [workspaces and upgrades](docs/workspaces.md).

## Contributing

Use a dedicated linked worktree. Keep changes generic: do not submit personal
notes, answers, topic records, or private configuration. Run:

```sh
python3 -m unittest discover -s tests -v
sh -n bin/setup-mermaid
```

GitHub Actions runs these contributor checks on Linux and macOS with Python.
The checks do not install or require Homebrew or the optional display tools.
Users do not need to run this workflow to learn.

Tests use temporary synthetic workspaces. The example lesson is also synthetic.
The repository uses the [MIT license](LICENSE).
