#!/usr/bin/env python3
"""
download_playlist.py - Production-grade bulk audio downloader using yt-dlp & FFmpeg

Parses plain-text song titles, formats optimized yt-dlp search queries, and invokes
yt-dlp with FFmpeg transcoding to produce 320k/VBR-0 ID3-tagged MP3 files with cover art,
rate limiting, and download archive tracking.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

DEFAULT_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DIR = os.path.join(DEFAULT_BASE_DIR, "output")
DEFAULT_SONGS_FILE = os.path.join(DEFAULT_BASE_DIR, "songs.txt")
FALLBACK_SONGS_FILE = "/tmp/GOA_ROAD_TRIP_200_SONGS.txt"


def clean_track_name(raw_name: str) -> str:
    """
    Cleans an input track line by:
    1. Ignoring comments and whitespace.
    2. Stripping leading track numbers (e.g. '1. ', '01 - ', '1) ').
    3. Normalizing em-dash (—) and en-dash (–) to standard hyphen (-).
    4. Trimming extraneous spaces.
    """
    if not raw_name:
        return ""
    line = raw_name.strip()
    if not line or line.startswith("#"):
        return ""

    # Strip leading track numbers: e.g. "1. ", "01 - ", "1) ", "10: ", "05 "
    line = re.sub(r"^\s*\d+\s*([\.\)\-:]\s*|\s+)", "", line)

    # Normalize Unicode dashes to standard hyphen
    line = line.replace("—", "-").replace("–", "-")

    # Clean double spaces or irregular spacing around hyphens
    line = re.sub(r"\s*-\s*", " - ", line)
    line = re.sub(r"\s+", " ", line)

    return line.strip()


def build_search_query(track_name: str, add_audio_suffix: bool = True) -> str:
    """
    Constructs a ytsearch1 query string.
    Optionally appends 'audio' to bias results toward official audio/lyrics tracks.
    """
    clean_name = track_name.strip()
    if add_audio_suffix:
        query_text = f"{clean_name} audio"
    else:
        query_text = clean_name
    return f'ytsearch1:"{query_text}"'


def parse_song_list(content: str) -> list[str]:
    """
    Parses a multiline string of songs, returning a list of cleaned track names.
    """
    tracks: list[str] = []
    for line in content.splitlines():
        cleaned = clean_track_name(line)
        if cleaned:
            tracks.append(cleaned)
    return tracks


def build_ytdlp_command(
    batch_file: str,
    output_dir: str,
    archive_file: str,
    ffmpeg_path: str = "/usr/bin/ffmpeg",
    min_sleep: int = 4,
    max_sleep: int = 10,
    sleep_requests: int = 2,
    retries: int = 10,
) -> list[str]:
    """
    Builds the production-grade yt-dlp argument list.
    """
    output_template = os.path.join(output_dir, "%(autonumber)03d - %(title)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "--batch-file",
        batch_file,
        "--extract-audio",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--embed-metadata",
        "--embed-thumbnail",
        "--convert-thumbnails",
        "jpg",
        "--ffmpeg-location",
        ffmpeg_path,
        "--output",
        output_template,
        "--download-archive",
        archive_file,
        "--ignore-errors",
        "--no-playlist",
        "--retries",
        str(retries),
        "--fragment-retries",
        str(retries),
        "--min-sleep-interval",
        str(min_sleep),
        "--max-sleep-interval",
        str(max_sleep),
        "--sleep-requests",
        str(sleep_requests),
    ]
    return cmd


def main() -> int:
    # Determine default input file
    if os.path.isfile(DEFAULT_SONGS_FILE):
        default_input = DEFAULT_SONGS_FILE
    elif os.path.isfile(FALLBACK_SONGS_FILE):
        default_input = FALLBACK_SONGS_FILE
    else:
        default_input = DEFAULT_SONGS_FILE

    parser = argparse.ArgumentParser(
        description="Batch download and transcode songs to MP3 using yt-dlp and ffmpeg."
    )
    parser.add_argument(
        "--input-file",
        "-i",
        default=default_input,
        help=f"Path to the song list text file (default: {default_input})",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Target directory for downloaded MP3 files (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--queries-file",
        "-q",
        default=None,
        help="Path to save the generated yt-dlp queries batch file (default: <output_dir>/queries.txt)",
    )
    parser.add_argument(
        "--archive-file",
        "-a",
        default=None,
        help="Path to the download archive tracking file (default: <output_dir>/archive.txt)",
    )
    parser.add_argument(
        "--ffmpeg-path",
        default="/usr/bin/ffmpeg",
        help="Path to ffmpeg executable (default: /usr/bin/ffmpeg)",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=None,
        help="Limit download to the first N tracks (useful for testing)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse tracks, generate queries, and print the planned yt-dlp command without downloading",
    )
    parser.add_argument(
        "--export-only",
        action="store_true",
        help="Generate the queries.txt batch file and exit without starting downloads",
    )
    parser.add_argument(
        "--no-audio-suffix",
        action="store_true",
        help="Do not append 'audio' to search queries",
    )

    args = parser.parse_args()

    # Determine default paths
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    queries_file = (
        args.queries_file
        if args.queries_file
        else os.path.join(output_dir, "queries.txt")
    )
    archive_file = (
        args.archive_file
        if args.archive_file
        else os.path.join(output_dir, "archive.txt")
    )

    # If archive does not exist in output_dir, check if a previous root archive exists
    root_archive = os.path.join(DEFAULT_BASE_DIR, "archive.txt")
    if not os.path.exists(archive_file) and os.path.exists(root_archive):
        shutil.copy2(root_archive, archive_file)

    # Validate input file
    if not os.path.isfile(args.input_file):
        print(
            f"Error: Input file '{args.input_file}' not found.\n"
            f"Please create a 'songs.txt' file (see 'songs.txt.example' for format) "
            f"or specify an input file with '--input-file <path>'.",
            file=sys.stderr,
        )
        return 1

    with open(args.input_file, "r", encoding="utf-8") as f:
        content = f.read()

    tracks = parse_song_list(content)
    if not tracks:
        print(f"Error: No valid tracks found in '{args.input_file}'.", file=sys.stderr)
        return 1

    if args.limit and args.limit > 0:
        tracks = tracks[: args.limit]

    print(f"Loaded {len(tracks)} tracks from {args.input_file}")

    # Build search query lines
    add_suffix = not args.no_audio_suffix
    query_lines = [build_search_query(t, add_audio_suffix=add_suffix) for t in tracks]

    # Write batch file
    with open(queries_file, "w", encoding="utf-8") as f:
        f.writelines(f"{q}\n" for q in query_lines)

    print(f"Exported {len(query_lines)} queries to: {queries_file}")

    # Assemble yt-dlp command
    cmd = build_ytdlp_command(
        batch_file=queries_file,
        output_dir=output_dir,
        archive_file=archive_file,
        ffmpeg_path=args.ffmpeg_path,
    )

    if args.dry_run:
        print("\n--- DRY RUN SUMMARY ---")
        print(f"Output Directory : {output_dir}")
        print(f"Queries File     : {queries_file}")
        print(f"Archive File     : {archive_file}")
        print(f"Total Tracks     : {len(tracks)}")
        print("\nFirst 5 Sample Queries:")
        for idx, q in enumerate(query_lines[:5], start=1):
            print(f"  {idx}. {q}")
        print("\nGenerated yt-dlp Command:")
        print(" \\\n  ".join(cmd))
        print("\nDry-run complete. No files were downloaded.")
        return 0

    if args.export_only:
        print("Export complete. Run without --export-only to begin downloading.")
        return 0

    # Verify tool prerequisites before execution
    ytdlp_path = shutil.which("yt-dlp")
    if not ytdlp_path:
        print(
            "Error: 'yt-dlp' executable not found on PATH. Install via 'uv tool install yt-dlp'.",
            file=sys.stderr,
        )
        return 1

    if not os.path.isfile(args.ffmpeg_path) and not shutil.which("ffmpeg"):
        print(
            f"Error: 'ffmpeg' not found at {args.ffmpeg_path} or on PATH.",
            file=sys.stderr,
        )
        return 1

    print(f"\nStarting batch download of {len(tracks)} tracks into {output_dir}...")
    print("Press Ctrl+C at any time to pause; downloads are safely tracked in archive.txt.\n")

    try:
        proc = subprocess.run(cmd, check=True)
        return proc.returncode
    except subprocess.CalledProcessError as e:
        print(f"yt-dlp exited with error code {e.returncode}", file=sys.stderr)
        return e.returncode
    except KeyboardInterrupt:
        print("\nExecution paused by user. Re-run to resume seamlessly from archive.txt.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
