#!/usr/bin/env python3
"""Create and verify a deployable WordPress plugin ZIP.

@author Sonny x Inkfire
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
import zipfile
from pathlib import Path


EXCLUDED_DIRECTORIES = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "e2e",
    "node_modules",
    "playwright-report",
    "test-results",
    "tests",
}
EXCLUDED_FILES = {
    ".DS_Store",
    ".phpunit.result.cache",
    ".wp-env.json",
    "Thumbs.db",
    "composer.lock",
    "package-lock.json",
}
EXCLUDED_PATTERNS = (
    "*.bak",
    "*.bak-*",
    "*.bak.*",
    "*.log",
    "*.map",
    "*.orig",
    "*.rej",
    "*error_log",
    "*~",
    "phpcs.xml*",
    "phpunit.xml*",
    "playwright.config.*",
)
PLATFORM_REQUIREMENTS = ("php", "composer-plugin-api", "composer-runtime-api")
PLUGIN_HEADER_RE = re.compile(r"^[ \t]*\*[ \t]+Plugin Name:", re.MULTILINE | re.IGNORECASE)
STATIC_INCLUDE_RE = re.compile(
    r"\b(?:require|include)(?:_once)?\s*(?:\(\s*)?__DIR__\s*\.\s*(['\"])(/[^'\"]+\.php)\1"
)
VENDOR_AUTOLOAD_RE = re.compile(r"vendor\s*/\s*autoload\.php|vendor/autoload\.php", re.IGNORECASE)


class PackageError(RuntimeError):
    """Raised when a project cannot produce a safe runtime archive."""


def parse_args() -> argparse.Namespace:
    """Parse the public packaging interface."""
    parser = argparse.ArgumentParser(description="Create a verified deployable WordPress plugin ZIP.")
    parser.add_argument("target", nargs="?", default=".", type=Path, help="Plugin directory (default: current directory)")
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        help="Output directory or exact .zip file (default: sibling dist directory)",
    )
    return parser.parse_args()


def archive_path(target: Path, output: Path | None) -> Path:
    """Resolve directory and exact-file output forms without ambiguous nesting."""
    if output is None:
        return target.parent / "dist" / f"{target.name}.zip"
    output = output.expanduser().resolve()
    if output.suffix.lower() == ".zip":
        return output
    return output / f"{target.name}.zip"


def excluded(relative: Path, include_vendor: bool) -> bool:
    """Return whether a project-relative file is development-only."""
    if any(part in EXCLUDED_DIRECTORIES for part in relative.parts[:-1]):
        return True
    if relative.parts and relative.parts[0] == "vendor" and not include_vendor:
        return True
    if relative.name in EXCLUDED_FILES:
        return True
    return any(fnmatch.fnmatch(relative.name, pattern) for pattern in EXCLUDED_PATTERNS)


def read_php(path: Path) -> str:
    """Read PHP for best-effort runtime dependency checks."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def php_sources(target: Path) -> list[Path]:
    """Return project PHP files without traversing dependencies or dev trees."""
    paths: list[Path] = []
    for directory, subdirectories, filenames in os.walk(target):
        subdirectories[:] = sorted(
            name for name in subdirectories if name not in EXCLUDED_DIRECTORIES and name != "vendor"
        )
        current = Path(directory)
        for filename in sorted(filenames):
            if filename.endswith(".php"):
                paths.append(current / filename)
    return paths


