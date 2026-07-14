#!/usr/bin/env python3
"""Create a WordPress project from a bundled starter.

@author Sonny x Inkfire
Generated project authorship is optional.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


STARTERS = {
    "plugin": "plugin-starter",
    "dashboard": "dashboard-plugin-starter",
    "block": "block-plugin-starter",
    "classic-theme": "classic-theme-starter",
    "block-theme": "block-theme-starter",
    "woocommerce": "woocommerce-extension-starter",
    "multisite": "multisite-plugin-starter",
    "wpcli": "wpcli-plugin-starter",
}

PRIMARY_FILES = {
    "plugin": "my-agentic-plugin.php",
    "dashboard": "myapp-dashboard.php",
    "block": "example-block.php",
    "woocommerce": "example-woocommerce-extension.php",
    "multisite": "example-multisite.php",
    "wpcli": "example-wpcli.php",
}

TEXT_SUFFIXES = {
    ".css", ".html", ".js", ".json", ".md", ".php", ".pot", ".scss",
    ".dist", ".lock", ".txt", ".xml", ".yaml", ".yml",
}


def slugify(value: str) -> str:
    """Return a valid lower-case project slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("Project name must contain at least one letter or number.")
    return slug


def display_name(value: str) -> str:
    """Turn a slug or free-form name into a readable title."""
    return " ".join(word.capitalize() for word in re.split(r"[-_\s]+", value) if word)


def namespace_for(slug: str) -> str:
    """Return a compact PascalCase PHP namespace."""
    namespace = "".join(part.capitalize() for part in slug.split("-"))
    return namespace if not namespace[:1].isdigit() else f"Project{namespace}"


def prefix_for(slug: str) -> str:
    """Return a stable prefix from the first characters of slug words."""
    words = slug.split("-")
    short = "".join(word[0] for word in words if word)
    return (short if len(short) >= 3 else "".join(words)[:8]).lower()


def replacements(project_type: str, raw_name: str, author: str) -> dict[str, str]:
    """Build placeholder and legacy-example replacement values."""
    slug = slugify(raw_name)
    title = display_name(raw_name)
    namespace = namespace_for(slug)
    prefix = prefix_for(slug)
    values = {
        "{{PROJECT_NAME}}": title,
        "{{PLUGIN_NAME}}": title,
        "{{TEXT_DOMAIN}}": slug,
        "{{NAMESPACE}}": namespace,
        "{{PREFIX}}": prefix,
        "{{AUTHOR}}": author,
        "Sonny x Inkfire": author,
    }

    legacy = {
        "plugin": {
            "My Agentic Plugin": title, "my-agentic-plugin": slug,
            "MyAgenticPlugin": namespace, "MYAP": prefix.upper(), "myap": prefix,
        },
        "dashboard": {
            "My App Dashboard": title, "My App": title,
            "myapp-dashboard": slug, "MyAppDashboard": namespace,
            "MYAPP_DASHBOARD": prefix.upper(), "myapp": prefix,
        },
        "block": {
            "Example Dynamic Block": title, "Example Message": title,
            "example-dynamic-block": slug, "example/message": f"{prefix}/message",
        },
        "classic-theme": {
            "My Agentic Child Theme": title, "my-agentic-child-theme": slug,
        },
        "block-theme": {
            "Example Block Theme": title, "example-block-theme": slug,
        },
        "woocommerce": {
            "Example WooCommerce Extension": title,
            "example-woocommerce-extension": slug,
            "ExampleWooCommerceExtension": namespace,
        },
        "multisite": {
            "Example Multisite Lifecycle": title, "example-multisite": slug,
            "ExampleMultisite": namespace,
        },
        "wpcli": {
            "Example WP-CLI Command": title, "example-wpcli": slug,
            "MyApp_Command": f"{namespace}_Command", "myapp": prefix,
        },
    }
    values.update(legacy.get(project_type, {}))
    return values


def rewrite_tree(target: Path, values: dict[str, str], author: str) -> None:
    """Replace placeholders in text files without touching binary assets."""
    for path in target.rglob("*"):
        if not path.is_file() or (path.suffix.lower() not in TEXT_SUFFIXES and path.name != ".gitignore"):
            continue
        content = path.read_text(encoding="utf-8")
        for old, new in sorted(values.items(), key=lambda pair: len(pair[0]), reverse=True):
            content = content.replace(old, new)
        if not author:
            content = re.sub(r'\s*"authors"\s*:\s*\[.*?\]\s*,?', "", content, flags=re.DOTALL)
            content = re.sub(r"^.*@author\s*$\n?", "", content, flags=re.MULTILINE)
            content = re.sub(r"^\s*\*?\s*Author:\s*$\n?", "", content, flags=re.MULTILINE)
            content = re.sub(r'^\s*"author":\s*"",?\s*$\n?', "", content, flags=re.MULTILINE)
            content = re.sub(r'^\s*\{\s*"name":\s*""\s*\},?\s*$\n?', "", content, flags=re.MULTILINE)
            content = content.replace(" by .", ".").replace(" by ,", ",")
        path.write_text(content, encoding="utf-8")


def run_optional(command: list[str], cwd: Path, label: str) -> bool:
    """Run an optional setup command and report a non-fatal failure."""
    try:
        result = subprocess.run(command, cwd=cwd, check=False)
    except OSError as error:
        print(f"Skipped {label}: {error}")
        return False
    if result.returncode:
        print(f"Warning: {label} failed with exit code {result.returncode}.")
        return False
    return True


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Scaffold a WordPress project.")
    parser.add_argument("--type", choices=sorted(STARTERS))
    parser.add_argument("--name", help="Project name or slug")
    parser.add_argument("--output", type=Path, help="Parent output directory")
    parser.add_argument("--author", default=None, help="Optional generated-code author")
    parser.add_argument("--no-git", action="store_true", help="Do not initialize Git")
    parser.add_argument("--skip-install", action="store_true", help="Do not install dependencies")
    return parser.parse_args()


def main() -> int:
    """Scaffold and optionally initialize the requested project."""
    args = parse_args()
    project_type = args.type or input(f"Project type ({', '.join(STARTERS)}): ").strip()
    raw_name = args.name or input("Project name: ").strip()
    author = args.author if args.author is not None else input("Author (optional): ").strip() if not args.name else ""

    if project_type not in STARTERS:
        print(f"Unsupported project type: {project_type}", file=sys.stderr)
        return 2

    try:
        slug = slugify(raw_name)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    output = (args.output or Path.cwd()).expanduser().resolve()
    target = output / slug
    source = Path(__file__).resolve().parent.parent / "assets" / STARTERS[project_type]
    if target.exists():
        print(f"Refusing to overwrite existing path: {target}", file=sys.stderr)
        return 3

    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("node_modules", "vendor", ".phpunit.result.cache"))
    values = replacements(project_type, raw_name, author)
    rewrite_tree(target, values, author)

    primary = PRIMARY_FILES.get(project_type)
    if primary and (target / primary).exists():
        (target / primary).rename(target / f"{slug}.php")

    if not args.no_git and shutil.which("git"):
        run_optional(["git", "init"], target, "Git initialization")

    if not args.skip_install:
        if (target / "composer.json").exists() and shutil.which("composer"):
            run_optional(["composer", "install", "--no-interaction"], target, "Composer install")
        if (target / "package.json").exists() and shutil.which("npm"):
            run_optional(["npm", "install"], target, "npm install")

    print(f"Created {project_type} project: {target}")
    print(f"Next: review the generated metadata, then run validate.sh {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
