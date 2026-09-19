# QA checklist

## Composition QA

- `npx hyperframes lint`
- `npx hyperframes validate`
- `npx hyperframes inspect --json`
- animation map for new or substantially changed timelines

Review at scene starts, hero frames, transitions, scene ends, and the final frame. Fix unintended overflow, clipped labels, low contrast, missing entrance animations, timing collisions, and unintentional blank frames.

## Content QA

Check names, dates, numbers, units, terminology, source boundaries, and all user-specified exclusions. Keep sources in project records, not as unapproved on-screen citations.

## Audio QA

Confirm the intended source track, duration, sample rate, channel layout, voice/music relationship, and whether the audio was stream-copied or intentionally re-encoded. Never silently normalize, time-stretch, duck, or replace protected audio.

## Media QA

Use `ffprobe` to verify:

- width and height;
- frame rate;
- duration within the project tolerance;
- video codec and pixel format;
- audio codec, sample rate, channels, and presence;
- absence of unintended extra streams.

Record the final output path and probe summary in the handoff.
