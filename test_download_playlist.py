import os
import unittest

from download_playlist import (
    DEFAULT_OUTPUT_DIR,
    build_search_query,
    build_ytdlp_command,
    clean_track_name,
    parse_song_list,
)


class TestDownloadPlaylist(unittest.TestCase):
    def test_default_output_dir(self):
        self.assertTrue(DEFAULT_OUTPUT_DIR.endswith("output"))
        self.assertTrue(os.path.isabs(DEFAULT_OUTPUT_DIR))

    def test_clean_track_name_numbered_dot(self):
        self.assertEqual(clean_track_name("1. Ilahi — Arijit Singh"), "Ilahi - Arijit Singh")
        self.assertEqual(clean_track_name("200. Tera Mera Rishta"), "Tera Mera Rishta")

    def test_clean_track_name_numbered_parenthesis_or_dash(self):
        self.assertEqual(clean_track_name("15) Zindagi Ek Safar"), "Zindagi Ek Safar")
        self.assertEqual(clean_track_name("05 - Aao Milo Chalo"), "Aao Milo Chalo")

    def test_clean_track_name_dashes_and_whitespace(self):
        self.assertEqual(clean_track_name("  Rock On!!  "), "Rock On!!")
        # En-dash and em-dash replacement
        self.assertEqual(clean_track_name("Safarnama – Lucky Ali"), "Safarnama - Lucky Ali")
        self.assertEqual(clean_track_name("Hairat — Lucky Ali"), "Hairat - Lucky Ali")

    def test_clean_track_name_empty(self):
        self.assertEqual(clean_track_name(""), "")
        self.assertEqual(clean_track_name("   "), "")
        self.assertEqual(clean_track_name("# Some comment"), "")

    def test_clean_track_name_urls_and_queries(self):
        url = "https://www.youtube.com/watch?v=-BzQVu8EuQ4"
        self.assertEqual(clean_track_name(url), url)
        query = 'ytsearch1:"Sirra - Guru Randhawa audio"'
        self.assertEqual(clean_track_name(query), query)

    def test_build_search_query(self):
        query = build_search_query("Ilahi - Arijit Singh")
        self.assertEqual(query, 'ytsearch1:"Ilahi - Arijit Singh audio"')

        query_no_suffix = build_search_query("Ilahi - Arijit Singh", add_audio_suffix=False)
        self.assertEqual(query_no_suffix, 'ytsearch1:"Ilahi - Arijit Singh"')

        url = "https://www.youtube.com/watch?v=oW9XAbYgGhs"
        self.assertEqual(build_search_query(url), url)
        self.assertEqual(build_search_query(url, add_audio_suffix=False), url)

    def test_parse_song_list_multiline(self):
        sample = """1. Ilahi — Arijit Singh
2. Phir Se Ud Chala — Mohit Chauhan

# Comment line
3. Safarnama
"""
        tracks = parse_song_list(sample)
        self.assertEqual(len(tracks), 3)
        self.assertEqual(tracks[0], "Ilahi - Arijit Singh")
        self.assertEqual(tracks[1], "Phir Se Ud Chala - Mohit Chauhan")
        self.assertEqual(tracks[2], "Safarnama")

    def test_parse_real_song_file(self):
        test_file = (
            "/tmp/GOA_ROAD_TRIP_200_SONGS.txt"
            if os.path.exists("/tmp/GOA_ROAD_TRIP_200_SONGS.txt")
            else os.path.join(os.path.dirname(__file__), "songs.txt.example")
        )
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()
        tracks = parse_song_list(content)
        self.assertGreater(len(tracks), 0)
        self.assertEqual(tracks[0], "Ilahi - Arijit Singh")

    def test_build_ytdlp_command(self):
        cmd = build_ytdlp_command(
            batch_file="queries.txt",
            output_dir="/tmp/music_output",
            archive_file="archive.txt",
            ffmpeg_path="/usr/bin/ffmpeg",
        )
        self.assertIn("yt-dlp", cmd)
        self.assertIn("--extract-audio", cmd)
        self.assertIn("--audio-format", cmd)
        self.assertIn("mp3", cmd)
        self.assertIn("--audio-quality", cmd)
        self.assertIn("0", cmd)
        self.assertIn("--embed-metadata", cmd)
        self.assertIn("--embed-thumbnail", cmd)
        self.assertIn("--download-archive", cmd)
        self.assertIn("archive.txt", cmd)
        self.assertIn("--ffmpeg-location", cmd)
        self.assertIn("/usr/bin/ffmpeg", cmd)
        self.assertIn("--batch-file", cmd)
        self.assertIn("queries.txt", cmd)

    def test_build_ytdlp_command_custom_sleep(self):
        cmd = build_ytdlp_command(
            batch_file="queries.txt",
            output_dir="/tmp/music_output",
            archive_file="archive.txt",
            min_sleep=5,
            max_sleep=15,
            sleep_requests=3,
            retries=15,
        )
        self.assertIn("--min-sleep-interval", cmd)
        self.assertEqual(cmd[cmd.index("--min-sleep-interval") + 1], "5")
        self.assertIn("--max-sleep-interval", cmd)
        self.assertEqual(cmd[cmd.index("--max-sleep-interval") + 1], "15")
        self.assertIn("--sleep-requests", cmd)
        self.assertEqual(cmd[cmd.index("--sleep-requests") + 1], "3")
        self.assertIn("--retries", cmd)
        self.assertEqual(cmd[cmd.index("--retries") + 1], "15")

if __name__ == "__main__":
    unittest.main()
