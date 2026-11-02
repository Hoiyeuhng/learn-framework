# Prepared lesson packs

The helper uses Python's standard library. Typst is needed only when a page source
is `.typ`; `.png` pages are accepted directly. Pane verification additionally
needs tmux and an existing presenterm pane. The helper does not install tools,
create panes, change fonts, or assess an answer's meaning.

Run the commands in the private topic worktree. All manifests, answers, generated
assets, active-state files, and logs belong there or in another private directory.
Do not put real lesson packs in this public skill directory.

## Files and responsibility

- `question.md`: the exact question currently displayed, including its conditions.
- `preferences.md`: the workspace's authoritative preferences file. Fingerprint
  this actual file so later changes invalidate a pack. If rendering also uses a
  derived profile, include that profile among the page dependencies; do not guard
  only a snapshot that can silently become stale.
- `manifest.json`: speculative routes, their page sources, and next questions.
- `index.json`: generated fingerprints and prepared asset locations.
- `active.json`: the intended published question and current deck fingerprint.
- `decision.json`: the tutor's assessment of the actual reply and selected route.
- `timings.jsonl`: local preparation and publication measurements.

A route's `match_notes` describe when it fits; they are not an automatic classifier.
Check the learner's reasoning and the exact displayed question before selecting it.
Missing or uncertain matches require an appropriate clarification or new preparation.

## Prepare

Create source pages in the workspace's established format. For Typst pages, declare
referenced diagrams, images, or shared style files in `dependencies`. Validation
evidence records code checks and inspection; a successful compile alone does not
establish correctness or readability.

```json
{
  "context": {
    "question_id": "area-1",
    "question_file": "question.md",
    "preferences_file": "preferences.md"
  },
  "routes": [
    {
      "id": "correct-with-reason",
      "match_notes": "Correct area and multiplication reasoning; no hints needed.",
      "pages": [
        {"source": "ready-feedback.typ", "dependencies": ["style.typ"]}
      ],
      "next_question": {"id": "area-2", "file": "next-question.md"},
      "evidence": {"content_review": "checked", "layout_review": "checked"}
    }
  ]
}
```

```sh
python path/to/lesson_pack.py prepare manifest.json \
  --output index.json --cache-dir prepared-assets --log timings.jsonl
```

Prepare several routes together: correct with reasoning, incomplete reasoning,
expected errors, and prerequisite clarification. Include further approved lesson
steps when useful. Each route still targets one actual question version.

The helper caches complete rendered files under content-derived names. Changed
input, dependencies, preferences, or question text requires preparing a new index.
An unselected route and its hidden evaluation evidence are not learning progress.

## Bind the existing question

Do this when adopting the helper for an already-running lesson. Inspect the current
pane and question first. Binding records an explicit bootstrap assertion; it is not
proof that the learner saw the question.

```sh
python path/to/lesson_pack.py bind \
  --active active.json --question-id area-1 --question-file question.md \
  --preferences-file preferences.md --lesson lesson.md --log timings.jsonl
```

Do not rebind on every reply to bypass a stale-context error. Resolve why the
question, preferences, or lesson file changed.

## Select and display

After the actual reply, make the smallest sufficient semantic assessment. Store
only the needed evidence in a private decision file:

```json
{
  "question_id": "area-1",
  "route_id": "correct-with-reason",
  "actual_answer": "28 square units; multiply width by height.",
  "reason": "The result and reasoning meet this question's criteria."
}
```

```sh
python path/to/lesson_pack.py show index.json \
  --active active.json --decision decision.json --pane %0 \
  --log timings.jsonl
```

Use the observed pane ID, not the illustrative `%0`. The helper checks fingerprints,
publishes a complete deck atomically, allows the watcher to reload, and resets to
the first page. It checks the pane command and page footer; that is backend status,
not a screenshot inspection. When no pane is supplied, publication is explicitly
reported as not display-verified.

After success, the intended identity advances to the selected route's next question.
This is publication state, not proof that the learner saw the new content. Resolve
any report of an old display or an answer to an older question before grading.
Copy the actual answer, assistance, verdict, and resume point into the normal topic
records. Do this after display so bookkeeping is not on the critical path. The
decision log does not replace those records.

## Timing and failures

Supply `--turn-start` only with a trustworthy Unix timestamp for the request start.
Set `--target-seconds` only from the learner's requested target. Without a request
timestamp, the helper can report local publication duration but not end-to-end
reply latency. A successful local benchmark is not proof of meeting the full target.

`backend_verified` reports the footer/error check. `display_verified` and
`target_met` remain unknown because a matching footer cannot prove fresh pixels.
`turn_to_publish_seconds` and `turn_to_backend_seconds` report the available
milestones; `backend_target_met` only evaluates that backend milestone against
the target. It does not certify the learner-visible target.

Preparation and publication log separate measured phases. Keep model preparation,
reasoning, transport, and other unmeasured intervals unattributed. Do not subtract
tool time and label the remainder pure thought.

Stale question, changed preferences, missing/changed source or assets, and an
inconsistent active deck must fail before publication. Backend display failure
must not be reported as verified success. Inspect the result, preserve evidence,
and repair the specific issue. Do not repeatedly overwrite the active question or
force a guessed route to satisfy the latency target.
