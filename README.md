# Bulk Songs Downloader

A fast, resilient, production-grade command-line tool to batch-search, download, transcode, and tag MP3 files from plain-text song lists using `yt-dlp` and `FFmpeg`.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)]()
[![Powered by yt-dlp](https://img.shields.io/badge/Powered%20by-yt--dlp-red.svg)](https://github.com/yt-dlp/yt-dlp)

---

## Features

- **Batch Search & Ingestion**: Reads plain-text tracklists containing raw song names and artists (no pre-existing URLs needed).
- **Search Query Optimization**: Automatically cleans track numbers (`1. `, `02 - `), normalizes dashes, and appends `audio` filters to prioritize studio recordings over music video dialogues.
- **Audiophile Quality Transcoding**: Extracts and transcodes audio to high-fidelity MP3 using FFmpeg's `libmp3lame` at VBR Quality 0 (~250–320 kbps).
- **Automatic ID3 Tagging & Artwork**: Embeds track metadata (Title, Artist, Album) and high-resolution thumbnail cover art directly into the MP3 container.
- **Anti-Bot & Rate-Limit Protection**: Employs randomized delay intervals (`--min-sleep-interval 4 --max-sleep-interval 10`), request pacing, and exponential backoff to prevent YouTube HTTP 429 throttling.
- **Resumable & Idempotent**: Maintains a download archive (`archive.txt`). If interrupted, re-running skips completed tracks instantly.
- **Self-Contained Output**: Automatically saves all completed music into the `output/` folder.

---

## Prerequisites

1. **Python 3.10+**
2. **FFmpeg** (installed on system `PATH` or at `/usr/bin/ffmpeg`):
   ```bash
   # Debian / Ubuntu / Mint:
   sudo apt update && sudo apt install -y ffmpeg

   # Arch Linux:
   sudo pacman -S ffmpeg

   # macOS (Homebrew):
   brew install ffmpeg
   ```
3. **yt-dlp**:
   ```bash
   # Recommended via uv:
   uv tool install yt-dlp

   # Or via pipx / pip:
   pip install yt-dlp
   ```

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/bulk_songs_downloader.git
cd bulk_songs_downloader
```

### 2. Prepare your playlist
Create a `songs.txt` file in the project folder with one song per line (see [`songs.txt.example`](songs.txt.example)):
```text
1. Ilahi — Arijit Singh
2. Phir Se Ud Chala — Mohit Chauhan
3. Safarnama — Lucky Ali
4. Heat Waves — Glass Animals
5. Until I Found You — Stephen Sanchez
```

### 3. Preview (Dry-Run)
Inspect the parsed tracks and planned `yt-dlp` commands without downloading anything:
```bash
./download_playlist.py --dry-run
```

### 4. Download
Run the batch downloader:
```bash
# Python CLI:
./download_playlist.py

# Or Bash runner:
./download_playlist.sh
```

All downloaded MP3 files will be stored in [`output/`](output/).

---

## CLI Options

```text
usage: download_playlist.py [-h] [-i INPUT_FILE] [-o OUTPUT_DIR] [-q QUERIES_FILE]
                            [-a ARCHIVE_FILE] [--ffmpeg-path FFMPEG_PATH]
                            [-l LIMIT] [--dry-run] [--export-only]
                            [--no-audio-suffix]

options:
  -h, --help            Show this help message and exit
  -i, --input-file      Path to song list file (default: songs.txt)
  -o, --output-dir      Target directory for MP3 files (default: output)
  -q, --queries-file    Path to export generated yt-dlp queries
  -a, --archive-file    Path to download archive tracking file
  --ffmpeg-path         Path to ffmpeg executable (default: /usr/bin/ffmpeg)
  -l, --limit           Limit download to first N tracks (for quick testing)
  --dry-run             Parse and preview command without downloading
  --export-only         Generate queries.txt batch file and exit
  --no-audio-suffix     Do not append 'audio' to YouTube queries
```

---

## Project Structure

```text
bulk_songs_downloader/
├── download_playlist.py       # Core batch downloader script
├── download_playlist.sh       # Bash wrapper script
├── test_download_playlist.py  # Unit test suite
├── songs.txt.example          # Sample song list template
├── RESEARCH_SPEC.md           # In-depth technical research & flag spec
├── README.md                  # Project documentation
├── LICENSE                    # MIT License
└── output/                    # Download target directory (gitignored)
    └── archive.txt            # Download history to prevent re-downloads
```

---

## Running Tests

Run the unit test suite:
```bash
python3 -m unittest test_download_playlist.py -v
```

Lint and type-check:
```bash
uvx ruff check .
uvx mypy download_playlist.py test_download_playlist.py
```

---

## License

This project is licensed under the [MIT License](LICENSE).
