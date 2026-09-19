# Project contract

## Required files

### `PROJECT.md`

Record the project title, objective, audience, language, route (`Compose`, `Generate`, `Edit`, or `Hybrid`), aspect ratio, target resolution, frame rate, duration, source media, audio policy, delivery formats, factual-source policy, and hard exclusions. State whether supplied audio is protected, editable, replaceable, or absent.

### `DESIGN.md`

Record the visual identity that every composition must follow: colors with roles, typography, canvas and safe margins, graphic primitives, motion language, transition rules, asset provenance, and a short “What not to do” list. Brand and logo exclusions belong here even when they apply to only one project.

### `scene-map.csv`

Required columns:

```text
scene_id,start_seconds,end_seconds,objective,vo,on_screen_text,visual,motion,source,risk,status,version,notes
```

`start_seconds` and `end_seconds` are numeric seconds. `risk` is `A`, `B`, or `C`. `status` is one of `planned`, `static-review`, `static-approved`, `motion-ready`, `motion-review`, `approved`, `final`, or `blocked`. `version` is a short value such as `v01`.

Optional columns may be added, but the required columns must remain unchanged so the helper script can validate the project.

## Status meanings

- `planned`: content is mapped but not approved.
- `static-review`: hero frame is awaiting review.
- `static-approved`: static content and layout are approved.
- `motion-ready`: approved for animation.
- `motion-review`: animated scene is awaiting review.
- `approved`: final motion/audio review passed.
- `final`: included in the final delivery lock.
- `blocked`: a factual, visual, technical, or authorization issue must be resolved.

## Feedback contract

Feedback must identify `scene_id`, issue type, required change, preserve list, priority, and resulting version. Do not apply a broad visual change to approved scenes unless the feedback explicitly includes those scenes.
