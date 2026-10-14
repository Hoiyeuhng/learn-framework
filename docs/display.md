# Optional lesson display

The AI coding tool configures the display for the learner's machine. Text-only
learning needs no renderer. For a separate lesson pane, these are the tools used:

| Tool | Purpose |
| --- | --- |
| presenterm | Show and reload a Markdown lesson in the terminal |
| Pandoc and Typst | Render LaTeX math for presenterm |
| Node.js/npm and Mermaid CLI (`mmdc`) | Render Mermaid diagrams |
| Chrome/Chromium | Browser used by Mermaid CLI |
| tmux | Optional chat and lesson panes in one terminal window |
| A terminal with image support | Show the rendered equations and diagrams |

Use the learner's preferred package manager or official installers. Homebrew is
optional. Inspect installed commands before adding tools. Configure `mmdc` to
use an available browser; `PUPPETEER_EXECUTABLE_PATH` can select its executable.

The original display was exercised with presenterm 0.16.1, Pandoc 3.12.1,
Typst 0.15.1, and Mermaid CLI 11.17.0. These are reference versions, not enforced
requirements. Verify settings against the versions installed on the machine.

## Lesson layout

When the learner wants side-by-side panes, keep chat on the left and the complete
lesson on the right in the same tmux window. Reuse existing panes without
interrupting the chat process. Check tmux's `allow-passthrough` setting when
images do not appear; changing it affects the session.

Save the active lesson in `topics/<topic>/lesson.md`. Launch presenterm directly
from the private workspace root, with the intended display configuration.
Use a topic's `display.yaml` when one exists; otherwise use the workspace's
`display.yaml`. Resolve relative paths from that workspace root.

Keep the explanation, formulas, input values, and question together. Use
`mermaid +render` for diagrams and `latex +render` for equations. The
[synthetic example](../examples/lesson.md) shows both. Keep sources in Markdown.

## Display settings

The AI can adapt this example into the private workspace's `display.yaml`:

```yaml
defaults:
  theme: dark
  image_protocol: auto
  max_columns: 120
  max_rows: 60
  validate_overflows: always
mermaid:
  config_path: framework/display/mermaid.json
  scale: 2
```

A local Ghostty/tmux setup can use `kitty-local`. Use `kitty-remote` when the
renderer and terminal do not share a filesystem. Other terminals may need a
different protocol. Check terminal support before selecting one.

## Verification and troubleshooting

Use the synthetic example to check the configured display in the actual
terminal. Confirm that both its diagram and equation appear and that their
labels are readable. Finding the tool commands alone does not verify graphics.

If text appears but equations are blank, check the image protocol, tmux
passthrough, and the renderer environment. Unset `NO_COLOR` for presenterm:
Kitty image placeholders encode image IDs as colors. Avoid output filters that
strip escape sequences. Strange symbols can be image placeholders displayed
without their image.

If a diagram is too small, enlarge the pane or simplify it. Do not fit an entire
lesson into one dense image.

Configuration is version-sensitive. Presenterm 0.16.1 uses
[`mermaid.config_path`](https://github.com/mfontanini/presenterm/blob/v0.16.1/config-file-schema.json).
See [presenterm images](https://mfontanini.github.io/presenterm/features/images.html),
[math](https://mfontanini.github.io/presenterm/features/code/latex.html), and
[Mermaid](https://mfontanini.github.io/presenterm/features/code/mermaid.html) for the
installed version's behavior.
