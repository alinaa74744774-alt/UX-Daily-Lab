#!/usr/bin/env python3
"""Reusable course generator foundation for UX Daily Lab.

This module can resolve a planned lesson, build the shared Gemini prompt,
validate the Markdown schema, and write a newly generated course file.
It never runs at import time; API calls happen only with the explicit
--generate command and only for a config entry enabled for generation.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

# Reuse the current Gemini endpoint/model constants without changing Day 01.
from generate_day01 import GEMINI_API, MODEL  # noqa: E402

PLAN_PATH = REPO_ROOT / "config" / "learning-plan.json"
REQUIRED_HEADINGS = (
    "## Today’s Idea｜今日核心知识",
    "## UX Fundamentals｜UX 基础知识",
    "## UX English Learning｜UX 专业英语学习",
    "## Mini Case｜案例理解",
    "## Daily UX Challenge｜今日挑战",
    "## Practice｜实践",
    "## Reflection Prompt｜今日思考",
)
VOCAB_HEADING = REQUIRED_HEADINGS[2]
VOCAB_FIELDS = (
    "**English definition:**",
    "中文理解：",
    "**UX-context example:**",
    "例句理解：",
)


class GeneratorError(RuntimeError):
    """Raised for invalid plans, content, or API responses."""


def load_plan(path=PLAN_PATH):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GeneratorError(f"Could not load learning plan: {exc}") from None
    if data.get("schema_version") != 1 or not isinstance(data.get("weeks"), list):
        raise GeneratorError("Unsupported learning-plan schema.")
    return data


def resolve_day(plan, week_number, day_number):
    matches = [
        (week, day)
        for week in plan["weeks"]
        if week.get("week") == week_number
        for day in week.get("days", [])
        if day.get("day") == day_number
    ]
    if len(matches) != 1:
        raise GeneratorError(
            f"Expected exactly one configured entry for Week {week_number}, Day {day_number:02d}."
        )
    return matches[0][1]


def build_prompt(day):
    if day.get("generation_mode") != "daily":
        raise GeneratorError("This entry is not a daily course; use its configured workflow.")
    return f"""You are a UX learning coach creating a beginner-friendly daily course.
Topic: {day['topic']}
Course title: {day['title']}

Write a practical 30–60 minute lesson in Markdown using this exact structure:
# Day {day['day']:02d} — {day['topic']}

{chr(10).join(REQUIRED_HEADINGS)}

Language requirements:
- English Primary with concise Chinese learning support, approximately 60% English and 40% Chinese.
- Keep UX concepts, professional explanations, examples, challenge instructions, and practice guidance in natural English first.
- Follow key explanations with concise, accurate Chinese support. Do not mechanically translate sentence by sentence or let Chinese sections overwhelm the English.
- Format first mentions as “User Persona 用户画像”, “Mental Model 心理模型”, and similar English-first terminology.
- Make the course appropriate for a UX / interaction design beginner and usable in an international UX learning portfolio.
- Never claim that real research or user testing has already taken place.

