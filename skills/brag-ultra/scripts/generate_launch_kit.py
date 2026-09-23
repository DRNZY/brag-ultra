#!/usr/bin/env python3
"""Brag Ultra - Launch Kit Generator.

Automates multi-format video conversion, two-pass palette-optimized GIF creation,
poster frame extraction, frame-0 poster baking, and launch-metadata.json packaging.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_cmd(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print(f"[exec] {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def extract_poster(video_path: Path, poster_path: Path, timestamp: float = 3.0) -> None:
    print(f"[*] Extracting poster at {timestamp}s -> {poster_path.name}...")
    run_cmd([
        "ffmpeg", "-y", "-ss", str(timestamp),
        "-i", str(video_path),
        "-frames:v", "1",
        "-q:v", "2",
        str(poster_path)
    ])


def bake_frame_zero(video_path: Path, poster_path: Path) -> None:
    print(f"[*] Baking poster {poster_path.name} into frame 0 of {video_path.name}...")
    temp_output = video_path.with_name(f"{video_path.stem}.baked{video_path.suffix}")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(poster_path),
        "-filter_complex", "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]",
        "-map", "[v]", "-map", "0:a?",
        "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart",
        str(temp_output)
    ]
    res = run_cmd(cmd, check=False)
    if res.returncode == 0 and temp_output.exists():
        temp_output.replace(video_path)
        print("[+] Poster successfully baked into frame 0.")
    else:
        print(f"[!] Frame-0 baking skipped or failed: {res.stderr}")


def generate_optimized_gif(video_path: Path, gif_path: Path, fps: int = 24, width: int = 800) -> None:
    print(f"[*] Generating 2-pass palette-optimized GIF -> {gif_path.name}...")
    palette_path = video_path.parent / "palette_temp.png"
    try:
        # Pass 1: generate palette
        run_cmd([
            "ffmpeg", "-y", "-i", str(video_path),
            "-vf", f"fps={fps},scale={width}:-1:flags=lanczos,palettegen=stats_mode=diff",
            str(palette_path)
        ])
        # Pass 2: apply palette
        run_cmd([
            "ffmpeg", "-y", "-i", str(video_path), "-i", str(palette_path),
            "-filter_complex", f"fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle",
            str(gif_path)
        ])
        print(f"[+] GIF generated: {gif_path.stat().st_size / (1024*1024):.2f} MB")
    finally:
        if palette_path.exists():
            palette_path.unlink()


def generate_metadata_json(
    output_dir: Path,
    title: str,
    tagline: str,
    tags: list[str]
) -> Path:
    meta_file = output_dir / "launch-metadata.json"
    data = {
        "title": f"{title} — {tagline}",
        "product": title,
        "tagline": tagline,
        "openGraph": {
            "title": title,
            "description": tagline,
            "image": "brag.jpg",
            "video": "brag.mp4",
            "type": "video.other"
        },
        "twitter": {
            "card": "player",
            "site": "@drnzy",
            "title": title,
            "description": tagline,
            "image": "brag.jpg",
            "player": "brag.mp4"
        },
        "tags": tags,
        "assets": {
            "video": "brag.mp4",
            "poster": "brag.jpg",
            "gif": "brag.gif" if (output_dir / "brag.gif").exists() else None,
            "caption": "share-copy.txt"
        },
        "generatedAt": datetime.now(timezone.utc).isoformat()
    }
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[+] Launch metadata written to {meta_file.name}")
    return meta_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Brag Ultra Launch Kit Generator")
    parser.add_argument("--output-dir", required=True, type=Path, help="Path to brag output directory")
    parser.add_argument("--title", default="Product Launch", help="Product Title")
    parser.add_argument("--tagline", default="Built with craftsmanship.", help="Product Tagline")
    parser.add_argument("--poster-time", type=float, default=3.0, help="Timestamp for poster extraction (seconds)")
    parser.add_argument("--gif", action="store_true", default=True, help="Generate animated preview GIF")
    parser.add_argument("--tags", nargs="*", default=["opensource", "developer", "apple", "design"], help="Keywords/tags")

    args = parser.parse_args()
    out_dir = args.output_dir.resolve()
    video = out_dir / "brag.mp4"
    poster = out_dir / "brag.jpg"
    gif = out_dir / "brag.gif"

    if not video.exists():
        print(f"Error: Video file {video} not found.", file=sys.stderr)
        sys.exit(1)

    # 1. Extract poster
    extract_poster(video, poster, timestamp=args.poster_time)

    # 2. Bake poster as frame 0
    bake_frame_zero(video, poster)

    # 3. Generate GIF
    if args.gif:
        generate_optimized_gif(video, gif)

    # 4. Generate launch metadata
    generate_metadata_json(out_dir, args.title, args.tagline, args.tags)

    print("\n🚀 [Brag Ultra] Launch Kit complete!")


if __name__ == "__main__":
    main()
