from __future__ import annotations

import os
import re
import subprocess
import sys
from importlib.metadata import distribution
from pathlib import Path

EXPECTED_CONSOLE_SCRIPTS = {
    "apolo": "apolo_cli.main:main",
    "apolo-extras": "apolo_extras:main",
    "apolo-flow": "apolo_flow.cli:main",
    "apolo-mcp": "apolo_mcp.cli:main",
    "docker-credential-apolo": "apolo_cli.docker_credential_helper:main",
}
EXPECTED_DEPENDENCIES = {
    "apolo-cli",
    "apolo-extras",
    "apolo-flow",
    "apolo-mcp",
    "apolo-sdk",
    "certifi",
}
CLI_DISTRIBUTIONS = {
    "apolo": "apolo-cli",
    "apolo-extras": "apolo-extras",
    "apolo-flow": "apolo-flow",
    "apolo-mcp": "apolo-mcp",
}


def command(name: str) -> str:
    suffix = ".exe" if os.name == "nt" else ""
    path = Path(sys.executable).parent / f"{name}{suffix}"
    assert path.is_file(), f"console script was not installed: {path}"
    return str(path)


def test_distribution_metadata() -> None:
    package = distribution("apolo-all")

    console_scripts = {
        entry_point.name: entry_point.value
        for entry_point in package.entry_points
        if entry_point.group == "console_scripts"
    }
    assert console_scripts == EXPECTED_CONSOLE_SCRIPTS

    plugins = {
        entry_point.name: entry_point.value
        for entry_point in package.entry_points
        if entry_point.group == "apolo_all"
    }
    assert plugins == {"apolo-all": "apolo_all:setup"}

    pinned_dependencies: dict[str, str] = {}
    for requirement in package.requires or ():
        match = re.fullmatch(r"([\w.-]+) \(==([^)]+)\)", requirement)
        assert match is not None, f"dependency is not pinned exactly: {requirement}"
        pinned_dependencies[match.group(1)] = match.group(2)

    assert set(pinned_dependencies) == EXPECTED_DEPENDENCIES
    for dep, expected_version in pinned_dependencies.items():
        installed_version = distribution(dep).version
        assert installed_version == expected_version, (
            f"{dep} {installed_version} is installed, expected {expected_version}"
        )


def test_clis_start() -> None:
    for name in CLI_DISTRIBUTIONS:
        proc = subprocess.run(
            [command(name), "--help"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, (
            f"{name} --help failed:\n{proc.stdout}{proc.stderr}"
        )

    proc = subprocess.run(
        [command("docker-credential-apolo"), "--help"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 64, proc.stdout + proc.stderr
    assert "credential helper" in (proc.stdout + proc.stderr).lower()


def test_cli_versions() -> None:
    for cli, package in CLI_DISTRIBUTIONS.items():
        expected_version = distribution(package).version
        proc = subprocess.run(
            [command(cli), "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = proc.stdout + proc.stderr
        assert proc.returncode == 0, f"{cli} --version failed:\n{output}"
        assert expected_version in output, (
            f"{cli} --version did not report {expected_version!r}:\n{output}"
        )
