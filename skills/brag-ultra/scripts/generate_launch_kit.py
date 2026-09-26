#!/usr/bin/env python3
"""Brag Ultra delivery stage: validate, render every aspect, package the launch kit.

This is step 4 of `/brag`, the only step that talks to the HyperFrames CLI. It
does what `SKILL.md` and `references/step-4-deliver.md` have always claimed:

1. Probe the pinned HyperFrames CLI, and pin the composition's own `package.json`
   so its scripts resolve the same version later.
2. Resolve a composition entry file per requested aspect, reading the
   `data-resolution` each one declares and refusing to render on a mismatch.
3. Run `hyperframes check` on the composition.
4. Render every requested aspect via the pinned CLI.
5. Extract a poster, bake it into frame 0, build a two-pass palette GIF.
6. Emit `share-copy.txt`, `share-copy-variants.md`, `brag-plan.md` and
   `launch-metadata.json`.

Every asset listed in the metadata is confirmed to exist on disk first.

Usage mirrors the documented `/brag` flags:

    generate_launch_kit.py --composition ./brag-output/composition \\
        --format all --kit --title "Pluvia" --tagline "Rainmeter, native on Linux."

Run `--help` for the full flag list, including the legacy names this script
accepted before it grew the documented interface.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import aspects as aspect_mod  # noqa: E402
import hyperframes_cli as hf  # noqa: E402
from launch_copy import (  # noqa: E402
    LaunchContext,
    RenderedAspect,
    render_brag_plan,
    render_metadata,
    render_share_copy,
    render_share_copy_variants,
)

DEFAULT_TAGS = ["opensource", "developer", "design", "linux"]


# ── ffmpeg helpers ────────────────────────────────────────────────────────────


def run_ffmpeg(args: list[str], what: str) -> None:
    """Run ffmpeg, raising with ffmpeg's own stderr on failure."""
    result = hf.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args,
                    check=False, timeout=1800)
    if not result.ok:
        raise RuntimeError(f"ffmpeg failed while {what}:\n{result.tail()}")


def probe_duration(video: Path) -> float:
    """Read a video's duration in seconds via ffprobe."""
    result = hf.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        check=False, timeout=120,
    )
    try:
        return float(result.stdout.strip())
    except (ValueError, AttributeError):
        return 0.0


def extract_poster(video: Path, poster: Path, timestamp: float) -> bool:
    """Pull a settled frame out as a high-quality JPEG.

    The poster timestamp is clamped inside the video: asking for 3.2s of a 2.1s
    render used to produce a zero-byte JPG that then got baked into frame 0 as a
    broken image.
    """
    duration = probe_duration(video)
    if duration > 0:
        timestamp = max(0.0, min(timestamp, max(0.0, duration - 0.1)))
    result = hf.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-ss", f"{timestamp:.3f}", "-i", str(video),
         "-frames:v", "1", "-q:v", "2", str(poster)],
        check=False, timeout=300,
    )
    ok = result.ok and poster.is_file() and poster.stat().st_size > 0
    if not ok:
        poster.unlink(missing_ok=True)
    return ok


def bake_frame_zero(video: Path, poster: Path) -> bool:
    """Overlay the poster onto frame 0 only, so link previews show it before playback."""
    temp = video.with_name(f"{video.stem}.baked{video.suffix}")
    result = hf.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-i", str(video), "-i", str(poster),
         "-filter_complex", "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]",
         "-map", "[v]", "-map", "0:a?",
         "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-c:a", "copy", "-movflags", "+faststart", str(temp)],
        check=False, timeout=1800,
    )
    if result.ok and temp.is_file() and temp.stat().st_size > 0:
        temp.replace(video)
        return True
    temp.unlink(missing_ok=True)
    return False


def build_gif(video: Path, gif: Path, fps: int = 24, width: int = 800) -> bool:
    """Two-pass palette-optimised GIF: palettegen, then paletteuse with bayer dithering."""
    palette = video.parent / f"{video.stem}.palette.png"
    try:
        run_ffmpeg(
            ["-i", str(video),
             "-vf", f"fps={fps},scale={width}:-1:flags=lanczos,palettegen=stats_mode=diff",
             str(palette)],
            "generating the GIF palette",
        )
        run_ffmpeg(
            ["-i", str(video), "-i", str(palette),
             "-filter_complex",
             f"fps={fps},scale={width}:-1:flags=lanczos[x];"
             f"[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle",
             str(gif)],
            "applying the GIF palette",
        )
    finally:
        palette.unlink(missing_ok=True)
    return gif.is_file() and gif.stat().st_size > 0


