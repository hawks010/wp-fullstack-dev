#!/usr/bin/env python3
"""Forward tests for the Sonny x Inkfire scaffold utility.

@author Sonny x Inkfire
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("scaffold.py")
DETECT_SCRIPT = Path(__file__).with_name("detect-project.sh")
PROJECT_TYPES = (
    "plugin",
    "dashboard",
    "block",
    "classic-theme",
    "block-theme",
    "woocommerce",
    "multisite",
    "wpcli",
)
FORBIDDEN_LEFTOVERS = (
    b"Sonny x Inkfire",
    b"sonny-x-inkfire",
    b"sonny_x_inkfire",
    b"my_agentic",
    b"my-agentic-plugin",
    b"MyAgenticPlugin",
    b"myapp",
    b"myApp",
    b"MyApp",
    b"MYAPP",
    b"example/message",
    b"example-dynamic-block",
    b"example_dynamic_block",
)


class ScaffoldTest(unittest.TestCase):
    """Exercise safe generation and project replacement behavior."""

    def scaffold(self, directory: str, project_type: str, name: str, author: str = "") -> Path:
        """Create a dependency-free test scaffold and return its path."""
        result = subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "--type",
                project_type,
                "--name",
                name,
                "--output",
                directory,
                "--author",
                author,
                "--no-git",
                "--skip-install",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        slug = "-".join(name.lower().replace("_", "-").split())
        return Path(directory) / slug

    def test_all_project_types_replace_identity_across_entire_tree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for project_type in PROJECT_TYPES:
                with self.subTest(project_type=project_type):
                    name = f"Client {project_type.replace('-', ' ')}"
                    target = self.scaffold(directory, project_type, name)

                    for path in target.rglob("*"):
                        relative = str(path.relative_to(target)).encode()
                        for leftover in FORBIDDEN_LEFTOVERS:
                            self.assertNotIn(leftover, relative, f"Leftover path {leftover!r} in {path}")
                        if not path.is_file():
                            continue
                        content = path.read_bytes()
                        for leftover in FORBIDDEN_LEFTOVERS:
                            self.assertNotIn(leftover, content, f"Leftover content {leftover!r} in {path}")
                        if path.suffix == ".json":
                            json.loads(content)

    def test_plugin_identity_updates_composer_shortcode_and_pot_filename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.scaffold(directory, "plugin", "Test Plugin")
            main_file = target / "test-plugin.php"
            content = main_file.read_text(encoding="utf-8")
            composer = json.loads((target / "composer.json").read_text(encoding="utf-8"))
            composer_lock = json.loads((target / "composer.lock").read_text(encoding="utf-8"))
            core = (target / "includes" / "class-core.php").read_text(encoding="utf-8")

            self.assertIn("Plugin Name: Test Plugin", content)
            self.assertIn("Text Domain: test-plugin", content)
            self.assertEqual("test-plugin/test-plugin", composer["name"])
            self.assertNotIn("authors", composer)
            self.assertTrue(any(package.get("authors") for package in composer_lock["packages-dev"]))
            self.assertIn("testplug_message", core)
            self.assertTrue((target / "languages" / "test-plugin.pot").exists())
            self.assertFalse((target / "languages" / "my-agentic-plugin.pot").exists())

    def test_block_identity_updates_source_and_prebuilt_assets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.scaffold(directory, "block", "Client Notice")
            expected = "client-notice/dynamic-message"
            source = json.loads((target / "src" / "block.json").read_text(encoding="utf-8"))
            build = json.loads((target / "build" / "block.json").read_text(encoding="utf-8"))
            bundle = (target / "build" / "index.js").read_text(encoding="utf-8")

            self.assertEqual(expected, source["name"])
            self.assertEqual(expected, build["name"])
            self.assertIn(expected, bundle)
            self.assertNotIn("sonny-x-inkfire", bundle)

    def test_dashboard_identity_updates_composer_and_js_bridge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.scaffold(directory, "dashboard", "Client Console")
            composer = json.loads((target / "composer.json").read_text(encoding="utf-8"))
            source = (target / "src" / "index.js").read_text(encoding="utf-8")
            plugin = (target / "includes" / "class-plugin.php").read_text(encoding="utf-8")
            bundle = (target / "build" / "index.js").read_text(encoding="utf-8")

            self.assertEqual("client-console/client-console", composer["name"])
            for content in (source, plugin, bundle):
                self.assertIn("ClientConsoleConfig", content)
                self.assertNotIn("myAppDashboard", content)

    def test_custom_author_becomes_composer_vendor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.scaffold(directory, "plugin", "Identity Plugin", "Jane Doe")
            composer = json.loads((target / "composer.json").read_text(encoding="utf-8"))
            self.assertEqual("jane-doe/identity-plugin", composer["name"])
            self.assertEqual([{"name": "Jane Doe"}], composer["authors"])

    def test_non_latin_author_falls_back_to_project_composer_vendor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.scaffold(directory, "plugin", "Identity Plugin", "作者")
            composer = json.loads((target / "composer.json").read_text(encoding="utf-8"))
            self.assertEqual("identity-plugin/identity-plugin", composer["name"])
            self.assertEqual([{"name": "作者"}], composer["authors"])

    def test_npm_install_is_followed_by_build(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as tools:
            npm_log = Path(directory) / "npm.log"
            fake_npm = Path(tools) / "npm"
            fake_npm.write_text(
                "#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$NPM_CALL_LOG\"\n",
                encoding="utf-8",
            )
            fake_npm.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = f"{tools}:{environment['PATH']}"
            environment["NPM_CALL_LOG"] = str(npm_log)
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--type",
                    "block",
                    "--name",
                    "Build Check",
                    "--output",
                    directory,
                    "--author",
                    "",
                    "--no-git",
                ],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(["install", "run build"], npm_log.read_text(encoding="utf-8").splitlines())

    def test_wpcli_rewritten_include_path_exists(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.scaffold(directory, "wpcli", "Client Commands")
            main = (target / "client-commands.php").read_text(encoding="utf-8")
            include = target / "includes" / "class-clientco-command.php"
            self.assertTrue(include.exists())
            self.assertIn("class-clientco-command.php", main)

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

    def test_project_detector_routes_specialized_plugins(self) -> None:
        cases = {
            "woocommerce": "add_filter( 'woocommerce_product_tabs', 'add_tab' );",
            "multisite": "if ( is_multisite() ) { get_sites(); }",
            "wp-cli": "WP_CLI::add_command( 'items', Example_Command::class );",
            "plugin": "add_action( 'init', 'example_init' );",
        }
        with tempfile.TemporaryDirectory() as directory:
            for expected, signal in cases.items():
                with self.subTest(expected=expected):
                    target = Path(directory) / expected
                    target.mkdir()
                    (target / "plugin.php").write_text(
                        "<?php\n/**\n * Plugin Name: Detection Test\n */\n" + signal + "\n",
                        encoding="utf-8",
                    )
                    if expected == "plugin":
                        vendor = target / "vendor" / "dependency"
                        vendor.mkdir(parents=True)
                        (vendor / "woocommerce.php").write_text(
                            "<?php\nadd_filter( 'woocommerce_product_tabs', 'dependency_tab' );\n",
                            encoding="utf-8",
                        )
                    result = subprocess.run(
                        [str(DETECT_SCRIPT), str(target)],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertEqual(expected, result.stdout.strip())

    def test_project_detector_prefers_dashboard_dependencies_over_hpos_boilerplate(self) -> None:
        dashboard_starter = SCRIPT.parent.parent / "assets" / "dashboard-plugin-starter"
        result = subprocess.run(
            [str(DETECT_SCRIPT), str(dashboard_starter)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("dashboard-plugin", result.stdout.strip())

    def test_project_detector_works_without_ripgrep(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "plugin.php").write_text(
                "<?php\n/**\n * Plugin Name: Grep Fallback\n */\n",
                encoding="utf-8",
            )
            environment = os.environ.copy()
            environment["PATH"] = "/usr/bin:/bin"
            result = subprocess.run(
                [str(DETECT_SCRIPT), str(target)],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("plugin", result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
