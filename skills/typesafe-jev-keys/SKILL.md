---
name: typesafe-jev-keys
description: Set up or safely inspect TypeSafe Jev API keys with the bundled CLI. Use when a user asks for TypeSafe Console key setup, listing, or explicit lifecycle guidance; do not use for application integration or general Jev prompting.
---

# TypeSafe Jev Keys

Use the repository's `typesafe-keys.py` CLI to help a user manage API keys for
TypeSafe's Jev model. The CLI uses the user's signed-in TypeSafe Console
session and does not persist cookies.

## Before you begin

1. Confirm the user has a TypeSafe account at
   [console.typesafe.ai](https://console.typesafe.ai) and is signed in.
2. Explain that console cookies and API keys are secrets. Never request,
   print, log, commit, or retain either value.
3. Install or run the CLI from this repository. Python 3.10+ is required and
   no package installation is needed.

## Safe operations

For an inventory, run:

```bash
typesafe-keys list
```

The default listing only displays server-redacted keys. Do not use `--json`
when its response could include sensitive account information.

If authentication is unavailable, direct the user to sign in at the TypeSafe
Console or set `TYPESAFE_CONSOLE_COOKIE` in their own short-lived shell. Do
not handle the cookie value yourself.

## Key lifecycle changes

Creating, activating, deactivating, and deleting a key all change persistent
access. Proceed only after the user directly specifies the action and its
target. Before a destructive change, restate the key ID and consequence.

Do not run `create` through an agent session: its response can contain a newly
generated secret. Instead, provide the user with the command to run in their
own terminal, for example:

```bash
typesafe-keys create "Example Project"
```

The CLI itself asks for confirmation. Use `--yes` only when the user has
explicitly requested non-interactive execution. Never use `--json` or `--copy`
for a create operation in an agent session.

For activation, deactivation, or deletion, first list keys, obtain direct
authorization for the exact ID, then run the requested command. Do not assume
that a similarly named key is the intended target.

## Scope boundary

This skill manages TypeSafe Console API-key lifecycle only. For building with
Jev or choosing SDK patterns, use the TypeSafe product documentation or an
appropriate integration skill.
