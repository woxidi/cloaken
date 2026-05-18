# Cloaken

Cloaken is a lightweight macOS CLI utility that toggles an app bundle between:

- **Visible app mode** (normal Dock + Cmd+Tab behavior)
- **Agent mode** (`LSUIElement=true`, hidden from Dock/Cmd+Tab)

It works by editing the target app's `Contents/Info.plist` and (by default) refreshing quarantine/signature metadata to reduce launch issues.

## Features

- Cloak apps by enabling `LSUIElement`
- Uncloak apps with `--undo`
- First-run backup at `Contents/Info.plist.bak`
- Optional `--skip-resign` for manual signing workflows

## Requirements

- macOS
- Python 3.9+
- `xattr` and `codesign` (built into macOS)
- `sudo` access (unless using `--skip-resign`)

## Usage

```bash
cloaken APP_PATH [--undo] [--skip-resign]
```

Examples:

```bash
# Hide an app from Dock/Cmd+Tab
cloaken /Applications/Music.app

# Restore normal app visibility
cloaken /Applications/Music.app --undo

# Only edit Info.plist (no xattr/codesign refresh)
cloaken /Applications/Music.app --skip-resign
```

Get full command help:

```bash
cloaken --help
```

## Homebrew Tap Setup

If you own a tap repo (for example `YOUR_GITHUB_USERNAME/homebrew-tap`):

```bash
brew tap YOUR_GITHUB_USERNAME/tap
brew install cloaken
```

This repository already includes a formula template at `Formula/cloaken.rb`.
Before publishing, update formula metadata:

1. `url` to your release tarball (for example a GitHub release tag)
2. `sha256` to match that tarball
3. `homepage` and owner/repo values

Then run:

```bash
brew audit --strict --online YOUR_GITHUB_USERNAME/tap/cloaken
brew install --build-from-source YOUR_GITHUB_USERNAME/tap/cloaken
brew test cloaken
```

## Safety Notes

- Modifying app bundles may break updates or invalidate vendor signatures.
- Re-signing with ad-hoc identity (`-`) can change app trust behavior.
- Back up critical apps before modifying them.

## License

MIT
