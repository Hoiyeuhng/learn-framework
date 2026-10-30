# <Topic>: Resume State

Replace placeholders when creating a topic. Save actual progress only; do not prefill learning results that have not occurred.

- Last updated: <YYYY-MM-DD>
- Topic status: <Active / Paused / Goal met>
- Session mode: <Learning / Practice / Review>
- Teaching phase: <Not started / Goal clarification / Assessment / Awaiting plan approval / Teaching / Review / Summary>
- Current node: <Node ID, or not yet determined>
- Plan approval: <Awaiting approval / Approved, with date / Not proposed: practice-only scope>
- Next step: <One actionable step for resumption>

## Learning worktree and PR

- Learning branch: <Actual name, such as learn/conditional-probability>
- PR base: <Actual remote default branch>
- PR: <Actual URL after successful creation; otherwise Pending, with the reason>

Locate this branch's dedicated local worktree with `git worktree list --porcelain` before editing. Worktree paths differ across machines; use the branch and PR as portable identifiers.

Pausing changes topic status while preserving the session mode, teaching phase, node, and pending question. Practice preserves the teaching resume point. Retain the worktree, and check actual remote branch and PR state when resuming. Further learning after a PR is merged uses a new worktree, branch, and PR; retain the old URL as history.

## Pending question

<Write None if there is no unanswered question. Otherwise save the one pending question with its necessary wording, options, and context. Do not mark unanswered questions as completed.>

## Practice context

<Optional. Use when practicing; remove unused placeholders. Keep the active problem in Pending question above, without its undisclosed solution.>

- Practice boundary: <Working on problem / Waiting for next-problem request / Paused>
- Problem ID and mode: <Stable ID; recall, discrimination, or composition>
- Attempts and disclosed assistance: <Actual attempts, exact hints or corrections, and highest hint level; None if unassisted>
- Last concluded problem: <Outcome and reference to dated evidence in plan.md or misses.md>
- Pending retests: <Target and prior evidence reference; do not prewrite a revealing prompt or solution>
- Suspended teaching resume point: <Prior phase, node, question, and context, or None>

## Context needed to resume

<Only temporary context another tool needs, such as the diagnostic step reached, hints already given, an unfamiliar word being explained, or an unverified claim.>
