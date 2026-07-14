#!/usr/bin/env python3
"""Forward tests for the Sonny x Inkfire scaffold utility.

@author Sonny x Inkfire
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("scaffold.py")


class ScaffoldTest(unittest.TestCase):
    """Exercise safe generation and project replacement behavior."""

    def test_plugin_scaffold_has_requested_identity_without_forced_author(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                ["python3", str(SCRIPT), "--type", "plugin", "--name", "Test Plugin", "--output", directory, "--no-git", "--skip-install"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            main_file = Path(directory) / "test-plugin" / "test-plugin.php"
            content = main_file.read_text(encoding="utf-8")
            self.assertIn("Plugin Name: Test Plugin", content)
            self.assertIn("Text Domain: test-plugin", content)
            self.assertNotIn("Sonny x Inkfire", content)

    def test_existing_destination_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "test-plugin"
            target.mkdir()
            marker = target / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            result = subprocess.run(
                ["python3", str(SCRIPT), "--type", "plugin", "--name", "test-plugin", "--output", directory, "--no-git", "--skip-install"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(3, result.returncode)
            self.assertEqual("keep", marker.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
