---
name: prepare-lessons
description: Prepare and reuse lesson pages and conditional feedback for an established tutoring session when the learner requests faster, pre-prepared delivery. Keep actual answer evaluation separate from speculative preparation.
---

# Prepare lessons before the next reply

Use this workflow for requested lesson preparation or an established prepared-lesson session. Keep the workspace's teaching rules, approved plan, and evidence standards. Read its preferences for language, layout, pacing, and any response-time target; this skill supplies no universal target or display style.

## Prepare a useful batch

1. Restore the actual displayed question and its conditions from the topic state. Locate the dedicated worktree. Read the relevant changed records, not the entire history on each reply.
2. Prepare a bounded stretch of the approved plan. Include prerequisite explanations and likely feedback branches, not just the next happy-path question. Use preparation agents only when authorized; give them separate private output directories and prohibit active-state or display changes.
3. Separate visible lesson assets from hidden answers, evaluation criteria, and validation results. Each branch identifies the question it answers, its semantic acceptance conditions, any assistance supplied, and its next question. A rendered draft is not a displayed question.
4. Produce the final reusable assets now. Verify new facts and code once, preserve the relevant source/version evidence, render pages, and inspect layout. Respect the workspace's code grouping, line numbering, and page preferences. Avoid code wrapping that makes displayed line numbers diverge from source lines.
5. Bind the prepared pack to the question content, display preferences, source files, and rendering dependencies. A change to any of these invalidates the affected assets. Keep packs and timing logs in the private workspace, never in the shared framework.

Use the helper in `scripts/lesson_pack.py` for content-hashed preparation and guarded publication. Read [the pack format and commands](references/pack-format.md) when building or operating a pack.

## On the learner's reply

The short path is **read current question → assess actual reply → choose prepared branch → display → save evidence**.

- Match meaning, not keywords. Check the conclusion and its reason. A correct conclusion with a faulty explanation is not independent mastery.
- Treat a clarification, display request, or response to the previously displayed question as such. Never grade against a speculative next question.
- Use a prepared branch only if its question, assumptions, and preferences still match. Otherwise prepare a focused replacement. Do not force an unexpected reply into the closest cached answer to meet a latency target.
- Reuse unchanged code checks and rendered assets. Avoid rereading stable documentation, regenerating the deck, or requesting another review on the delivery path.
- Publish only completed assets. The helper atomically replaces the deck and uses content-hashed filenames to avoid stale image reuse. When using a pane, restore the configured initial page after reload and verify the backend status. Do not claim pixel-level verification from a footer check.
- Record the actual reply, evaluation, assistance, and new pending question after display. Keep one active question. Speculation never becomes learner evidence. Batch remote bookkeeping at the workspace's authorized checkpoints.

## Refill and measure

After delivering the selected page, refill consumed branches or prepare additional approved material. Keep preparation reusable across turns and sessions; preserve provenance so only changed material needs revalidation.

Time preparation, verification, rendering, and publication separately. Record both the local delivery duration and a reply-to-display duration when a trustworthy reply timestamp is available. A local subsecond publish does not prove an end-to-end target was met. Record misses and their causes; preserve the learner's chosen model settings.

Do not call unaccounted wall time “thinking.” It can contain model generation, planning, transport, scheduling, and other work that local command timers do not separate. This workflow reduces repeated work; it does not guarantee a response time or run a background service by itself.
