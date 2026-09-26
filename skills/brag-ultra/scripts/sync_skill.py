#!/usr/bin/env python3
"""Generate the installable skill mirror at `skills/brag-ultra/` from the repo root.

Why this exists
---------------
This repository carried two copies of the same skill: the root `SKILL.md`,
`references/`, `scripts/` and `assets/`, and a byte-for-byte duplicate under
`skills/brag-ultra/`. The duplicate existed because `npx skills add` expects a
`skills/<name>/` layout, but nothing kept the two in step, so any edit to one
copy silently left the other stale. Two copies of a skill is one copy too many:
whichever one an agent happens to load may not be the one that was edited.

So: the repository root is the single source of truth, and
`skills/brag-ultra/` is a generated artefact. This script regenerates it, and
`--check` proves it is in sync without writing anything.

    ./scripts/sync_skill.py --check     # exit 1 on drift, for CI
    ./scripts/sync_skill.py --write     # regenerate the mirror

The mirror differs from the root in exactly one intentional way: the `name:`
field in the YAML frontmatter. The root declares `name: brag`, which is the
`/brag` invocation and what `skills-lock.json` records. A skill directory has to
declare its own directory name, so the mirror declares `name: brag-ultra`.
That single substitution is applied here rather than maintained by hand, which
is what stops the two files from drifting again.
"""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MIRROR = REPO_ROOT / "skills" / "brag-ultra"

#: Directories mirrored verbatim.
MIRRORED_DIRS = ("references", "scripts", "assets")

#: Root files mirrored, as (source, destination) relative to REPO_ROOT.
MIRRORED_FILES = (("SKILL.md", "SKILL.md"),)

#: The one intentional divergence between root and mirror.
ROOT_SKILL_NAME = "brag"
MIRROR_SKILL_NAME = "brag-ultra"

#: Written into the mirror so a reader knows not to hand-edit it.
GENERATED_BANNER = (
    "<!-- GENERATED FILE. Source of truth: the repository root.\n"
    "     Regenerate with scripts/sync_skill.py --write; verify with --check. -->\n"
)


def mirror_skill_md(source: Path) -> str:
    """Return the root SKILL.md with the skill name swapped for the mirror."""
    text = source.read_text(encoding="utf-8")
    needle = f"name: {ROOT_SKILL_NAME}\n"
    if needle not in text:
        raise SystemExit(
            f"{source} no longer declares `name: {ROOT_SKILL_NAME}` in its "
            f"frontmatter. Update sync_skill.py's ROOT_SKILL_NAME to match, or "
            f"fix the frontmatter, before regenerating the mirror."
        )
    text = text.replace(needle, f"name: {MIRROR_SKILL_NAME}\n", 1)
    return GENERATED_BANNER + text


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def expected_files() -> dict[Path, Path]:
    """Map every mirror destination to the bytes it should contain."""
    expected: dict[Path, Path] = {}
    for name in MIRRORED_FILES:
        expected[MIRROR / name[1]] = REPO_ROOT / name[0]
    for directory in MIRRORED_DIRS:
        source_dir = REPO_ROOT / directory
        if not source_dir.is_dir():
            continue
        for source in sorted(source_dir.rglob("*")):
            if source.is_file() and "__pycache__" not in source.parts:
                expected[MIRROR / directory / source.relative_to(source_dir)] = source
    return expected


def build_expected_text(source: Path, destination: Path) -> str | None:
    """Return transformed text for a destination, or None to copy bytes verbatim."""
    if destination.name == "SKILL.md":
        return mirror_skill_md(source)
    return None


def check() -> int:
    """Report drift between the root and the mirror. Returns a process exit code."""
    expected = expected_files()
    if not expected:
        print("error: found nothing to mirror; is REPO_ROOT correct?", file=sys.stderr)
        return 2

    problems: list[str] = []
    for destination, source in sorted(expected.items()):
        if not destination.exists():
            problems.append(f"  missing   {destination.relative_to(REPO_ROOT)}")
            continue
        text = build_expected_text(source, destination)
        if text is not None:
            if destination.read_text(encoding="utf-8") != text:
                problems.append(f"  differs   {destination.relative_to(REPO_ROOT)}")
        elif not filecmp.cmp(source, destination, shallow=False):
            problems.append(f"  differs   {destination.relative_to(REPO_ROOT)}")

    # Flag files in the mirror that the root no longer produces.
    for existing in sorted(MIRROR.rglob("*")):
        if not existing.is_file():
            continue
        if "__pycache__" in existing.parts:
            continue
        if existing not in expected:
            problems.append(f"  orphaned  {existing.relative_to(REPO_ROOT)}")

    print(f"skill mirror: {len(expected)} file(s) expected at {MIRROR.relative_to(REPO_ROOT)}")
    if problems:
        print(f"DRIFT: {len(problems)} problem(s)")
        for problem in problems:
            print(problem)
        print("\nRun scripts/sync_skill.py --write to regenerate.")
        return 1
    print("in sync")
    return 0


def write() -> int:
    """Regenerate the mirror from the root."""
    expected = expected_files()
    if not expected:
        print("error: found nothing to mirror.", file=sys.stderr)
        return 2

    for destination, source in sorted(expected.items()):
        destination.parent.mkdir(parents=True, exist_ok=True)
        text = build_expected_text(source, destination)
        if text is not None:
            if not destination.exists() or destination.read_text(encoding="utf-8") != text:
                destination.write_text(text, encoding="utf-8")
                print(f"  wrote     {destination.relative_to(REPO_ROOT)}")
        else:
            if not destination.exists() or not filecmp.cmp(source, destination, shallow=False):
                shutil.copy2(source, destination)
                print(f"  copied    {destination.relative_to(REPO_ROOT)}")

    # Remove files the root no longer produces, so the mirror cannot accumulate
    # stale entries. Only ever touches paths inside MIRROR.
    removed = 0
    for existing in sorted(MIRROR.rglob("*"), reverse=True):
        if existing.is_file() and existing not in expected and "__pycache__" not in existing.parts:
            existing.unlink()
            print(f"  removed   {existing.relative_to(REPO_ROOT)}")
            removed += 1
    for existing in sorted(MIRROR.rglob("*"), reverse=True):
        if existing.is_dir() and not any(existing.iterdir()):
            existing.rmdir()
            removed += 1

    print(f"mirror written: {len(expected)} file(s), {removed} stale entr(ies) removed")
    print(f"  root       {REPO_ROOT}")
    print(f"  mirror     {MIRROR}")
    print(f"  pin        hyperframes@{__import__('hyperframes_cli').HYPERFRAMES_VERSION}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true",
                       help="Fail if the mirror has drifted from the root.")
    group.add_argument("--write", action="store_true",
                       help="Regenerate the mirror from the root.")
    args = parser.parse_args(argv)
    return check() if args.check else write()


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
