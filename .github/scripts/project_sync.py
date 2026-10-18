#!/usr/bin/env python3
"""Synchronize the personal GitHub Project plan into config/learning-plan.json.

This is read-only against GitHub Projects. It never creates or updates Project
items, Issues, course files, or Dashboard files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API_URL = "https://api.github.com/graphql"
PROJECT_TITLE = "UX × English 每周学习计划"
DATE_FIELD_NAME = "学习日期"
STATUS_FIELD_NAME = "Status"
TIMEZONE = "Asia/Shanghai"
COURSE_PATH_TEMPLATE = "content/courses/week-{week:02d}/day-{day:02d}.md"
LEGACY_DAY_ONE_PATH = "Day01_User_Research_Interview_Plan.md"
REPO_ROOT = Path(__file__).resolve().parents[2]
DAY_RE = re.compile(r"^\s*Day\s*0*(\d{1,3})\s*(?:[|｜:：—–-]\s*)?(.*?)\s*$", re.IGNORECASE)

PROJECTS_QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    projectsV2(first: 100, after: $cursor) {
      nodes { id title number url }
      pageInfo { hasNextPage endCursor }
    }
  }
}
"""

PROJECT_ITEMS_QUERY = """
query($projectId: ID!, $cursor: String) {
  node(id: $projectId) {
    ... on ProjectV2 {
      id title number url
      fields(first: 100) {
        nodes {
          __typename
          ... on ProjectV2FieldCommon { id name dataType }
          ... on ProjectV2SingleSelectField {
            id name
            options { id name }
          }
        }
      }
      items(first: 50, after: $cursor) {
        nodes {
          id
          content {
            __typename
            ... on Issue { number title }
            ... on DraftIssue { title }
            ... on PullRequest { number title }
          }
          fieldValues(first: 100) {
            nodes {
              __typename
              ... on ProjectV2ItemFieldDateValue {
                date
                field { ... on ProjectV2FieldCommon { name } }
              }
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field { ... on ProjectV2FieldCommon { name } }
              }
              ... on ProjectV2ItemFieldTextValue {
                text
                field { ... on ProjectV2FieldCommon { name } }
              }
            }
          }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
"""


class SyncError(RuntimeError):
    """Raised when Project data cannot be safely normalized."""


