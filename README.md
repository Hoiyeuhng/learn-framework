# learn-framework

Shared teaching instructions and templates for Codex and Claude Code. Keep this
framework in a public repository and your learning records in a private one.

The tutor connects new ideas to what you know, uses small examples, and saves
progress so another session or tool can continue. Each learning round uses a
separate Git worktree and an AI-managed draft PR. You decide when to merge.

Teaching builds understanding, practice exercises its use, and review checks what
you retain. Practice uses varied problems, gradual hints, and new-situation
retests. Connections in topic notes link related ideas across subjects. The same
four records preserve the material, actual attempts, assistance, and resume point.

Language, writing style, reference works, and display layout belong in the private
workspace's `preferences.md`. Public templates contain placeholders, and examples
use synthetic material. The publication rules in [AGENTS.md](AGENTS.md#public-and-private-content)
keep learner-specific data out of the shared framework.

## Acknowledgments

Inspired by [amosblomqvist/learn](https://github.com/amosblomqvist/learn).
Credit to its author for sharing the original AI learning system and teaching
workflow. This project adapts those ideas for Codex and Claude Code, with shared
rules, private learning records, and Git worktree and PR support.

## Start with your AI coding tool

Create or open your private learning repository. Give Codex or Claude Code this
request:

> Read https://github.com/Hoiyeuhng/learn-framework. Use it as the `framework/`
> Git submodule in this private learning repository. Adapt its workspace templates
> without overwriting my existing records or preferences. Read the tool list and
> check what is installed. Use my operating system and preferred package manager
> for any tools I need. I want [text-only learning / a rendered lesson pane].

The AI handles repository configuration and tool-specific commands. This
framework provides documentation and templates, with no setup scripts, helper
CLI, or required CI workflow. See [workspace guidance](docs/workspaces.md) when
adapting an existing repository.

## Tools we use

Install only what your chosen features need. Use your preferred package manager
or the tools' official installers. Homebrew is optional.

| Feature | Tools |
| --- | --- |
| Learning and saved records | Git, plus Codex or Claude Code |
| Automatic learning PRs | GitHub CLI (`gh`), authentication, and repository write access |
| Optional lesson display | presenterm and a terminal with image support |
| Optional math rendering | Pandoc and Typst |
| Optional Mermaid rendering | Node.js/npm, Mermaid CLI (`mmdc`), and Chrome/Chromium |
| Optional side-by-side layout | tmux |

Text-only learning needs no renderer. Your AI tool can identify suitable versions
and configure the tools already on your machine. The [display guide](docs/display.md)
records the tested tools, display settings, and fixes for blank equations.

## What lives where

| Path in your private repository | Purpose |
| --- | --- |
| `framework/` | This public repository, pinned as a Git submodule |
| `AGENTS.md` | A small loader for shared rules and personal preferences |
| `CLAUDE.md` | Imports the same loader for Claude Code |
| `preferences.md` | Your personal preferences |
| `topics/<topic>/plan.md` | Goal, dependencies, and teaching, practice, and review evidence |
| `topics/<topic>/notes.md` | Compact notes and useful connections across topics |
| `topics/<topic>/misses.md` | Actual errors, assistance, diagnoses, and retest history |
| `topics/<topic>/state.md` | Session mode, active problem, resume point, and learning PR |
| `topics/<topic>/lesson.md` | Optional current lesson display |

[AGENTS.md](AGENTS.md) is the single source of shared teaching rules. The
[workspace templates](templates/workspace) provide the loaders and preferences;
[topic templates](templates/topic) provide the learning records.

The root loader tells Codex to read the shared rules explicitly. Claude can load
them through [imports](https://code.claude.com/docs/en/memory#import-additional-files).
See the official [Codex instructions guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
for instruction discovery. These files guide the AI; they do not run a background
service.

## Daily use

- Start: “I want to learn X so I can do Y.”
- Resume: “Continue topic X. Read its records first.”
- Practice: “Give me mixed application problems from topic X, with hints only when I ask.”
- Review: “Quiz me on the unresolved errors in topic X.”
- Change topics: “Pause X and start Y.”
- Finish: “Save my progress.”

The AI creates or restores the topic's worktree and initializes the pinned
submodule. It opens a draft PR after saving initial records and updates the same
PR at checkpoints. Paused topics keep their worktrees and PRs. Completed rounds
become ready for your review.

## Contributing

Use a dedicated worktree and a separate framework PR. Check links, templates,
and any affected display settings. Keep personal notes, answers, progress, and
configuration in the private learning repository. The example lesson is synthetic.

The repository uses the [MIT license](LICENSE).
