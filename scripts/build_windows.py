#!/usr/bin/env python3
"""Build script for Windows."""

import sys
import argparse
from pathlib import Path

from build import (
    get_project_root,
    get_architecture,
    ensure_dependencies_installed,
    run_pyinstaller,
    get_artifact_name,
    print_build_info,
)


def build_windows(version: str, output_dir: Path) -> Path:
    """Build for Windows x86-64.

    Args:
        version: Version string (e.g., "0.1.0")
        output_dir: Output directory for dist/

    Returns:
        Path: Path to built executable
    """
    project_root = get_project_root()
    spec_file = project_root / "scripts" / "pyinstaller.spec"
    arch = get_architecture()

    print_build_info(version, "Windows", arch)

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

    # Find and rename executable
    exe_files = list(dist_dir.glob("obs-multi-instance-controller.exe"))
    if not exe_files:
        raise RuntimeError("No executable found in dist/")

    exe_path = exe_files[0]
    artifact_name = get_artifact_name(version, ".exe")
    final_path = output_dir / artifact_name

    exe_path.rename(final_path)

    print(f"\n[OK] Build complete: {final_path.name}")
    print(f"  Size: {final_path.stat().st_size / 1024 / 1024:.1f} MB")

    return final_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build OBS Multi Instance Controller for Windows")
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
        build_windows(args.version, args.output)
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
