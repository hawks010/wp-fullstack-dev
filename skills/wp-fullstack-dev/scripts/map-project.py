#!/usr/bin/env python3
"""Build a compact static map of a WordPress project.

This is a best-effort regex scanner, not a PHP or JavaScript parser.

@author Sonny x Inkfire
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


EXCLUDED_DIRECTORIES = {"vendor", "node_modules", "build", ".git"}
SCANNED_SUFFIXES = {".php", ".js", ".jsx", ".json", ".css", ".scss", ".html"}
EXCLUDED_FILES = {"composer.lock", "package-lock.json"}
HOOK_REGISTRATION_FUNCTIONS = {"add_action", "add_filter"}
HOOK_FIRING_FUNCTIONS = {"do_action", "apply_filters"}
OPTION_FUNCTIONS = {"get_option", "update_option", "delete_option"}
TRANSIENT_FUNCTIONS = {"get_transient", "set_transient", "delete_transient"}
CALL_FUNCTIONS = (
    HOOK_REGISTRATION_FUNCTIONS
    | HOOK_FIRING_FUNCTIONS
    | OPTION_FUNCTIONS
    | TRANSIENT_FUNCTIONS
    | {
        "register_rest_route",
        "register_post_type",
        "register_taxonomy",
        "register_block_type",
        "add_shortcode",
    }
)
CALL_START_RE = re.compile(r"\b(" + "|".join(sorted(CALL_FUNCTIONS, key=len, reverse=True)) + r")\s*\(")
WPCLI_RE = re.compile(r"\bWP_CLI::add_command\s*\(")
CLASS_RE = re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)")
HEADER_RE = re.compile(r"^[ \t]*(?:\*[ \t]+)?(?:Plugin|Theme) Name:", re.MULTILINE | re.IGNORECASE)
TABLE_RE = re.compile(r"\$wpdb->prefix\s*\.\s*(['\"])([^'\"]+)\1")
FUNCTION_RE = re.compile(r"\bfunction\b")

FUNCTION_DEF_RE = re.compile(r"^function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE)
DEFINE_RE = re.compile(r"\bdefine\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]")
OPTION_WRITE_FUNCTIONS = {"update_option", "delete_option"}
IDENTICAL_FILE_MINIMUM_CHARS = 200

SECTION_FILES = "Files"
SECTION_CONFLICTS = "Cross-component conflicts"
SECTION_REGISTERED = "Hooks registered (add_action / add_filter)"
SECTION_FIRED = "Hooks fired (do_action / apply_filters)"
SECTION_GRAPH = "Hook graph"
SECTION_REST = "REST routes"
SECTION_CONTENT = "Post types and taxonomies"
SECTION_BLOCKS = "Blocks"
SECTION_SHORTCODES = "Shortcodes"
SECTION_WPCLI = "WP-CLI commands"
SECTION_DATABASE = "Database touchpoints"
SECTION_JAVASCRIPT = "JavaScript entry points"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Map a WordPress project's static wiring.")
    parser.add_argument("path", nargs="?", default=".", type=Path, help="Project root (default: current directory)")
    parser.add_argument("--output", type=Path, help="Write the map to a file instead of stdout")
    parser.add_argument("--format", choices=("md", "json"), default="md", help="Output format (default: md)")
    return parser.parse_args()


def is_excluded(path: Path, root: Path) -> bool:
    """Return whether a path belongs to an excluded directory."""
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in EXCLUDED_DIRECTORIES for part in parts)


def source_files(root: Path) -> list[Path]:
    """Return stable, relevant source files below the project root."""
    files: list[Path] = []
    for directory, subdirectories, filenames in os.walk(root):
        subdirectories[:] = sorted(name for name in subdirectories if name not in EXCLUDED_DIRECTORIES)
        current = Path(directory)
        for filename in sorted(filenames):
            path = current / filename
            if path.name in EXCLUDED_FILES or path.name.endswith(".min.js"):
                continue
            if path.suffix.lower() in SCANNED_SUFFIXES:
                files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def read_text(path: Path) -> str | None:
    """Read UTF-8-ish source and skip unreadable or binary files."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def relative(path: Path, root: Path) -> str:
    """Return a portable project-relative path."""
    return path.relative_to(root).as_posix()


def line_number(text: str, offset: int) -> int:
    """Return a one-based line number for a text offset."""
    return text.count("\n", 0, offset) + 1


