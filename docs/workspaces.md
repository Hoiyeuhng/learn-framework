# Workspaces, migration, and upgrades

The framework is a Git submodule. Each learning commit records one exact framework
commit. Private records stay in the parent repository, including its branches and
PRs. Adding a public submodule does not publish the parent repository.

## Existing learning repository

Make a dedicated maintenance worktree from the latest default branch. Add the
framework submodule there. Replace the old shared-rule file with the small loader
in `framework/templates/workspace/AGENTS.md`. Keep the original file in Git history.
Use the matching `CLAUDE.md`, and put personal overrides in `preferences.md`.

Compare the existing templates with `framework/templates/topic/` before removing
local duplicates. Preserve unique changes. Point future topic creation to the
framework templates. Existing topic files do not need to be recreated.

Keep existing `lesson.md`, `display.yaml`, and `mermaid.json` files. The shared
`present` command honors topic display configuration. A topic's old `display.sh`
can remain in use or become a short wrapper:

```sh
#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
exec ./framework/bin/learn present your-topic
```

Do not run setup over customized loaders or preferences. It refuses to replace
them. Reconcile those files in the maintenance PR.

## Open learning branches

Merge the framework-refactor PR into the default branch first. Then, from each
learning branch's own worktree:

```sh
git fetch origin
git merge origin/main
git submodule update --init --recursive
```

Use the actual default branch if it is not `main`. If the merge conflicts in
`AGENTS.md`, keep the framework loader and move any personal changes into
`preferences.md`. For duplicate template conflicts, keep the shared templates and
preserve any unique edits. Never discard topic records or pending questions.

This migration belongs in each branch only when that branch is resumed. Do not
merge unfinished learning branches together. Keep their existing PRs and history.

## Framework updates

Create a dedicated maintenance worktree in the private repository. In it:

```sh
git submodule update --init --recursive
git -C framework fetch origin main
git -C framework checkout --detach origin/main
./framework/bin/learn doctor
```

Review the old and new framework commits and test your display if you use it.
Commit the changed submodule pointer in a private maintenance PR. Do not use
`git submodule update --remote` during lessons, because it changes the selected
version. Do not edit the detached framework checkout for feature work.

For framework changes, create a separate linked worktree of the framework repo,
open a public PR, then update the private pointer after it is merged. Keep real
notes and personal data out of commits and public PR descriptions.

## First extraction across two PRs

If the private refactor points at the public framework PR's commit, that commit
must be pushed before the private PR is opened. Merge the public framework PR
first. A regular merge preserves that commit. If the public PR is squash-merged
or rebased, update the private pointer to the resulting `main` commit before
merging the private refactor. This keeps the selected commit reachable from the
public default branch.