# ── pipeline stages ───────────────────────────────────────────────────────────


def resolve_output_dir(requested: Path | None) -> Path:
    """Default to `brag-output/`, or a timestamped sibling when that already exists.

    An existing output directory is never written into by default, so a second
    run cannot clobber the first run's renders.
    """
    if requested:
        return requested.resolve()
    base = Path.cwd() / "brag-output"
    if not base.exists():
        return base
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return Path.cwd() / f"brag-output-{stamp}"


def stage_check(ctx: LaunchContext, entries: list, strict: bool) -> None:
    """Run the pinned `hyperframes check` once per aspect project.

    `check` has no `--composition` flag: it validates the root `index.html` of
    the project directory it is given. Running it once on a shared directory
    therefore only ever validates the landscape aspect, and a portfolio of extra
    `index-portrait.html` files in the same directory additionally trips the
    `multiple_root_compositions` lint error, which aborts the run before layout
    and contrast sampling happens at all. One project directory per aspect is
    what makes every aspect genuinely validated.
    """
    seen: set[Path] = set()
    for entry in entries:
        if entry.project_dir in seen:
            continue
        seen.add(entry.project_dir)
        print(f"\n[check] {entry.aspect.key} {entry.aspect.label} "
              f"({entry.project_dir})")
        args = ["."]
        if strict:
            args.append("--strict")
        result = hf.run_hyperframes("check", args, cwd=entry.project_dir,
                                    check=False, timeout=1800)
        print(result.tail(20))
        if result.returncode != 0:
            ctx.warnings.append(
                f"`hyperframes check` failed for the {entry.aspect.key} aspect "
                f"({entry.project_dir.name}). Fix it before publishing."
            )


def stage_render(ctx: LaunchContext, entries: list, quality: str,
                 fps: int | None, timeout: int) -> None:
    """Render every resolved aspect and record only confirmed outputs."""
    for entry in entries:
        target = ctx.output_dir / entry.aspect.video_filename
        print(f"\n[render] {entry.aspect.key} {entry.aspect.label} "
              f"from {entry.entry_relative} -> {target.name}")
        args = [
            ".",
            "--composition", entry.entry_relative,
            "--resolution", entry.aspect.resolution,
            "--quality", quality,
            "--skill", hf.AUTHORING_SKILL,
            "--output", str(target),
        ]
        if fps:
            args += ["--fps", str(fps)]
        result = hf.run_hyperframes("render", args, cwd=entry.project_dir,
                                    check=False, timeout=timeout)
        if not result.ok:
            print(result.tail(20))
            ctx.warnings.append(
                f"{entry.aspect.key} render failed; no {entry.aspect.video_filename} "
                f"was written."
            )
            continue
        if not target.is_file() or target.stat().st_size == 0:
            ctx.warnings.append(
                f"{entry.aspect.key} render reported success but produced no "
                f"non-empty {entry.aspect.video_filename}."
            )
            continue
        size = target.stat().st_size
        print(f"[ok] {target.name} {size / (1024 * 1024):.2f} MB")
        ctx.rendered.append(
            RenderedAspect(
                aspect=entry.aspect,
                composition=entry.entry,
                video=target,
                size_bytes=size,
                duration_seconds=probe_duration(target),
            )
        )


