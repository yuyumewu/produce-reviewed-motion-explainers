# Produce Reviewed Motion Explainers

A reusable Codex skill for narrated institutional, research, policy, data, and educational motion explainers built with HyperFrames.

The workflow separates content approval, static scene approval, motion review, and final delivery. It renders only changed scenes during iteration and produces one final 4K master after approval.

## Install locally

Copy this folder into your Codex skills directory:

```text
~/.codex/skills/produce-reviewed-motion-explainers/
```

The skill is automatically discoverable as `produce-reviewed-motion-explainers`.

## Helper script

```bash
python3 scripts/motion_workflow.py init ./my-project
python3 scripts/motion_workflow.py check ./my-project
python3 scripts/motion_workflow.py review ./my-project --scenes S03,S04
python3 scripts/motion_workflow.py final ./my-project --output renders/project_final_4k.mp4
python3 scripts/motion_workflow.py probe renders/project_final_4k.mp4
```

HyperFrames must be available in the project environment. Set `HYPERFRAMES_CMD` when a project uses a pinned launcher such as `pnpm dlx hyperframes@<version>`.
