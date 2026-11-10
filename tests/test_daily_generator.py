import json
import os
import socket
import unittest
import urllib.error
from datetime import datetime
from pathlib import Path
from unittest import mock

import importlib.util
import sys

REPO = Path(__file__).resolve().parents[1]
SCRIPT_DIR = REPO / '.github' / 'scripts'
sys.path.insert(0, str(SCRIPT_DIR))
_spec = importlib.util.spec_from_file_location('daily_generator_under_test', SCRIPT_DIR / 'daily_generator.py')
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

def _load_generator():
    return _module




class DailyGeneratorBackfillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_generator()

    def setUp(self):
        self.mod.REPO_ROOT = Path.cwd()
        self.plan = {
            "generated": True,
            "source_of_truth": "GitHub Project",
            "source": {"type": "github_project"},
            "timezone": "Asia/Shanghai",
            "weeks": [{"week": 1, "days": [
                {"day": 6, "week": 1, "title": "Day 06 Interactive Prototype",
                 "scheduled_date": "2026-10-23", "project_item_id": "item-6"},
                {"day": 7, "week": 1, "title": "Day 07 Weekly Review",
                 "scheduled_date": "2026-10-24", "project_item_id": "item-7"},
                {"day": 8, "week": 2, "title": "Day 08 Future",
                 "scheduled_date": "2026-10-25", "project_item_id": "item-8"},
            ]}],
        }

    def test_due_backfill_sorted_and_capped_at_two(self):
        with mock.patch.object(self.mod, "existing_course_path", return_value=None):
            selected = self.mod.select_due_items(
                self.plan, {"weeks": []}, "2026-10-25", backfill_missing=True
            )
        self.assertEqual([x["day"] for x in selected], [6, 7])

    def test_manual_target_date_matches_only_real_project_item(self):
        with mock.patch.object(self.mod, "existing_course_path", return_value=None):
            selected = self.mod.select_due_items(
                self.plan, {"weeks": []}, "2026-11-10",
                target_date="2026-10-23", backfill_missing=True
            )
            missing = self.mod.select_due_items(
                self.plan, {"weeks": []}, "2026-11-10",
                target_date="2026-10-22", backfill_missing=True
            )
        self.assertEqual([x["day"] for x in selected], [6])
        self.assertEqual(missing, [])

    def test_future_day_remains_scheduled_until_due(self):
        with mock.patch.object(self.mod, "existing_course_path", return_value=None):
            selected = self.mod.select_due_items(self.plan, {"weeks": []}, "2026-10-24")
        self.assertEqual([x["day"] for x in selected], [6, 7])

    def test_existing_course_is_skipped_without_gemini(self):
        item = self.plan["weeks"][0]["days"][0]
        with mock.patch.object(self.mod, "existing_course_path", return_value=Path("content/day-06.md")), \
             mock.patch.object(self.mod, "request_gemini") as api:
            pending = self.mod.select_due_items(self.plan, {"weeks": []}, "2026-10-25")
        self.assertEqual(pending, [])
        api.assert_not_called()

    def test_partial_success_is_retained_and_failed_item_can_retry(self):
        items = self.plan["weeks"][0]["days"][:2]
        manifest = {"weeks": []}
        calls = []
        def fake_generate(item, current):
            calls.append(item["day"])
            if item["day"] == 7:
                raise self.mod.GeneratorError("temporary outage")
            return {"weeks": [{"week": 1, "days": [{"day": 6, "generation_status": "generated"}]}]}, True
        updated, generated, skipped, errors = self.mod.process_items(items, manifest, fake_generate)
        self.assertEqual(generated, 1)
        self.assertEqual(skipped, 0)
        self.assertEqual(calls, [6, 7])
        self.assertEqual(updated["weeks"][0]["days"][0]["day"], 6)
        self.assertEqual(len(errors), 1)

    def test_http_503_and_timeout_retry_then_succeed(self):
        success = mock.MagicMock()
        success.__enter__.return_value.read.return_value = json.dumps({
            "candidates": [{"content": {"parts": [{"text": "course"}]}}]
        }).encode()
        sequence = [
            urllib.error.HTTPError("https://example.invalid", 503, "busy", {}, None),
            socket.timeout("read timed out"),
            success,
        ]
        with mock.patch.object(self.mod.urllib.request, "urlopen", side_effect=sequence) as urlopen, \
             mock.patch.object(self.mod.time, "sleep") as sleep:
            value = self.mod.request_gemini("mock-key", "prompt")
        self.assertEqual(value, "course")
        self.assertEqual(urlopen.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    def test_exhausted_transient_retries_are_bounded(self):
        failure = urllib.error.HTTPError("https://example.invalid", 503, "busy", {}, None)
        with mock.patch.object(self.mod.urllib.request, "urlopen", side_effect=failure), \
             mock.patch.object(self.mod.time, "sleep") as sleep:
            with self.assertRaises(self.mod.GeneratorError):
                self.mod.request_gemini("mock-key", "prompt")
        self.assertEqual(sleep.call_count, self.mod.MAX_RETRIES)

    def test_day01_to_day05_files_are_never_selected_for_replacement(self):
        for day in range(1, 6):
            item = {"day": day, "week": 1, "scheduled_date": "2026-10-20",
                    "title": f"Day {day:02d}", "project_item_id": f"item-{day}"}
            with mock.patch.object(self.mod, "existing_course_path", return_value=Path(f"content/day-{day:02d}.md")):
                selected = self.mod.select_due_items(
                    {"generated": True, "source_of_truth": "GitHub Project",
                     "source": {"type": "github_project"},
                     "weeks": [{"week": 1, "days": [item]}]},
                    {"weeks": []}, "2026-10-25"
                )
            self.assertEqual(selected, [])


    def test_retry_budget_exhaustion_stops_without_long_wait(self):
        failure = urllib.error.HTTPError("https://example.invalid", 503, "busy", {}, None)
        with mock.patch.object(self.mod, "COURSE_RETRY_BUDGET_SECONDS", 10), \
             mock.patch.object(self.mod.time, "monotonic", return_value=0), \
             mock.patch.object(self.mod, "retry_delay", return_value=20), \
             mock.patch.object(self.mod.urllib.request, "urlopen", side_effect=failure) as urlopen, \
             mock.patch.object(self.mod.time, "sleep") as sleep:
            with self.assertRaisesRegex(self.mod.GeneratorError, "budget exhausted"):
                self.mod.request_gemini("mock-key", "prompt")
        self.assertEqual(urlopen.call_count, 1)
        sleep.assert_not_called()

    def test_verified_model_is_default_and_request_config_is_supported(self):
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({
            "candidates": [{"content": {"parts": [{"text": "course"}]}}]
        }).encode()
        with mock.patch.dict(os.environ, {"GEMINI_MODEL": ""}), \\
             mock.patch.object(self.mod.urllib.request, "urlopen", return_value=response) as urlopen:
            self.mod.request_gemini("mock-key", "prompt")
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode())
        self.assertEqual(self.mod.configured_model(), "gemini-3.1-flash-lite")
        self.assertEqual(payload["generationConfig"], {"maxOutputTokens": 6000})
        self.assertEqual(
            request.full_url,
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-3.1-flash-lite:generateContent",
        )

    def test_original_model_is_available_only_as_explicit_override(self):
        with mock.patch.dict(os.environ, {"GEMINI_MODEL": "gemini-3.8-flash"}):
            self.assertEqual(self.mod.configured_model(), "gemini-3.8-flash")
            self.assertEqual(
                self.mod.gemini_endpoint(),
                "https://generativelanguage.googleapis.com/v1beta/models/"
                "gemini-3.8-flash:generateContent",
            )

    def test_unapproved_model_fails_before_network_request(self):
        with mock.patch.dict(os.environ, {"GEMINI_MODEL": "unapproved-model"}), \\
             mock.patch.object(self.mod.urllib.request, "urlopen") as urlopen:
            with self.assertRaisesRegex(self.mod.GeneratorError, "unsupported"):
                self.mod.request_gemini("mock-key", "prompt")
        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
