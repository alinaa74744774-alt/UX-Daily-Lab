#!/usr/bin/env python3
"""One-shot, privacy-safe Gemini request-length diagnostic."""

from __future__ import annotations

import json
import os
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

MODEL = "gemini-3.1-flash-lite"
ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODEL}:generateContent"
)
REQUEST_TIMEOUT_SECONDS = 45
MEDIUM_PROMPT_TARGET_CHARS = 3744
SAFE_FINISH_REASONS = {
    "STOP",
    "MAX_TOKENS",
    "SAFETY",
    "RECITATION",
    "OTHER",
    "BLOCKLIST",
    "PROHIBITED_CONTENT",
    "SPII",
    "MALFORMED_FUNCTION_CALL",
    "IMAGE_SAFETY",
}


@dataclass
class ProbeResult:
    status: str
    elapsed_seconds: float
    error_category: str
    finish_reason: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    output_empty: bool | None = None

    @property
    def usable(self) -> bool:
        return (
            self.status == "200"
            and self.error_category == "none"
            and self.output_empty is False
        )


def medium_prompt() -> str:
    """Build a representative ~Day 06-sized prompt without logging its contents."""
    opening = (
        "You are a UX design educator. Review this interactive prototype planning "
        "scenario and return one concise sentence naming the most important "
        "usability risk. Do not create a course or a long explanation.\n\n"
        "Project context: A beginner designer is prototyping a mobile service "
        "that helps people plan, save, and revisit weekly meals. The prototype "
        "contains onboarding, search, recipe details, saved items, a weekly "
        "planner, and a profile. Users should be able to move between these "
        "areas, understand system feedback, recover from mistakes, and complete "
        "a realistic planning task.\n\n"
        "Review considerations include clear goals, visible system status, "
        "consistent controls, meaningful navigation, useful feedback, error "
        "prevention, undo and recovery, readable labels, accessible touch "
        "targets, information hierarchy, realistic content, and a coherent "
        "mental model. Consider how a first-time user discovers a recipe, "
        "saves it, adds it to a plan, changes a serving size, and returns to "
        "the correct place after an interruption.\n\n"
    )
    note = (
        "Evaluate the flow from the user's point of view, using observable "
        "actions rather than assumptions. "
    )
    closing = (
        "\n\nReturn exactly one short English sentence. Do not include a "
        "course, headings, bullets, or private information."
    )
    remaining = MEDIUM_PROMPT_TARGET_CHARS - len(opening) - len(closing)
    if remaining < 0:
        raise RuntimeError("Diagnostic prompt target is too small.")
    context = (note * ((remaining // len(note)) + 1))[:remaining]
    prompt = opening + context + closing
    if len(prompt) != MEDIUM_PROMPT_TARGET_CHARS:
        raise RuntimeError("Diagnostic prompt length did not match its target.")
    return prompt


def _safe_category(status: int | None, exc: BaseException | None) -> str:
    if status is not None:
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
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return "timeout"
    if isinstance(exc, urllib.error.URLError):
        reason = exc.reason
        if isinstance(reason, (TimeoutError, socket.timeout)):
            return "timeout"
        return "network_error"
    if exc is not None:
        return "request_error"
    return "none"


def _safe_finish_reason(value: Any) -> str:
    return value if isinstance(value, str) and value in SAFE_FINISH_REASONS else "other"


def _safe_count(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def run_probe(name: str, api_key: str, prompt: str, output_limit: int) -> ProbeResult:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": output_limit},
    }
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
    )
    started = time.monotonic()
    status: int | None = None
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            status = int(response.status)
            body = response.read()
        elapsed = round(time.monotonic() - started, 3)
        if not 200 <= status < 300:
            return ProbeResult(str(status), elapsed, _safe_category(status, None))
        try:
            data = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return ProbeResult(str(status), elapsed, "invalid_response")

        candidates = data.get("candidates")
        candidate = candidates[0] if isinstance(candidates, list) and candidates else None
        if not isinstance(candidate, dict):
            return ProbeResult(str(status), elapsed, "invalid_response")

        content = candidate.get("content")
        parts = content.get("parts") if isinstance(content, dict) else None
        output_text = "".join(
            part.get("text", "")
            for part in (parts if isinstance(parts, list) else [])
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        )
        usage = data.get("usageMetadata")
        usage = usage if isinstance(usage, dict) else {}
        result = ProbeResult(
            str(status),
            elapsed,
            "none" if output_text.strip() else "empty_output",
            _safe_finish_reason(candidate.get("finishReason")),
            _safe_count(usage.get("promptTokenCount")),
            _safe_count(usage.get("candidatesTokenCount")),
            not bool(output_text.strip()),
        )
        return result
    except urllib.error.HTTPError as exc:
        elapsed = round(time.monotonic() - started, 3)
        return ProbeResult(str(exc.code), elapsed, _safe_category(exc.code, None))
    except (TimeoutError, socket.timeout):
        elapsed = round(time.monotonic() - started, 3)
        return ProbeResult("none", elapsed, "timeout")
    except urllib.error.URLError as exc:
        elapsed = round(time.monotonic() - started, 3)
        return ProbeResult("none", elapsed, _safe_category(None, exc))
    except Exception:
        elapsed = round(time.monotonic() - started, 3)
        return ProbeResult("none", elapsed, "request_error")


def report(name: str, result: ProbeResult) -> None:
    print(f"{name} model: {MODEL}")
    print(f"{name} HTTP status: {result.status}")
    print(f"{name} elapsed seconds: {result.elapsed_seconds:.3f}")
    print(f"{name} error category: {result.error_category}")
    if result.status == "200" and result.finish_reason is not None:
        print(f"{name} finishReason: {result.finish_reason}")
        print(f"{name} input tokens: {result.input_tokens if result.input_tokens is not None else 'unavailable'}")
        print(f"{name} output tokens: {result.output_tokens if result.output_tokens is not None else 'unavailable'}")
        print(f"{name} output empty: {str(bool(result.output_empty)).lower()}")


def main() -> int:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print(f"Short probe model: {MODEL}")
        print("Short probe HTTP status: not_sent")
        print("Short probe elapsed seconds: 0.000")
        print("Short probe error category: missing_secret")
        print("Medium probe: skipped (short probe failed)")
        return 1

    short = run_probe("Short probe", api_key, "Reply with OK.", 8)
    report("Short probe", short)
    if not short.usable:
        print("Medium probe: skipped (short probe failed)")
        return 1

    medium = run_probe("Medium probe", api_key, medium_prompt(), 64)
    report("Medium probe", medium)
    return 0 if medium.usable else 1


if __name__ == "__main__":
    raise SystemExit(main())
