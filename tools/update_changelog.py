#!/usr/bin/env python3
import click
import datetime
import subprocess
import sys
from difflib import SequenceMatcher
from importlib.metadata import version
from pathlib import Path
from typing import Optional


UPSTREAMS = [
    "apolo-cli",
    "apolo-extras",
    "apolo-flow",
]


def update_repos() -> None:
    for upstream in UPSTREAMS:
        cloned = Path("cloned")
        cloned.mkdir(parents=True, exist_ok=True)
        path = cloned / upstream
        click.secho(f"Sync {upstream}", fg="yellow")
        if not path.exists():
            subprocess.run(
                ["git", "clone", f"https://github.com/neuro-inc/{upstream}.git"],
                check=True,
                cwd=Path("cloned"),
            )
        else:
            subprocess.run(
                ["git", "checkout", "master", "-q"],
                check=True,
                cwd=str(path),
            )
            subprocess.run(
                ["git", "pull"],
                check=True,
                cwd=str(path),
            )

        subprocess.run(
            ["git", "config", "advice.detachedHead", "false"], check=True, cwd=str(path)
        )

        ver = version(upstream)
        subprocess.run(["git", "checkout", f"v{ver}"], check=True, cwd=str(path))


def fetch(upstream: str) -> Optional[str]:
    changelog = Path("cloned") / upstream / "CHANGELOG.md"
    txt = changelog.read_text()
    TEMPLATE = "[comment]: # (towncrier release notes start)\n"
    idx = txt.index(TEMPLATE)
    right = txt[idx + len(TEMPLATE) :]
    old = Path(upstream + ".txt")
    left = old.read_text()
    matcher = SequenceMatcher(None, left, right)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            return None
        if tag != "insert":
            raise ValueError(
                f"insert is expected as a first matcher opcode, "
                f"found {tag} '{left[i1:i2]}' ---> '{right[j1:j2]}'"
            )
        old.write_text(right)
        return right[j1:j2]


@click.command()
def main() -> None:
    print("Installing apolo-all")
    subprocess.run(
        ["poetry", "install"],
        check=True,
    )

    update_repos()
    changes = []
    for upstream in UPSTREAMS:
        ret = fetch(upstream)
        if ret is not None:
            changes.append(ret)

    if not changes:
        click.secho(
            "CHANGELOG.md is not updated:\n"
            f"Nothing changed in upstreams {','.join(UPSTREAMS)}",
            fg="red",
        )
        sys.exit(1)

    changelog = Path("CHANGELOG.md")
    txt = changelog.read_text()
    TEMPLATE = "[comment]: # (release notes start)"
    idx = txt.index(TEMPLATE) + len(TEMPLATE)
    pre = txt[:idx]
    post = txt[idx:]
    proc = subprocess.run(
        ["poetry", "version", "--short"], capture_output=True, check=True, text=True
    )
    version = proc.stdout.strip()
    date = datetime.date.today().isoformat()
    header = f"Apolo {version} ({date})\n"
    header += "=" * (len(header) - 1) + "\n"
    changelog.write_text(pre + "\n\n" + header + "".join(changes) + post)

    click.secho("CHANGELOG.md is updated", fg="green")


if __name__ == "__main__":
    main()
