"""Integration tests use disposable Git workspaces, never real learning records."""
import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

FRAMEWORK = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("learn", str(FRAMEWORK / "bin/learn"))
spec = importlib.util.spec_from_loader(loader.name, loader)
learn = importlib.util.module_from_spec(spec)
loader.exec_module(learn)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="learn-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace with spaces"
        self.root.mkdir()
        self.root = self.root.resolve()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "framework").symlink_to(FRAMEWORK, target_is_directory=True)

    def make_lesson(self):
        topic = self.root / "topics/demo"
        topic.mkdir(parents=True)
        (topic / "lesson.md").write_text("A synthetic lesson.\n")
        return topic

    def test_workspace_from_nested_directory(self):
        topic = self.make_lesson()
        self.assertEqual(learn.workspace(topic), self.root.resolve())

    def test_refuses_public_framework_as_workspace(self):
        with self.assertRaisesRegex(ValueError, "outside the framework"):
            learn.workspace(FRAMEWORK)

    def test_refuses_missing_or_wrong_framework(self):
        (self.root / "framework").unlink()
        with self.assertRaisesRegex(ValueError, "Initialize"):
            learn.workspace(self.root)
        (self.root / "framework").mkdir()
        (self.root / "framework/AGENTS.md").write_text("unrelated")
        with self.assertRaisesRegex(ValueError, "pinned version"):
            learn.workspace(self.root)

    def test_setup_is_idempotent(self):
        with contextlib.redirect_stdout(io.StringIO()):
            learn.setup(self.root)
            first = {p.name: p.read_bytes() for p in self.root.glob("*.md")}
            learn.setup(self.root)
        self.assertEqual(first, {p.name: p.read_bytes() for p in self.root.glob("*.md")})
        self.assertEqual(set(first), {"AGENTS.md", "CLAUDE.md", "preferences.md"})
        self.assertIn(b"@framework/AGENTS.md", first["AGENTS.md"])
        self.assertFalse((self.root / "topics").exists())

    def test_setup_preflights_all_files_before_writing(self):
        (self.root / "preferences.md").write_text("Keep this personal preference.")
        with self.assertRaisesRegex(ValueError, "will not overwrite"):
            learn.setup(self.root)
        self.assertFalse((self.root / "AGENTS.md").exists())
        self.assertEqual((self.root / "preferences.md").read_text(), "Keep this personal preference.")

    def test_setup_refuses_symlink_destination(self):
        target = self.root / "keep.md"
        target.write_text("Keep this file.")
        (self.root / "AGENTS.md").symlink_to(target)
        with self.assertRaises(ValueError):
            learn.setup(self.root)
        self.assertEqual(target.read_text(), "Keep this file.")

    def dry_run(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            learn.present(self.root, "demo", dry_run=True)
        return json.loads(output.getvalue())

    def test_default_display_keeps_workspace_and_removes_no_color(self):
        self.make_lesson()
        with patch.dict(os.environ, {"NO_COLOR": "1"}):
            result = self.dry_run()
        self.assertEqual(result["cwd"], str(self.root))
        self.assertFalse(result["no_color"])
        self.assertIn(str(FRAMEWORK / "display/mermaid.json"), result["config"])
        self.assertIn("config_path:", result["config"])
        self.assertEqual(result["command"][-1], str(self.root / "topics/demo/lesson.md"))

    def test_topic_config_wins_over_workspace_config(self):
        topic = self.make_lesson()
        (self.root / "display.yaml").write_text("defaults: {theme: light}\n")
        self.assertEqual(self.dry_run()["command"][2], str(self.root / "display.yaml"))
        (topic / "display.yaml").write_text("mermaid: {config_path: topics/demo/mermaid.json}\n")
        result = self.dry_run()
        self.assertEqual(result["command"][2], str(topic / "display.yaml"))
        self.assertIn("topics/demo/mermaid.json", result["config"])

    def test_rejects_invalid_topic_and_missing_lesson(self):
        for name in ("../private", "demo/a", "demo;echo", "Demo", ""):
            with self.assertRaises(ValueError):
                learn.present(self.root, name, dry_run=True)
        with self.assertRaisesRegex(ValueError, "No lesson"):
            learn.present(self.root, "absent", dry_run=True)

    def test_renderer_receives_live_config_and_clean_environment(self):
        self.make_lesson()
        def renderer(command, *, cwd, env):
            self.assertTrue(Path(command[2]).is_file())
            self.assertEqual(cwd, self.root)
            self.assertNotIn("NO_COLOR", env)
            return 7
        with patch.object(learn.subprocess, "call", side_effect=renderer) as call:
            with patch.object(learn.shutil, "which", return_value="/tools/presenterm"):
                with patch.dict(os.environ, {"NO_COLOR": "1"}):
                    self.assertEqual(learn.present(self.root, "demo"), 7)
        self.assertFalse(Path(call.call_args.args[0][2]).exists())

    def test_doctor_reports_missing_required_files(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(learn.doctor(self.root))
            learn.setup(self.root)
            self.assertFalse(learn.doctor(self.root))


if __name__ == "__main__":
    unittest.main()