def compact(expression: str, limit: int = 120) -> str:
    """Collapse an expression to a readable single line."""
    value = " ".join(expression.strip().split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def extract_parenthesized(text: str, opening: int) -> tuple[str, int] | None:
    """Extract one balanced call argument string from an opening parenthesis."""
    depth = 0
    quote = ""
    escaped = False
    pairs = {"(": ")", "[": "]", "{": "}"}
    closing = {value: key for key, value in pairs.items()}
    stack: list[str] = []

    for index in range(opening, len(text)):
        character = text[index]
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = ""
            continue
        if character in {"'", '"'}:
            quote = character
            continue
        if character in pairs:
            stack.append(character)
            depth += 1
            continue
        if character in closing:
            if not stack or stack[-1] != closing[character]:
                return None
            stack.pop()
            depth -= 1
            if depth == 0:
                return text[opening + 1 : index], index + 1
    return None


def split_arguments(arguments: str) -> list[str]:
    """Split top-level call arguments while preserving callback arrays and closures."""
    values: list[str] = []
    start = 0
    stack: list[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    closing = {value: key for key, value in pairs.items()}
    quote = ""
    escaped = False

    for index, character in enumerate(arguments):
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = ""
            continue
        if character in {"'", '"'}:
            quote = character
        elif character in pairs:
            stack.append(character)
        elif character in closing and stack and stack[-1] == closing[character]:
            stack.pop()
        elif character == "," and not stack:
            values.append(arguments[start:index].strip())
            start = index + 1
    values.append(arguments[start:].strip())
    return values


def literal_string(expression: str) -> str | None:
    """Return a complete literal string expression, or None for dynamic values."""
    match = re.fullmatch(r"\s*(['\"])(.*?)\1\s*", expression, re.DOTALL)
    if not match or "{$" in match.group(2):
        return None
    return match.group(2)


CONST_RE = re.compile(
    r"(?:(?:private|protected|public|final|static)\s+)*const\s+"
    r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(['\"])(.*?)\2",
)
CONST_REFERENCE_RE = re.compile(
    r"\s*(self|static|[A-Za-z_\\][A-Za-z0-9_\\]*)::([A-Za-z_][A-Za-z0-9_]*)\s*"
)


def class_constant_scopes(text: str) -> list[dict[str, Any]]:
    """Map string class constants per class body so ``self::NAME`` stays class-scoped."""
    scopes: list[dict[str, Any]] = []
    for match in CLASS_RE.finditer(text):
        brace = text.find("{", match.end())
        if brace == -1:
            continue
        extracted = extract_parenthesized(text, brace)
        if not extracted:
            continue
        body, end = extracted
        constants: dict[str, str] = {}
        for constant in CONST_RE.finditer(body):
            name, _quote, value = constant.groups()
            if "{$" not in value:
                constants.setdefault(name, value)
        scopes.append({"name": match.group(1), "start": brace, "end": end, "constants": constants})
    return scopes


def resolve_route_argument(expression: str, offset: int, scopes: list[dict[str, Any]]) -> str:
    """Resolve a REST route argument to a literal, a class constant, or an unresolved marker."""
    value = literal_string(expression)
    if value is not None:
        return value
    reference = CONST_REFERENCE_RE.fullmatch(expression)
    if reference:
        qualifier, name = reference.groups()
        if qualifier in {"self", "static"}:
            enclosing = [scope for scope in scopes if scope["start"] <= offset < scope["end"]]
            scope = max(enclosing, key=lambda item: item["start"], default=None)
        else:
            class_name = qualifier.rsplit("\\", 1)[-1]
            scope = next((item for item in scopes if item["name"] == class_name), None)
        if scope and name in scope["constants"]:
            return scope["constants"][name]
    return f"<unresolved: {compact(expression, 60)}>"


def hook_name(expression: str) -> str | None:
    """Return a literal hook name or a conservative dynamic marker."""
    value = literal_string(expression)
    if value is not None:
        return value
    if "{$" in expression or re.search(r"['\"]\s*\.", expression):
        return "<dynamic>"
    return None


def iter_calls(text: str) -> Iterable[tuple[str, list[str], int, int]]:
    """Yield recognized function calls, parsed only far enough for static arguments."""
    for match in CALL_START_RE.finditer(text):
        extracted = extract_parenthesized(text, match.end() - 1)
        if not extracted:
            continue
        arguments, end = extracted
        yield match.group(1), split_arguments(arguments), match.start(), end
    for match in WPCLI_RE.finditer(text):
        extracted = extract_parenthesized(text, match.end() - 1)
        if not extracted:
            continue
        arguments, end = extracted
        yield "WP_CLI::add_command", split_arguments(arguments), match.start(), end


def classify_file(path: Path, root: Path, text: str) -> str:
    """Classify one source file with conservative WordPress heuristics."""
    rel = relative(path, root)
    if HEADER_RE.search(text):
        return "bootstrap"
    if path.name == "uninstall.php":
        return "uninstall routine"
    if path.name == "block.json":
        return "block definition"
    class_match = CLASS_RE.search(text)
    if "register_rest_route" in text and (
        "controller" in path.name.lower() or (class_match and "controller" in class_match.group(1).lower())
    ):
        return "REST controller"
    if path.suffix.lower() == ".php" and (re.search(r"(?:^|/)includes/class-[^/]+\.php$", rel) or class_match):
        class_name = class_match.group(1) if class_match else path.stem
        return f"class: {class_name}"
    if path.suffix.lower() in {".js", ".jsx"} and "src" in path.parts:
        if re.search(r"(?:from\s*|import\s*)['\"](?:@wordpress/element|react)['\"]", text):
            return "React entry/component"
    return "other"


def detect_project_type(root: Path) -> str:
    """Use the bundled detector so mapper and scaffold routing stay aligned."""
    detector = Path(__file__).with_name("detect-project.sh")
    try:
        result = subprocess.run(
            [str(detector), str(root)],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else "unknown"


def capture_array_value(expression: str, start: int) -> str:
    """Capture one array value expression, stopping at its enclosing comma or closer."""
    stack: list[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    closing = {value: key for key, value in pairs.items()}
    quote = ""
    escaped = False
    for index in range(start, len(expression)):
        character = expression[index]
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = ""
            continue
        if character in {"'", '"'}:
            quote = character
        elif character in pairs:
            stack.append(character)
        elif character in closing:
            if not stack:
                return expression[start:index].strip()
            if stack[-1] == closing[character]:
                stack.pop()
        elif character == "," and not stack:
            return expression[start:index].strip()
    return expression[start:].strip()


def array_key_values(expression: str, key: str) -> list[str]:
    """Return every value assigned to ``key`` within one call's array argument."""
    return [
        capture_array_value(expression, match.end())
        for match in re.finditer(r"['\"]" + re.escape(key) + r"['\"]\s*=>\s*", expression)
    ]


def permission_callback(context: str) -> str:
    """Summarize the permission callbacks declared in one route's own arguments."""
    summaries: list[str] = []
    for value in array_key_values(context, "permission_callback"):
        expression = compact(value, 80)
        literal = literal_string(expression)
        if literal:
            summary = literal
        elif re.fullmatch(r"[A-Za-z_\\][A-Za-z0-9_:\\]*", expression):
            summary = expression
        else:
            summary = "yes"
        if summary not in summaries:
            summaries.append(summary)
    return " | ".join(summaries) if summaries else "no"


def rest_methods(context: str) -> str:
    """Summarize literal or constant REST method declarations in one route's arguments."""
    values: list[str] = []
    for value in array_key_values(context, "methods"):
        value = compact(value, 80)
        if value and value not in values:
            values.append(value)
    return " | ".join(values) if values else "UNKNOWN"


def load_block_json(path: Path) -> dict[str, Any] | None:
    """Load block metadata when the file is valid and named."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("name"), str):
        return None
    return data


def nearest_block(path: Path, root: Path, definitions: list[dict[str, Any]], expression: str) -> dict[str, Any] | None:
    """Resolve an __DIR__ registration to nearby block metadata without guessing a name."""
    candidates: list[Path] = [path.parent / "block.json"]
    suffix = re.search(r"__DIR__\s*\.\s*(['\"])([^'\"]+)\1", expression)
    if suffix:
        candidates.insert(0, path.parent / suffix.group(2).strip("/") / "block.json")
    for candidate in candidates:
        if is_excluded(candidate, root):
            continue
        data = load_block_json(candidate)
        if data:
            return {"name": data["name"], "file": relative(candidate, root), "dynamic": bool(data.get("render"))}
    if not definitions:
        return None

    def distance(item: dict[str, Any]) -> int:
        source_parts = path.parent.resolve().parts
        block_parts = Path(item["absolute"]).parent.resolve().parts
        common = 0
        for source_part, block_part in zip(source_parts, block_parts):
            if source_part != block_part:
                break
            common += 1
        return len(source_parts) + len(block_parts) - (2 * common)

    return min(
        definitions,
        key=distance,
    )


def same_function_has_dbdelta(text: str, offset: int) -> bool:
    """Require dbDelta in the nearest static function region around a table expression."""
    starts = [match.start() for match in FUNCTION_RE.finditer(text)]
    previous = max((start for start in starts if start <= offset), default=0)
    following = min((start for start in starts if start > offset), default=len(text))
    return re.search(r"\bdbDelta\s*\(", text[previous:following]) is not None


def javascript_entry(path: Path, root: Path, text: str) -> dict[str, Any] | None:
    """Return WordPress package and export information for a JavaScript source file."""
    packages = sorted(
        set(
            re.findall(
                r"(?:from\s*|import\s*|require\s*\(\s*)['\"](@wordpress/[^'\"]+)['\"]",
                text,
            )
        )
    )
    exports = set(re.findall(r"\bexport\s+(?:const|let|var|function|class)\s+([A-Za-z_$][\w$]*)", text))
    if re.search(r"\bexport\s+default\b", text):
        exports.add("default")
    exports.update(re.findall(r"\bexports\.([A-Za-z_$][\w$]*)\s*=", text))
    if re.search(r"\bmodule\.exports\s*=", text):
        exports.add("module.exports")
    if not packages and not exports and path.name not in {"index.js", "index.jsx"}:
        return None
    return {"file": relative(path, root), "packages": packages, "exports": sorted(exports)}


def component_of(rel: str) -> str:
    """Return the top-level component directory of a project-relative path."""
    return rel.split("/", 1)[0]


def site_components(files: list[dict[str, Any]]) -> list[str]:
    """Detect component subdirectories when the scanned root is a multi-component site."""
    if any("/" not in item["file"] and item["role"] == "bootstrap" for item in files):
        return []
    components = sorted(
        {component_of(item["file"]) for item in files if "/" in item["file"] and item["role"] == "bootstrap"}
    )
    return components if len(components) >= 2 else []


def cross_component_conflicts(
    result: dict[str, Any],
    contents: dict[Path, str],
    root: Path,
    components: list[str],
    option_writes: list[tuple[str, str]],
) -> dict[str, Any]:
    """Report duplicated hooks, files, symbols, and option ownership across components."""
    member = set(components)
    conflicts: dict[str, Any] = {
        "duplicate_hooks": [],
        "identical_files": [],
        "duplicate_functions": [],
        "duplicate_constants": [],
        "contested_option_writes": [],
    }

    hooks: dict[tuple[str, str], dict[str, list[str]]] = {}
    for item in result["registered"]:
        component = component_of(item["file"])
        if component not in member or item["hook"] == "<dynamic>":
            continue
        hooks.setdefault((item["hook"], item["callback"]), {}).setdefault(component, []).append(
            f"{item['file']}:{item['line']}"
        )
    for (hook, callback), by_component in sorted(hooks.items()):
        if len(by_component) >= 2:
            conflicts["duplicate_hooks"].append(
                {
                    "hook": hook,
                    "callback": callback,
                    "locations": sorted(location for group in by_component.values() for location in group),
                }
            )

    digests: dict[str, list[tuple[str, str]]] = {}
    functions: dict[str, dict[str, list[str]]] = {}
    constants: dict[str, dict[str, list[str]]] = {}
    for path, text in contents.items():
        rel = relative(path, root)
        component = component_of(rel)
        if component not in member:
            continue
        if len(text) >= IDENTICAL_FILE_MINIMUM_CHARS:
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            digests.setdefault(digest, []).append((component, rel))
        if path.suffix.lower() == ".php":
            for name in set(FUNCTION_DEF_RE.findall(text)):
                functions.setdefault(name, {}).setdefault(component, []).append(rel)
            for name in set(DEFINE_RE.findall(text)):
                constants.setdefault(name, {}).setdefault(component, []).append(rel)
    for _digest, entries in sorted(digests.items()):
        if len({component for component, _rel in entries}) >= 2:
            conflicts["identical_files"].append({"files": sorted(rel for _component, rel in entries)})
    for table, key in ((functions, "duplicate_functions"), (constants, "duplicate_constants")):
        for name, by_component in sorted(table.items()):
            if len(by_component) >= 2:
                conflicts[key].append(
                    {"name": name, "files": sorted(rel for group in by_component.values() for rel in group)}
                )

    writes: dict[str, dict[str, list[str]]] = {}
    for option, rel in option_writes:
        component = component_of(rel)
        if component in member:
            writes.setdefault(option, {}).setdefault(component, []).append(rel)
    for option, by_component in sorted(writes.items()):
        if len(by_component) >= 2:
            conflicts["contested_option_writes"].append(
                {"option": option, "files": sorted(rel for group in by_component.values() for rel in group)}
            )
    return conflicts


def scan_project(root: Path) -> dict[str, Any]:
    """Scan a project and return structured, stable map data."""
    paths = source_files(root)
    contents: dict[Path, str] = {}
    for path in paths:
        text = read_text(path)
        if text is not None:
            contents[path] = text

    result: dict[str, Any] = {
        "detected_type": detect_project_type(root),
        "file_count": len(contents),
        "files": [],
        "registered": [],
        "fired": [],
        "graph": [],
        "rest": [],
        "content": [],
        "blocks": [],
        "shortcodes": [],
        "wpcli": [],
        "tables": [],
        "options": set(),
        "transients": set(),
        "javascript": [],
    }

    option_writes: list[tuple[str, str]] = []
    block_definitions: list[dict[str, Any]] = []
    for path, text in contents.items():
        rel = relative(path, root)
        result["files"].append({"file": rel, "role": classify_file(path, root, text)})
        if path.name == "block.json":
            data = load_block_json(path)
            if data:
                definition = {
                    "name": data["name"],
                    "file": rel,
                    "dynamic": bool(data.get("render")),
                    "absolute": str(path),
                }
                block_definitions.append(definition)
                result["blocks"].append({key: definition[key] for key in ("name", "file", "dynamic")})

    for path, text in contents.items():
        rel = relative(path, root)
        scopes = class_constant_scopes(text)
        for function, arguments, start, end in iter_calls(text):
            line = line_number(text, start)
            if function in HOOK_REGISTRATION_FUNCTIONS and len(arguments) >= 2:
                name = hook_name(arguments[0])
                if not name:
                    continue
                priority = arguments[2].strip() if len(arguments) >= 3 and re.fullmatch(r"-?\d+", arguments[2].strip()) else "10"
                result["registered"].append(
                    {"hook": name, "priority": int(priority), "file": rel, "line": line, "callback": compact(arguments[1])}
                )
            elif function in HOOK_FIRING_FUNCTIONS and arguments:
                name = hook_name(arguments[0])
                if name:
                    result["fired"].append({"hook": name, "file": rel, "line": line})
            elif function == "register_rest_route" and len(arguments) >= 2:
                namespace = resolve_route_argument(arguments[0], start, scopes)
                route = resolve_route_argument(arguments[1], start, scopes)
                context = arguments[2] if len(arguments) >= 3 else ""
                result["rest"].append(
                    {
                        "route": namespace.rstrip("/") + "/" + route.lstrip("/"),
                        "methods": rest_methods(context),
                        "file": rel,
                        "line": line,
                        "permission_callback": permission_callback(context),
                    }
                )
            elif function in {"register_post_type", "register_taxonomy"} and arguments:
                name = literal_string(arguments[0])
                if name:
                    result["content"].append(
                        {"name": name, "kind": "post_type" if function == "register_post_type" else "taxonomy", "file": rel, "line": line}
                    )
            elif function == "register_block_type" and arguments:
                expression = arguments[0]
                block: dict[str, Any] | None = None
                if "__DIR__" in expression:
                    block = nearest_block(path, root, block_definitions, expression)
                else:
                    name = literal_string(expression)
                    if name:
                        block = {
                            "name": name,
                            "file": rel,
                            "dynamic": "render_callback" in text[start:end],
                        }
                if block and not any(item["name"] == block["name"] for item in result["blocks"]):
                    result["blocks"].append({key: block[key] for key in ("name", "file", "dynamic")})
            elif function == "add_shortcode" and arguments:
                tag = literal_string(arguments[0])
                if tag:
                    result["shortcodes"].append({"tag": tag, "file": rel, "line": line})
            elif function == "WP_CLI::add_command" and arguments:
                command = literal_string(arguments[0])
                if command:
                    result["wpcli"].append({"command": command, "file": rel, "line": line})
            elif function in OPTION_FUNCTIONS and arguments:
                key = literal_string(arguments[0])
                if key:
                    result["options"].add(key)
                    if function in OPTION_WRITE_FUNCTIONS:
                        option_writes.append((key, rel))
            elif function in TRANSIENT_FUNCTIONS and arguments:
                key = literal_string(arguments[0])
                if key:
                    result["transients"].add(key)

        for match in TABLE_RE.finditer(text):
            if same_function_has_dbdelta(text, match.start()):
                result["tables"].append(
                    {"name": f"$wpdb->prefix . '{match.group(2)}'", "file": rel, "line": line_number(text, match.start())}
                )

        if path.suffix.lower() in {".js", ".jsx"}:
            entry = javascript_entry(path, root, text)
            if entry:
                result["javascript"].append(entry)

    registered_by_hook: dict[str, list[dict[str, Any]]] = {}
    fired_by_hook: dict[str, list[dict[str, Any]]] = {}
    for item in result["registered"]:
        if item["hook"] != "<dynamic>":
            registered_by_hook.setdefault(item["hook"], []).append(item)
    for item in result["fired"]:
        if item["hook"] != "<dynamic>":
            fired_by_hook.setdefault(item["hook"], []).append(item)
    for name in sorted(registered_by_hook.keys() & fired_by_hook.keys()):
        result["graph"].append(
            {"hook": name, "fired_by": fired_by_hook[name], "registered_by": registered_by_hook[name]}
        )

    for key in ("files", "registered", "fired", "rest", "content", "blocks", "shortcodes", "wpcli", "tables", "javascript"):
        result[key] = sorted(result[key], key=lambda item: tuple(str(value) for value in item.values()))
    result["options"] = sorted(result["options"])
    result["transients"] = sorted(result["transients"])
    result["components"] = site_components(result["files"])
    result["conflicts"] = (
        cross_component_conflicts(result, contents, root, result["components"], option_writes)
        if result["components"]
        else {}
    )
    return result


def markdown(data: dict[str, Any]) -> str:
    """Render map data as compact Markdown."""
    lines = [f"# Project map — {data['detected_type']} — {data['file_count']} files scanned"]

    if data["files"]:
        lines.extend(["", f"## {SECTION_FILES}"])
        lines.extend(f"{item['file']} — {item['role']}" for item in data["files"])
    if data["components"]:
        conflicts = data["conflicts"]
        lines.extend(["", f"## {SECTION_CONFLICTS} ({len(data['components'])} components: {', '.join(data['components'])})"])
        if not any(conflicts.values()):
            lines.append("None detected: no duplicate hooks, identical files, duplicated symbols, or contested option writes.")
        if conflicts["duplicate_hooks"]:
            lines.append("Duplicate hook registrations (same hook and callback in more than one component):")
            lines.extend(
                f"`{item['hook']}` → {item['callback']} — {', '.join(item['locations'])}"
                for item in conflicts["duplicate_hooks"]
            )
        if conflicts["identical_files"]:
            lines.append("Identical files shipped by more than one component:")
            lines.extend(" == ".join(item["files"]) for item in conflicts["identical_files"])
        if conflicts["duplicate_functions"]:
            lines.append("Functions defined in more than one component (fatal redeclaration risk):")
            lines.extend(f"{item['name']}() — {', '.join(item['files'])}" for item in conflicts["duplicate_functions"])
        if conflicts["duplicate_constants"]:
            lines.append("Constants defined in more than one component (drift risk):")
            lines.extend(f"{item['name']} — {', '.join(item['files'])}" for item in conflicts["duplicate_constants"])
        if conflicts["contested_option_writes"]:
            lines.append("Options written by more than one component (contested ownership):")
            lines.extend(f"{item['option']} — {', '.join(item['files'])}" for item in conflicts["contested_option_writes"])
    if data["registered"]:
        lines.extend(["", f"## {SECTION_REGISTERED}"])
        lines.extend(
            f"`{item['hook']}` [priority {item['priority']}] — {item['file']}:{item['line']} → {item['callback']}"
            for item in data["registered"]
        )
    if data["fired"]:
        lines.extend(["", f"## {SECTION_FIRED}"])
        lines.extend(f"`{item['hook']}` — {item['file']}:{item['line']}" for item in data["fired"])
    if data["graph"]:
        lines.extend(["", f"## {SECTION_GRAPH}"])
        for item in data["graph"]:
            fired = ", ".join(f"{entry['file']}:{entry['line']}" for entry in item["fired_by"])
            registered = ", ".join(f"{entry['file']}:{entry['line']}" for entry in item["registered_by"])
            lines.extend([f"`{item['hook']}`", f"  fired by:      {fired}", f"  registered by: {registered}"])
    if data["rest"]:
        lines.extend(["", f"## {SECTION_REST}"])
        lines.extend(
            f"`{item['route']}` [{item['methods']}] — {item['file']}:{item['line']} — permission_callback: {item['permission_callback']}"
            for item in data["rest"]
        )
    if data["content"]:
        lines.extend(["", f"## {SECTION_CONTENT}"])
        lines.extend(
            f"{item['name']} ({item['kind']}) — {item['file']}:{item['line']}" for item in data["content"]
        )
    if data["blocks"]:
        lines.extend(["", f"## {SECTION_BLOCKS}"])
        lines.extend(
            f"`{item['name']}` — {item['file']} — dynamic: {'yes' if item['dynamic'] else 'no'}" for item in data["blocks"]
        )
    if data["shortcodes"]:
        lines.extend(["", f"## {SECTION_SHORTCODES}"])
        lines.extend(f"`[{item['tag']}]` — {item['file']}:{item['line']}" for item in data["shortcodes"])
    if data["wpcli"]:
        lines.extend(["", f"## {SECTION_WPCLI}"])
        lines.extend(f"`{item['command']}` — {item['file']}:{item['line']}" for item in data["wpcli"])
    if data["tables"] or data["options"] or data["transients"]:
        lines.extend(["", f"## {SECTION_DATABASE}"])
        if data["tables"]:
            lines.append(
                "Custom tables: "
                + ", ".join(f"{item['name']} (dbDelta in {item['file']})" for item in data["tables"])
            )
        if data["options"]:
            lines.append("Options referenced: " + ", ".join(data["options"]))
        if data["transients"]:
            lines.append("Transients referenced: " + ", ".join(data["transients"]))
    if data["javascript"]:
        lines.extend(["", f"## {SECTION_JAVASCRIPT}"])
        for item in data["javascript"]:
            packages = ", ".join(item["packages"]) if item["packages"] else "none"
            exports = ", ".join(item["exports"]) if item["exports"] else "none"
            lines.append(f"{item['file']} — WP packages used: {packages}, exports: {exports}")
    return "\n".join(lines) + "\n"


def json_document(data: dict[str, Any]) -> str:
    """Render map data with Markdown section names as JSON object keys."""
    document: dict[str, Any] = {
        "Project map": {"detected_type": data["detected_type"], "file_count": data["file_count"]}
    }
    sections = (
        (SECTION_FILES, data["files"]),
        (
            SECTION_CONFLICTS,
            {"components": data["components"], **data["conflicts"]} if data["components"] else None,
        ),
        (SECTION_REGISTERED, data["registered"]),
        (SECTION_FIRED, data["fired"]),
        (SECTION_GRAPH, data["graph"]),
        (SECTION_REST, data["rest"]),
        (SECTION_CONTENT, data["content"]),
        (SECTION_BLOCKS, data["blocks"]),
        (SECTION_SHORTCODES, data["shortcodes"]),
        (SECTION_WPCLI, data["wpcli"]),
        (
            SECTION_DATABASE,
            {
                "custom_tables": data["tables"],
                "options_referenced": data["options"],
                "transients_referenced": data["transients"],
            }
            if data["tables"] or data["options"] or data["transients"]
            else None,
        ),
        (SECTION_JAVASCRIPT, data["javascript"]),
    )
    for name, value in sections:
        if value:
            document[name] = value
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    """Run the project mapper."""
    args = parse_args()
    root = args.path.expanduser().resolve()
    if not root.is_dir():
        print(f"Project path is not a directory: {root}", file=sys.stderr)
        return 2
    data = scan_project(root)
    output = json_document(data) if args.format == "json" else markdown(data)
    if args.output:
        destination = args.output.expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
