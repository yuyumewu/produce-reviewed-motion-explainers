# Gated workflow

## Sequence

1. Brief the objective and lock the production route.
2. Lock script, claims, sources, and voice-over.
3. Build the scene map and assign Type A/B/C risk.
4. Create 2–3 representative style frames and a project `DESIGN.md`.
5. Approve static keyframes using the risk rule.
6. Author each approved scene as a local-time HyperFrames composition.
7. Render only changed scenes or contiguous batches for motion review.
8. Use Studio to inspect the complete assembled timeline.
9. Apply feedback by scene ID and version; preserve approved scenes.
10. Mark all required scenes `approved`/`final` and render one delivery master.

## Static review checklist

Confirm the scene communicates the objective within two seconds at 50% scale, uses exact approved copy, contains no invented data or marks, has separable layers for motion, and leaves enough space for animation. Type C review must include the source or evidence note before motion begins.

## Motion brief

Every scene must state the order of appearance, approximate durations, emphasis, transition behavior, and elements that remain unchanged. Use deterministic GSAP timelines and local scene time. Avoid random values, infinite loops, unexplained camera movement, or motion that makes the viewer chase the information.

## Revision rule

One feedback item should map to one or more explicit scene IDs. Regenerate only affected scene compositions and any directly dependent transition. Increment the scene version and retain the previous output until the replacement is approved.