def composer_runtime_packages(target: Path) -> list[str]:
    """Return Composer runtime packages that need a distributable vendor tree."""
    composer_file = target / "composer.json"
    if not composer_file.exists():
        return []
    try:
        composer = json.loads(composer_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PackageError(f"Invalid composer.json: {error}") from error
    requirements = composer.get("require", {})
    if not isinstance(requirements, dict):
        raise PackageError("composer.json require must be an object")
    return sorted(
        name
        for name in requirements
        if name not in PLATFORM_REQUIREMENTS
        and not name.startswith("ext-")
        and not name.startswith("lib-")
    )


def installed_dev_packages(target: Path) -> list[str]:
    """Detect development packages in Composer's installed metadata."""
    installed_file = target / "vendor" / "composer" / "installed.json"
    if not installed_file.exists():
        return []
    try:
        installed = json.loads(installed_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PackageError(f"Invalid vendor/composer/installed.json: {error}") from error
    packages = installed.get("packages", []) if isinstance(installed, dict) else installed
    if not isinstance(packages, list):
        raise PackageError("vendor/composer/installed.json packages must be an array")
    return sorted(
        package.get("name", "<unknown>")
        for package in packages
        if isinstance(package, dict) and package.get("dev_requirement") is True
    )


def runtime_analysis(target: Path) -> tuple[bool, list[Path], list[str]]:
    """Determine vendor needs and resolve static __DIR__ runtime includes."""
    sources = php_sources(target)
    runtime_packages = composer_runtime_packages(target)
    static_dependencies: list[Path] = []
    references_vendor = False

    for source in sources:
        content = read_php(source)
        if VENDOR_AUTOLOAD_RE.search(content):
            references_vendor = True
        for match in STATIC_INCLUDE_RE.finditer(content):
            dependency = (source.parent / match.group(2).lstrip("/")).resolve()
            try:
                dependency.relative_to(target)
            except ValueError as error:
                raise PackageError(f"Runtime include escapes the plugin directory: {source}") from error
            if not dependency.is_file():
                relative = dependency.relative_to(target).as_posix()
                raise PackageError(f"Missing static runtime include: {relative} (referenced by {source.relative_to(target)})")
            static_dependencies.append(dependency)

    vendor_required = references_vendor or bool(runtime_packages)
    if vendor_required:
        autoload = target / "vendor" / "autoload.php"
        if not autoload.is_file():
            reason = ", ".join(runtime_packages) if runtime_packages else "vendor/autoload.php is referenced"
            raise PackageError(f"Runtime Composer dependencies are not installed ({reason}); run composer install --no-dev first")
        dev_packages = installed_dev_packages(target)
        if dev_packages:
            raise PackageError(
                "Development Composer packages are installed ("
                + ", ".join(dev_packages)
                + "); run composer install --no-dev before packaging"
            )
    return vendor_required, static_dependencies, runtime_packages


def plugin_bootstraps(target: Path) -> list[Path]:
    """Find plugin headers before creating an archive."""
    bootstraps = []
    for path in php_sources(target):
        if PLUGIN_HEADER_RE.search(read_php(path)):
            bootstraps.append(path)
    if not bootstraps:
        raise PackageError("No WordPress Plugin Name header found in the target")
    return bootstraps


def collect_files(target: Path, include_vendor: bool, archive: Path) -> list[Path]:
    """Collect stable runtime files while pruning development trees before traversal."""
    files: list[Path] = []
    for directory, subdirectories, filenames in os.walk(target):
        subdirectories[:] = sorted(
            name
            for name in subdirectories
            if name not in EXCLUDED_DIRECTORIES and (name != "vendor" or include_vendor)
        )
        current = Path(directory)
        for filename in sorted(filenames):
            path = current / filename
            if path.resolve() == archive:
                continue
            relative = path.relative_to(target)
            if excluded(relative, include_vendor):
                continue
            if path.is_symlink():
                resolved = path.resolve()
                try:
                    resolved.relative_to(target)
                except ValueError as error:
                    raise PackageError(f"Refusing to package external symlink: {relative}") from error
            if path.is_file():
                files.append(path)
    if not files:
        raise PackageError("No runtime files remain after packaging exclusions")
    return sorted(files, key=lambda path: path.relative_to(target).as_posix())


def create_archive(target: Path, archive: Path, files: list[Path]) -> None:
    """Create a single-root compressed archive."""
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.unlink(missing_ok=True)
    try:
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as handle:
            for path in files:
                handle.write(path, (Path(target.name) / path.relative_to(target)).as_posix())
    except Exception:
        archive.unlink(missing_ok=True)
        raise


def verify_archive(
    target: Path,
    archive: Path,
    bootstraps: list[Path],
    static_dependencies: list[Path],
    vendor_required: bool,
) -> None:
    """Fail closed when the produced ZIP omits known runtime files or ships dev artifacts."""
    expected_root = f"{target.name}/"
    with zipfile.ZipFile(archive) as handle:
        bad = handle.testzip()
        if bad:
            raise PackageError(f"Archive integrity check failed at {bad}")
        names = set(handle.namelist())

    if not names or any(not name.startswith(expected_root) for name in names):
        raise PackageError("Archive must contain exactly one top-level plugin directory")

    required = set(bootstraps + static_dependencies)
    if vendor_required:
        required.add(target / "vendor" / "autoload.php")
    missing = []
    for path in sorted(required):
        name = (Path(target.name) / path.relative_to(target)).as_posix()
        if name not in names:
            missing.append(path.relative_to(target).as_posix())
    if missing:
        raise PackageError("Archive is missing runtime files: " + ", ".join(missing))

    forbidden_fragments = ("/.git/", "/.github/", "/node_modules/", "/tests/", "/e2e/")
    leaked = sorted(name for name in names if any(fragment in f"/{name}" for fragment in forbidden_fragments))
    if leaked:
        raise PackageError("Archive contains development files: " + ", ".join(leaked[:5]))


def main() -> int:
    """Package and verify one plugin."""
    args = parse_args()
    target = args.target.expanduser().resolve()
    if not target.is_dir():
        print(f"Plugin path is not a directory: {target}", file=sys.stderr)
        return 2
    archive = archive_path(target, args.output)
    try:
        bootstraps = plugin_bootstraps(target)
        vendor_required, static_dependencies, _runtime_packages = runtime_analysis(target)
        files = collect_files(target, vendor_required, archive)
        create_archive(target, archive, files)
        verify_archive(target, archive, bootstraps, static_dependencies, vendor_required)
    except (PackageError, OSError, zipfile.BadZipFile) as error:
        archive.unlink(missing_ok=True)
        print(f"Packaging failed: {error}", file=sys.stderr)
        return 2
    print(f"Created {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
