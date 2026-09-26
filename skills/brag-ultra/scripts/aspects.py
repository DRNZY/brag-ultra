"""Aspect-ratio resolution for Brag Ultra.

Why this module exists
----------------------
Brag Ultra's documentation used to claim that one composition "reflows
intelligently" across 16:9, 9:16 and 1:1, and rendered them with
`npx hyperframes render --width 1920 --height 1080`. Both claims were wrong
against the real CLI:

1. `hyperframes render` has no `--width` / `--height` flags. Aspect is selected
   with `--resolution <preset>`.
2. `--resolution` does not rescale or reflow anything. A composition declares
   exactly one aspect via `data-resolution` on `<html>`, and rendering it at a
   mismatched `--resolution` fails hard:

       Output resolution incompatible
       outputResolution portrait (1080x1920) does not match the aspect ratio of
       the composition (1920x1080). The composition is landscape — use
       --resolution landscape instead.

The HyperFrames CLI does contain a routine (`applyResolutionPreset()`) that
rewrites `data-resolution`, `data-width`, `data-height` and the viewport meta
tag — but it is only reachable from `hyperframes init --resolution`, never from
`render`. Running it by hand produces a landscape layout with portrait
dimensions: letterboxed, overflowing, and exactly the "awkward black bars" the
skill claims to avoid.

So multi-format output is an *authoring* obligation, not a render flag. This
module encodes the real contract:

* Each aspect gets its own composition entry file, authored as a genuine layout
  for that aspect (a vertical stack for 9:16, not a squashed 16:9).
* Before spending a render, Brag Ultra reads the `data-resolution` each entry
  file actually declares and refuses to continue on a mismatch.

The mismatch check is the part that matters. It turns a silent bad render into
an up-front, actionable error, and it is the check that would have caught the
original documentation bug.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_HTML_OPEN_RE = re.compile(r"<html\b([^>]*)>", re.IGNORECASE)
_DATA_RESOLUTION_RE = re.compile(
    r"""data-resolution\s*=\s*["']([^"']+)["']""", re.IGNORECASE
)
_DATA_WIDTH_RE = re.compile(r"""data-width\s*=\s*["'](\d+)["']""", re.IGNORECASE)
_DATA_HEIGHT_RE = re.compile(r"""data-height\s*=\s*["'](\d+)["']""", re.IGNORECASE)
_VIEWPORT_RE = re.compile(
    r"""<meta[^>]*name\s*=\s*["']viewport["'][^>]*content\s*=\s*["']([^"']*)["']""",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Aspect:
    """One output aspect: its CLI preset, its dimensions, and its filename."""

    key: str
    #: The `/brag --format` value documented in SKILL.md.
    format_flag: str
    #: The `--resolution` preset the HyperFrames CLI accepts.
    resolution: str
    width: int
    height: int
    #: Output filename stem suffix, e.g. `16x9`.
    suffix: str

    @property
    def label(self) -> str:
        return f"{self.width}x{self.height}"

    @property
    def ratio(self) -> str:
        return f"{self.width // self.gcd}:{self.height // self.gcd}"

    def gcd(self) -> int:
        from math import gcd

        return gcd(self.width, self.height)

    @property
    def video_filename(self) -> str:
        return f"brag-{self.suffix}.mp4"


LANDSCAPE = Aspect("landscape", "landscape", "landscape", 1920, 1080, "16x9")
PORTRAIT = Aspect("portrait", "vertical", "portrait", 1080, 1920, "9x16")
SQUARE = Aspect("square", "square", "square", 1080, 1080, "1x1")

ASPECTS: dict[str, Aspect] = {
    LANDSCAPE.key: LANDSCAPE,
    PORTRAIT.key: PORTRAIT,
    SQUARE.key: SQUARE,
}

#: `--format` aliases accepted on the command line, mapped to an aspect key.
FORMAT_ALIASES: dict[str, str] = {
    "landscape": "landscape",
    "16x9": "landscape",
    "horizontal": "landscape",
    "wide": "landscape",
    # The documented flag word for 9:16 is `vertical`.
    "vertical": "portrait",
    "portrait": "portrait",
    "9x16": "portrait",
    "story": "portrait",
    "reels": "portrait",
    "tiktok": "portrait",
    "shorts": "portrait",
    "square": "square",
    "1x1": "square",
    "feed": "square",
}

#: Order aspects are rendered and reported in.
ASPECT_ORDER: tuple[str, ...] = ("landscape", "portrait", "square")


def resolve_format(value: str) -> list[str]:
    """Resolve a `--format` value to an ordered, de-duplicated list of aspect keys."""
    normalized = (value or "").strip().lower()
    if normalized in ("all", "kit", "every"):
        return list(ASPECT_ORDER)
    if normalized in ("", "default", "landscape"):
        return ["landscape"]
    if normalized not in FORMAT_ALIASES:
        valid = sorted({*FORMAT_ALIASES, "all"})
        raise ValueError(
            f"Unknown --format {value!r}. Valid values: {', '.join(valid)}"
        )
    return [FORMAT_ALIASES[normalized]]


def parse_declared_resolution(html: str) -> str | None:
    """Read the `data-resolution` a composition declares on `<html>`.

    Mirrors `parseResolutionFromHtml()` in the HyperFrames CLI: an explicit
    `data-resolution` wins; otherwise `data-composition-width` /
    `data-composition-height` are used to infer the aspect.
    """
    match = _HTML_OPEN_RE.search(html)
    if not match:
        return None
    attrs = match.group(1)

    explicit = _DATA_RESOLUTION_RE.search(attrs)
    if explicit:
        return explicit.group(1).strip().lower()

    width = _DATA_WIDTH_RE.search(html)
    height = _DATA_HEIGHT_RE.search(html)
    if width and height:
        return resolution_from_dimensions(int(width.group(1)), int(height.group(1)))
    return None


def resolution_from_dimensions(width: int, height: int) -> str:
    """Infer a `--resolution` preset from pixel dimensions.

    Same thresholds as `resolveResolutionFromDimensions()` in the CLI: UHD is
    anything whose long side reaches 3840.
    """
    long_side = max(width, height)
    if width == height:
        return "square-4k" if long_side >= 3840 else "square"
    is_uhd = long_side >= 3840
    if width > height:
        return "landscape-4k" if is_uhd else "landscape"
    return "portrait-4k" if is_uhd else "portrait"


def base_resolution(resolution: str) -> str:
    """Strip a `-4k` suffix, so `square-4k` and `square` compare equal."""
    return resolution.replace("-4k", "")


@dataclass(frozen=True)
class CompositionEntry:
    """A resolved composition entry: a project directory plus an entry file.

    `project_dir` and `entry` are separate because HyperFrames' `check` command
    takes no `--composition` flag. It validates exactly one entry point: the root
    `index.html` of the project directory it is pointed at. So to have every
    aspect actually validated, each aspect has to be its own project directory.
    """

    aspect: Aspect
    project_dir: Path
    entry: Path

    @property
    def declared_resolution(self) -> str | None:
        html = self.entry.read_text(encoding="utf-8", errors="replace")
        return parse_declared_resolution(html)

    @property
    def is_valid(self) -> bool:
        declared = self.declared_resolution
        if declared is None:
            return False
        return base_resolution(declared) == self.aspect.resolution

    @property
    def entry_relative(self) -> str:
        """The entry path as passed to `--composition`, relative to `project_dir`."""
        try:
            return self.entry.relative_to(self.project_dir).as_posix()
        except ValueError:
            return self.entry.name

    @property
    def relative(self) -> str:
        return str(self.entry)


class AspectResolutionError(RuntimeError):
    """Raised when a composition's declared aspect does not match the request."""


def candidate_project_dirs(aspect: Aspect, is_primary: bool) -> list[str]:
    """Per-aspect subdirectory names to look for under the composition root."""
    names = [aspect.key]
    if aspect.format_flag != aspect.key:
        names.append(aspect.format_flag)
    if not is_primary:
        names.append(f"aspect-{aspect.key}")
    return names


def candidate_entry_names(aspect: Aspect, is_primary: bool) -> list[str]:
    """Ordered candidate entry filenames for an aspect, inside a project dir.

    `index.html` is the default entry point, and is the only one `check` will
    validate. The `index-<aspect>.html` forms support a flat single-directory
    layout, but a flat layout cannot have more than one root composition, so it
    only works for a single aspect per project.
    """
    names: list[str] = []
    if is_primary:
        names.append("index.html")
    names.extend(
        [
            f"index-{aspect.key}.html",
            f"index-{aspect.suffix}.html",
            f"index-{aspect.format_flag}.html",
            f"{aspect.key}.html",
            f"{aspect.format_flag}.html",
            f"aspects/{aspect.key}.html",
            f"aspects/{aspect.format_flag}.html",
            f"aspects/index-{aspect.key}.html",
        ]
    )
    return names


def find_entry(composition_root: Path, aspect: Aspect, is_primary: bool) -> tuple[Path, Path] | None:
    """Locate an aspect's (project_dir, entry_file).

    Prefers a dedicated per-aspect project directory, because that is the only
    layout where `hyperframes check` can actually validate the aspect.
    """
    for name in candidate_project_dirs(aspect, is_primary):
        project_dir = composition_root / name
        if (project_dir / "index.html").is_file():
            return project_dir, project_dir / "index.html"

    for name in candidate_entry_names(aspect, is_primary):
        candidate = composition_root / name
        if candidate.is_file():
            return composition_root, candidate
    return None


def describe_missing(aspect: Aspect, composition_root: Path) -> str:
    """Build an actionable message naming the exact paths that would satisfy an aspect."""
    lines = [
        f"No composition found for {aspect.key} ({aspect.label}, "
        f"`--resolution {aspect.resolution}`).",
        "  Preferred: one self-contained project per aspect, so `check` can "
        "validate each one:",
    ]
    for name in candidate_project_dirs(aspect, is_primary=False):
        lines.append(f"    {composition_root / name / 'index.html'}")
    lines.append("  Or a single-directory layout, which supports one aspect per project:")
    for name in candidate_entry_names(aspect, is_primary=False)[:4]:
        lines.append(f"    {composition_root / name}")
    lines.append(
        f"  The entry must set data-resolution=\"{aspect.resolution}\" on <html> "
        f"and lay out for {aspect.label}. HyperFrames will not reflow a "
        f"{ASPECTS['landscape'].label} composition into {aspect.label}; the "
        f'render fails with "Output resolution incompatible".'
    )
    return "\n".join(lines)


@dataclass(frozen=True)
class MissingEntry:
    """An aspect that was requested but has no composition."""

    aspect: Aspect
    message: str


def resolve_all(
    composition_root: Path,
    aspect_keys: list[str],
    manifest: dict[str, str] | None = None,
) -> tuple[list[CompositionEntry], list[MissingEntry]]:
    """Resolve every requested aspect, failing loudly on a declared mismatch.

    Returns `(entries, missing)`. A requested aspect with no composition at all
    lands in `missing` so the caller can warn and carry on with the rest. A
    declared aspect mismatch raises instead: an entry exists and is wrong, which
    is a different class of error, because the author wrote a file that cannot
    render at the aspect it was requested for.
    """
    entries: list[CompositionEntry] = []
    missing: list[MissingEntry] = []
    manifest = manifest or {}

    for index, key in enumerate(ASPECT_ORDER):
        if key not in aspect_keys:
            continue
        aspect = ASPECTS[key]
        is_primary = index == 0 and key == "landscape"

        if key in manifest:
            target = (composition_root / manifest[key]).resolve()
            if not target.is_file():
                raise AspectResolutionError(
                    f"Composition manifest points {aspect.key} at a missing file: {target}"
                )
            entry = CompositionEntry(aspect=aspect, project_dir=target.parent, entry=target)
        else:
            found = find_entry(composition_root, aspect, is_primary)
            if found is None:
                missing.append(
                    MissingEntry(aspect, describe_missing(aspect, composition_root))
                )
                continue
            project_dir, entry_path = found
            entry = CompositionEntry(aspect=aspect, project_dir=project_dir, entry=entry_path)

        if not entry.is_valid:
            declared = entry.declared_resolution or "nothing"
            raise AspectResolutionError(
                f"{entry.relative} declares data-resolution=\"{declared}\" but "
                f"{aspect.key} requires \"{aspect.resolution}\".\n"
                f"  HyperFrames renders a composition only at its own declared "
                f'aspect, so this would fail with "Output resolution '
                f'incompatible".\n'
                f"  Either author a {aspect.label} layout, or request "
                f"--format {declared if declared else 'landscape'}."
            )
        entries.append(entry)

    return entries, missing


def load_manifest(composition_root: Path) -> dict[str, str] | None:
    """Load an optional `brag-composition.json` aspect -> entry-file map.

    The manifest is the escape hatch for projects whose aspect entries do not
    follow the naming convention, e.g. `compositions/v-9x16.html`.
    """
    manifest_path = composition_root / "brag-composition.json"
    if not manifest_path.is_file():
        return None
    import json

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AspectResolutionError(
            f"{manifest_path} is not valid JSON: {exc}"
        ) from exc
    aspects = data.get("aspects", data)
    if not isinstance(aspects, dict):
        raise AspectResolutionError(
            f"{manifest_path} must map aspect keys to entry files, got "
            f"{type(aspects).__name__}"
        )
    unknown = set(aspects) - set(ASPECTS)
    if unknown:
        raise AspectResolutionError(
            f"{manifest_path} references unknown aspect keys: {sorted(unknown)}. "
            f"Valid keys: {sorted(ASPECTS)}"
        )
    return {str(k): str(v) for k, v in aspects.items()}
