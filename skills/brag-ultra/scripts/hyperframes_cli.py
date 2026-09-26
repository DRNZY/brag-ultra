"""Pinned HyperFrames CLI invocation.

Every HyperFrames call in Brag Ultra goes through this module so that the CLI
version is pinned in exactly one place. `npx hyperframes` with no version
specifier re-resolves the registry on every invocation, so a render can silently
change behaviour between runs; `npx --yes hyperframes@<version>` cannot.

The specifier format matches the one the HyperFrames CLI itself writes into the
`package.json` it scaffolds (`getHyperframesPackageSpecifier()` in
`packages/cli`), so a project pinned here and a project pinned by
`hyperframes init` produce byte-identical script entries.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

#: The one place the HyperFrames version is pinned for the whole skill.
#: Bump deliberately, then re-run the launch kit end to end: a version change can
#: alter lint findings, render defaults, and encoder settings.
HYPERFRAMES_VERSION = "0.8.78"

#: Authoring workflow recorded on render telemetry for per-skill breakdowns.
AUTHORING_SKILL = "brag"


def specifier() -> str:
    """Return the pinned npm specifier, e.g. ``hyperframes@0.8.78``."""
    return f"hyperframes@{HYPERFRAMES_VERSION}"


def base_command(command: str) -> list[str]:
    """Build the argv prefix for a pinned HyperFrames invocation."""
    return ["npx", "--yes", specifier(), command]


def script_line(command: str) -> str:
    """Return the pinned command as a copy-pasteable shell line."""
    return " ".join(base_command(command))


@dataclass
class CommandResult:
    argv: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    @property
    def command_line(self) -> str:
        return " ".join(self.argv)

    def tail(self, lines: int = 12) -> str:
        """Return the last `lines` lines of combined output, for error reports."""
        combined = (self.stdout + "\n" + self.stderr).strip()
        parts = combined.splitlines()
        return "\n".join(parts[-lines:])


def run(command: list[str], cwd: Path | None = None, check: bool = True,
        timeout: int = 3600) -> CommandResult:
    """Run a command, streaming nothing, capturing everything.

    HyperFrames writes its progress UI to the terminal with cursor control
    sequences. Piping it through `capture_output` keeps that noise out of the
    launch kit log, and on failure `CommandResult.tail()` still shows the part
    that matters.
    """
    print(f"[exec] {' '.join(command)}")
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"Required executable not found: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Command timed out after {timeout}s: {' '.join(command)}"
        ) from exc

    result = CommandResult(command, proc.returncode, proc.stdout, proc.stderr)
    if check and not result.ok:
        raise RuntimeError(
            f"Command failed (exit {result.returncode}): {result.command_line}\n"
            f"{result.tail()}"
        )
    return result


def run_hyperframes(command: str, args: list[str], cwd: Path | None = None,
                    check: bool = True, timeout: int = 3600) -> CommandResult:
    """Run a pinned `hyperframes <command> ...` invocation."""
    return run(base_command(command) + args, cwd=cwd, check=check, timeout=timeout)


@dataclass
class SdkCheck:
    """Result of probing whether the pinned CLI is actually installed."""

    version: str | None = None
    available: bool = False
    detail: str = ""


def probe() -> SdkCheck:
    """Confirm the pinned CLI resolves locally before starting a long render.

    A render is expensive enough that discovering a bad pin afterwards is
    wasteful, and `npx` will happily fall back to the network for a version
    that does not exist only to fail deep inside the first render.
    """
    if shutil.which("npx") is None:
        return SdkCheck(available=False, detail="npx not found on PATH")
    result = run(base_command("--version"), check=False, timeout=300)
    if not result.ok:
        return SdkCheck(
            available=False,
            detail=f"{specifier()} did not resolve: {result.tail(4)}",
        )
    reported = (result.stdout or result.stderr).strip().splitlines()
    version = reported[-1].strip() if reported else None
    return SdkCheck(version=version, available=True, detail=specifier())


def ensure_project_pin(composition_dir: Path) -> Path:
    """Write or patch `package.json` in the composition so its own scripts pin the CLI.

    This mirrors `writeDefaultPackageJson()` in the HyperFrames CLI. Doing it here
    means the composition directory is self-describing: someone who later runs
    `npm run render` inside it gets the same pinned version Brag Ultra used,
    rather than whatever the registry serves that day.
    """
    package_json = composition_dir / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"{package_json} is not valid JSON; refusing to overwrite it: {exc}"
            ) from exc
    else:
        data = {"name": composition_dir.name, "private": True, "type": "module"}

    data.setdefault("name", composition_dir.name)
    data["private"] = True
    data["type"] = "module"
    data["bragUltra"] = {
        "hyperframes": HYPERFRAMES_VERSION,
        "pin": specifier(),
    }
    scripts = data.setdefault("scripts", {})
    for name, command in (
        ("dev", "preview"),
        ("check", "check"),
        ("render", "render"),
        ("publish", "publish"),
    ):
        scripts[name] = script_line(command)

    package_json.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return package_json


@dataclass
class TimelineClip:
    """One timed row from `hyperframes timeline --json`."""

    id: str
    kind: str
    start: float
    duration: float
    file: str

    @property
    def end(self) -> float:
        return round(self.start + self.duration, 3)


@dataclass
class Timeline:
    duration: float
    clips: list[TimelineClip] = field(default_factory=list)

    @property
    def graphics(self) -> list[TimelineClip]:
        return [c for c in self.clips if c.kind != "audio"]


def read_timeline(composition_dir: Path, composition: str | None = None) -> Timeline:
    """Read the real timeline so the plan is derived from the composition, not guessed.

    Brag Ultra's `brag-plan.md` is only worth writing if it describes the piece
    that actually rendered, so this reads the same pinned CLI the render uses
    rather than re-parsing HTML.

    `hyperframes timeline` accepts no `--composition` flag; it always reads the
    project directory's root `index.html`. Pass the *project directory* of the
    aspect you want described, not the parent portfolio directory.
    """
    result = run_hyperframes("timeline", ["--json"], cwd=composition_dir, timeout=600)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Could not parse `hyperframes timeline --json` output: {exc}\n"
            f"{result.tail()}"
        ) from exc

    timeline = payload.get("timeline", payload)
    duration = float(timeline.get("duration") or 0.0)
    clips: list[TimelineClip] = []
    for track in timeline.get("tracks", []):
        for row in track.get("rows", []):
            clips.append(
                TimelineClip(
                    id=str(row.get("id") or row.get("ref") or "clip"),
                    kind=str(track.get("kind") or row.get("kind") or "graphics"),
                    start=float(row.get("absStart", row.get("start", 0.0)) or 0.0),
                    duration=float(row.get("duration", 0.0) or 0.0),
                    file=str(row.get("file") or ""),
                )
            )
    clips.sort(key=lambda c: c.start)
    return Timeline(duration=duration, clips=clips)
