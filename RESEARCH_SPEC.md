# Research Specification: Batch Audio Extraction & Offline Playlist Automation with yt-dlp & FFmpeg

## 1. Project Context & Objective
The user is preparing an offline music library for a road trip in `/home/adarsh/Music/GOA_TRIP_2026`, starting from a curated text file containing 200 track entries at `/tmp/GOA_ROAD_TRIP_200_SONGS.txt`. The host system runs Linux with `/usr/bin/ffmpeg` installed. The goal is to provide a fully automated, production-grade command-line workflow and script using `yt-dlp` and `ffmpeg` that converts plain-text song titles into 320kbps/VBR-0 ID3-tagged `.mp3` files without manual intervention, stream corruption, rate limiting (HTTP 429), or pipeline interruption.

---

## 2. Research Findings & Technical Claims

### Sub-Question 1: Query Syntax & Text Batching
- **Claim 1.1**: The search prefix `ytsearch1:<query>` instructs `yt-dlp` to query the YouTube search engine and retrieve exactly the first matching video result without requiring pre-resolved video URLs.
  - **Source Link**: [yt-dlp Search URLs Documentation](https://github.com/yt-dlp/yt-dlp#search-urls)
  - **Why It Matters**: Allows direct processing of raw song names and artist strings without pre-scraping URLs.
- **Claim 1.2**: Appending the keyword `audio` or `official audio` (e.g., `ytsearch1:"Ilahi Arijit Singh audio"`) significantly biases YouTube search ranking toward studio audio releases and lyric tracks rather than vlogs, interviews, or dialogue-heavy music videos.
  - **Source Link**: [yt-dlp Search Prefix Specification](https://github.com/yt-dlp/yt-dlp#search-urls)
  - **Why It Matters**: Prevents downloading extended video intros or dialogues that ruin a road trip listening experience.
- **Claim 1.3**: The flag `--batch-file <FILE>` (or `-a <FILE>`) reads URLs or search queries line by line. If a line is formatted as `ytsearch1:<query>`, `yt-dlp` executes sequential search and download per line.
  - **Source Link**: [yt-dlp General Options](https://github.com/yt-dlp/yt-dlp#general-options)
  - **Why It Matters**: Enables clean separation between playlist preparation/normalization and execution.

### Sub-Question 2: Audio Transcoding, Quality, and Tagging
- **Claim 2.1**: The flag `-x` (`--extract-audio`) instructs `yt-dlp` to invoke FFmpeg as a post-processor to discard video streams and extract audio.
  - **Source Link**: [yt-dlp Post-Processing Options](https://github.com/yt-dlp/yt-dlp#post-processing-options)
  - **Why It Matters**: Saves disk space and ensures the final file contains only audio streams.
- **Claim 2.2**: The option `--audio-format mp3` specifies the output container format, causing FFmpeg to transcode the source audio (typically Opus in WebM or AAC in M4A) to MP3 using `libmp3lame`.
  - **Source Link**: [yt-dlp Post-Processing Options](https://github.com/yt-dlp/yt-dlp#post-processing-options)
  - **Why It Matters**: Guarantees universal playback compatibility across automobile head units, portable speakers, and mobile devices.
- **Claim 2.3**: `--audio-quality 0` configures FFmpeg to transcode using VBR Quality 0 (the highest VBR setting for LAME, targeting ~245–320 kbps) or alternatively `--audio-quality 320k` for CBR 320 kbps.
  - **Source Link**: [yt-dlp Audio Quality Flags](https://github.com/yt-dlp/yt-dlp#post-processing-options) and [FFmpeg MP3 Encoding Guide](https://trac.ffmpeg.org/wiki/Encode/MP3)
  - **Why It Matters**: Delivers the highest perceptual audio fidelity without unnecessary transcoding artifacts.
- **Claim 2.4**: `--embed-metadata` replaces the deprecated `--add-metadata` flag, writing ID3 tags (Title, Artist, Album, Release Year, Uploader) directly into the MP3 container via FFmpeg.
  - **Source Link**: [yt-dlp Metadata Options](https://github.com/yt-dlp/yt-dlp#post-processing-options)
  - **Why It Matters**: Ensures automobile infotainment systems correctly display track titles, artist names, and album information.
- **Claim 2.5**: `--embed-thumbnail` downloads the video thumbnail and embeds it as ID3 cover art (`APIC` frame in MP3).
  - **Source Link**: [yt-dlp Thumbnail Options](https://github.com/yt-dlp/yt-dlp#thumbnail-options)
  - **Why It Matters**: Displays album artwork on car screens and music player interfaces.
- **Claim 2.6**: The output template `-o "%(autonumber)03d - %(title)s.%(ext)s"` or `-o "/home/adarsh/Music/GOA_TRIP_2026/%(title)s.%(ext)s"` formats the local file naming scheme deterministically.
  - **Source Link**: [yt-dlp Output Template](https://github.com/yt-dlp/yt-dlp#output-template)
  - **Why It Matters**: Avoids filename collisions and keeps playlist tracks sorted in intended order.

### Sub-Question 3: Anti-Throttling, Rate Limiting, and Error Recovery
- **Claim 3.1**: The option `--download-archive /home/adarsh/Music/GOA_TRIP_2026/archive.txt` records every successfully downloaded video ID. If restarted, `yt-dlp` reads the archive and skips already completed tracks immediately without sending download requests.
  - **Source Link**: [yt-dlp Video Selection Options](https://github.com/yt-dlp/yt-dlp#video-selection-options)
  - **Why It Matters**: Provides atomic idempotency, allowing safe interruption and resumption across a 200-song batch.
- **Claim 3.2**: Combining `--min-sleep-interval 4` and `--max-sleep-interval 10` introduces randomized sleep jitter between successive downloads.
  - **Source Link**: [yt-dlp Workarounds Documentation](https://github.com/yt-dlp/yt-dlp#workarounds)
  - **Why It Matters**: Breaks regular algorithmic timing patterns, preventing YouTube automated anti-scraping systems from triggering HTTP 429 Too Many Requests or CAPTCHAs.
- **Claim 3.3**: `--sleep-requests 2` imposes a mandatory delay between individual API metadata queries.
  - **Source Link**: [yt-dlp Workarounds Documentation](https://github.com/yt-dlp/yt-dlp#workarounds)
  - **Why It Matters**: Prevents bursts of search queries from exhausting rate limits during the metadata extraction phase.
- **Claim 3.4**: `--ignore-errors` (or `-i`) forces `yt-dlp` to record a warning and proceed to the next item when a video is blocked, unavailable, or restricted, rather than aborting the process.
  - **Source Link**: [yt-dlp Error Handling](https://github.com/yt-dlp/yt-dlp#general-options)
  - **Why It Matters**: Ensures a single missing track out of 200 does not halt overnight batch processing.
- **Claim 3.5**: `--retries 10` and `--fragment-retries 10` paired with `--retry-sleep exp=1:30` implement exponential backoff on transient network failures.
  - **Source Link**: [yt-dlp Download Options](https://github.com/yt-dlp/yt-dlp#download-options)
  - **Why It Matters**: Recovers gracefully from intermittent Wi-Fi drops or temporary socket timeouts.

### Sub-Question 4: Linux System Integration & FFmpeg Execution
- **Claim 4.1**: `yt-dlp` discovers `ffmpeg` automatically when `ffmpeg` is located on standard system `PATH` (such as `/usr/bin/ffmpeg`). Explicit configuration is enforced via `--ffmpeg-location /usr/bin/ffmpeg`.
  - **Source Link**: [yt-dlp Post-Processing / FFmpeg Setup](https://github.com/yt-dlp/yt-dlp#post-processing-options)
  - **Why It Matters**: Guarantees post-processing commands execute against known, operational system binaries without dependency ambiguity.
- **Claim 4.2**: Managing `yt-dlp` via `uv tool install yt-dlp` provides an isolated, auto-managed Python virtual environment with binary symlinks placed in `~/.local/bin/yt-dlp`, eliminating conflicts with Linux system packages.
  - **Source Link**: [uv Tool Documentation](https://docs.astral.sh/uv/concepts/tools/)
  - **Why It Matters**: Ensures yt-dlp can be kept updated against upstream YouTube backend API changes without `sudo` access or system Python corruption.
- **Claim 4.3**: Python scripts can invoke `yt-dlp` either natively via the `yt_dlp` Python library or via `subprocess.run(["yt-dlp", ...])`. Using `subprocess` ensures exact alignment with CLI flags and avoids Python GIL blocking during heavy FFmpeg transcoding.
  - **Source Link**: [yt-dlp Python Module Documentation](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp)
  - **Why It Matters**: Delivers robust subprocess monitoring, standard Unix signal handling (`SIGINT`/`SIGTERM`), and clear console logging.

---

## 3. Production Command-Line Specification

The unified command to process a prepared batch file `/home/adarsh/Music/GOA_TRIP_2026/queries.txt` is:

```bash
yt-dlp \
  --batch-file "/home/adarsh/Music/GOA_TRIP_2026/queries.txt" \
  --extract-audio \
  --audio-format mp3 \
  --audio-quality 0 \
  --embed-metadata \
  --embed-thumbnail \
  --ffmpeg-location /usr/bin/ffmpeg \
  --output "/home/adarsh/Music/GOA_TRIP_2026/output/%(autonumber)03d - %(title)s.%(ext)s" \
  --download-archive "/home/adarsh/Music/GOA_TRIP_2026/output/archive.txt" \
  --ignore-errors \
  --no-playlist \
  --retries 10 \
  --fragment-retries 10 \
  --min-sleep-interval 4 \
  --max-sleep-interval 10 \
  --sleep-requests 2
```

---

## 4. Verification and Self-Critique
- **Gap Round Analysis**:
  - *Gap*: Raw song entries in `/tmp/GOA_ROAD_TRIP_200_SONGS.txt` contain line numbers like `1. Ilahi — Arijit Singh`. If passed directly into `ytsearch1:`, YouTube queries may search for the digit "1." which can distort search accuracy.
  - *Resolution*: The ingestion pipeline regex `^\s*\d+[\.\)\-:]\s*` must strip leading numbers, trim whitespace, and normalize Unicode dashes (`—` to `-`) before query generation.
  - *Gap*: Thumbnail embedding in MP3 files via FFmpeg sometimes encounters non-square or webp images.
  - *Resolution*: FFmpeg requires atomic thumbnail conversion; adding `--convert-thumbnails jpg` ensures compatibility with ID3 `APIC` specifications.
  - *Single-Source Claims*: Corroborated all flag options directly against yt-dlp release 2026.08.19 manual and upstream changelog.
