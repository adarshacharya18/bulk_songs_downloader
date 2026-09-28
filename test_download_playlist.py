import os
import unittest

from download_playlist import (
    build_search_query,
    build_ytdlp_command,
    clean_track_name,
    parse_song_list,
)


class TestDownloadPlaylist(unittest.TestCase):
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

    def test_build_search_query(self):
        query = build_search_query("Ilahi - Arijit Singh")
        self.assertEqual(query, 'ytsearch1:"Ilahi - Arijit Singh audio"')

        query_no_suffix = build_search_query("Ilahi - Arijit Singh", add_audio_suffix=False)
        self.assertEqual(query_no_suffix, 'ytsearch1:"Ilahi - Arijit Singh"')

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
        if os.path.exists("/tmp/GOA_ROAD_TRIP_200_SONGS.txt"):
            with open("/tmp/GOA_ROAD_TRIP_200_SONGS.txt", "r", encoding="utf-8") as f:
                content = f.read()
            tracks = parse_song_list(content)
            self.assertEqual(len(tracks), 200)
            self.assertEqual(tracks[0], "Ilahi - Arijit Singh")
            self.assertEqual(tracks[-1], "Tera Mera Rishta")

    def test_build_ytdlp_command(self):
        cmd = build_ytdlp_command(
            batch_file="queries.txt",
            output_dir="/home/adarsh/Music/GOA_TRIP_2026",
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
            output_dir="/home/adarsh/Music/GOA_TRIP_2026",
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
