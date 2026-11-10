#!/usr/bin/env python3
"""One-shot Gemini API health check; never logs credentials or response bodies."""

import json
import os
import time
import urllib.error
import urllib.request

ALLOWED_MODELS = frozenset({
    "gemini-3.8-flash",
    "gemini-3.1-flash-lite",
})
DEFAULT_MODEL = "gemini-3.8-flash"
TIMEOUT_SECONDS = 30


def error_category(status: int) -> str:
    """Map HTTP codes to generic, non-sensitive categories."""
    return {
        400: "bad_request",
        401: "authentication",
        403: "access_denied",
        404: "model_or_endpoint_not_found",
        429: "rate_limited",
        500: "server_error",
        502: "gateway_error",
        503: "service_unavailable",
        504: "gateway_timeout",
    }.get(status, "http_error")


def main() -> int:
    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL).strip()
    if model not in ALLOWED_MODELS:
        print(f"Model: {model or 'not_selected'}")
        print("HTTP status: not_sent")
        print("Elapsed: 0.000 seconds")
        print("Error type: invalid_model_selection")
        return 1

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(f"Model: {model}")
        print("HTTP status: unavailable")
        print("Elapsed: 0.000 seconds")
        print("Error type: missing_secret")
        return 1

    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent"
    )
    payload = {
        "contents": [{"parts": [{"text": "Reply with OK."}]}],
        "generationConfig": {"maxOutputTokens": 8},
    }
    request = urllib.request.Request(
        endpoint,
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
            # Consume the response once; never print response content.
            response.read()
    except urllib.error.HTTPError as error:
        status = str(error.code)
        error_type = error_category(error.code)
        error.close()
    except (TimeoutError, urllib.error.URLError):
        error_type = "network_or_timeout"
    except Exception:
        # Avoid exception text: it may include request details.
        error_type = "request_error"

    elapsed = time.monotonic() - started
    print(f"Model: {model}")
    print(f"HTTP status: {status}")
    print(f"Elapsed: {elapsed:.3f} seconds")
    if error_type:
        print(f"Error type: {error_type}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
