#!/usr/bin/env python3
"""TypeSafe API Key Management CLI.

Manage TypeSafe AI (Jev) API keys through console.typesafe.ai.

This client uses an authenticated TypeSafe Console session. It never persists
cookies or generated API keys. Mutating commands require explicit confirmation.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

CONSOLE_BASE = "https://console.typesafe.ai"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
REQUEST_TIMEOUT_SECONDS = 30


def get_session_cookies() -> str:
    """Retrieve cookies for typesafe.ai using agentcookie or environment."""
    if "TYPESAFE_CONSOLE_COOKIE" in os.environ:
        return os.environ["TYPESAFE_CONSOLE_COOKIE"]

    agentcookie_bin = os.path.expanduser("~/.local/bin/agentcookie")
    if not os.path.exists(agentcookie_bin):
        agentcookie_bin = "agentcookie"

    try:
        proc = subprocess.run(
            [agentcookie_bin, "cookies", "--domain", "typesafe.ai"],
            capture_output=True,
            text=True,
            check=True,
        )
        cookies = proc.stdout.strip()
        if cookies:
            return cookies
    except (OSError, subprocess.SubprocessError):
        pass

    raise RuntimeError(
        "Could not retrieve TypeSafe console session cookies from agentcookie. "
        "Make sure you are logged into https://console.typesafe.ai in Chrome or set TYPESAFE_CONSOLE_COOKIE."
    )


def api_request(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    cookies: Optional[str] = None,
) -> Any:
    """Make an authenticated HTTP request to console.typesafe.ai."""
    if not cookies:
        cookies = get_session_cookies()

    url = f"{CONSOLE_BASE}{endpoint}"
    headers = {
        "Cookie": cookies,
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    encoded_body = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        encoded_body = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=encoded_body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            content = resp.read().decode("utf-8")
            if not content.strip():
                return {}
            return json.loads(content)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            err_json = json.loads(err_body)
            msg = err_json.get("title") or err_json.get("error") or err_body
        except Exception:
            msg = err_body or str(e)
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {msg}") from e


def copy_to_clipboard(text: str) -> bool:
    """Copy text to macOS pasteboard."""
    try:
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        p.communicate(input=text.encode("utf-8"))
        return p.returncode == 0
    except Exception:
        return False


def require_confirmation(args: argparse.Namespace, action: str) -> None:
    """Require an interactive confirmation or --yes before changing account state."""
    if getattr(args, "yes", False):
        return
    if not sys.stdin.isatty():
        raise RuntimeError(f"Refusing to {action} without --yes in a non-interactive session.")
    answer = input(f"About to {action}. Continue? [y/N] ").strip().lower()
    if answer not in {"y", "yes"}:
        raise RuntimeError("Cancelled.")


def cmd_list(args: argparse.Namespace) -> None:
    data = api_request("/api/api-keys")
    keys: List[Dict[str, Any]] = data.get("api_keys", [])

    if args.json:
        print(json.dumps(keys, indent=2))
        return

    if not keys:
        print("No TypeSafe API keys found.")
        return

    print(f"{'NAME':<28} {'STATUS':<10} {'KEY (REDACTED)':<26} {'CREATED':<20} {'ID'}")
    print("-" * 115)
    for k in keys:
        status = "Active" if k.get("active") else "Inactive"
        created = (k.get("created") or "")[:10]
        print(
            f"{k.get('name', ''):<28} "
            f"{status:<10} "
            f"{k.get('api_key_redacted', ''):<26} "
            f"{created:<20} "
            f"{k.get('id', '')}"
        )


def cmd_create(args: argparse.Namespace) -> None:
    name = args.name.strip()
    if not name:
        sys.exit("Error: Key name cannot be empty.")

    require_confirmation(args, f"create the API key '{name}'")

    resp = api_request("/api/api-keys", method="POST", data={"name": name})
    api_key = resp.get("api_key")
    key_id = resp.get("id")

    if args.json:
        print(json.dumps(resp, indent=2))
        return

    print(f"Successfully created TypeSafe API key: '{name}'")
    print(f"Key ID:  {key_id}")
    print(f"API Key: {api_key}")

    if args.copy:
        if copy_to_clipboard(api_key):
            print("\nCopied API key to clipboard.")
        else:
            print("\nCould not copy to clipboard.")

def cmd_activate(args: argparse.Namespace) -> None:
    require_confirmation(args, f"activate API key {args.key_id}")
    key_id = urllib.parse.quote(args.key_id, safe="")
    api_request(f"/api/api-keys/{key_id}", method="PATCH", data={"active": True})
    print(f"Activated key {args.key_id}.")


def cmd_deactivate(args: argparse.Namespace) -> None:
    require_confirmation(args, f"deactivate API key {args.key_id}")
    key_id = urllib.parse.quote(args.key_id, safe="")
    api_request(f"/api/api-keys/{key_id}", method="PATCH", data={"active": False})
    print(f"Deactivated key {args.key_id}.")


def cmd_delete(args: argparse.Namespace) -> None:
    require_confirmation(args, f"permanently delete API key {args.key_id}")
    key_id = urllib.parse.quote(args.key_id, safe="")
    api_request(f"/api/api-keys/{key_id}", method="DELETE")
    print(f"Deleted key {args.key_id}.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="typesafe-keys",
        description="TypeSafe (Jev) API Key Manager (https://console.typesafe.ai/keys)",
    )
    subparsers = parser.add_subparsers(dest="command")

    # list
    p_list = subparsers.add_parser("list", help="List all API keys")
    p_list.add_argument("--json", action="store_true", help="Output raw JSON")

    # create
    p_create = subparsers.add_parser("create", help="Create a new API key")
    p_create.add_argument("name", help="Name or purpose of the API key (for example, 'Example Project')")
    p_create.add_argument("-c", "--copy", action="store_true", help="Copy the new secret key to clipboard")
    p_create.add_argument("--json", action="store_true", help="Output raw JSON")
    p_create.add_argument("--yes", action="store_true", help="Confirm key creation without a prompt")

    # activate
    p_activate = subparsers.add_parser("activate", help="Activate an API key")
    p_activate.add_argument("key_id", help="The ID of the key to activate")
    p_activate.add_argument("--yes", action="store_true", help="Confirm activation without a prompt")

    # deactivate
    p_deact = subparsers.add_parser("deactivate", help="Deactivate an API key")
    p_deact.add_argument("key_id", help="The ID of the key to deactivate")
    p_deact.add_argument("--yes", action="store_true", help="Confirm deactivation without a prompt")

    # delete
    p_delete = subparsers.add_parser("delete", help="Delete an API key")
    p_delete.add_argument("key_id", help="The ID of the key to delete")
    p_delete.add_argument("--yes", action="store_true", help="Confirm deletion without a prompt")

    args = parser.parse_args()

    if not args.command or args.command == "list":
        # default to list if no subcommand specified
        cmd_list(args if hasattr(args, "json") else argparse.Namespace(json=False))
        return

    if args.command == "create":
        cmd_create(args)
    elif args.command == "activate":
        cmd_activate(args)
    elif args.command == "deactivate":
        cmd_deactivate(args)
    elif args.command == "delete":
        cmd_delete(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.exit(f"Error: {e}")
