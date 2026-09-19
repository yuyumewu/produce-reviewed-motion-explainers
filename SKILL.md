---
name: produce-reviewed-motion-explainers
description: Build and revise narrated, scene-based motion explainers in HyperFrames with gated static approvals, local review renders, and one final delivery export. Use for institutional, research, policy, data, or educational videos; not for generic live-action editing or one-off social clips.
---

# Produce reviewed motion explainers

Use this skill for a controlled, reusable production workflow in which meaning is approved before appearance, appearance before motion, and motion before final export.

## Required route and tools

Lock the production route before authoring:

- `Compose`: default for deterministic HTML/SVG/CSS explainers, charts, data graphics, titles, and transitions.
- `Generate`: only when the brief genuinely needs generated imagery or footage.
- `Edit`: only for bounded changes to supplied footage.
- `Hybrid`: when supplied media and designed compositions must be assembled together.

Use HyperFrames for the composition, GSAP for deterministic motion, and FFmpeg/ffprobe for media assembly and QA. Read the installed HyperFrames and HyperFrames CLI skills when authoring or rendering. Do not install a second motion engine unless the user explicitly requests a different runtime or the project has an existing dependency that must be preserved.

## Project contract

Before writing composition HTML, create or inspect:

1. `PROJECT.md` — objective, audience, route, source media, audio policy, delivery targets, and scope boundaries.
2. `DESIGN.md` — palette, typography, layout language, motion language, references, and anti-patterns.
3. `scene-map.csv` — the source of truth for scene timing, copy, evidence, assets, risk, status, and versions.

Use the templates in `assets/templates/` when starting a project. The scene map must contain at least:

`scene_id,start_seconds,end_seconds,objective,vo,on_screen_text,visual,motion,source,risk,status,version,notes`

Scene IDs are stable. Do not renumber approved scenes because another scene changed.

## Approval gates

- Gate 1: script and claims approved.
- Gate 2: voice-over approved and protected according to `PROJECT.md`.
- Gate 3: visual identity approved through 2–3 representative style frames.
- Gate 4: static scene approval. Type C scenes require individual hero-frame approval; Type B scenes may be approved in batches of 3–4; Type A title/transition scenes may pass through Studio inspection.
- Gate 5: final motion and audio approval.

Risk classes:

- Type A: title cards, simple transitions, non-factual decoration.
- Type B: conceptual diagrams, ordinary comparisons, general process graphics.
- Type C: statistics, scientific thresholds, methodology definitions, policy claims, named institutions, market claims, or other high-cost factual scenes.

Never animate a Type C scene whose static content is not marked `static-approved` or `motion-ready`. Never run final export while any required scene is not `approved` or `final`.

## Modular composition rules

Build each scene as an independent local-time composition. The root `index.html` should assemble scenes, the protected audio track, and transitions; it should not contain all scene-specific logic. A scene edit must not regenerate or overwrite approved scenes.

Keep all factual text, numbers, labels, URLs, and charts editable. If imagery is generated, it must not contain final text, numbers, logos, watermarks, or invented factual marks.

## Efficient render policy

This is the default unless the user explicitly asks for another output:

- Static review: hero-frame PNGs only for scenes requiring approval.
- Motion review: render only changed scenes or a contiguous changed batch at 1920×1080, `draft` quality.
- Full pacing: use HyperFrames Studio; do not automatically render a full-length 1080p file.
- Final delivery: after Gate 5, render one 3840×2160 MP4 at delivery quality.
- Do not create both full 4K and full 1080p by default. Do not create unrequested segment reviews, subtitles, WebM files, or contact sheets.

Use `scripts/motion_workflow.py` for `init`, `check`, `static-review`, `review`, `final`, and `probe`. It creates temporary review hosts under the project cache and never replaces the main composition or source media.

## Verification

Before review, run HyperFrames `lint`, `validate`, and `inspect`; for substantial animation changes also run the animation map. Check scene boundaries, overflow, contrast, transition timing, text readability, protected audio behavior, and logo/branding constraints from `DESIGN.md`.

Before delivery, use `probe`/ffprobe to verify resolution, frame rate, duration, streams, and codec. Report exactly which outputs were produced. If a requirement is not specified in `PROJECT.md`, stop and state the assumption instead of silently changing the audio or delivery target.

For detailed contracts and procedures, read only the relevant reference:

- [project-contract.md](references/project-contract.md) for files, fields, and statuses.
- [gated-workflow.md](references/gated-workflow.md) for planning, risk, and revision gates.
- [render-policy.md](references/render-policy.md) for local review hosts and output rules.
- [qa-checklist.md](references/qa-checklist.md) for HyperFrames, audio, and final-media QA.
