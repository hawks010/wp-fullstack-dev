#!/usr/bin/env python3
"""Regression tests for the WordPress project mapper.

@author Sonny x Inkfire
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


MAP_SCRIPT = Path(__file__).with_name("map-project.py")
SCAFFOLD_SCRIPT = Path(__file__).with_name("scaffold.py")
DASHBOARD_STARTER = MAP_SCRIPT.parent.parent / "assets" / "dashboard-plugin-starter"
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
DETECTED_TYPES = {
    "plugin": "plugin",
    "dashboard": "dashboard-plugin",
    "block": "block",
    "classic-theme": "classic-theme",
    "block-theme": "block-theme",
    "woocommerce": "woocommerce",
    "multisite": "multisite",
    "wpcli": "wp-cli",
}


class MapProjectTest(unittest.TestCase):
    """Exercise mapper output through its public command-line interface."""

    def run_map(self, target: Path, output_format: str = "md") -> subprocess.CompletedProcess[str]:
        """Run the mapper for one fixture."""
        return subprocess.run(
            ["python3", str(MAP_SCRIPT), str(target), "--format", output_format],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )

    def test_maps_all_eight_scaffolded_project_types(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for project_type in PROJECT_TYPES:
                with self.subTest(project_type=project_type):
                    name = f"Map {project_type.replace('-', ' ')}"
                    scaffold = subprocess.run(
                        [
                            "python3",
                            str(SCAFFOLD_SCRIPT),
                            "--type",
                            project_type,
                            "--name",
                            name,
                            "--output",
                            str(output),
                            "--author",
                            "",
                            "--no-git",
                            "--skip-install",
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    self.assertEqual(0, scaffold.returncode, scaffold.stderr)
                    slug = "-".join(name.lower().split())
                    mapped = self.run_map(output / slug)
                    self.assertEqual(0, mapped.returncode, mapped.stderr)
                    self.assertTrue(mapped.stdout.strip())
                    self.assertIn(f"# Project map — {DETECTED_TYPES[project_type]} —", mapped.stdout)

    def test_hook_graph_connects_registered_and_fired_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "listener.php").write_text(
                "<?php\nadd_action( 'demo_custom_hook', 'demo_listener', 20 );\n",
                encoding="utf-8",
            )
            (target / "publisher.php").write_text(
                "<?php\ndo_action( 'demo_custom_hook' );\n",
                encoding="utf-8",
            )
            result = self.run_map(target)
            self.assertEqual(0, result.returncode, result.stderr)
            graph = result.stdout.split("## Hook graph", 1)[1]
            self.assertIn("demo_custom_hook", graph)
            self.assertIn("listener.php:2", graph)
            self.assertIn("publisher.php:2", graph)

    def test_unmatched_fired_hook_is_not_added_to_graph(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "publisher.php").write_text(
                "<?php\ndo_action( 'demo_unmatched_hook' );\n",
                encoding="utf-8",
            )
            result = self.run_map(target)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("## Hooks fired (do_action / apply_filters)", result.stdout)
            self.assertIn("demo_unmatched_hook", result.stdout)
            self.assertNotIn("## Hook graph", result.stdout)

    def test_directory_block_registration_resolves_block_json_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "block.json").write_text(
                json.dumps({"apiVersion": 3, "name": "acme/example", "render": "file:./render.php"}),
                encoding="utf-8",
            )
            (target / "plugin.php").write_text(
                "<?php\nregister_block_type( __DIR__ );\n",
                encoding="utf-8",
            )
            result = self.run_map(target)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("`acme/example`", result.stdout)
            self.assertIn("dynamic: yes", result.stdout)

    def test_json_and_markdown_contain_the_same_hook_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "hooks.php").write_text(
                "<?php\nadd_filter( 'acme_value', 'acme_filter' );\napply_filters( 'acme_value', 'value' );\n",
                encoding="utf-8",
            )
            markdown = self.run_map(target)
            json_result = self.run_map(target, "json")
            self.assertEqual(0, markdown.returncode, markdown.stderr)
            self.assertEqual(0, json_result.returncode, json_result.stderr)
            data = json.loads(json_result.stdout)
            registered = {item["hook"] for item in data["Hooks registered (add_action / add_filter)"]}
            fired = {item["hook"] for item in data["Hooks fired (do_action / apply_filters)"]}
            graph = {item["hook"] for item in data["Hook graph"]}
            self.assertEqual({"acme_value"}, registered)
            self.assertEqual(registered, fired)
            self.assertEqual(registered, graph)
            self.assertIn("acme_value", markdown.stdout)

    def test_empty_directory_returns_header_without_sections(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_map(Path(directory))
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("0 files scanned", result.stdout)
            self.assertNotIn("\n## ", result.stdout)

    def test_indexes_supported_wordpress_surfaces_and_excludes_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "plugin.php").write_text(
                """<?php
