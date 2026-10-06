"""Offline reliability checks. No sample content is written into the real archive."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/slack_archive.py"
spec = importlib.util.spec_from_file_location("slack_archive", SCRIPT)
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


def page(messages, cursor="", next_cursor="", thread=None):
    args = {"channel_id": "CTEST1"}
    if cursor:
        args["cursor"] = cursor
    if thread:
        args["message_ts"] = thread
    return {"tool": "slack_read_thread" if thread else "slack_read_channel",
            "arguments": args, "next_cursor": next_cursor,
            "result": {"content": [{"type": "text", "text": "fixture"}],
                       "structuredContent": {"ok": True, "messages": messages,
                                             "response_metadata": {"next_cursor": next_cursor}}}}


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="capstone-slack-test-")
        self.root = Path(self.temp.name)
        archive.write_json(self.root / "slack/config.json", {
            "workspace_name": "capstone2", "workspace_id": "TTEST1",
            "expected_workspace_id": "TTEST1", "channel_scope": "public_channels",
            "channel_ids": [], "connection_status": "WORKSPACE_VERIFIED"})
        self.batch = {"workspace": {"name": "capstone2", "id": "TTEST1"},
                      "captured_at": "2026-10-06T15:10:00+09:00",
                      "channel": {"id": "CTEST1", "name": "fixture", "team_id": "TTEST1",
                                  "is_private": False}, "complete": True,
                      "history": [page([{"ts": "1791266400.000001", "text": "fixture only"}])],
                      "threads": [], "thread_parents": []}

    def tearDown(self):
        self.temp.cleanup()

    def test_native_envelope_is_preserved_and_identical_rerun_changes_nothing(self):
        self.assertEqual(archive.ingest(self.root, self.batch)["new_pages"], 1)
        source = next((self.root / "slack/raw").glob("*/*.jsonl"))
        row = json.loads(source.read_text(encoding="utf-8"))
        self.assertEqual(row["result"], self.batch["history"][0]["result"])
        before = {p: p.read_bytes() for p in (self.root / "slack").rglob("*") if p.is_file()}
        repeated = copy.deepcopy(self.batch)
        repeated["captured_at"] = "2026-10-06T16:10:00+09:00"
        self.assertEqual(archive.ingest(self.root, repeated)["new_pages"], 0)
        self.assertTrue(all(p.read_bytes() == data for p, data in before.items()))

    def test_missing_second_page_leaves_no_raw_or_checkpoint(self):
        self.batch["history"] = [page([], next_cursor="NEXT")]
        with self.assertRaises(archive.ArchiveError):
            archive.ingest(self.root, self.batch)
        self.assertFalse((self.root / "slack/raw").exists())
        self.assertFalse((self.root / "slack/state").exists())

    def test_pagination_chain_is_verified_against_slack(self):
        self.batch["history"] = [page([], next_cursor="NEXT"), page([], cursor="NEXT")]
        self.assertEqual(archive.ingest(self.root, self.batch)["new_pages"], 2)
        self.batch["history"][0]["next_cursor"] = "FABRICATED"
        with self.assertRaises(archive.ArchiveError):
            archive.ingest(self.root, self.batch)

    def test_wrong_workspace_and_private_channel_are_rejected(self):
        self.batch["workspace"]["id"] = "TOTHER"
        with self.assertRaises(archive.ArchiveError):
            archive.ingest(self.root, self.batch)
        self.batch["workspace"]["id"] = "TTEST1"
        self.batch["channel"]["is_private"] = True
        with self.assertRaises(archive.ArchiveError):
            archive.ingest(self.root, self.batch)

    def test_missing_thread_or_failed_reply_does_not_advance_checkpoint(self):
        ts = "1791266400.000001"
        self.batch["history"] = [page([{"ts": ts, "reply_count": 1}])]
        with self.assertRaises(archive.ArchiveError):
            archive.ingest(self.root, self.batch)
        self.batch["thread_parents"] = [ts]
        self.batch["threads"] = [{"ts": ts, "pages": [page([], thread=ts)]}]
        self.batch["threads"][0]["pages"][0]["result"]["structuredContent"] = {
            "ok": False, "error": "missing_scope"}
        with self.assertRaises(archive.ArchiveError):
            archive.ingest(self.root, self.batch)
        self.assertFalse((self.root / "slack/state").exists())

    def test_summary_receipt_detects_later_raw_changes(self):
        archive.ingest(self.root, self.batch)
        self.assertEqual(len(archive.summary_plan(self.root)), 1)
        text = "# fixture\n\n## 수집 범위\n[원문](../../raw/2026-10-06/CTEST1.jsonl)\n"
        archive.save_summary(self.root, "2026-10-06", "CTEST1", text)
        self.assertEqual(archive.summary_plan(self.root), [])
        self.batch["history"][0]["result"]["structuredContent"]["messages"][0]["text"] = "edited"
        archive.ingest(self.root, self.batch)
        self.assertEqual(len(archive.summary_plan(self.root)), 1)

    def test_unbound_source_never_claims_live_collection(self):
        config = archive.config_at(self.root)
        config["workspace_id"] = None
        archive.write_json(self.root / "slack/config.json", config)
        with self.assertRaises(archive.ArchiveError):
            archive.ingest(self.root, self.batch)
        self.assertFalse(archive.status(self.root)["live_collection_confirmed"])
        with self.assertRaises(archive.ArchiveError):
            archive.bind(self.root, {"name": "capstone2", "id": "TOTHER"})


if __name__ == "__main__":
    unittest.main()
