"""Shared build utilities for PyInstaller."""

import os
import sys
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """Get the project root directory.

    Returns:
        Path: Project root directory
    """
    return Path(__file__).parent.parent


def extract_version_from_git() -> str:
    """Extract version from git tags.

    Returns:
        str: Version string (e.g., "0.1.0")

    Raises:
        RuntimeError: If git tag cannot be read
    """
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--always"],
            cwd=get_project_root(),
            capture_output=True,
            text=True,
            check=True
        )
        tag = result.stdout.strip()

        # Extract version from v0.1.0 format
        match = re.match(r"v?(\d+\.\d+\.\d+)", tag)
        if match:
            return match.group(1)

        # Fallback: use tag as-is if it matches version pattern
        if re.match(r"^\d+\.\d+\.\d+", tag):
            return tag

        raise RuntimeError(f"Invalid version format in git tag: {tag}")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get git tag: {e}")


def get_version(version_arg: Optional[str] = None) -> str:
    """Get version from argument or git tag.

    Args:
        version_arg: Version string (overrides git tag if provided)

    Returns:
        str: Version string

    Raises:
        RuntimeError: If version cannot be determined
    """
    if version_arg:
        return version_arg

    return extract_version_from_git()


def get_platform_slug() -> str:
    """Get platform slug for naming.

    Returns:
        str: Platform slug (windows, macos, linux)
    """
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "darwin":
        return "macos"
    elif sys.platform == "linux":
        return "linux"
    else:
        return sys.platform


def get_architecture() -> str:
    """Get architecture slug.

    Returns:
        str: Architecture (x86_64, arm64, etc.)
    """
    import platform
    machine = platform.machine().lower()

    if machine in ("amd64", "x86_64"):
        return "x86_64"
    elif machine in ("arm64", "aarch64"):
        return "arm64"
    elif machine in ("i386", "i686"):
        return "x86"
    else:
        return machine


def clean_build_artifacts(build_dir: Path) -> None:
    """Clean PyInstaller build artifacts.

    Args:
        build_dir: Build directory to clean
    """
    for pattern in ["build", "__pycache__", "*.spec"]:
        for item in build_dir.glob(f"**/{pattern}" if "/" in pattern else pattern):
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink(missing_ok=True)


def ensure_dependencies_installed() -> None:
    """Ensure PyInstaller and build dependencies are installed.

    Raises:
        RuntimeError: If dependencies cannot be installed
    """
    required_packages = ["pyinstaller>=6.0.0"]
    project_root = get_project_root()

    # Install from requirements.txt
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", "-r", str(requirements_file)],
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install requirements: {e}")

    # Install PyInstaller
    for package in required_packages:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", package],
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to install {package}: {e}")


def run_pyinstaller(
    spec_file: Path,
    output_dir: Path,
    version: str,
    onefile: bool = True,
) -> Path:
    """Run PyInstaller with given spec file.

    Args:
        spec_file: Path to .spec file
        output_dir: Output directory for dist/
        version: Version string for naming
        onefile: Build as single file

    Returns:
        Path: Path to built executable/bundle

    Raises:
        RuntimeError: If PyInstaller fails
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "-y",  # Overwrite existing build
        "--distpath", str(output_dir / "dist"),
    ]

    cmd.append(str(spec_file))

    try:
        subprocess.run(cmd, check=True, cwd=get_project_root())
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"PyInstaller build failed: {e}")

    # Return path to built executable
    dist_dir = output_dir / "dist"
    if not dist_dir.exists():
        raise RuntimeError(f"Build output not found in {dist_dir}")

    return dist_dir


def create_archive(source_dir: Path, output_path: Path, archive_format: str = "zip") -> Path:
    """Create archive of build output.

    Args:
        source_dir: Source directory to archive
        output_path: Output archive path (without extension)
        archive_format: Format (zip, tar, tar.gz)

    Returns:
        Path: Path to created archive

    Raises:
        ValueError: If archive format is invalid
    """
    if archive_format not in ("zip", "tar", "tar.gz", "tgz"):
        raise ValueError(f"Unsupported archive format: {archive_format}")

    format_map = {
        "zip": "zip",
        "tar": "tar",
        "tar.gz": "tar.gz",
        "tgz": "tar.gz",
    }

    fmt = format_map.get(archive_format, archive_format)

    base_name = str(output_path)
    if base_name.endswith(f".{fmt}"):
        base_name = base_name[: -len(fmt) - 1]

    shutil.make_archive(base_name, fmt, source_dir)

    # Return actual created file path
    if fmt == "tar.gz":
        return Path(f"{base_name}.tar.gz")
    else:
        return Path(f"{base_name}.{fmt}")


def get_artifact_name(version: str, extension: str = "") -> str:
    """Get standard artifact naming.

    Args:
        version: Version string
        extension: File extension (e.g., .exe, .zip)

    Returns:
        str: Artifact name (e.g., obs-multi-instance-controller-0.1.0-windows-x86_64.exe)
    """
    platform_slug = get_platform_slug()
    arch = get_architecture()
    name = f"obs-multi-instance-controller-{version}-{platform_slug}-{arch}"

    if extension and not extension.startswith("."):
        extension = f".{extension}"

    return name + extension


def print_build_info(version: str, platform: str, arch: str) -> None:
    """Print build information.

    Args:
        version: Version string
        platform: Platform name
        arch: Architecture name
    """
    print(f"\n{'='*60}")
    print(f"Building OBS Multi Instance Controller {version}")
    print(f"Platform: {platform} ({arch})")
    print(f"{'='*60}\n")
