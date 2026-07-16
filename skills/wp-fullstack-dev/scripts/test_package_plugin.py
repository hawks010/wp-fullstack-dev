#!/usr/bin/env python3
"""Regression tests for the public plugin packaging command."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("package-plugin.sh")


class PackagePluginTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def plugin(self, slug: str = "demo-plugin") -> Path:
        target = self.root / slug
        target.mkdir()
        (target / f"{slug}.php").write_text(
            "<?php\n/**\n * Plugin Name: Demo Plugin\n */\n",
            encoding="utf-8",
        )
        return target

    def run_package(self, target: Path, output: Path | None = None) -> subprocess.CompletedProcess[str]:
        command = [str(SCRIPT), str(target)]
        if output is not None:
            command.append(str(output))
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def names(self, archive: Path) -> set[str]:
        with zipfile.ZipFile(archive) as handle:
            return set(handle.namelist())

    def test_runtime_src_and_vendor_are_included_and_exact_zip_is_respected(self) -> None:
        target = self.plugin()
        (target / "src").mkdir()
        (target / "src" / "Runtime.php").write_text("<?php\n", encoding="utf-8")
        (target / "vendor").mkdir()
        (target / "vendor" / "autoload.php").write_text("<?php\n", encoding="utf-8")
        (target / "composer.json").write_text(json.dumps({"require": {"php": ">=8.0", "acme/runtime": "^1"}}))
        archive = self.root / "release.zip"

        result = self.run_package(target, archive)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            {"demo-plugin/demo-plugin.php", "demo-plugin/src/Runtime.php", "demo-plugin/vendor/autoload.php", "demo-plugin/composer.json"},
            self.names(archive),
        )

    def test_dev_artifacts_are_excluded(self) -> None:
        target = self.plugin()
        for directory in ("tests", "node_modules", ".github"):
            (target / directory).mkdir()
            (target / directory / "leak.php").write_text("<?php\n", encoding="utf-8")
        (target / "debug.log").write_text("secret", encoding="utf-8")
        archive = self.root / "release.zip"

        result = self.run_package(target, archive)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual({"demo-plugin/demo-plugin.php"}, self.names(archive))

    def test_output_directory_and_default_dist_forms(self) -> None:
        target = self.plugin()
        output = self.root / "releases"
        first = self.run_package(target, output)
        second = self.run_package(target)
        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(0, second.returncode, second.stderr)
        self.assertTrue((output / "demo-plugin.zip").is_file())
        self.assertTrue((self.root / "dist" / "demo-plugin.zip").is_file())

    def test_dev_only_vendor_is_not_shipped(self) -> None:
        target = self.plugin()
        (target / "vendor").mkdir()
        (target / "vendor" / "autoload.php").write_text("<?php\n", encoding="utf-8")
        (target / "composer.json").write_text(json.dumps({"require": {"php": ">=8.0"}, "require-dev": {"phpunit/phpunit": "^10"}}))
        archive = self.root / "release.zip"

        result = self.run_package(target, archive)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("demo-plugin/vendor/autoload.php", self.names(archive))

    def test_missing_runtime_vendor_fails_closed_without_archive(self) -> None:
        target = self.plugin()
        (target / "composer.json").write_text(json.dumps({"require": {"acme/runtime": "^1"}}))
        archive = self.root / "release.zip"

        result = self.run_package(target, archive)

        self.assertEqual(2, result.returncode)
        self.assertIn("composer install --no-dev", result.stderr)
        self.assertFalse(archive.exists())

    def test_installed_composer_dev_packages_fail_closed(self) -> None:
        target = self.plugin()
        composer = target / "vendor" / "composer"
        composer.mkdir(parents=True)
        (target / "vendor" / "autoload.php").write_text("<?php\n", encoding="utf-8")
        (composer / "installed.json").write_text(
            json.dumps([{"name": "acme/runtime", "dev_requirement": False}, {"name": "phpunit/phpunit", "dev_requirement": True}]),
            encoding="utf-8",
        )
        (target / "composer.json").write_text(json.dumps({"require": {"acme/runtime": "^1"}}))
        archive = self.root / "release.zip"

        result = self.run_package(target, archive)

        self.assertEqual(2, result.returncode)
        self.assertIn("composer install --no-dev", result.stderr)
        self.assertFalse(archive.exists())

    def test_missing_static_runtime_include_fails_closed(self) -> None:
        target = self.plugin()
        bootstrap = target / "demo-plugin.php"
        bootstrap.write_text(bootstrap.read_text() + "require_once __DIR__ . '/src/Missing.php';\n", encoding="utf-8")
        archive = self.root / "release.zip"

        result = self.run_package(target, archive)

        self.assertEqual(2, result.returncode)
        self.assertIn("Missing static runtime include", result.stderr)
        self.assertFalse(archive.exists())

    def test_archive_has_one_plugin_root(self) -> None:
        target = self.plugin("one-root")
        archive = self.root / "release.zip"
        result = self.run_package(target, archive)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(all(name.startswith("one-root/") for name in self.names(archive)))


if __name__ == "__main__":
    unittest.main()