def stage_assets(ctx: LaunchContext, poster_time: float, want_gif: bool) -> None:
    """Poster, frame-0 bake and GIF, built from the primary render only."""
    primary = next((r for r in ctx.rendered if r.aspect.key == "landscape"),
                   ctx.rendered[0] if ctx.rendered else None)
    if primary is None:
        ctx.warnings.append("No render succeeded, so no poster or GIF was built.")
        return

    poster = ctx.output_dir / "brag.jpg"
    if extract_poster(primary.video, poster, poster_time):
        print(f"[ok] poster {poster.name} {poster.stat().st_size / 1024:.0f} KB")
        if not bake_frame_zero(primary.video, poster):
            ctx.warnings.append(
                "Poster extraction succeeded but baking it into frame 0 failed; "
                "the video plays normally but link previews will not use it."
            )
        else:
            print(f"[ok] frame 0 baked into {primary.video.name}")
    else:
        ctx.warnings.append(f"Poster extraction failed; {poster.name} not written.")

    # The historical single-aspect filename. The landscape render is the primary
    # deliverable, so `brag.mp4` is a copy of it rather than a second encode:
    # README and Discord embeds hardcode that name, and re-encoding to produce
    # it would cost quality for nothing. This runs *after* the frame-0 bake, or
    # the alias would ship the pre-bake video while its source ships the baked
    # one, and the two would silently differ in size and first frame.
    if primary.aspect.key == "landscape":
        alias = ctx.output_dir / "brag.mp4"
        shutil.copy2(primary.video, alias)
        print(f"[ok] alias   {alias.name} = {primary.video.name}")

    # Sizes are re-read after the in-place bake rewrote the file.
    for rendered in ctx.rendered:
        if rendered.video.is_file():
            rendered.size_bytes = rendered.video.stat().st_size

    if want_gif:
        gif = ctx.output_dir / "brag.gif"
        if build_gif(primary.video, gif):
            print(f"[ok] gif {gif.name} {gif.stat().st_size / (1024 * 1024):.2f} MB")
        else:
            gif.unlink(missing_ok=True)
            ctx.warnings.append("GIF generation failed.")


def summarise(ctx: LaunchContext) -> None:
    print("\n" + "=" * 68)
    print("Brag Ultra launch kit")
    print("=" * 68)
    print(f"  output      {ctx.output_dir}")
    print(f"  composition {ctx.composition_dir}")
    print(f"  hyperframes {hf.specifier()}")
    for rendered in ctx.rendered:
        print(f"  video       {rendered.video.name} "
              f"{rendered.aspect.label} {rendered.size_bytes / (1024 * 1024):.2f} MB")
    for name in ("brag.jpg", "brag.gif", "share-copy.txt",
                 "share-copy-variants.md", "brag-plan.md", "launch-metadata.json"):
        path = ctx.output_dir / name
        mark = "ok " if path.is_file() and path.stat().st_size else "-- "
        detail = f"{path.stat().st_size / 1024:.1f} KB" if path.is_file() else "missing"
        print(f"  {mark} {name:<24} {detail}")
    if ctx.warnings:
        print("\n  warnings:")
        for warning in ctx.warnings:
            print(f"    - {warning}")
    if not ctx.rendered:
        print("\n  No video was produced. See warnings above.")
    print("=" * 68)


