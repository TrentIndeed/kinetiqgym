# Contributing

Thanks for helping. Useful contributions:

- **Build reports:** photos, what went wrong, print settings that worked, measured loads. Open an issue.
- **Fixes and adaptations:** another motor mount, a rotary-encoder front panel, a different battery. Open a pull request with
  the changed CAD (FreeCAD and STEP), a short description and what you tested.
- **Docs:** clearer build steps, translations.

## Propose, contribute, review

1. Open a proposal or build-report issue before a substantial change. Describe the problem, intended improvement and affected design revision.
2. Fork the repository and use a branch for a focused change. Submit a pull request with the changed files and supporting evidence. Do not upload a replacement of the whole assembly for an unrelated small fix.
3. Project maintainers review the change for usefulness, compatibility, documentation and testing. Changes are accepted, revised or declined through the pull request discussion. Community changes do not go directly into `main`.

The initial reviewer is the repository owner, **@TrentIndeed**. Additional moderators can be added as the project grows; moderator access is appointed by the owner, not granted automatically to contributors. CODEOWNERS identifies the current review owner. The main branch requires a pull request and a code-owner approval for community changes; repository administrators retain a pull-request-only bypass for owner-authored maintenance.

### What to include

- **CAD:** source model and neutral export when applicable, dimensions or interfaces changed, clearance checks, and any manufacturing assumptions. Distinguish a proposed improvement from a physically tested one.
- **Software:** intended behavior, screenshots where relevant, and how you checked it. Mark mock interfaces clearly; the Pi, Teensy and companion software are upcoming.
- **Build or test reports:** revision, materials, settings, measurements and photos. State test conditions and what remains unverified.
- **Documentation:** the relevant Markdown and website reference copies together.

An animation or simulation alone does not establish a resistance rating or a validated build. The updated CAD, confirmed BOM and final instructions are still pending.

## Ground rules

- Never commit supplier CAD (bearings, gears, boards, connectors...): reference it in `cad/vendor/README.md` instead.
- Never commit API keys, tokens, passwords or personal data.
- Keep part names as they are (the documentation and the assembly refer to them); add new parts with a clear prefix.
- By contributing you agree that your contribution is licensed under the licences in `LICENSE.md`.
