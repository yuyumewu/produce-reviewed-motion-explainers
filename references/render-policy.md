# Render policy

## Default outputs

| Stage | Output | Default settings |
| --- | --- | --- |
| Static approval | Hero-frame PNG | Selected scene only |
| Motion review | Scene/batch MP4 | 1920×1080, `draft` |
| Full pacing | HyperFrames Studio | No automatic MP4 |
| Final delivery | One master MP4 | 3840×2160, delivery quality |

Do not render a complete 1080p review file unless the user explicitly requests it.

## Local review host

The helper script creates a temporary host under the project's cache directory. It mounts the selected scene compositions at local time zero or sequentially, attaches the source audio with the correct media offset, and renders only that selection. The host is disposable and must not replace the main `index.html`.

Scene files conventionally live at `compositions/<scene_id>.html`. If a project uses a different layout, pass the project-specific composition path or record the convention in `PROJECT.md`.

For a transition review, include the outgoing and incoming scene IDs in the same contiguous batch. For a scene-only content change, do not render unrelated scenes.

## Final render gate

The `final` command must fail when:

- required project files are missing;
- scene IDs are duplicated or times are invalid;
- any required scene is `blocked`, `planned`, `static-review`, `static-approved`, `motion-ready`, or `motion-review`;
- the project has not passed HyperFrames checks;
- the requested output is not the configured final target.

The final command may be run again only after a new approved change; it should create a new versioned output rather than overwrite an existing master.