/**
 * Plugin Name: Mapper Fixture
 */
add_shortcode( 'acme_card', 'acme_card' );
register_post_type( 'acme_item', array() );
register_taxonomy( 'acme_group', array( 'acme_item' ) );
register_rest_route( 'acme/v1', '/items', array(
    'methods' => 'GET',
    'permission_callback' => 'acme_permissions',
) );
WP_CLI::add_command( 'acme items', 'Acme_Command' );
get_option( 'acme_settings' );
set_transient( 'acme_cache', array(), 60 );
function acme_install() {
    global $wpdb;
    $table = $wpdb->prefix . 'acme_items';
    dbDelta( $table );
}
""",
                encoding="utf-8",
            )
            source = target / "src"
            source.mkdir()
            (source / "index.js").write_text(
                "import { createElement } from '@wordpress/element';\nexport const AcmeApp = () => createElement( 'div' );\n",
                encoding="utf-8",
            )
            vendor = target / "vendor" / "dependency"
            vendor.mkdir(parents=True)
            (vendor / "ghost.php").write_text(
                "<?php\nadd_action( 'excluded_dependency_hook', 'ghost' );\n",
                encoding="utf-8",
            )

            result = self.run_map(target, "json")
            self.assertEqual(0, result.returncode, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual("wp-cli", data["Project map"]["detected_type"])
            self.assertEqual("acme/v1/items", data["REST routes"][0]["route"])
            self.assertIn("GET", data["REST routes"][0]["methods"])
            self.assertEqual("acme_permissions", data["REST routes"][0]["permission_callback"])
            self.assertEqual({"acme_item", "acme_group"}, {item["name"] for item in data["Post types and taxonomies"]})
            self.assertEqual("acme_card", data["Shortcodes"][0]["tag"])
            self.assertEqual("acme items", data["WP-CLI commands"][0]["command"])
            self.assertEqual(["acme_settings"], data["Database touchpoints"]["options_referenced"])
            self.assertEqual(["acme_cache"], data["Database touchpoints"]["transients_referenced"])
            self.assertEqual("$wpdb->prefix . 'acme_items'", data["Database touchpoints"]["custom_tables"][0]["name"])
            self.assertEqual(["@wordpress/element"], data["JavaScript entry points"][0]["packages"])
            self.assertEqual(["AcmeApp"], data["JavaScript entry points"][0]["exports"])
            roles = {item["file"]: item["role"] for item in data["Files"]}
            self.assertEqual("bootstrap", roles["plugin.php"])
            self.assertEqual("React entry/component", roles["src/index.js"])
            self.assertNotIn("excluded_dependency_hook", result.stdout)

    def test_indexes_rest_routes_declared_with_class_constants(self) -> None:
        """The bundled dashboard controller registers routes via ``self::NAMESPACE``."""
        self.assertTrue(DASHBOARD_STARTER.is_dir(), f"missing starter: {DASHBOARD_STARTER}")
        result = self.run_map(DASHBOARD_STARTER, "json")
        self.assertEqual(0, result.returncode, result.stderr)
        data = json.loads(result.stdout)
        routes = {item["route"] for item in data.get("REST routes", [])}
        self.assertEqual(
            {"myapp/v1/settings", "myapp/v1/items", "myapp/v1/items/(?P<id>\\d+)"},
            routes,
        )
        markdown = self.run_map(DASHBOARD_STARTER)
        self.assertIn("## REST routes", markdown.stdout)
        self.assertIn("myapp/v1/settings", markdown.stdout)
        self.assertNotIn("<unresolved:", markdown.stdout)

    def test_unresolvable_rest_route_argument_is_marked_not_dropped(self) -> None:
        """A dynamic namespace still produces a row, marked unresolved rather than omitted."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "routes.php").write_text(
                "<?php\nregister_rest_route( $this->namespace, '/thing', array(\n"
                "    'methods' => 'GET',\n) );\n",
                encoding="utf-8",
            )
            result = self.run_map(target)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("## REST routes", result.stdout)
            self.assertIn("<unresolved: $this->namespace>/thing", result.stdout)

    def test_rest_metadata_does_not_bleed_between_adjacent_routes(self) -> None:
        """An open route must not inherit methods or permission_callback from a neighbor."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "routes.php").write_text(
                "<?php\n"
                "register_rest_route( 'ns/v1', '/public-open', array(\n"
                "    'methods' => 'GET',\n"
                ") );\n"
                "register_rest_route( 'ns/v1', '/admin-only', array(\n"
                "    'methods' => 'POST',\n"
                "    'permission_callback' => 'is_admin_cb',\n"
                ") );\n",
                encoding="utf-8",
            )
            result = self.run_map(target, "json")
            self.assertEqual(0, result.returncode, result.stderr)
            routes = {item["route"]: item for item in json.loads(result.stdout)["REST routes"]}
            self.assertEqual("no", routes["ns/v1/public-open"]["permission_callback"])
            self.assertEqual("'GET'", routes["ns/v1/public-open"]["methods"])
            self.assertEqual("is_admin_cb", routes["ns/v1/admin-only"]["permission_callback"])
            self.assertEqual("'POST'", routes["ns/v1/admin-only"]["methods"])

    def test_same_named_constants_resolve_within_their_own_class(self) -> None:
        """Two classes sharing a constant name must each resolve to their own value."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "controllers.php").write_text(
                "<?php\n"
                "class Alpha_Controller {\n"
                "    private const NS = 'alpha/v1';\n"
                "    public function register(): void {\n"
                "        register_rest_route( self::NS, '/a', array( 'methods' => 'GET' ) );\n"
                "    }\n"
                "}\n"
                "class Beta_Controller {\n"
                "    private const NS = 'beta/v2';\n"
                "    public function register(): void {\n"
                "        register_rest_route( self::NS, '/b', array( 'methods' => 'POST' ) );\n"
                "    }\n"
                "}\n",
                encoding="utf-8",
            )
            result = self.run_map(target, "json")
            self.assertEqual(0, result.returncode, result.stderr)
            routes = {item["route"] for item in json.loads(result.stdout)["REST routes"]}
            self.assertEqual({"alpha/v1/a", "beta/v2/b"}, routes)

    def test_trailing_methods_value_excludes_closing_brackets(self) -> None:
        """A methods value that ends the array must not capture the closing `) );`."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "routes.php").write_text(
                "<?php\nregister_rest_route( 'ns/v1', '/one-liner', array( 'methods' => 'GET' ) );\n",
                encoding="utf-8",
            )
            result = self.run_map(target, "json")
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("'GET'", json.loads(result.stdout)["REST routes"][0]["methods"])

    def test_static_block_next_to_dynamic_block_stays_static(self) -> None:
        """A static block registration must not inherit a neighbor's render_callback."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "blocks.php").write_text(
                "<?php\n"
                "register_block_type( 'acme/static-card' );\n"
                "register_block_type( 'acme/dynamic-card', array( 'render_callback' => 'acme_render' ) );\n",
                encoding="utf-8",
            )
            result = self.run_map(target, "json")
            self.assertEqual(0, result.returncode, result.stderr)
            blocks = {item["name"]: item["dynamic"] for item in json.loads(result.stdout)["Blocks"]}
            self.assertEqual({"acme/static-card": False, "acme/dynamic-card": True}, blocks)

    def test_output_option_writes_the_requested_format(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "project"
            target.mkdir()
            (target / "plugin.php").write_text(
                "<?php\n/**\n * Plugin Name: Output Fixture\n */\n",
                encoding="utf-8",
            )
            destination = Path(directory) / "maps" / "project.json"
            result = subprocess.run(
                ["python3", str(MAP_SCRIPT), str(target), "--format", "json", "--output", str(destination)],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("", result.stdout)
            self.assertEqual("plugin", json.loads(destination.read_text(encoding="utf-8"))["Project map"]["detected_type"])


if __name__ == "__main__":
    unittest.main()
