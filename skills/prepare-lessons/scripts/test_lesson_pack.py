"""Synthetic behavior tests; no live display or network operations."""

import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = Path(__file__).with_name("lesson_pack.py")
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aN1cAAAAASUVORK5CYII="
)


class LessonPackTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lesson pack ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.env = os.environ.copy()
        self.write("question.md", "What is the result?\n")
        self.write("next.md", "Explain the next result.\n")
        self.write("preferences.json", '{"font_size":18}\n')
        self.write("lesson.md", "Original displayed lesson\n")
        (self.root / "page.png").write_bytes(PNG)
        self.manifest = {
            "context": {"question_id": "q1", "question_file": "question.md",
                        "preferences_file": "preferences.json"},
            "routes": [{"id": "correct", "match_notes": "Correct result with a reason",
                        "pages": [{"source": "page.png"}],
                        "next_question": {"id": "q2", "file": "next.md"}}]}
        self.write_json("manifest.json", self.manifest)
        self.decision = {"question_id": "q1", "route_id": "correct",
                         "actual_answer": "An answer with explanation.",
                         "reason": "The answer matches the required reasoning."}
        self.write_json("decision.json", self.decision)
        self.run_cli("bind", "--active", "active.json", "--question-id", "q1",
                     "--question-file", "question.md", "--preferences-file", "preferences.json",
                     "--lesson", "lesson.md")

    def write(self, name, value):
        (self.root / name).write_text(value)

    def write_json(self, name, value):
        self.write(name, json.dumps(value))

    def read_json(self, name):
        return json.loads((self.root / name).read_text())

    def run_cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.root,
                                env=self.env, capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        return json.loads(result.stderr)

    def prepare(self, *extra):
        return self.run_cli("prepare", "manifest.json", "--output", "index.json",
                            "--cache-dir", "cache", *extra)

    def show(self, *extra, ok=True):
        return self.run_cli("show", "index.json", "--active", "active.json",
                            "--decision", "decision.json", "--log", "timings.jsonl",
                            *extra, ok=ok)

    def assert_no_mutation(self, before):
        self.assertEqual((self.root / "lesson.md").read_bytes(), before[0])
        self.assertEqual((self.root / "active.json").read_bytes(), before[1])

    def snapshot(self):
        return ((self.root / "lesson.md").read_bytes(),
                (self.root / "active.json").read_bytes())

    def fake_binary(self, name, text):
        directory = self.root / "fake bin"
        directory.mkdir(exist_ok=True)
        path = directory / name
        path.write_text(f"#!{sys.executable}\n" + text)
        path.chmod(0o755)
        self.env["PATH"] = str(directory) + os.pathsep + self.env["PATH"]
        return str(path)

    def test_publish_only_advances_without_claiming_visible_success(self):
        self.prepare()
        result = self.show("--turn-start", str(time.time() - 1), "--target-seconds", "10")
        self.assertFalse(result["backend_verified"])
        self.assertIsNone(result["display_verified"])
        self.assertFalse(result["fresh_content_verified"])
        self.assertIsNone(result["target_met"])
        self.assertIsNone(result["backend_target_met"])
        self.assertIsNone(result["turn_to_backend_seconds"])
        self.assertIsNotNone(result["turn_to_publish_seconds"])
        self.assertEqual(self.read_json("active.json")["question"]["id"], "q2")
        deck = (self.root / "lesson.md").read_text()
        self.assertIn("assets/", deck)
        self.assertIn("(<", deck)  # Paths with spaces remain valid Markdown destinations.
        logs = (self.root / "timings.jsonl").read_text().splitlines()
        self.assertEqual(json.loads(logs[-1])["decision"], self.decision)

    def test_stale_question_and_preferences_do_not_publish(self):
        for name in ("question.md", "preferences.json"):
            with self.subTest(name=name):
                self.prepare()
                before = self.snapshot()
                original = (self.root / name).read_text()
                self.write(name, original + "changed")
                result = self.show(ok=False)
                self.assertEqual(result["status"], "error")
                self.assert_no_mutation(before)
                self.write(name, original)

    def test_modified_source_asset_and_next_question_are_rejected(self):
        for target in ("source", "asset", "next"):
            with self.subTest(target=target):
                self.prepare()
                index = self.read_json("index.json")
                path = {"source": self.root / "page.png",
                        "asset": Path(index["routes"][0]["assets"][0]["path"]),
                        "next": self.root / "next.md"}[target]
                original = path.read_bytes()
                before = self.snapshot()
                path.write_bytes(original + b"changed")
                self.show(ok=False)
                self.assert_no_mutation(before)
                path.write_bytes(original)

    def test_unknown_route_empty_answer_and_wrong_question_are_rejected(self):
        self.prepare()
        for change in ({"route_id": "missing"}, {"actual_answer": " "}, {"question_id": "old"}):
            with self.subTest(change=change):
                self.write_json("decision.json", {**self.decision, **change})
                before = self.snapshot()
                self.show(ok=False)
                self.assert_no_mutation(before)

    def test_changed_current_display_is_not_overwritten(self):
        self.prepare()
        self.write("lesson.md", "External display edit")
        before = self.snapshot()
        self.show(ok=False)
        self.assert_no_mutation(before)

    def test_invalid_log_destination_fails_before_publishing(self):
        self.prepare()
        (self.root / "blocked-log").mkdir()
        before = self.snapshot()
        self.show("--log", "blocked-log", ok=False)
        self.assert_no_mutation(before)

    def test_invalid_timing_values_do_not_publish(self):
        self.prepare()
        for option, value in (("--target-seconds", "nan"), ("--timeout-seconds", "inf"),
                              ("--turn-start", "nan"), ("--settle-ms", "-1")):
            with self.subTest(option=option):
                before = self.snapshot()
                self.show(option, value, ok=False)
                self.assert_no_mutation(before)

    def test_typst_render_cached_and_dependencies_invalidate_recipe(self):
        self.write("page.typ", "A synthetic page")
        self.write("dependency.txt", "first")
        fake = self.fake_binary("typst", """import base64, os, pathlib, sys
if '--version' in sys.argv:
    print('typst synthetic-test')
else:
    with open(os.environ['RENDER_COUNT'], 'a') as f: f.write('render\\n')
    pathlib.Path(sys.argv[-1]).write_bytes(base64.b64decode(os.environ['TEST_PNG']))
""")
        self.env["RENDER_COUNT"] = str(self.root / "renders.txt")
        self.env["TEST_PNG"] = base64.b64encode(PNG).decode()
        self.manifest["routes"][0]["pages"] = [{"source": "page.typ",
                                                 "dependencies": ["dependency.txt"]}]
        self.write_json("manifest.json", self.manifest)
        self.assertEqual(self.prepare("--typst", fake)["cache_hits"], 0)
        self.assertEqual(self.prepare("--typst", fake)["cache_hits"], 1)
        self.write("dependency.txt", "second")
        self.assertEqual(self.prepare("--typst", fake)["cache_hits"], 0)
        self.assertEqual(len((self.root / "renders.txt").read_text().splitlines()), 2)

    def test_batch_routes_and_duplicate_ids(self):
        second = {**self.manifest["routes"][0], "id": "clarification"}
        self.manifest["routes"].append(second)
        self.write_json("manifest.json", self.manifest)
        self.assertEqual(self.prepare()["routes"], 2)
        second["id"] = "correct"
        self.write_json("manifest.json", self.manifest)
        self.run_cli("prepare", "manifest.json", "--output", "bad.json",
                     "--cache-dir", "cache", ok=False)
        self.assertFalse((self.root / "bad.json").exists())

    def test_stale_footer_cannot_certify_visible_content_or_target(self):
        self.prepare()
        self.fake_binary("tmux", """import os, pathlib, sys
with open(os.environ['TMUX_CALLS'], 'a') as f: f.write(' '.join(sys.argv[1:])+'\\n')
if sys.argv[1] == 'display-message': print('presenterm')
if sys.argv[1] == 'capture-pane': print('Old displayed content\\n 1 / 1 ')
""")
        self.env["TMUX_CALLS"] = str(self.root / "tmux.txt")
        result = self.show("--pane", "%9", "--settle-ms", "0",
                           "--turn-start", str(time.time() - 1), "--target-seconds", "10")
        self.assertTrue(result["backend_verified"])
        self.assertIsNone(result["display_verified"])
        self.assertFalse(result["fresh_content_verified"])
        self.assertEqual(result["verification"], "backend-footer-only")
        self.assertTrue(result["backend_target_met"])
        self.assertIsNone(result["target_met"])
        self.assertIsNotNone(result["turn_to_backend_seconds"])
        state = self.read_json("active.json")
        self.assertEqual(state["question_status"], "intended-unverified")
        self.assertIsNone(state["display_verified"])
        self.assertFalse(state["fresh_content_verified"])
        self.assertNotIn("shown_at", state)
        self.assertIn("send-keys -t %9 Home", (self.root / "tmux.txt").read_text())

    def test_display_failure_rolls_back_and_logs_error(self):
        self.prepare()
        self.fake_binary("tmux", """import sys
if sys.argv[1] == 'display-message': print('presenterm')
if sys.argv[1] == 'capture-pane': print('Error loading presentation')
""")
        before = self.snapshot()
        self.show("--pane", "%9", "--settle-ms", "0", "--timeout-seconds", "0.1", ok=False)
        self.assert_no_mutation(before)
        logs = (self.root / "timings.jsonl").read_text().splitlines()
        self.assertEqual(json.loads(logs[-1])["status"], "error")


if __name__ == "__main__":
    unittest.main()
