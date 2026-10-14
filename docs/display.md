# Optional lesson display

Text-only learning needs no renderer. For a lesson pane, install presenterm,
Pandoc, and Typst. Install Node.js/npm if you need Mermaid diagrams.
Use a terminal that supports presenterm's image protocols.

Install these tools with your preferred package manager or their official
installers. Make their commands available in `PATH`. Homebrew is one option on
macOS; it is not required by the framework or its checks.

For example, if you already use Homebrew on macOS:

```sh
brew install presenterm pandoc typst tmux node
```

After installing the tools by your chosen method, run:

```sh
./framework/bin/setup-mermaid
./framework/bin/learn doctor --render
```

Skip `setup-mermaid` if you already installed `mmdc` by another method. Install
tmux only if you want the pane layout described below.

`setup-mermaid` installs Mermaid CLI 11.17.0 in the user cache, outside both repos.
It reuses Chrome on macOS when available. Otherwise Puppeteer can download its
browser. Set `PUPPETEER_EXECUTABLE_PATH` to use another installed browser. The
helper uses an existing `mmdc` command first, then the pinned cache installation.
It also recognizes the older `~/.cache/learn/mermaid-cli-11.17.0` cache.

The extracted configuration was exercised with presenterm 0.16.1, Pandoc 3.12.1,
Typst 0.15.1, and Mermaid CLI 11.17.0. Package manager versions can differ.

## Keep chat left and lesson right

In your existing tmux window, create a pane on the right. Keep the chat process
running on the left. Run these commands in the right pane, from the learning
worktree:

```sh
tmux set-option -g allow-passthrough on
./framework/bin/learn present your-topic
```

The tmux command changes a session-wide option. The helper does not run it for
you. Presenterm reloads `topics/your-topic/lesson.md` when it changes. Keep the
explanation, formulas, given values, and active question together in that file.
Chat can stay short: feedback and coordination belong there.

## Smoke test

In a learning worktree, use a temporary topic with no private records:

```sh
mkdir -p topics/display-check
cp framework/examples/lesson.md topics/display-check/lesson.md
./framework/bin/learn present display-check
```

Check that you see the diagram and the equation, then press `q`. Remove the
synthetic lesson when you no longer need it. Run this check in the actual terminal;
command detection alone cannot prove that terminal graphics work.

Use `mermaid +render` for diagrams and `latex +render` for equations. The example
shows both. Keep the original Markdown as the source.

## Display settings and troubleshooting

The helper uses `topics/<topic>/display.yaml` when present. Otherwise it uses a
workspace-root `display.yaml`, then the built-in defaults. Relative paths in
existing configurations resolve from the workspace root. Existing topic launchers
continue to work; new lessons can use the shared helper directly.

For a local Ghostty/tmux setup, a private `display.yaml` can contain:

```yaml
defaults:
  theme: dark
  image_protocol: kitty-local
  max_columns: 120
  max_rows: 60
  validate_overflows: always
mermaid:
  config_path: framework/display/mermaid.json
  scale: 2
```

Use `kitty-remote` when the renderer and terminal do not share a filesystem.
Other terminals may need a different protocol. Start with `auto`, the default.

If text appears but equations are blank, check the image protocol and tmux
passthrough. The helper removes `NO_COLOR` from the renderer environment: Kitty
image placeholders use color values to identify images. Do not pipe the output
through a tool that strips escape sequences. A block of strange symbols can mean
that the terminal is showing image placeholders without the image.

If the diagram is too small, enlarge the pane or simplify the diagram. Keep labels
readable. Avoid fitting a complete lesson into one dense image.

Configuration is version-sensitive. The tested presenterm version uses
[`mermaid.config_path`](https://github.com/mfontanini/presenterm/blob/v0.16.1/config-file-schema.json); verify the matching version's schema before changing it.
See [presenterm images](https://mfontanini.github.io/presenterm/features/images.html),
[math](https://mfontanini.github.io/presenterm/features/code/latex.html), and
[Mermaid](https://mfontanini.github.io/presenterm/features/code/mermaid.html).
