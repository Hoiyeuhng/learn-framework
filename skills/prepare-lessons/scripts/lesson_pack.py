#!/usr/bin/env python3
"""Prepare immutable lesson images and publish an explicitly selected route.

This helper never grades an answer. Manifests, decisions, active state, and logs
belong in the caller's private workspace, not in the skill distribution.
"""

import argparse
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

VERSION = 1
PNG = b"\x89PNG\r\n\x1a\n"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def resolve(base, path):
    return (base / path).resolve()


def fingerprint(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": digest(path.read_bytes())}


def check(item):
    if fingerprint(item["path"]) != item:
        raise ValueError(f"stale or modified input: {item['path']}")


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def save(path, obj):
    atomic(path, (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode())


class Run:
    def __init__(self, action, log=None):
        self.action, self.log = action, log
        self.started = time.perf_counter()
        self.phases = {}

    @contextmanager
    def phase(self, name):
        start = time.perf_counter()
        try:
            yield
        finally:
            self.phases[name] = self.phases.get(name, 0) + time.perf_counter() - start

    def finish(self, status, **fields):
        record = {"operation": self.action, "status": status,
                  "recorded_at": time.time(),
                  "elapsed_seconds": time.perf_counter() - self.started,
                  "phase_seconds": self.phases, **fields}
        if self.log:
            path = Path(self.log)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record


def question(base, data):
    if not isinstance(data.get("id"), str) or not data["id"].strip():
        raise ValueError("question id is required")
    return {"id": data["id"], "file": fingerprint(resolve(base, data["file"]))}


def bind(args, run):
    with run.phase("bind"):
        record = {"schema_version": VERSION,
                  "question": question(Path.cwd(), {"id": args.question_id,
                                                     "file": args.question_file}),
                  "preferences": fingerprint(args.preferences_file),
                  "lesson": fingerprint(args.lesson),
                  "origin": "manual_binding", "question_status": "manually-bound",
                  "backend_verified": False, "display_verified": None,
                  "fresh_content_verified": False}
        save(args.active, record)
    return {"active": str(Path(args.active).resolve()), "origin": "manual_binding"}


def image_asset(source, inputs, cache, args, run, renderer):
    recipe = digest(json.dumps({"inputs": inputs, "renderer": renderer,
                                "ppi": args.ppi, "version": VERSION},
                               sort_keys=True).encode())
    receipt = cache / "recipes" / f"{recipe}.json"
    if receipt.exists():
        asset = load(receipt)
        try:
            check(asset)
            return asset, True
        except (OSError, ValueError):
            pass
    if source.suffix.lower() == ".typ":
        with tempfile.TemporaryDirectory(dir=cache) as temporary:
            output = Path(temporary) / "page.png"
            with run.phase("render"):
                subprocess.run([args.typst, "compile", "--format", "png", "--ppi",
                                str(args.ppi), str(source), str(output)],
                               check=True, capture_output=True, text=True)
            data = output.read_bytes()
    elif source.suffix.lower() == ".png":
        with run.phase("copy"):
            data = source.read_bytes()
    else:
        raise ValueError("page source must be .typ or .png")
    with run.phase("cache_write"):
        if not data.startswith(PNG):
            raise ValueError("renderer did not produce a PNG")
        target = cache / "assets" / f"{digest(data)}.png"
        if target.exists() and target.read_bytes() != data:
            raise ValueError(f"corrupt immutable asset: {target}")
        if not target.exists():
            atomic(target, data)
        asset = fingerprint(target)
        save(receipt, asset)
        return asset, False


def prepare(args, run):
    if args.ppi <= 0:
        raise ValueError("ppi must be positive")
    base = Path(args.manifest).resolve().parent
    cache = Path(args.cache_dir).resolve()
    cache.mkdir(parents=True, exist_ok=True)
    manifest = load(args.manifest)
    with run.phase("validate"):
        context = manifest["context"]
        context = {"question": question(base, {"id": context["question_id"],
                                               "file": context["question_file"]}),
                   "preferences": fingerprint(resolve(base, context["preferences_file"]))}
        routes = manifest["routes"]
        ids = [route["id"] for route in routes]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError("route ids must be nonempty and unique")
        if any(not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name) for name in ids):
            raise ValueError("route ids must use lowercase letters, numbers, and hyphens")
    renderer = "png-copy"
    if any(Path(page["source"]).suffix.lower() == ".typ"
           for route in routes for page in route["pages"]):
        renderer = subprocess.run([args.typst, "--version"], check=True,
                                  capture_output=True, text=True).stdout.strip()
    prepared, hits = [], 0
    for route in routes:
        if not route["pages"] or not route.get("match_notes"):
            raise ValueError("each route needs pages and semantic match_notes")
        next_question = question(base, route["next_question"])
        item = {"id": route["id"], "match_notes": route["match_notes"],
                "next_question": next_question, "assets": [], "inputs": [],
                "evidence": route.get("evidence", [])}
        for page in route["pages"]:
            source = resolve(base, page["source"])
            inputs = [fingerprint(source)] + [fingerprint(resolve(base, dep))
                                              for dep in page.get("dependencies", [])]
            item["inputs"].extend(inputs)
            asset, hit = image_asset(source, inputs + [context["preferences"]],
                                     cache, args, run, renderer)
            item["assets"].append(asset)
            hits += hit
        prepared.append(item)
    index = {"schema_version": VERSION, "context": context, "routes": prepared,
             "prepared_at": time.time()}
    with run.phase("write_index"):
        save(args.output, index)
    return {"index": str(Path(args.output).resolve()), "routes": len(prepared),
            "pages": sum(len(r["assets"]) for r in prepared), "cache_hits": hits}


@contextmanager
def lock(active):
    path = Path(str(active) + ".lock")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    try:
        yield
    finally:
        path.unlink(missing_ok=True)


def tmux(*args):
    return subprocess.run(["tmux", *args], check=True, capture_output=True,
                          text=True).stdout


def verify_backend(pane, count, settle, timeout):
    """Check process/footer only: this does not prove fresh pixels were shown."""
    if tmux("display-message", "-p", "-t", pane,
            "#{pane_current_command}").strip() != "presenterm":
        raise ValueError("target pane is not running presenterm")
    time.sleep(settle)
    tmux("send-keys", "-t", pane, "Home")
    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        capture = tmux("capture-pane", "-p", "-t", pane)
        if tmux("display-message", "-p", "-t", pane,
                "#{pane_current_command}").strip() != "presenterm":
            raise ValueError("presentation exited during display verification")
        has_error = re.search(r"error loading presentation|could not load image|"
                              r"no such file or directory", capture, re.I)
        if not has_error and re.search(rf"(?m)^\s*1\s*/\s*{count}\s*$", capture):
            return
        time.sleep(0.05)
    raise ValueError("display verification timed out; active question was not advanced")


def show(args, run):
    if args.settle_ms < 0 or not math.isfinite(args.timeout_seconds) or args.timeout_seconds <= 0:
        raise ValueError("display timing values must be nonnegative with a positive timeout")
    if args.turn_start is not None and not 0 < args.turn_start <= time.time():
        raise ValueError("turn-start must be an observed past epoch timestamp")
    if args.target_seconds is not None and (
            not math.isfinite(args.target_seconds) or args.target_seconds <= 0):
        raise ValueError("target-seconds must be positive")
    with lock(args.active):
        with run.phase("validate"):
            active, index, decision = load(args.active), load(args.index), load(args.decision)
            if index.get("schema_version") != VERSION or active.get("schema_version") != VERSION:
                raise ValueError("unsupported schema version")
            if not all(isinstance(decision.get(k), str) and decision[k].strip()
                       for k in ("question_id", "route_id", "actual_answer", "reason")):
                raise ValueError("decision requires question_id, route_id, actual_answer, and reason")
            if active["question"] != index["context"]["question"] or \
                    decision["question_id"] != active["question"]["id"]:
                raise ValueError("stale question: decision, active state, and pack must agree")
            if active["preferences"] != index["context"]["preferences"]:
                raise ValueError("stale preferences: bind and prepare again")
            for item in (active["question"]["file"], active["preferences"], active["lesson"]):
                check(item)
            route = next((r for r in index["routes"] if r["id"] == decision["route_id"]), None)
            if route is None:
                raise ValueError("unknown route")
            for item in route["inputs"] + route["assets"] + [route["next_question"]["file"]]:
                check(item)
            if args.pane and tmux("display-message", "-p", "-t", args.pane,
                                  "#{pane_current_command}").strip() != "presenterm":
                raise ValueError("target pane is not running presenterm")
            lesson = Path(active["lesson"]["path"])
            previous = lesson.read_bytes()
            if any(any(char in a["path"] for char in "<>\r\n") for a in route["assets"]):
                raise ValueError("asset path contains unsupported Markdown delimiters")
            deck = "\n\n<!-- end_slide -->\n\n".join(
                f"![image:width:100%](<{Path(a['path']).as_posix()}>)" for a in route["assets"]
            ).encode() + b"\n"
        try:
            with run.phase("publish"):
                atomic(lesson, deck)
            published_at = time.time()
            backend_at = None
            if args.pane:
                with run.phase("backend_reload_check"):
                    verify_backend(args.pane, len(route["assets"]),
                                   args.settle_ms / 1000, args.timeout_seconds)
                backend_at = time.time()
            advanced = {"schema_version": VERSION, "question": route["next_question"],
                        "preferences": active["preferences"], "lesson": fingerprint(lesson),
                        "origin": "prepared_route", "question_status": "intended-unverified",
                        "backend_verified": bool(args.pane), "display_verified": None,
                        "fresh_content_verified": False,
                        "verification": "backend-footer-only" if args.pane else "publish-only",
                        "published_at": published_at, "backend_checked_at": backend_at,
                        "route_id": route["id"]}
            with run.phase("record_state"):
                save(args.active, advanced)
        except Exception:
            # Do not overwrite a concurrent external edit during rollback.
            if lesson.read_bytes() == deck:
                atomic(lesson, previous)
            raise
        publication = None if args.turn_start is None else published_at - args.turn_start
        backend = None if args.turn_start is None or backend_at is None else backend_at - args.turn_start
        return {"route_id": route["id"], "decision": decision,
                "intended_question_id": advanced["question"]["id"],
                "backend_verified": bool(args.pane), "display_verified": None,
                "fresh_content_verified": False,
                "verification": advanced["verification"],
                "turn_to_publish_seconds": publication,
                "turn_to_backend_seconds": backend,
                "target_seconds": args.target_seconds,
                "target_met": None,
                "backend_target_met": (backend <= args.target_seconds)
                if backend is not None and args.target_seconds is not None else None}


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="operation", required=True)
    p = sub.add_parser("bind", help="explicitly bind the current question and display")
    for name in ("active", "question-id", "question-file", "preferences-file", "lesson"):
        p.add_argument("--" + name, required=True)
    p = sub.add_parser("prepare", help="render private manifest routes before a reply")
    p.add_argument("manifest")
    p.add_argument("--output", required=True)
    p.add_argument("--cache-dir", required=True)
    p.add_argument("--typst", default="typst")
    p.add_argument("--ppi", type=int, default=144)
    p = sub.add_parser("show", help="publish one explicitly selected prepared route")
    p.add_argument("index")
    for name in ("active", "decision"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--pane")
    p.add_argument("--settle-ms", type=int, default=650)
    p.add_argument("--timeout-seconds", type=float, default=4)
    p.add_argument("--turn-start", type=float)
    p.add_argument("--target-seconds", type=float)
    for p in sub.choices.values():
        p.add_argument("--log", help="private JSONL measurement log")
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    run = Run(args.operation, args.log)
    try:
        if args.log:
            path = Path(args.log)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8"):
                pass  # Fail before publishing when the audit destination is invalid.
        result = {"bind": bind, "prepare": prepare, "show": show}[args.operation](args, run)
        print(json.dumps(run.finish("ok", **result), ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        message = str(error)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            message += ": " + str(error.stderr).strip()
        try:
            record = run.finish("error", error=message)
        except OSError as log_error:
            run.log = None
            record = run.finish("error", error=message, log_error=str(log_error))
        print(json.dumps(record, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
