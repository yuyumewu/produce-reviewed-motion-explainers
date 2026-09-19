#!/usr/bin/env python3
"""Deterministic project checks and targeted HyperFrames renders.

The script intentionally keeps review renders disposable under .motion-cache and
never overwrites the root composition or source media.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = ("PROJECT.md", "DESIGN.md", "scene-map.csv")
REQUIRED_COLUMNS = (
    "scene_id",
    "start_seconds",
    "end_seconds",
    "objective",
    "vo",
    "on_screen_text",
    "visual",
    "motion",
    "source",
    "risk",
    "status",
    "version",
    "notes",
)
VALID_RISKS = {"A", "B", "C"}
VALID_STATUSES = {
    "planned",
    "static-review",
    "static-approved",
    "motion-ready",
    "motion-review",
    "approved",
    "final",
    "blocked",
}
MOTION_READY = {"static-approved", "motion-ready", "motion-review", "approved", "final"}
FINAL_READY = {"approved", "final"}
AUDIO_SUFFIXES = {".aac", ".m4a", ".mp3", ".mp4", ".mov", ".wav", ".webm", ".mkv"}


def die(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 2


def project_dir(value: str) -> Path:
    return Path(value).expanduser().resolve()


def parse_rows(project: Path) -> tuple[list[dict], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    csv_path = project / "scene-map.csv"
    if not csv_path.exists():
        return [], [f"missing {csv_path}"], warnings
    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = reader.fieldnames or []
            missing = [column for column in REQUIRED_COLUMNS if column not in columns]
            if missing:
                errors.append("scene-map.csv missing columns: " + ", ".join(missing))
            rows = list(reader)
    except OSError as exc:
        return [], [f"cannot read {csv_path}: {exc}"], warnings

    seen: set[str] = set()
    previous_end: float | None = None
    for index, row in enumerate(rows, start=2):
        scene_id = (row.get("scene_id") or "").strip()
        if not scene_id:
            errors.append(f"row {index}: scene_id is empty")
        elif scene_id in seen:
            errors.append(f"row {index}: duplicate scene_id {scene_id}")
        seen.add(scene_id)
        try:
            start = float(row.get("start_seconds", ""))
            end = float(row.get("end_seconds", ""))
        except ValueError:
            errors.append(f"row {index}: start_seconds/end_seconds must be numeric")
            continue
        if start < 0 or end <= start:
            errors.append(f"row {index} ({scene_id}): invalid time range {start}–{end}")
        if previous_end is not None and start < previous_end - 1e-6:
            errors.append(f"row {index} ({scene_id}): overlaps previous scene")
        if previous_end is not None and start > previous_end + 0.05:
            warnings.append(f"row {index} ({scene_id}): timeline gap of {start - previous_end:.3f}s")
        previous_end = end
        risk = (row.get("risk") or "").strip().upper()
        if risk not in VALID_RISKS:
            errors.append(f"row {index} ({scene_id}): risk must be A, B, or C")
        status = (row.get("status") or "").strip().lower()
        if status not in VALID_STATUSES:
            errors.append(f"row {index} ({scene_id}): unknown status {status!r}")
        row["scene_id"] = scene_id
        row["start"] = start
        row["end"] = end
        row["risk_normalized"] = risk
        row["status_normalized"] = status
    return rows, errors, warnings


def check_project(project: Path, for_motion: bool = False, for_final: bool = False) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    if not project.exists():
        return die(f"project directory does not exist: {project}")
    for filename in REQUIRED_FILES:
        if not (project / filename).exists():
            errors.append(f"missing {filename}")
    rows, row_errors, row_warnings = parse_rows(project)
    errors.extend(row_errors)
    warnings.extend(row_warnings)
    if for_motion:
        for row in rows:
            if row.get("status_normalized") not in MOTION_READY:
                errors.append(
                    f"{row.get('scene_id')}: status {row.get('status_normalized')!r} is not motion-ready"
                )
    if for_final:
        if not rows:
            errors.append("scene-map.csv contains no scenes")
        for row in rows:
            if row.get("status_normalized") not in FINAL_READY:
                errors.append(
                    f"{row.get('scene_id')}: status {row.get('status_normalized')!r} is not final-ready"
                )
        index_path = project / "index.html"
        if not index_path.exists():
            errors.append("missing index.html for final assembly")
    for warning in warnings:
        print(f"WARN: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {len(rows)} scene rows validated in {project}")
    return 0


def copy_template(name: str, destination: Path, force: bool = False) -> None:
    source = SKILL_ROOT / "assets" / "templates" / name
    if destination.exists() and not force:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def init_project(project: Path, force: bool = False) -> int:
    project.mkdir(parents=True, exist_ok=True)
    for directory in ("compositions", "assets", "renders", "reviews", ".motion-cache"):
        (project / directory).mkdir(exist_ok=True)
    copy_template("PROJECT.md", project / "PROJECT.md", force)
    copy_template("DESIGN.md", project / "DESIGN.md", force)
    copy_template("scene-map.csv", project / "scene-map.csv", force)
    copy_template("feedback.md", project / "feedback.md", force)
    print(f"PASS: initialized {project}")
    print("Next: complete PROJECT.md, DESIGN.md, and scene-map.csv before authoring HTML.")
    return 0


def selected_rows(project: Path, scene_ids: str) -> tuple[list[dict], list[str], list[str]]:
    rows, errors, warnings = parse_rows(project)
    if errors:
        return [], errors, warnings
    wanted = [item.strip() for item in scene_ids.split(",") if item.strip()]
    by_id = {row["scene_id"]: row for row in rows}
    missing = [scene_id for scene_id in wanted if scene_id not in by_id]
    if missing:
        errors.append("unknown scene IDs: " + ", ".join(missing))
    chosen = [by_id[scene_id] for scene_id in wanted if scene_id in by_id]
    chosen.sort(key=lambda row: row["start"])
    return chosen, errors, warnings


def composition_for(project: Path, scene_id: str) -> Path | None:
    exact = project / "compositions" / f"{scene_id}.html"
    if exact.exists():
        return exact
    candidates = sorted((project / "compositions").glob(f"*{scene_id}*.html"))
    return candidates[0] if candidates else None


def audio_for(project: Path, explicit: str | None) -> Path | None:
    if explicit:
        candidate = Path(explicit).expanduser()
        if not candidate.is_absolute():
            candidate = project / candidate
        return candidate.resolve()
    assets = project / "assets"
    if not assets.exists():
        return None
    candidates = [
        path for path in sorted(assets.iterdir())
        if path.is_file() and path.suffix.lower() in AUDIO_SUFFIXES and "font" not in path.name.lower()
    ]
    return candidates[0] if len(candidates) == 1 else None


def write_review_host(project: Path, rows: list[dict], host_dir: Path, audio: Path | None) -> tuple[Path, float]:
    if not rows:
        raise ValueError("at least one scene is required")
    host_dir.mkdir(parents=True, exist_ok=True)
    first_start = rows[0]["start"]
    last_end = max(row["end"] for row in rows)
    duration = last_end - first_start
    body: list[str] = []
    for row in rows:
        composition = composition_for(project, row["scene_id"])
        if composition is None:
            raise FileNotFoundError(
                f"missing composition for {row['scene_id']} (expected compositions/{row['scene_id']}.html)"
            )
        source = os.path.relpath(composition, host_dir).replace(os.sep, "/")
        local_start = row["start"] - first_start
        local_duration = row["end"] - row["start"]
        body.append(
            f'<div id="{html.escape(row["scene_id"])}" data-composition-id="{html.escape(row["scene_id"])}" '
            f'data-composition-src="{html.escape(source)}" data-start="{local_start:.6f}" '
            f'data-duration="{local_duration:.6f}" data-track-index="1"></div>'
        )
    if audio and audio.exists():
        audio_src = os.path.relpath(audio, host_dir).replace(os.sep, "/")
        body.append(
            f'<audio id="review-audio" data-start="0" data-duration="{duration:.6f}" '
            f'data-media-start="{first_start:.6f}" data-track-index="2" src="{html.escape(audio_src)}"></audio>'
        )
    html_text = f'''<!doctype html>
<html><head><meta charset="utf-8"><title>Motion review</title>
<style>html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#000}}
[data-composition-id="review-host"]{{width:100vw;height:100vh;overflow:hidden}}</style></head>
<body><div id="review-host" data-composition-id="review-host" data-start="0" data-duration="{duration:.6f}" data-width="1920" data-height="1080">
{os.linesep.join(body)}
</div></body></html>
'''
    host = host_dir / "index.html"
    host.write_text(html_text, encoding="utf-8")
    return host, duration


def hf_base() -> list[str]:
    override = os.environ.get("HYPERFRAMES_CMD")
    return shlex.split(override) if override else ["npx", "hyperframes"]


def run_command(command: list[str], cwd: Path) -> int:
    print("RUN:", " ".join(shlex.quote(part) for part in command))
    result = subprocess.run(command, cwd=str(cwd), check=False)
    return result.returncode


def render_review(args: argparse.Namespace, static: bool = False) -> int:
    project = project_dir(args.project)
    check_status = check_project(project)
    if check_status:
        return check_status
    rows, errors, _ = selected_rows(project, args.scenes)
    if errors:
        return die("; ".join(errors))
    if static and len(rows) != 1:
        return die("static-review accepts exactly one scene")
    if not static:
        not_ready = [
            row["scene_id"]
            for row in rows
            if row.get("status_normalized") not in MOTION_READY
        ]
        if not_ready:
            return die("selected scenes are not motion-ready: " + ", ".join(not_ready))
    else:
        blocked = [
            row["scene_id"]
            for row in rows
            if row.get("status_normalized") == "blocked"
        ]
        if blocked:
            return die("selected scenes are blocked: " + ", ".join(blocked))
    review_name = "review-" + "-".join(row["scene_id"] for row in rows)
    host_dir = project / ".motion-cache" / review_name
    audio = audio_for(project, args.audio)
    try:
        host, _ = write_review_host(project, rows, host_dir, audio)
    except (FileNotFoundError, ValueError) as exc:
        return die(str(exc))
    if static:
        output_dir = Path(args.output).expanduser().resolve() if args.output else project / "reviews" / review_name
        output_dir.mkdir(parents=True, exist_ok=True)
        raw_dir = output_dir / "frames"
        command = hf_base() + [
            "render",
            str(project),
            "--composition",
            str(host.relative_to(project)),
            "--output",
            str(raw_dir),
            "--format",
            "png-sequence",
            "--resolution",
            "1080p",
            "--quality",
            "draft",
        ]
        code = run_command(command, project)
        if code:
            return code
        frames = sorted(raw_dir.glob("*.png"))
        if not frames:
            return die(f"no PNG frames found in {raw_dir}")
        hero = max(0, min(len(frames) - 1, int(round(float(args.hero_time) * float(args.fps)))))
        target = output_dir / f"{rows[0]['scene_id']}_{rows[0]['version']}_hero.png"
        shutil.copy2(frames[hero], target)
        print(f"PASS: static hero frame {target}")
        return 0
    output = Path(args.output).expanduser().resolve() if args.output else project / "reviews" / f"{review_name}.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    command = hf_base() + [
        "render",
        str(project),
        "--composition",
        str(host.relative_to(project)),
        "--output",
        str(output),
        "--resolution",
        "1080p",
        "--quality",
        "draft",
    ]
    code = run_command(command, project)
    if code == 0:
        print(f"PASS: targeted review {output}")
    return code


def run_hyperframes_checks(project: Path) -> int:
    for subcommand in (("lint",), ("validate",), ("inspect", "--json")):
        code = run_command(hf_base() + list(subcommand) + [str(project)], project)
        if code:
            return code
    return 0


def final_render(args: argparse.Namespace) -> int:
    project = project_dir(args.project)
    code = check_project(project, for_final=True)
    if code:
        return code
    if not args.skip_checks:
        code = run_hyperframes_checks(project)
        if code:
            return die("HyperFrames checks failed; final render was not started")
    output = Path(args.output).expanduser().resolve() if args.output else project / "renders" / "final_4k.mp4"
    if output.exists() and not args.allow_existing:
        return die(f"refusing to overwrite existing output: {output}; choose a new versioned path")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = hf_base() + [
        "render",
        str(project),
        "--output",
        str(output),
        "--resolution",
        "4k",
        "--quality",
        "delivery",
        "--strict-all",
    ]
    code = run_command(command, project)
    if code == 0:
        print(f"PASS: final 4K render {output}")
    return code


def probe(args: argparse.Namespace) -> int:
    media = Path(args.media).expanduser().resolve()
    if not media.exists():
        return die(f"media file does not exist: {media}")
    ffprobe = os.environ.get("FFPROBE") or shutil.which("ffprobe")
    if not ffprobe:
        machine = platform.machine()
        platform_dir = "darwin" if sys.platform == "darwin" else "linux"
        machine_dir = "arm64" if machine in {"arm64", "aarch64"} else "x64"
        for ancestor in (media.parent, *media.parents):
            candidates = sorted(
                ancestor.glob(
                    f"node_modules/.pnpm/ffprobe-static*/node_modules/ffprobe-static/bin/{platform_dir}/{machine_dir}/ffprobe"
                )
            )
            if candidates:
                ffprobe = str(candidates[0])
                break
    if not ffprobe:
        return die("ffprobe was not found; set FFPROBE or install ffprobe-static in the project")
    command = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration,format_name:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
        "-of",
        "json",
        str(media),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    print(json.dumps(json.loads(result.stdout), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="initialize a reusable project scaffold")
    init.add_argument("project")
    init.add_argument("--force", action="store_true", help="replace only template files")

    check = subparsers.add_parser("check", help="validate the project contract")
    check.add_argument("project")
    check.add_argument("--for-motion", action="store_true")
    check.add_argument("--for-final", action="store_true")

    for name, help_text in (("review", "render selected scene(s)"), ("static-review", "render one hero frame")):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("project")
        command.add_argument("--scenes", required=True, help="comma-separated scene IDs")
        command.add_argument("--audio", help="audio path, relative to project or absolute")
        command.add_argument("--output")
        command.add_argument("--hero-time", type=float, default=1.0, help="local seconds for static-review")
        command.add_argument("--fps", type=float, default=30.0, help="FPS used to select a hero PNG")

    final = subparsers.add_parser("final", help="render the one gated 4K master")
    final.add_argument("project")
    final.add_argument("--output")
    final.add_argument("--skip-checks", action="store_true", help="only for a previously recorded QA pass")
    final.add_argument("--allow-existing", action="store_true", help="allow a deliberate versioned overwrite")

    inspect = subparsers.add_parser("probe", help="probe media with ffprobe")
    inspect.add_argument("media")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "init":
        return init_project(project_dir(args.project), args.force)
    if args.command == "check":
        return check_project(project_dir(args.project), args.for_motion, args.for_final)
    if args.command == "review":
        return render_review(args, static=False)
    if args.command == "static-review":
        return render_review(args, static=True)
    if args.command == "final":
        return final_render(args)
    if args.command == "probe":
        return probe(args)
    return die(f"unknown command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
