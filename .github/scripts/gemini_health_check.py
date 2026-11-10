#!/usr/bin/env python3
"""One-shot Gemini API health check; never logs credentials or response bodies."""

import json
import os
import sys
import time
import urllib.error
import urllib.request

MODEL = "gemini-3.8-flash"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
TIMEOUT_SECONDS = 30


def main() -> int:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("HTTP status: unavailable")
        print("Error type: missing_secret")
        print("Elapsed: 0.000 seconds")
        return 1

    payload = {
        "contents": [{"parts": [{"text": "Reply with OK."}]}],
        "generationConfig": {"maxOutputTokens": 8},
    }
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
    )

    started = time.monotonic()
    status = "unavailable"
    error_type = None
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = str(response.status)
            # Consume the response once so the request completes; never print content.
            response.read()
    except urllib.error.HTTPError as error:
        status = str(error.code)
        error_type = "http_error"
        error.close()
    except (TimeoutError, urllib.error.URLError):
        error_type = "network_or_timeout"
    except Exception:
        error_type = "request_error"

    elapsed = time.monotonic() - started
    print(f"HTTP status: {status}")
    print(f"Elapsed: {elapsed:.3f} seconds")
    if error_type:
        print(f"Error type: {error_type}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
