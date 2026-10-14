# <Topic>: Resume State

Replace placeholders when creating a topic. Save actual progress only; do not prefill learning results that have not occurred.

- Last updated: <YYYY-MM-DD>
- Topic status: <Active / Paused / Goal met>
- Teaching phase: <Goal clarification / Assessment / Awaiting plan approval / Teaching / Review / Summary>
- Current node: <Node ID, or not yet determined>
- Plan approval: <Awaiting approval / Approved, with date>
- Next step: <One actionable step for resumption>

## Learning worktree and PR

- Learning branch: <Actual name, such as learn/conditional-probability>
- PR base: <Actual remote default branch>
- PR: <Actual URL after successful creation; otherwise Pending, with the reason>

Locate this branch's dedicated local worktree with `git worktree list --porcelain` before editing. Worktree paths differ across machines; use the branch and PR as portable identifiers.

Pausing changes topic status while preserving the teaching phase, node, and pending question. Retain the worktree, and check actual remote branch and PR state when resuming. Further learning after a PR is merged uses a new worktree, branch, and PR; retain the old URL as history.

## Pending question

<Write None if there is no unanswered question. Otherwise save the one pending question with its necessary wording, options, and context. Do not mark unanswered questions as completed.>

## Context needed to resume

<Only temporary context another tool needs, such as the diagnostic step reached, hints already given, an unfamiliar word being explained, or an unverified claim.>
