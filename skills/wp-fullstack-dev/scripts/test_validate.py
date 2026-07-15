#!/usr/bin/env python3
"""Regression tests for the evidence-based validator.

@author Sonny x Inkfire
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


VALIDATE_SCRIPT = Path(__file__).with_name("validate.sh")


class ValidateTest(unittest.TestCase):
    """Exercise validate.sh through its command-line interface."""

    def run_validate(self, target: Path) -> subprocess.CompletedProcess[str]:
        """Run the validator against one project directory."""
        return subprocess.run(
            ["bash", str(VALIDATE_SCRIPT), str(target)],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_shipping_hygiene_fails_on_backup_and_debug_artifacts(self) -> None:
        """Backup files and error_log dumps must fail validation, naming each artifact."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "inc").mkdir()
            (target / "inc" / "module.php.bak-20260708").write_text("<?php\n", encoding="utf-8")
            (target / "error_log").write_text("PHP Warning: something\n", encoding="utf-8")
            result = self.run_validate(target)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("FAIL Shipping hygiene", result.stdout)
            self.assertIn("module.php.bak-20260708", result.stdout)
            self.assertIn("error_log", result.stdout)

    def test_shipping_hygiene_ignores_vendor_and_node_modules(self) -> None:
        """Artifacts inside dependency directories are not the project's to fix."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "vendor" / "dependency").mkdir(parents=True)
            (target / "vendor" / "dependency" / "junk.bak").write_text("x", encoding="utf-8")
            result = self.run_validate(target)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("PASS Shipping hygiene", result.stdout)

    def test_clean_project_passes(self) -> None:
        """A clean directory completes validation without failures."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "plugin.php").write_text(
                "<?php\n/**\n * Plugin Name: Clean Fixture\n */\n", encoding="utf-8"
            )
            result = self.run_validate(target)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("PASS Shipping hygiene", result.stdout)
            self.assertIn("Validation completed without failures", result.stdout)


if __name__ == "__main__":
    unittest.main()
