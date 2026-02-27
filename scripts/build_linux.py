#!/usr/bin/env python3
"""Build script for Linux."""

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


def build_linux(version: str, output_dir: Path) -> Path:
    """Build for Linux x86-64.

    Args:
        version: Version string (e.g., "0.1.0")
        output_dir: Output directory for dist/

    Returns:
        Path: Path to built archive
    """
    project_root = get_project_root()
    spec_file = project_root / "scripts" / "pyinstaller.spec"
    arch = get_architecture()

    print_build_info(version, "Linux", arch)

    # Ensure dependencies
    print("Installing dependencies...")
    ensure_dependencies_installed()

    # Run PyInstaller
    print("Building executable with PyInstaller...")
    dist_dir = run_pyinstaller(
        spec_file=spec_file,
        output_dir=output_dir,
        version=version,
        onefile=True,
    )

    # Find executable
    exe_files = list(dist_dir.glob("obs-multi-instance-controller"))
    if not exe_files:
        raise RuntimeError("No executable found in dist/")

    exe_path = exe_files[0]

    # Make executable
    exe_path.chmod(0o755)

    # Create tar.gz archive for distribution
    print("Creating distribution archive...")
    artifact_name = get_artifact_name(version, "")
    archive_path = create_archive(
        source_dir=dist_dir,
        output_path=output_dir / artifact_name,
        archive_format="tar.gz",
    )

    print(f"\n[OK] Build complete: {archive_path.name}")
    print(f"  Size: {archive_path.stat().st_size / 1024 / 1024:.1f} MB")

    return archive_path


def main():
    """Main entry point."""
    # Verify we're on Linux
    if sys_platform.system() != "Linux":
        print("Error: This script is for Linux only", file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(description="Build OBS Multi Instance Controller for Linux")
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

    args = parser.parse_args()

    try:
        build_linux(args.version, args.output)
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
