# Goa Road Trip 2026 - Batch Audio Extraction & Offline Playlist

Production-grade automated tooling to search, download, transcode, and tag MP3 tracks from `/tmp/GOA_ROAD_TRIP_200_SONGS.txt` using `yt-dlp` and `ffmpeg`.

## Project Components
- `RESEARCH_SPEC.md`: Exhaustive technical research, official documentation citations, flag specifications, and architecture decisions.
- `download_playlist.py`: Core Python script supporting query normalization, batch generation, dry runs, and error-resilient execution.
- `download_playlist.sh`: Shell wrapper for single-command terminal execution.
- `test_download_playlist.py`: Unit test suite verifying title cleaning, regex parsing, search query formatting, and flag assembly.
- `queries.txt`: Generated batch query file containing all 200 formatted `ytsearch1:` entries.
- `archive.txt`: Download tracking archive ensuring downloads are resumable and idempotent.

## Quick Start

### 1. Dry Run / Inspection
Preview the cleaned queries and the planned yt-dlp execution without downloading:
```bash
./download_playlist.py --dry-run
```

### 2. Export Queries Only
Export the batch query file for inspection or separate use:
```bash
./download_playlist.py --export-only
```

### 3. Run Batch Download
To start downloading the 200 songs into `/home/adarsh/Music/GOA_TRIP_2026`:
```bash
# Using the Python runner:
./download_playlist.py

# Or using the Bash wrapper:
./download_playlist.sh
```

### 4. Running Tests
Run the unit test suite:
```bash
python3 -m unittest test_download_playlist.py -v
```

Type check and lint:
```bash
uvx mypy download_playlist.py test_download_playlist.py
uvx ruff check .
```
