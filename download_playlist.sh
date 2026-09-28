#!/usr/bin/env bash
# ==============================================================================
# download_playlist.sh
# Production batch audio extraction script for Goa Trip 2026 using yt-dlp & FFmpeg
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${SCRIPT_DIR}/output"
mkdir -p "${TARGET_DIR}"
INPUT_FILE="${1:-/tmp/GOA_ROAD_TRIP_200_SONGS.txt}"
QUERIES_FILE="${TARGET_DIR}/queries.txt"
ARCHIVE_FILE="${TARGET_DIR}/archive.txt"
FFMPEG_PATH="/usr/bin/ffmpeg"

if [[ ! -f "${ARCHIVE_FILE}" && -f "${SCRIPT_DIR}/archive.txt" ]]; then
    cp -p "${SCRIPT_DIR}/archive.txt" "${ARCHIVE_FILE}"
fi

echo "=== Goa Trip 2026 Playlist Batch Downloader ==="
echo "Input songlist : ${INPUT_FILE}"
echo "Target folder  : ${TARGET_DIR}"
echo "Queries file   : ${QUERIES_FILE}"
echo "Archive file   : ${ARCHIVE_FILE}"

# 1. Verify dependencies
if ! command -v yt-dlp &>/dev/null; then
    echo "Error: yt-dlp not found in PATH. Install via: uv tool install yt-dlp" >&2
    exit 1
fi

if [[ ! -x "${FFMPEG_PATH}" ]] && ! command -v ffmpeg &>/dev/null; then
    echo "Error: ffmpeg not found at ${FFMPEG_PATH} or in PATH." >&2
    exit 1
fi

# 2. Check input file
if [[ ! -f "${INPUT_FILE}" ]]; then
    echo "Error: Input file '${INPUT_FILE}' does not exist." >&2
    exit 1
fi

# 3. Clean track names and generate queries.txt if not already done or if forced
echo "Preparing search queries from ${INPUT_FILE}..."
python3 "${SCRIPT_DIR}/download_playlist.py" --output-dir "${TARGET_DIR}" --input-file "${INPUT_FILE}" --export-only

# 4. Execute yt-dlp batch download
echo ""
echo "Starting batch audio extraction into ${TARGET_DIR}..."
echo "Press Ctrl+C to pause at any time (progress is saved in archive.txt)."
echo ""

yt-dlp \
  --batch-file "${QUERIES_FILE}" \
  --extract-audio \
  --audio-format mp3 \
  --audio-quality 0 \
  --embed-metadata \
  --embed-thumbnail \
  --convert-thumbnails jpg \
  --ffmpeg-location "${FFMPEG_PATH}" \
  --output "${TARGET_DIR}/%(autonumber)03d - %(title)s.%(ext)s" \
  --download-archive "${ARCHIVE_FILE}" \
  --ignore-errors \
  --no-playlist \
  --retries 10 \
  --fragment-retries 10 \
  --min-sleep-interval 4 \
  --max-sleep-interval 10 \
  --sleep-requests 2

echo ""
echo "=== Batch processing completed successfully! ==="
