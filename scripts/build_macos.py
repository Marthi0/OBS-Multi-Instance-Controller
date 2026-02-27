#!/usr/bin/env python3
"""Build script for macOS."""

import sys
import argparse
import platform as sys_platform
from pathlib import Path

from build import (
    get_project_root,
    get_architecture,
    ensure_dependencies_installed,
    run_pyinstaller,
    create_archive,
    get_artifact_name,
    print_build_info,
)


def build_macos(version: str, output_dir: Path, arch: str = "") -> Path:
    """Build for macOS (current architecture).

    Args:
        version: Version string (e.g., "0.1.0")
        output_dir: Output directory for dist/
        arch: Optional architecture override (e.g., "x86_64", "arm64")

    Returns:
        Path: Path to built application
    """
    project_root = get_project_root()
    spec_file = project_root / "scripts" / "pyinstaller.spec"
    detected_arch = get_architecture()

    # Use provided arch or auto-detect
    final_arch = arch if arch else detected_arch

    print_build_info(version, "macOS", final_arch)

    # Ensure dependencies
    print("Installing dependencies...")
    ensure_dependencies_installed()

    # Run PyInstaller (creates app bundle)
    print("Building app bundle with PyInstaller...")
    dist_dir = run_pyinstaller(
        spec_file=spec_file,
        output_dir=output_dir,
        version=version,
        onefile=False,  # Create app bundle, not one-file
    )

    # Find app bundle
    app_bundles = list(dist_dir.glob("*.app"))
    if not app_bundles:
        raise RuntimeError("No .app bundle found in dist/")

    app_path = app_bundles[0]

    # Create zip archive for distribution
    print("Creating distribution archive...")
    artifact_name = get_artifact_name(version, "", final_arch)
    archive_path = create_archive(
        source_dir=app_path.parent,
        output_path=output_dir / artifact_name,
        archive_format="zip",
    )

    print(f"\n[OK] Build complete: {archive_path.name}")
    print(f"  Size: {archive_path.stat().st_size / 1024 / 1024:.1f} MB")

    return archive_path


def main():
    """Main entry point."""
    # Verify we're on macOS
    if sys_platform.system() != "Darwin":
        print("Error: This script is for macOS only", file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(description="Build OBS Multi Instance Controller for macOS")
    parser.add_argument(
        "--version",
        type=str,
        required=True,
        help="Version string (e.g., 0.1.0)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist"),
        help="Output directory (default: dist/)",
    )
    parser.add_argument(
        "--arch",
        type=str,
        default=None,
        help="Architecture override (e.g., x86_64, arm64)",
    )

    args = parser.parse_args()

    try:
        build_macos(args.version, args.output, args.arch)
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
