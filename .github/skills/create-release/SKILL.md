---
name: create-release
description: 'Create a new GitHub release for the ui-store-shop-cart-test project. Use when asked to cut/tag/publish a release, bump the version, or prepare release notes for this repo.'
---

# Create a Release

This repo has no version file — versioning lives entirely in git via `release/vX.Y.Z`
branches and matching `vX.Y.Z` annotated tags (see `git branch -a` / `git tag -l` for
history, e.g. `release/v1.0.0`, `release/v1.0.1`).

## Procedure

0. **Confirm the plan with the user before doing anything hard-to-reverse** (pushes, tags,
   published releases). Ask, at minimum:
   - Whether they actually want a version file (default: no — this repo intentionally has
     none; versioning is git-native).
   - The next version number (semver `vMAJOR.MINOR.PATCH`).
   - Explicit go-ahead to push the branch/tag to origin.
   - How to handle the GitHub Release publish step (see step 8) if `gh` isn't ready.

1. **Verify the suite passes before tagging anything:**
   ```bash
   docker compose run --rm tests
   ```
   Do not proceed if this fails.

2. **Commit the actual code change(s) being released** on the current branch (typically
   `main`) with a descriptive message, before branching. Only stage files relevant to the
   change — do not sweep up unrelated untracked files (e.g. local tooling/skill files)
   without asking first.

3. **Clean up local commit history with an interactive rebase** before pushing anything,
   so the release carries a readable, logically-ordered history instead of noisy
   work-in-progress commits:
   ```bash
   git rebase -i <base-commit-or-branch>
   ```
   Squash fixups, reword messages, and reorder as needed. Only rebase commits that are
   still local/unpushed — if any of the commits being rewritten already exist on
   `origin`, this requires a force-push (`git push --force-with-lease`), which rewrites
   shared history; get explicit user confirmation before doing that.

4. **Confirm no secrets are staged.** `.env` must never be committed:
   ```bash
   git check-ignore -v .env   # must print a match
   git ls-files | grep -x '\.env'   # must print nothing
   ```

5. **Pick the next version** (semver `vMAJOR.MINOR.PATCH`) based on the highest existing
   `release/vX.Y.Z` branch or `vX.Y.Z` tag.

6. **Create and push the release branch** from the commit you want to release:
   ```bash
   git checkout -b release/vX.Y.Z
   git push -u origin release/vX.Y.Z
   ```

7. **Write release notes** to a temp file, following this project's established format
   (see prior tags with `git tag -n99 <tag>` for examples):
   ```markdown
   ## vX.Y.Z

   <one-line summary of what this release does>

   ### Added
   - ...

   ### Fixed
   - ...

   ### Known limitations
   - ...
   ```

8. **Create an annotated tag using the notes file as the tag message, and push it:**
   ```bash
   git tag -a vX.Y.Z -F /tmp/release_notes_vX.Y.Z.md
   git push origin vX.Y.Z
   ```

9. **Publish the GitHub Release with `gh` CLI:**
   ```bash
   gh --version         # confirm it's installed
   gh auth status       # confirm it's authenticated
   ```
   - If not installed, install it (e.g. via the system package manager) — ask the user first
     since this modifies their system.
   - If not authenticated, run `gh auth login` interactively (device/browser flow). This is
     safe to relay through the terminal: the prompts are non-secret choices (host, protocol,
     SSH key upload) and the one-time device code is not a credential. Never handle the
     actual GitHub password/token yourself.
   - Then create the release:
     ```bash
     gh release create vX.Y.Z -F /tmp/release_notes_vX.Y.Z.md --title vX.Y.Z
     ```
   - Fallback if `gh` isn't available/authenticated and the user doesn't want to set it up:
     draft the release manually at `https://github.com/<owner>/<repo>/releases/new`, select
     the `vX.Y.Z` tag just pushed, and paste the same release notes.

## Notes

- `git push`, tag creation, force-pushing a rebased branch, and publishing a GitHub Release
  are hard-to-reverse actions on a shared remote — always get explicit confirmation (step 0)
  before doing any of them.
- This project targets a real, live account on production store.ui.com; don't include
  account details, TOTP secrets, or `.env` contents in release notes.