Section requirements:
- Today’s Idea: a concise English learning objective followed by Chinese understanding support.
- UX Fundamentals: explain the topic, its purpose, and practical principles in English first with concise Chinese support.
- UX English Learning: include exactly five relevant terms. Use one numbered level-three heading per term, followed by all four labels: {", ".join(VOCAB_FIELDS)}. Each example must sound plausible in a real UX context and include a Chinese explanation.
- Mini Case: use a clearly fictional or generic scenario; explain the UX reasoning in English with concise Chinese support.
- Daily UX Challenge: specify a concrete goal, task, and observable completion criteria in English first, with Chinese support.
- Practice: provide numbered beginner-friendly steps whose total estimated time is 30–60 minutes; include a concrete file name and suggested content structure.
- Reflection Prompt: ask one useful question in natural English, followed by a concise Chinese learning prompt.
- Keep each required second-level heading exactly as written above. Output Markdown only.
"""


def request_gemini(api_key, prompt):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.6, "maxOutputTokens": 6000},
    }
    request = urllib.request.Request(
        GEMINI_API,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            error = json.loads(exc.read().decode("utf-8")).get("error", {})
            message = error.get("message") or "Unknown Gemini API error."
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            message = "No readable Gemini error message."
        message = str(message).replace(api_key, "[REDACTED]")
        message = " ".join(message.split())[:1000]
        host = urlparse(GEMINI_API).netloc
        raise GeneratorError(f"Gemini request to {host} failed with HTTP {exc.code}: {message}") from None
    except urllib.error.URLError as exc:
        raise GeneratorError(f"Gemini connection failed ({exc.reason}).") from None

    try:
        return "".join(
            part.get("text", "")
            for candidate in result["candidates"]
            for part in candidate["content"]["parts"]
        ).strip()
    except (KeyError, TypeError, IndexError):
        raise GeneratorError("Gemini returned no usable course text.") from None


def validate_course(markdown, day):
    expected_title = f"# Day {day['day']:02d} — {day['topic']}"
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != expected_title:
        raise GeneratorError(f"Course must begin with: {expected_title}")
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in markdown]
    if missing:
        raise GeneratorError("Course is missing required sections: " + ", ".join(missing))

    start = markdown.find(VOCAB_HEADING)
    following = re.search(r"^##\s", markdown[start + len(VOCAB_HEADING):], flags=re.MULTILINE)
    end = start + len(VOCAB_HEADING) + following.start() if following else len(markdown)
    vocabulary = markdown[start:end]
    terms = re.findall(r"^###\s+\d+\.\s+.+$", vocabulary, flags=re.MULTILINE)
    if len(terms) != 5:
        raise GeneratorError("UX English Learning must contain exactly five numbered terms.")
    for number, term_heading in enumerate(terms, start=1):
        term_start = vocabulary.find(term_heading) + len(term_heading)
        term_end = vocabulary.find(terms[number], term_start) if number < len(terms) else len(vocabulary)
        entry = vocabulary[term_start:term_end]
        missing_fields = [field for field in VOCAB_FIELDS if field not in entry]
        if missing_fields:
            raise GeneratorError(
                f"Vocabulary item {number} is missing required fields: " + ", ".join(missing_fields)
            )


def write_course(plan, day, markdown):
    output_path = day.get("output_path")
    if not output_path:
        raise GeneratorError("No output path is configured for this lesson.")
    target = (REPO_ROOT / output_path).resolve()
    if not target.is_relative_to(REPO_ROOT.resolve()):
        raise GeneratorError("Configured output path must remain inside the repository.")
    if target.exists():
        raise GeneratorError(f"Refusing to overwrite an existing course file: {output_path}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    return target


def update_manifest(week_number, day, course_path):
    manifest_path = REPO_ROOT / "content" / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GeneratorError(f"Could not load Dashboard manifest: {exc}") from None
    matches = [
        item
        for week in manifest.get("weeks", [])
        if week.get("week") == week_number
        for item in week.get("days", [])
        if item.get("day") == day["day"]
    ]
    if len(matches) != 1:
        raise GeneratorError("Dashboard manifest must contain exactly one matching week/day entry.")
    entry = matches[0]
    if entry.get("status") != "upcoming" or entry.get("content_path") is not None:
        raise GeneratorError("Refusing to replace an existing Dashboard manifest entry.")
    entry["content_path"] = course_path.relative_to(REPO_ROOT).as_posix()
    entry["status"] = "available"
    entry["source_type"] = "generated"
    temporary = manifest_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, manifest_path)


def generate_course(plan, week_number, day):
    if day.get("status") != "upcoming" or day.get("generation_enabled") is not True:
        raise GeneratorError("Generation is disabled for this day in learning-plan.json.")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise GeneratorError("GEMINI_API_KEY is unavailable to this process.")
    prompt = build_prompt(day)
    markdown = request_gemini(api_key, prompt)
    validate_course(markdown, day)
    target = write_course(plan, day, markdown)
    try:
        update_manifest(week_number, day, target)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return target


def main():
    parser = argparse.ArgumentParser(description="Generate or inspect a planned UX Daily Lab course.")
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--day", type=int, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--print-prompt", action="store_true", help="Print the prompt; do not call Gemini.")
    mode.add_argument("--generate", action="store_true", help="Call Gemini and write an enabled course.")
    args = parser.parse_args()

    plan = load_plan()
    day = resolve_day(plan, args.week, args.day)
    if args.print_prompt:
        print(build_prompt(day))
        return
    path = generate_course(plan, args.week, day)
    print(f"Generated course file: {path.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    try:
        main()
    except GeneratorError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        raise SystemExit(1)
