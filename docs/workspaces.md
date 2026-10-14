# Workspaces, migration, and upgrades

The AI coding tool manages the repository configuration. This framework supplies
instructions, templates, and display examples. Choose tools from the README and
adapt their configuration to the learner's machine.

## Private learning workspace

Add the public framework as a `framework/` Git submodule in a dedicated
maintenance worktree of the private repository. Use the files in
`templates/workspace/` as examples for the root loader and personal preferences.
Inspect existing files before changing them; preserve personal settings and
learning records.

The framework's `AGENTS.md` holds shared teaching rules. The private root loader
loads those rules and `preferences.md`. Its `CLAUDE.md` imports that loader.
Keep actual topic records in the private repository, using `templates/topic/`
for new topics. Each parent commit pins one exact framework commit.

Initialize the pinned submodule in every new clone or linked worktree. Keep
framework changes separate from learning changes. Publishing the framework does
not publish the parent repository or its learning branches.

## Existing learning repositories

Replace duplicated shared rules with the workspace loader. Move personal
overrides into `preferences.md`. Keep old rules in Git history. Compare local
templates with the shared ones before removing duplicates; preserve unique edits.

Existing topic files need no conversion. Keep their `lesson.md`, `display.yaml`,
and `mermaid.json` files. Existing local launchers may remain in use. For direct
presenterm use, select the intended configuration as described in
[the display guide](display.md). Do not delete configuration files that a topic
still references.

Merge the framework refactor into the default branch first. When resuming an
older topic, merge that default branch into the topic's own worktree and
initialize its pinned submodule. Resolve rule conflicts in favor of the shared
loader, while preserving personal settings and all topic evidence. Keep separate
learning branches and their existing PRs.

## Framework updates

Use a dedicated private maintenance worktree. Fetch the framework's default
branch, check out the intended commit inside the submodule, and inspect the
change. Check the loaders, template paths, and display settings that it affects.
Commit the new submodule pointer in a private maintenance PR.

Normal lessons use the recorded commit. Do not advance the framework to a branch
tip as part of a lesson. Make shared framework changes in a separate framework
worktree and public PR, then update the private pointer after merge. Keep private
data out of public commits and PR descriptions.

## First extraction across two PRs

Push the framework commit before opening a private PR that references it. Merge
the public framework PR first. A regular merge preserves its commits. If it is
squash-merged or rebased, update the private pointer to the resulting default
branch commit before merging the private refactor.
