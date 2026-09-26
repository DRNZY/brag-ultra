"""Launch copy and plan generation.

Everything here is derived from real inputs: the composition's actual timeline
(read from the pinned HyperFrames CLI), the invocation flags, and the aspect
renders that actually succeeded. Nothing invents a scene list or claims an
output file exists unless it was confirmed on disk.

Copy follows the anti-crutch rules that apply to prose: no emoji in headings, no
generic launch hype ("supercharge", "unleash", "next-generation"), no
stacked one-line closers, and em dashes used sparingly rather than as a default
conjunction.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from hyperframes_cli import HYPERFRAMES_VERSION, Timeline
from aspects import ASPECTS, ASPECT_ORDER, Aspect

#: The `/brag --tone` presets, kept in step with references/tones.md.
TONES: dict[str, str] = {
    "apple-keynote": "Quiet confidence, tactile physics, sublime restraint",
    "default": "Playful, clean, postable",
    "polished": "Serious, elegant, high craft",
    "yc-parody": "Deadpan startup energy",
    "chaotic": "Fast, loud, unhinged",
    "deadpan": "Calm, dry, understated",
    "cinematic": "Dramatic, blockbuster scale",
    "app-store": "Smooth, feature-card clean",
}

#: Which tone a given platform expects. Used to keep the variants from reading
#: like the same paragraph pasted four times.
PLATFORM_TONES: dict[str, str] = {
    "x": "deadpan",
    "linkedin": "polished",
    "reddit": "polished",
    "product-hunt": "yc-parody",
}


@dataclass
class RenderedAspect:
    """An aspect that actually rendered to a confirmed non-empty file."""

    aspect: Aspect
    composition: Path
    video: Path
    size_bytes: int
    duration_seconds: float


@dataclass
class LaunchContext:
    """Everything the copy and plan generators need to know."""

    output_dir: Path
    composition_dir: Path
    title: str
    tagline: str
    tone: str
    tags: list[str]
    duration: str | None
    voice: bool
    music: bool
    sfx: bool
    terminal: bool
    kit: bool
    requested_formats: list[str]
    rendered: list[RenderedAspect] = field(default_factory=list)
    timeline: Timeline | None = None
    highlights: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _scene_label(clip_id: str) -> str:
    """Turn `scene-3` into `Scene 3` for plan tables."""
    parts = clip_id.replace("_", "-").split("-")
    if len(parts) == 2 and parts[0].lower() in ("scene", "shot", "beat"):
        return f"{parts[0].capitalize()} {parts[1]}"
    return clip_id.replace("-", " ").replace("_", " ").strip().title()


def _fallback_highlights(ctx: LaunchContext) -> list[str]:
    """Derive scene labels from the real timeline when no manual highlights given."""
    if ctx.timeline is None:
        return []
    clips = [c for c in ctx.timeline.clips if c.kind != "audio"]
    return [_scene_label(c.id) for c in clips]


def _rendered_map(ctx: LaunchContext) -> dict[str, RenderedAspect]:
    return {r.aspect.key: r for r in ctx.rendered}


def _asset_table(ctx: LaunchContext) -> list[str]:
    """Build the verified-asset table from files confirmed on disk."""
    rows = ["| Aspect | Composition entry | Video | Size |", "|---|---|---|---|"]
    for rendered in ctx.rendered:
        exists = rendered.video.is_file() and rendered.size_bytes > 0
        mark = "" if exists else " (missing)"
        # Qualify the entry with its project directory. Every aspect's entry file
        # is called index.html, so the bare name is ambiguous on its own.
        try:
            project = rendered.composition.parent.name
        except Exception:  # noqa: BLE001 - defensive, name is cosmetic
            project = ""
        entry = (f"{project}/{rendered.composition.name}" if project
                 else rendered.composition.name)
        rows.append(
            f"| {rendered.aspect.label}{mark} "
            f"| `{entry}` "
            f"| `{rendered.video.name}` "
            f"| {rendered.size_bytes / (1024 * 1024):.2f} MB |"
        )
    if not ctx.rendered:
        rows.append("| _none rendered_ | | | |")
    return rows


def _invocation_table(ctx: LaunchContext) -> list[str]:
    """The invocation flags, split by whether delivery actually honours them."""
    rows = ["| Flag | Value | Honoured at delivery |", "|---|---|---|"]
    rows.append(
        f"| `--title` | {ctx.title} | yes (copy + metadata) |"
    )
    rows.append(
        f"| `--format` | {', '.join(ctx.requested_formats) or 'landscape'} "
        f"| yes (drives render set) |"
    )
    rows.append(
        f"| `--kit` | {'on' if ctx.kit else 'off'} "
        f"| yes (full asset set) |"
    )
    rows.append(
        f"| `--tone` | {ctx.tone} | recorded as an authoring directive |"
    )
    rows.append(
        f"| `--duration` | {ctx.duration or 'auto'} "
        f"| recorded; duration comes from the composition |"
    )
    rows.append(
        f"| `--voice` | {'on' if ctx.voice else 'off'} "
        f"| recorded; narration is authored in step 3 |"
    )
    rows.append(
        f"| `--no-music` | {'music off' if not ctx.music else 'music on'} "
        f"| recorded; the bed is placed in the composition |"
    )
    rows.append(
        f"| `--no-sfx` | {'sfx off' if not ctx.sfx else 'sfx on'} "
        f"| recorded; effects are placed in the composition |"
    )
    rows.append(
        f"| `--terminal` | {'on' if ctx.terminal else 'auto'} "
        f"| recorded; terminal chrome is authored in step 3 |"
    )
    return rows


def render_brag_plan(ctx: LaunchContext) -> str:
    """Write `brag-plan.md` from the real timeline and the real render set."""
    out = ctx.output_dir / "brag-plan.md"
    timeline = ctx.timeline
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")

    lines: list[str] = [
        f"# {ctx.title} launch plan",
        "",
        f"Generated by Brag Ultra at {generated} using "
        f"`hyperframes@{HYPERFRAMES_VERSION}`.",
        "",
        "This file is derived from the composition that rendered, not from a "
        "template. Clip names, start times and durations come from "
        "`hyperframes timeline --json` on the same pinned CLI used for the "
        "renders below.",
        "",
        "## Invocation",
        "",
    ]
    lines.extend(_invocation_table(ctx))
    lines += [
        "",
        "Flags marked *authoring directive* shape step 2 and step 3 (planning "
        "and composition). They are recorded here for traceability, but the "
        "delivery stage cannot apply them on its own: `--tone`, `--duration`, "
        "`--voice`, `--no-music`, `--no-sfx` and `--terminal` all change what "
        "gets authored into the composition, not how an existing composition is "
        "encoded. Only `--format`, `--kit` and `--title` change delivery output.",
        "",
        "## Composition",
        "",
        f"- Entry directory: `{ctx.composition_dir}`",
    ]
    if timeline and timeline.duration:
        lines.append(f"- Timeline duration: {timeline.duration:g}s")
    lines += [
        "",
        "## Timeline",
        "",
    ]

    if timeline and timeline.clips:
        lines += ["| Clip | Type | Start | Duration | End |", "|---|---|---|---|---|"]
        for clip in timeline.clips:
            lines.append(
                f"| `{clip.id}` | {clip.kind} | {clip.start:g}s | "
                f"{clip.duration:g}s | {clip.end:g}s |"
            )
    else:
        lines.append("_Timeline unavailable; the pinned CLI returned no clips._")

    lines += [
        "",
        "## Rendered aspects",
        "",
    ]
    lines.extend(_asset_table(ctx))

    requested = set(ctx.requested_formats)
    missing = [k for k in ASPECT_ORDER if k in requested and k not in _rendered_map(ctx)]
    if missing:
        lines += [
            "",
            "### Requested but not rendered",
            "",
        ]
        for key in missing:
            aspect = ASPECTS[key]
            lines.append(
                f"- {aspect.key} ({aspect.label}): no composition entry declared "
                f"`data-resolution=\"{aspect.resolution}\"`, so the render was "
                f"refused rather than produced letterboxed."
            )

    highlights = ctx.highlights or _fallback_highlights(ctx)
    if highlights:
        lines += ["", "## Beats", ""]
        for index, highlight in enumerate(highlights, start=1):
            lines.append(f"{index}. {highlight}")

    if ctx.warnings:
        lines += ["", "## Warnings", ""]
        for warning in ctx.warnings:
            lines.append(f"- {warning}")

    lines += [
        "",
        "## Next step",
        "",
        "Multi-aspect output is an authoring obligation, not a render flag. A "
        "composition declares one aspect through `data-resolution` on `<html>`, "
        "and HyperFrames refuses to render it at any other. To add an aspect, "
        "author a second entry file with a real layout at those dimensions, then "
        "re-run with `--format all`.",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def render_share_copy(ctx: LaunchContext) -> Path:
    """Write `share-copy.txt`: the canonical single-post caption.

    Two or three lines. Concrete claims, no hype adjectives, no emoji.
    """
    out = ctx.output_dir / "share-copy.txt"
    highlights = ctx.highlights or _fallback_highlights(ctx)

    lines = [f"Built {ctx.title}. {ctx.tagline}"]
    if highlights:
        # Concrete beats beat adjectives: name what the video actually shows.
        named = ", ".join(h.lower() for h in highlights[:3])
        lines.append(f"In the video: {named}.")
    rendered = _rendered_map(ctx)
    if rendered:
        aspects = ", ".join(f"{r.aspect.label}" for r in ctx.rendered)
        # Count the distinct compositions actually rendered, never assume one.
        sources = {r.composition for r in ctx.rendered}
        if len(sources) > 1:
            noun, count = "compositions", len(sources)
        else:
            noun, count = "composition", 1
        lines.append(
            f"Rendered at {aspects} from {count} authored {noun}."
        )
    if ctx.rendered and len(ctx.rendered) == len(set(ctx.requested_formats)):
        lines.append("Source and link below.")
    if ctx.tags:
        lines.append(" ".join(f"#{t}" for t in ctx.tags[:4]))
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def _x_variant(ctx: LaunchContext, highlights: list[str]) -> list[str]:
    hook = f"{ctx.title}: {ctx.tagline}"
    lines = [hook, ""]
    if highlights:
        lines.append(" ".join(highlights[:2]))
    rendered = _rendered_map(ctx)
    if rendered:
        lines.append(
            "One HTML layout per aspect, rendered at "
            + ", ".join(r.aspect.label for r in ctx.rendered)
            + "."
        )
    else:
        lines.append("Source below.")
    if ctx.tags:
        lines.append(" ".join(f"#{t}" for t in ctx.tags[:3]))
    return lines


def _linkedin_variant(ctx: LaunchContext, highlights: list[str]) -> list[str]:
    lines = [
        f"{ctx.title} is live.",
        "",
        ctx.tagline,
        "",
    ]
    if highlights:
        lines.append("What the video covers:")
        lines.append("")
        for highlight in highlights[:4]:
            lines.append(f"- {highlight}")
        lines.append("")
    if ctx.timeline and ctx.timeline.duration:
        lines.append(
            f"The whole piece is a {ctx.timeline.duration:g}s HTML composition. "
            f"Timing lives in `data-start` and `data-duration` attributes, so a "
            f"change to the storyboard is a diff in one file rather than a re-edit "
            f"in a timeline application."
        )
    rendered = _rendered_map(ctx)
    if len(ctx.rendered) > 1:
        aspects = ", ".join(f"{r.aspect.label}" for r in ctx.rendered)
        lines.append("")
        lines.append(
            f"Each aspect is authored as its own layout at {aspects} rather "
            f"than scaled from one master, so none of them letterbox."
        )
    return lines


def _reddit_variant(ctx: LaunchContext, highlights: list[str]) -> list[str]:
    lines = [
        f"**{ctx.title}** — {ctx.tagline}",
        "",
    ]
    if highlights:
        lines.append("Covers:")
        for highlight in highlights:
            lines.append(f"- {highlight}")
        lines.append("")
    rendered = _rendered_map(ctx)
    if rendered:
        entries = ", ".join(
            f"{r.aspect.label} from `{r.composition.parent.name}/"
            f"{r.composition.name}`" for r in ctx.rendered
        )
        lines.append(f"Renders: {entries}.")
        lines.append("")
    lines.append(
        "Worth noting for anyone doing the same thing: the renderer will not "
        "rescale a composition to a new aspect. `hyperframes render "
        "--resolution` checks the aspect against `data-resolution` on `<html>` "
        "and errors out on a mismatch, so multi-format output means authoring a "
        "layout per aspect. That is a real cost and it is deliberate, since a "
        "scaled landscape layout in a vertical frame is worse than no vertical "
        "cut."
    )
    return lines


def _product_hunt_variant(ctx: LaunchContext, highlights: list[str]) -> list[str]:
    lines = [f"{ctx.title}: {ctx.tagline}", ""]
    if highlights:
        lines.append("Three things it does:")
        for highlight in highlights[:3]:
            lines.append(f"- {highlight}")
        lines.append("")
    lines.append(
        "Anyone here maintaining a piece of software want to see what this "
        "looks like applied to your own repo?"
    )
    return lines


def render_share_copy_variants(ctx: LaunchContext) -> Path:
    """Write `share-copy-variants.md` with genuinely different copy per platform.

    Each platform gets its own voice and its own factual content, rather than one
    caption with the platform name swapped in.
    """
    out = ctx.output_dir / "share-copy-variants.md"
    highlights = ctx.highlights or _fallback_highlights(ctx)
    rendered = _rendered_map(ctx)

    sections = [
        ("X / Twitter", _x_variant(ctx, highlights)),
        ("LinkedIn", _linkedin_variant(ctx, highlights)),
        ("Reddit", _reddit_variant(ctx, highlights)),
        ("Product Hunt", _product_hunt_variant(ctx, highlights)),
    ]

    lines = [
        f"# {ctx.title} — share copy variants",
        "",
        f"Tone: `{ctx.tone}`"
        + (f" ({TONES[ctx.tone]})" if ctx.tone in TONES else "")
        + ".",
        "",
        "Each variant is written for its platform's reading behaviour. The facts "
        "come from the composition that actually rendered; where a claim depends "
        "on something not confirmed on disk, it is left out.",
        "",
    ]

    for name, body in sections:
        lines += [f"## {name}", "", "```text", *body, "```", ""]

    if not rendered:
        lines += [
            "## Not claimed",
            "",
            "No render completed, so no variant above claims a file exists.",
            "",
        ]

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def render_metadata(ctx: LaunchContext) -> Path:
    """Write `launch-metadata.json`.

    Asset fields are derived from files confirmed on disk, so the metadata can
    never advertise a render that failed.
    """
    out = ctx.output_dir / "launch-metadata.json"
    rendered = _rendered_map(ctx)
    primary = rendered.get("landscape") or (ctx.rendered[0] if ctx.rendered else None)
    poster = ctx.output_dir / "brag.jpg"
    gif = ctx.output_dir / "brag.gif"

    data = {
        "title": f"{ctx.title} — {ctx.tagline}",
        "product": ctx.title,
        "tagline": ctx.tagline,
        "description": ctx.tagline,
        "openGraph": {
            "title": ctx.title,
            "description": ctx.tagline,
            "type": "video.other" if primary else "website",
            "image": poster.name if poster.is_file() and poster.stat().st_size else None,
            "video": primary.video.name if primary else None,
        },
        "twitter": {
            "card": "player" if primary else "summary_large_image",
            "site": "@drnzy",
            "title": ctx.title,
            "description": ctx.tagline,
            "image": poster.name if poster.is_file() and poster.stat().st_size else None,
            "player": primary.video.name if primary else None,
        },
        "tags": ctx.tags,
        "assets": {
            "videos": {
                r.aspect.key: {
                    "file": r.video.name,
                    "resolution": r.aspect.label,
                    "composition": r.composition.name,
                    "bytes": r.size_bytes,
                }
                for r in ctx.rendered
            },
            "poster": poster.name if poster.is_file() and poster.stat().st_size else None,
            "gif": gif.name if gif.is_file() and gif.stat().st_size else None,
            "caption": "share-copy.txt",
            "copyVariants": "share-copy-variants.md",
            "plan": "brag-plan.md",
        },
        "invocation": {
            "tone": ctx.tone,
            "formats": ctx.requested_formats,
            "duration": ctx.duration,
            "voice": ctx.voice,
            "music": ctx.music,
            "sfx": ctx.sfx,
            "terminal": ctx.terminal,
            "kit": ctx.kit,
        },
        "tooling": {
            "hyperframes": HYPERFRAMES_VERSION,
            "durationSeconds": ctx.timeline.duration if ctx.timeline else None,
        },
        "warnings": ctx.warnings,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return out
