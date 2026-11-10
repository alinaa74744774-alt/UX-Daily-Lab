import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from unittest import TestCase, main
from unittest import mock
import urllib.error

SCRIPT = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "gemini_api_diagnostic.py"
SPEC = importlib.util.spec_from_file_location("gemini_api_diagnostic", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def response(payload):
    result = mock.MagicMock()
    result.__enter__.return_value.status = 200
    result.__enter__.return_value.read.return_value = json.dumps(payload).encode("utf-8")
    return result


def success_response(text="OK"):
    return response({
        "candidates": [{
            "content": {"parts": [{"text": text}]},
            "finishReason": "STOP",
        }],
        "usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": 1},
    })


class GeminiDiagnosticTests(TestCase):
    def run_with(self, responses):
        output = io.StringIO()
        with (
            mock.patch.dict("os.environ", {"GEMINI_API_KEY": "mock-secret"}),
            mock.patch.object(MODULE.urllib.request, "urlopen", side_effect=responses) as opener,
            redirect_stdout(output),
        ):
            code = MODULE.main()
        return code, opener, output.getvalue()

    def test_success_sends_two_requests_and_logs_metadata_only(self):
        code, opener, logs = self.run_with([success_response(), success_response("A clear recovery path.")])
        self.assertEqual(code, 0)
        self.assertEqual(opener.call_count, 2)
        requests = [call.args[0] for call in opener.call_args_list]
        limits = [json.loads(request.data)["generationConfig"]["maxOutputTokens"] for request in requests]
        prompts = [json.loads(request.data)["contents"][0]["parts"][0]["text"] for request in requests]
        self.assertEqual(limits, [8, 64])
        self.assertEqual(prompts[0], "Reply with OK.")
        self.assertEqual(len(prompts[1]), MODULE.MEDIUM_PROMPT_TARGET_CHARS)
        self.assertIn("Short probe finishReason: STOP", logs)
        self.assertIn("Medium probe input tokens: 12", logs)
        self.assertIn("Medium probe output empty: false", logs)
        self.assertNotIn("mock-secret", logs)
        self.assertNotIn("A clear recovery path.", logs)

    def test_http_failure_skips_second_request(self):
        error = urllib.error.HTTPError("https://example.invalid", 503, "private", {}, io.BytesIO(b"sensitive body"))
        code, opener, logs = self.run_with([error])
        self.assertEqual(code, 1)
        self.assertEqual(opener.call_count, 1)
        self.assertIn("Short probe HTTP status: 503", logs)
        self.assertIn("Short probe error category: service_unavailable", logs)
        self.assertIn("Medium probe: skipped (short probe failed)", logs)
        self.assertNotIn("private", logs)
        self.assertNotIn("sensitive body", logs)

    def test_timeout_skips_second_request(self):
        code, opener, logs = self.run_with([TimeoutError("secret timeout detail")])
        self.assertEqual(code, 1)
        self.assertEqual(opener.call_count, 1)
        self.assertIn("Short probe error category: timeout", logs)
        self.assertIn("Medium probe: skipped (short probe failed)", logs)
        self.assertNotIn("secret timeout detail", logs)

    def test_empty_or_invalid_short_response_skips_second_request(self):
        code, opener, logs = self.run_with([success_response("")])
        self.assertEqual(code, 1)
        self.assertEqual(opener.call_count, 1)
        self.assertIn("Short probe error category: empty_output", logs)
        self.assertIn("Medium probe: skipped (short probe failed)", logs)

        code, opener, logs = self.run_with([response({"candidates": []})])
        self.assertEqual(code, 1)
        self.assertEqual(opener.call_count, 1)
        self.assertIn("Short probe error category: invalid_response", logs)


if __name__ == "__main__":
    main()