# ── argument parsing ──────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="generate_launch_kit.py",
        description="Brag Ultra step 4: validate, render all aspects, package the launch kit.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Aspect ratios are an authoring obligation. A HyperFrames composition "
            "declares one aspect via data-resolution on <html> and the renderer "
            "refuses any other. To ship 16:9, 9:16 and 1:1, author one entry file "
            "per aspect:\n"
            "  index.html          data-resolution=\"landscape\"  (default)\n"
            "  index-portrait.html data-resolution=\"portrait\"\n"
            "  index-square.html   data-resolution=\"square\"\n"
            "Or point all three at arbitrary paths with brag-composition.json in the "
            "composition directory:\n"
            '  {"aspects": {"landscape": "index.html",\n'
            '                "portrait": "compositions/v.html",\n'
            '                "square": "compositions/s.html"}}'
        ),
    )
    parser.add_argument("--composition", type=Path, default=Path("brag-output/composition"),
                        help="HyperFrames composition directory (default: brag-output/composition)")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Launch kit directory. Default brag-output/, or a "
                             "timestamped sibling when that already exists.")

    group = parser.add_argument_group("documented /brag flags")
    group.add_argument("--format", default="landscape",
                       help="landscape (16:9), vertical (9:16), square (1:1), or all. "
                            "Aliases: portrait, 16x9, 9x16, 1x1.")
    group.add_argument("--kit", action="store_true",
                       help="Full launch kit: every aspect, poster, GIF, copy and metadata.")
    group.add_argument("--title", default="Product Launch",
                       help="Product title used in copy and metadata.")
    group.add_argument("--tagline", default=None,
                       help="One-line claim. Defaults to a summary of the timeline.")
    group.add_argument("--tone", default="apple-keynote",
                       help="Aesthetic preset: apple-keynote, default, polished, "
                            "yc-parody, chaotic, deadpan, cinematic, app-store. "
                            "Recorded as an authoring directive.")
    group.add_argument("--duration", default=None,
                       help="Target duration, e.g. 20s. Recorded as an authoring "
                            "directive; the composition's own timeline governs.")
    group.add_argument("--voice", action="store_true",
                       help="Narration was authored. Recorded as an authoring directive.")
    group.add_argument("--terminal", action="store_true",
                       help="Terminal/TUI chrome was authored. Recorded as an "
                            "authoring directive.")
    group.add_argument("--no-music", dest="music", action="store_false", default=True,
                       help="No music bed was authored. Recorded as an authoring directive.")
    group.add_argument("--no-sfx", dest="sfx", action="store_false", default=True,
                       help="No sound effects were authored. Recorded as an authoring directive.")

    render_group = parser.add_argument_group("render controls")
    render_group.add_argument("--quality", default="delivery",
                              choices=["draft", "looks", "standard", "high", "delivery"],
                              help="HyperFrames render quality (default: delivery).")
    render_group.add_argument("--fps", type=int, default=None,
                              help="Override the composition's frame rate.")
    render_group.add_argument("--poster-time", type=float, default=3.0,
                              help="Poster extraction timestamp in seconds, clamped to "
                                   "the render's duration (default: 3.0).")
    render_group.add_argument("--no-gif", dest="gif", action="store_false", default=True,
                              help="Skip the animated GIF.")
    render_group.add_argument("--no-check", dest="check", action="store_false", default=True,
                              help="Skip `hyperframes check`.")
    render_group.add_argument("--strict-check", action="store_true",
                              help="Make `hyperframes check` exit non-zero on warnings.")
    render_group.add_argument("--skip-render", action="store_true",
                              help="Package copy and metadata from existing renders "
                                   "without invoking the renderer.")
    render_group.add_argument("--timeout", type=int, default=3600,
                              help="Per-render timeout in seconds (default: 3600).")

    parser.add_argument("--tags", nargs="*", default=None,
                        help=f"Hashtags and metadata tags (default: {' '.join(DEFAULT_TAGS)})")
    parser.add_argument("--highlight", nargs="*", default=None, dest="highlights",
                        help="Beat names for the plan and copy. Defaults to the "
                             "composition's real scene ids.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Resolve aspects and run check, but do not render.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        requested_formats = aspect_mod.resolve_format(args.format)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.kit:
        requested_formats = list(aspect_mod.ASPECT_ORDER)

    composition_dir = args.composition.resolve()
    if not composition_dir.is_dir():
        print(f"error: composition directory not found: {composition_dir}\n"
              f"  Step 3 writes the HyperFrames project here before delivery runs.",
              file=sys.stderr)
        return 2

    output_dir = resolve_output_dir(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Brag Ultra delivery stage\n  composition {composition_dir}\n"
          f"  output      {output_dir}\n  formats     {', '.join(requested_formats)}")

    sdk = hf.probe()
    if not sdk.available:
        print(f"error: pinned HyperFrames CLI unavailable.\n  {sdk.detail}",
              file=sys.stderr)
        return 3
    print(f"  hyperframes {sdk.detail} (reports {sdk.version})")

    missing_warnings: list[str] = []

    try:
        manifest = aspect_mod.load_manifest(composition_dir)
        entries, missing = aspect_mod.resolve_all(
            composition_dir, requested_formats, manifest)
    except aspect_mod.AspectResolutionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4

    for item in missing:
        print(f"\n[!] {item.message}", file=sys.stderr)
    if missing and len(missing) == len(requested_formats):
        print("\nerror: no requested aspect has a composition.", file=sys.stderr)
        return 4

    # Pin every aspect project's own package.json before anything long-running,
    # so an interrupted run still leaves reproducible projects behind.
    for project_dir in dict.fromkeys(e.project_dir for e in entries):
        pinned = hf.ensure_project_pin(project_dir)
        print(f"  pinned      {pinned} -> {hf.specifier()}")

    if missing:
        for item in missing:
            ctx_warn = (
                f"{item.aspect.key} was requested but has no composition, so "
                f"{item.aspect.video_filename} was not produced."
            )
            print(f"  warning     {ctx_warn}")
            missing_warnings.append(ctx_warn)

    # The timeline is read from the primary aspect's project, which is the
    # composition the plan and copy describe.
    primary_entry = next(
        (e for e in entries if e.aspect.key == "landscape"),
        entries[0] if entries else None,
    )

    tagline = args.tagline
    if not tagline:
        if len(entries) > 1:
            tagline = (f"A launch video shipped as {len(entries)} aspect ratios "
                       f"from {len(entries)} authored compositions.")
        else:
            tagline = "A launch video rendered from an HTML composition."

    ctx = LaunchContext(
        output_dir=output_dir,
        composition_dir=composition_dir,
        title=args.title,
        tagline=tagline,
        tone=args.tone,
        tags=list(args.tags) if args.tags else list(DEFAULT_TAGS),
        duration=args.duration,
        voice=args.voice,
        music=args.music,
        sfx=args.sfx,
        terminal=args.terminal,
        kit=args.kit,
        requested_formats=requested_formats,
        highlights=list(args.highlights or []),
    )
    ctx.warnings.extend(missing_warnings)

    # Pick up renders that already exist, so --skip-render and re-runs package
    # what is genuinely on disk rather than only what this invocation produced.
    entry_by_key = {e.aspect.key: e for e in entries}
    for key in aspect_mod.ASPECT_ORDER:
        if key not in requested_formats:
            continue
        candidate = output_dir / aspect_mod.ASPECTS[key].video_filename
        if not (candidate.is_file() and candidate.stat().st_size > 0):
            continue
        if any(r.video == candidate for r in ctx.rendered):
            continue
        entry = entry_by_key.get(key)
        if entry is None:
            continue
        ctx.rendered.append(RenderedAspect(
            aspect=entry.aspect,
            composition=entry.entry,
            video=candidate,
            size_bytes=candidate.stat().st_size,
            duration_seconds=probe_duration(candidate),
        ))
    if ctx.rendered:
        print(f"  existing    {len(ctx.rendered)} render(s) already in {output_dir.name}")

    if primary_entry is not None:
        try:
            ctx.timeline = hf.read_timeline(primary_entry.project_dir)
            print(f"  timeline    {ctx.timeline.duration:g}s, "
                  f"{len(ctx.timeline.clips)} clip(s) from "
                  f"{primary_entry.project_dir.name}")
        except RuntimeError as exc:
            print(f"  timeline    unavailable ({exc.__class__.__name__}: "
                  f"{str(exc)[:120]}); brag-plan.md will note it")
            ctx.warnings.append(
                "Could not read the composition timeline via the pinned CLI.")

    if args.check and entries:
        stage_check(ctx, entries, args.strict_check)

    if args.dry_run:
        print("\n[dry-run] resolved aspects:")
        for entry in entries:
            print(f"  {entry.aspect.key:9} {entry.aspect.label:9} "
                  f"{entry.relative} (data-resolution={entry.declared_resolution}, "
                  f"project={entry.project_dir.name})")
        for item in missing:
            print(f"  {'missing':9} {item.aspect.key} {item.aspect.label} "
                  f"no composition declaring "
                  f"data-resolution=\"{item.aspect.resolution}\"")
        print("\n[dry-run] no render performed.")
        return 0

    if not args.skip_render:
        stage_render(ctx, entries, args.quality, args.fps, args.timeout)

    # Recompute sizes after any frame-0 bake rewrote the file in place.
    for rendered in ctx.rendered:
        if rendered.video.is_file():
            rendered.size_bytes = rendered.video.stat().st_size

    if not args.skip_render and ctx.rendered:
        stage_assets(ctx, args.poster_time, args.gif)

    written = [
        render_brag_plan(ctx),
        render_share_copy(ctx),
        render_share_copy_variants(ctx),
        render_metadata(ctx),
    ]
    for path in written:
        print(f"[ok] wrote {path.name}")

    summarise(ctx)
    return 0 if ctx.rendered else 5


if __name__ == "__main__":
    sys.exit(main())
