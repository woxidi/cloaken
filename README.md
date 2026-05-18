# Cloaken

Cloaken is a lightweight macOS CLI utility that toggles an app bundle between:

- **Visible app mode** (normal Dock + Cmd+Tab behavior)
- **Agent mode** (`LSUIElement=true`, hidden from Dock/Cmd+Tab)

It works by editing the target app's `Contents/Info.plist` and (by default) refreshing quarantine/signature metadata to reduce launch issues. It's useful when you want to run specific apps in the background without cramming your Dock. For example your favorite music player, video player and pdf reader. 

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

## Safety Notes

- Modifying app bundles may break updates or invalidate vendor signatures.
- Re-signing with ad-hoc identity (`-`) can change app trust behavior.
- Back up critical apps before modifying them.

## License

MIT