def graphql(token: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_body = response.read()
    except urllib.error.HTTPError as error:
        if error.code in (401, 403):
            raise SyncError(
                f"GitHub GraphQL access denied (HTTP {error.code}). "
                "Confirm PROJECTS_READ_TOKEN can read this personal Project."
            ) from None
        raise SyncError(
            f"GitHub GraphQL request failed (HTTP {error.code}); response details withheld."
        ) from None
    except (urllib.error.URLError, TimeoutError):
        raise SyncError("GitHub GraphQL request failed due to a network error.") from None

    try:
        result = json.loads(response_body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise SyncError("GitHub GraphQL returned an unreadable response.") from None

    errors = result.get("errors") or []
    if errors:
        combined = " ".join(str(error.get("message", "")) for error in errors)
        if any(
            hint in combined.lower()
            for hint in ("read:project", "resource not accessible", "must have", "not authorized")
        ):
            raise SyncError(
                "GitHub denied Project access. Confirm PROJECTS_READ_TOKEN has the existing "
                "read:project authorization; no permission changes were attempted."
            )
        raise SyncError("GitHub GraphQL query failed: " + "; ".join(
            str(error.get("message", "Unknown GraphQL error")) for error in errors
        ))
    return result.get("data") or {}


def find_project(token: str, owner: str) -> dict[str, Any]:
    cursor = None
    matches: list[dict[str, Any]] = []
    while True:
        data = graphql(token, PROJECTS_QUERY, {"login": owner, "cursor": cursor})
        user = data.get("user")
        if user is None:
            raise SyncError("The GitHub repository owner could not be resolved as a personal account.")
        connection = user["projectsV2"]
        matches.extend(project for project in connection["nodes"] if project.get("title") == PROJECT_TITLE)
        page = connection["pageInfo"]
        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]

    if not matches:
        raise SyncError(f'Personal Project "{PROJECT_TITLE}" was not found for {owner}.')
    if len(matches) != 1:
        raise SyncError(f'Found {len(matches)} Projects named "{PROJECT_TITLE}"; refusing to guess.')
    return matches[0]


def read_project(token: str, project_id: str) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    cursor = None
    project_info: dict[str, Any] | None = None
    fields: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []

    while True:
        data = graphql(token, PROJECT_ITEMS_QUERY, {"projectId": project_id, "cursor": cursor})
        project = data.get("node")
        if project is None:
            raise SyncError("The matched Project could not be read.")
        project_info = {
            "id": project["id"],
            "number": project["number"],
            "title": project["title"],
            "url": project["url"],
        }
        fields = project["fields"]["nodes"]
        connection = project["items"]
        items.extend(connection["nodes"])
        page = connection["pageInfo"]
        if not page["hasNextPage"]:
            return project_info, fields, items
        cursor = page["endCursor"]


def extract_fields(item: dict[str, Any]) -> tuple[str | None, str | None]:
    scheduled_date = None
    status = None
    for value in item.get("fieldValues", {}).get("nodes", []):
        field_name = (value.get("field") or {}).get("name")
        typename = value.get("__typename", "")
        if field_name == DATE_FIELD_NAME:
            if typename == "ProjectV2ItemFieldDateValue":
                scheduled_date = value.get("date")
            elif typename == "ProjectV2ItemFieldTextValue":
                scheduled_date = value.get("text")
        if field_name == STATUS_FIELD_NAME:
            if typename == "ProjectV2ItemFieldSingleSelectValue":
                status = value.get("name")
            elif typename == "ProjectV2ItemFieldTextValue":
                status = value.get("text")
    return scheduled_date, status


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    content = item.get("content") or {}
    content_type = content.get("__typename") or "NoContent"
    title = content.get("title") or "(untitled)"
    match = DAY_RE.match(title)
    day = int(match.group(1)) if match else None
    topic = (match.group(2) or "").strip() if match else None
    scheduled_date, status = extract_fields(item)

    warnings: list[str] = []
    if day is None:
        warnings.append("unrecognized_day_title")
    if not scheduled_date:
        warnings.append("missing_learning_date")
    if status is None:
        warnings.append("missing_status")

    issue_number = content.get("number") if content_type == "Issue" else None
    if day is not None:
        week = ((day - 1) // 7) + 1
        day_in_week = ((day - 1) % 7) + 1
        generation_mode = "legacy" if day == 1 else ("weekly_review" if day_in_week == 7 else "daily")
        existing_content_path = (
            LEGACY_DAY_ONE_PATH
            if day == 1 and (REPO_ROOT / LEGACY_DAY_ONE_PATH).is_file()
            else None
        )
        output_path = (
            None
            if existing_content_path or day_in_week == 7
            else COURSE_PATH_TEMPLATE.format(week=week, day=day_in_week)
        )
    else:
        week = None
        day_in_week = None
        generation_mode = None
        existing_content_path = None
        output_path = None

    return {
        "project_item_id": item["id"],
        "day": day,
        "day_in_week": day_in_week,
        "week": week,
        "topic": topic or title,
        "title": title,
        "scheduled_date": scheduled_date,
        "status": status,
        "content_type": content_type,
        "issue_number": issue_number,
        "generation_mode": generation_mode,
        "generation_enabled": False,
        "content_path": existing_content_path,
        "output_path": output_path,
        "sync_warnings": warnings,
    }


def build_plan(owner: str, project: dict[str, Any], fields: list[dict[str, Any]], raw_items: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = [normalize_item(item) for item in raw_items]
    by_day: dict[int, list[str]] = {}
    for entry in normalized:
        if entry["day"] is not None:
            by_day.setdefault(entry["day"], []).append(entry["project_item_id"])
    duplicates = {day: ids for day, ids in by_day.items() if len(ids) > 1}
    if duplicates:
        detail = ", ".join(f"Day {day:02d} ({len(ids)} items)" for day, ids in sorted(duplicates.items()))
        raise SyncError("Duplicate Day number(s) detected; refusing to write the plan: " + detail)

    day_fields = {field.get("name") for field in fields}
    if DATE_FIELD_NAME not in day_fields:
        raise SyncError(f'Project field "{DATE_FIELD_NAME}" was not found; refusing to guess a date field.')
    if STATUS_FIELD_NAME not in day_fields:
        raise SyncError(f'Project field "{STATUS_FIELD_NAME}" was not found; refusing to guess a Status field.')

    weeks_by_number: dict[int, list[dict[str, Any]]] = {}
    unassigned: list[dict[str, Any]] = []
    warnings: list[dict[str, str]] = []
    for entry in normalized:
        if entry["week"] is None:
            unassigned.append(entry)
        else:
            weeks_by_number.setdefault(entry["week"], []).append(entry)
        for warning in entry["sync_warnings"]:
            warnings.append({
                "project_item_id": entry["project_item_id"],
                "title": entry["title"],
                "code": warning,
            })

    weeks = []
    for number, days in sorted(weeks_by_number.items()):
        days.sort(key=lambda entry: (entry["day"], entry["project_item_id"]))
        weeks.append({
            "week": number,
            "title": f"Week {number:02d}",
            "days": days,
        })

    return {
        "schema_version": 1,
        "generated": True,
        "source_of_truth": "GitHub Project",
        "source": {
            "type": "github_project",
            "owner_type": "User",
            "owner": owner,
            "title": project["title"],
            "project_id": project["id"],
            "project_number": project["number"],
            "url": project["url"],
            "date_field": DATE_FIELD_NAME,
            "status_field": STATUS_FIELD_NAME,
        },
        "timezone": TIMEZONE,
        "course_path_template": COURSE_PATH_TEMPLATE,
        "weeks": weeks,
        "unassigned_items": sorted(unassigned, key=lambda entry: (entry["title"], entry["project_item_id"])),
        "sync_warnings": sorted(warnings, key=lambda entry: (entry["title"], entry["code"], entry["project_item_id"])),
    }


def write_if_changed(path: Path, data: dict[str, Any]) -> bool:
    serialized = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    encoded = serialized.encode("utf-8")
    if path.exists() and path.read_bytes() == encoded:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(encoded)
    os.replace(temporary, path)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync the personal GitHub Project into the generated learning-plan cache.")
    parser.add_argument("--output", default=str(REPO_ROOT / "config" / "learning-plan.json"))
    args = parser.parse_args()

    token = os.environ.get("PROJECTS_READ_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    if not token:
        print("PROJECTS_READ_TOKEN is unavailable; its value was not printed.")
        return 1
    if "/" not in repository:
        print("GITHUB_REPOSITORY is unavailable or malformed.")
        return 1

    owner = repository.split("/", 1)[0]
    try:
        project_match = find_project(token, owner)
        project, fields, items = read_project(token, project_match["id"])
        plan = build_plan(owner, project, fields, items)
        changed = write_if_changed(Path(args.output), plan)
    except SyncError as error:
        print(f"PROJECT SYNC FAILED: {error}")
        return 1

    print(f"PROJECT SYNC SUCCESS: {project['title']}")
    print(f"Owner type: User")
    print(f"Project ID: {project['id']}")
    print(f"Project number: {project['number']}")
    print(f"Items synced: {len(items)}")
    print(f"Output: {args.output}")
    print(f"File result: {'updated' if changed else 'unchanged'}")
    for week in plan["weeks"]:
        for entry in week["days"]:
            print(
                "ITEM "
                + json.dumps(
                    {
                        "project_item_id": entry["project_item_id"],
                        "day": entry["day"],
                        "title": entry["title"],
                        "scheduled_date": entry["scheduled_date"],
                        "status": entry["status"],
                        "content_type": entry["content_type"],
                        "issue_number": entry["issue_number"],
                        "sync_warnings": entry["sync_warnings"],
                    },
                    ensure_ascii=False,
                )
            )
    for entry in plan["unassigned_items"]:
        print(
            "UNASSIGNED ITEM "
            + json.dumps(
                {
                    "project_item_id": entry["project_item_id"],
                    "title": entry["title"],
                    "scheduled_date": entry["scheduled_date"],
                    "status": entry["status"],
                    "content_type": entry["content_type"],
                    "issue_number": entry["issue_number"],
                    "sync_warnings": entry["sync_warnings"],
                },
                ensure_ascii=False,
            )
        )
    for number in range(1, 8):
        found = sum(1 for entry in normalized_entries(plan) if entry["day"] == number)
        print(f"Day {number:02d}: {'FOUND' if found else 'NOT FOUND'}")
    if plan["sync_warnings"]:
        print(f"Sync warnings: {len(plan['sync_warnings'])}; missing dates/unrecognized titles remain non-generatable.")
    else:
        print("Sync warnings: none")
    return 0


def normalized_entries(plan: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        entry
        for week in plan["weeks"]
        for entry in week["days"]
    ] + plan["unassigned_items"]


if __name__ == "__main__":
    sys.exit(main())
