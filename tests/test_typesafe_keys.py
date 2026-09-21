"""Offline checks for the public TypeSafe Keys CLI."""

from __future__ import annotations

import argparse
import importlib.util
import os
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("typesafe_keys", ROOT / "typesafe-keys.py")
assert SPEC and SPEC.loader
typesafe_keys = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(typesafe_keys)


class TypeSafeKeysTests(unittest.TestCase):
    def test_session_cookie_uses_explicit_environment_value(self) -> None:
        with mock.patch.dict(os.environ, {"TYPESAFE_CONSOLE_COOKIE": "session=value"}, clear=True):
            self.assertEqual("session=value", typesafe_keys.get_session_cookies())

    def test_delete_requires_confirmation_before_network_request(self) -> None:
        args = argparse.Namespace(key_id="key_1", yes=False)
        with mock.patch.object(typesafe_keys.sys.stdin, "isatty", return_value=False), mock.patch.object(
            typesafe_keys, "api_request"
        ) as api_request:
            with self.assertRaisesRegex(RuntimeError, "--yes"):
                typesafe_keys.cmd_delete(args)
        api_request.assert_not_called()

    def test_delete_sends_explicitly_confirmed_request(self) -> None:
        args = argparse.Namespace(key_id="key/1", yes=True)
        with mock.patch.object(typesafe_keys, "api_request") as api_request:
            typesafe_keys.cmd_delete(args)
        api_request.assert_called_once_with("/api/api-keys/key%2F1", method="DELETE")

    def test_public_source_has_no_machine_specific_reference(self) -> None:
        source = (ROOT / "typesafe-keys.py").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"/Users/[A-Za-z0-9_-]+")


if __name__ == "__main__":
    unittest.main()
