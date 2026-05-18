#!/usr/bin/env python3
"""Cloaken: hide macOS app bundles from Dock and Cmd+Tab."""

import argparse
import os
import plistlib
import shutil
import subprocess
import sys


class CloakenError(Exception):
    """Raised when a cloaken operation cannot be completed."""


def run_command(command, description):
    """Execute a command and raise a clear error on failure."""
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip() or "(no stderr output)"
        raise CloakenError(f"{description} failed: {stderr}")


def find_cloakened_apps(search_paths=None):
    """Find all cloakened apps in the given directories."""
    if search_paths is None:
        search_paths = [
            "/Applications",
            "/System/Applications",
            os.path.expanduser("~/Applications"),
        ]

    cloakened_apps = []

    for search_path in search_paths:
        if not os.path.isdir(search_path):
            continue

        for item in os.listdir(search_path):
            if not item.endswith(".app"):
                continue

            app_path = os.path.join(search_path, item)
            plist_path = os.path.join(app_path, "Contents", "Info.plist")

            if not os.path.isfile(plist_path):
                continue

            try:
                plist_data = read_plist(plist_path)
                if plist_data.get("LSUIElement") is True:
                    cloakened_apps.append((item, app_path))
            except Exception:
                continue

    return sorted(cloakened_apps)


def normalize_app_path(app_path):
    """Normalize and validate a target .app bundle path."""
    normalized = os.path.abspath(os.path.expanduser(app_path.rstrip("/")))

    if not normalized.endswith(".app"):
        raise CloakenError("Target must be a valid macOS .app bundle path ending in '.app'.")
    if not os.path.isdir(normalized):
        raise CloakenError(f"App bundle not found: {normalized}")

    plist_path = os.path.join(normalized, "Contents", "Info.plist")
    if not os.path.isfile(plist_path):
        raise CloakenError(f"Info.plist not found at: {plist_path}")

    return normalized, plist_path


def write_plist(plist_path, data):
    with open(plist_path, "wb") as file_handle:
        plistlib.dump(data, file_handle)


def read_plist(plist_path):
    with open(plist_path, "rb") as file_handle:
        return plistlib.load(file_handle)


def get_signing_status(app_path):
    """Check if an app bundle is properly signed. Returns (is_signed, details)."""
    result = subprocess.run(
        ["codesign", "-v", app_path],
        check=False,
        capture_output=True,
        text=True
    )
    is_signed = result.returncode == 0
    details = result.stderr.strip() if result.stderr else result.stdout.strip()
    return is_signed, details


def check_cloaking_status(app_path):
    """Check if an app is cloakened and its signing status."""
    target_app, plist_path = normalize_app_path(app_path)
    plist_data = read_plist(plist_path)

    is_cloakened = plist_data.get("LSUIElement") is True
    is_signed, sign_details = get_signing_status(target_app)

    return {
        "name": os.path.basename(target_app),
        "path": target_app,
        "cloakened": is_cloakened,
        "signed": is_signed,
        "sign_details": sign_details,
    }


def show_status(app_path=None):
    """Show status of app(s). If app_path is None, show all cloakened apps."""
    if app_path:
        status = check_cloaking_status(app_path)
        cloakened_str = "✓ Cloakened" if status["cloakened"] else "✗ Visible"
        signed_str = "✓ Signed" if status["signed"] else "✗ Unsigned"
        print(f"{status['name']}")
        print(f"  Status:   {cloakened_str}")
        print(f"  Signing:  {signed_str}")
        if status["sign_details"]:
            print(f"  Details:  {status['sign_details']}")
    else:
        cloakened_apps = find_cloakened_apps()
        if not cloakened_apps:
            print("No cloakened apps found.")
        else:
            print(f"Found {len(cloakened_apps)} cloakened app(s):\n")
            for app_name, app_path in cloakened_apps:
                try:
                    _, sign_details = get_signing_status(app_path)
                    is_signed = not sign_details or "valid" in sign_details.lower()
                    signed_str = "✓" if is_signed else "✗"
                    print(f"  {signed_str} {app_name:<40} {app_path}")
                except Exception:
                    print(f"  ? {app_name:<40} {app_path}")


def toggle_cloaking(app_path, undo=False, skip_resign=False):
    """Toggle LSUIElement in the target app's Info.plist."""
    target_app, plist_path = normalize_app_path(app_path)

    backup_path = plist_path + ".bak"
    if not os.path.exists(backup_path):
        shutil.copy2(plist_path, backup_path)
        print(f"Backup created: {backup_path}")

    plist_data = read_plist(plist_path)

    if undo:
        if "LSUIElement" not in plist_data:
            print("Application is already visible (no LSUIElement flag present).")
            return
        del plist_data["LSUIElement"]
        print(f"Uncloaking {os.path.basename(target_app)} (visible mode).")
    else:
        plist_data["LSUIElement"] = True
        print(f"Cloaking {os.path.basename(target_app)} (agent/background mode).")

    write_plist(plist_path, plist_data)

    if skip_resign:
        print("Skipping quarantine/signature refresh (--skip-resign enabled).")
    else:
        print("Refreshing quarantine and code signature (sudo may prompt)...")
        run_command(
            ["sudo", "xattr", "-rd", "com.apple.quarantine", target_app],
            "Removing quarantine attribute",
        )
        run_command(
            ["sudo", "codesign", "--force", "--deep", "--sign", "-", target_app],
            "Re-signing app bundle",
        )

    print("Done. Restart the target app for changes to take effect.")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="cloaken",
        description=(
            "Hide or restore macOS applications in Dock/Cmd+Tab by toggling "
            "the LSUIElement key in the app's Info.plist."
            "Useful when you want apps to run in background without cramming the Dock."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  cloaken /Applications/Music.app\n"
            "  cloaken ~/Applications/MyApp.app --undo\n"
            "  cloaken /Applications/SomeApp.app --skip-resign\n"
            "  cloaken --status\n"
            "  cloaken /Applications/Music.app --status\n\n"
            "Notes:\n"
            "  - A backup is created at Contents/Info.plist.bak on first run.\n"
            "  - By default, cloaken runs 'sudo xattr' and 'sudo codesign' after plist edits.\n"
            "  - Use --skip-resign only if you plan to handle signing/quarantine manually."
        ),
    )

    parser.add_argument(
        "path",
        metavar="APP_PATH",
        nargs="?",
        help="Path to a macOS .app bundle (for example: /Applications/Music.app)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show cloaking and signing status. Without APP_PATH, show all cloakened apps.",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Remove LSUIElement and restore normal Dock/Cmd+Tab visibility.",
    )
    parser.add_argument(
        "--skip-resign",
        action="store_true",
        help="Skip xattr/codesign refresh after modifying Info.plist.",
    )

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.status:
            show_status(args.path)
        else:
            if not args.path:
                parser.print_help()
                return 1
            toggle_cloaking(args.path, undo=args.undo, skip_resign=args.skip_resign)
    except CloakenError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
