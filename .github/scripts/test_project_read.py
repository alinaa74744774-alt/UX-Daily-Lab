#!/usr/bin/env python3
"""Read-only inspection of the account's GitHub Projects v2 for Actions."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from typing import Any

API_URL = "https://api.github.com/graphql"
EXPECTED_PROJECT_TITLE = "UX × English 每周学习计划"
EXPECTED_DAYS = range(1, 8)

PROJECTS_QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    projectsV2(first: 100, after: $cursor) {
      nodes { id title number }
      pageInfo { hasNextPage endCursor }
    }
  }
}
"""

PROJECT_DETAILS_QUERY = """
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
          fieldValues(first: 50) {
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


class ProjectReadError(Exception):
    pass


def graphql(token: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        # Never print request headers, request objects, or token values.
        if error.code in (401, 403):
            raise ProjectReadError(
                f"GitHub GraphQL access denied (HTTP {error.code}). "
                "Confirm PROJECTS_READ_TOKEN is a valid classic PAT with read:project "
                "and that the account can access this Project."
            ) from None
        raise ProjectReadError(
            f"GitHub GraphQL request failed (HTTP {error.code}); response details withheld."
        ) from None
    except (urllib.error.URLError, TimeoutError):
        raise ProjectReadError("GitHub GraphQL request failed due to a network error.") from None

    try:
        result = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProjectReadError("GitHub GraphQL returned an unreadable response.") from None

    errors = result.get("errors") or []
    if errors:
        messages = " ".join(str(item.get("message", "")) for item in errors)
        if any(term in messages.lower() for term in ("read:project", "resource not accessible", "must have")):
            raise ProjectReadError(
                "GitHub denied Project access. Confirm PROJECTS_READ_TOKEN is a valid classic "
                "PAT with read:project and that the account can access this Project."
            )
        # GraphQL messages are from GitHub; never include request headers or credential data.
        safe_messages = "; ".join(
            re.sub(r"(?i)(authorization|token|secret)\s*[:=]\s*[^\s,]+", r"\1=[redacted]", str(item.get("message", "")))
            for item in errors
        )
        raise ProjectReadError(f"GitHub GraphQL query failed: {safe_messages}")
    return result.get("data") or {}


def all_account_projects(token: str, login: str) -> list[dict[str, Any]]:
    projects: list[dict[str, Any]] = []
    cursor = None
    while True:
        data = graphql(token, PROJECTS_QUERY, {"login": login, "cursor": cursor})
        user = data.get("user")
        if user is None:
            raise ProjectReadError("Could not resolve the repository owner's personal GitHub account.")
        connection = user["projectsV2"]
        projects.extend(connection["nodes"])
        page = connection["pageInfo"]
        if not page["hasNextPage"]:
            return projects
        cursor = page["endCursor"]


def get_project_details(token: str, project_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    fields: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    cursor = None
    project_meta = None
    while True:
        data = graphql(token, PROJECT_DETAILS_QUERY, {"projectId": project_id, "cursor": cursor})
        project = data.get("node")
        if project is None:
            raise ProjectReadError("The matched Project could not be read.")
        project_meta = {
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
            return project_meta, fields, items
        cursor = page["endCursor"]


def title_and_type(item: dict[str, Any]) -> tuple[str, str, int | None]:
    content = item.get("content")
    if content is None:
        return "(no content)", "NoContent", None
    content_type = content.get("__typename", "Unknown")
    title = content.get("title") or "(untitled)"
    issue_number = content.get("number") if content_type == "Issue" else None
    return title, content_type, issue_number


def day_number(title: str) -> int | None:
    match = re.match(r"^\s*Day\s*0*(\d{1,2})\b", title, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def item_field_values(item: dict[str, Any]) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    dates: list[tuple[str, str]] = []
    statuses: list[tuple[str, str]] = []
    for value in item.get("fieldValues", {}).get("nodes", []):
        field = value.get("field") or {}
        name = field.get("name") or "(unnamed field)"
        typename = value.get("__typename", "")
        if typename == "ProjectV2ItemFieldDateValue":
            dates.append((name, value.get("date") or "(empty)"))
        elif typename == "ProjectV2ItemFieldSingleSelectValue":
            statuses.append((name, value.get("name") or "(empty)"))
        elif typename == "ProjectV2ItemFieldTextValue":
            # Include text values when the field is clearly a learning date or status,
            # so unexpected field types/names are visible without exposing item bodies.
            if name.casefold() in {"学习日期", "learning date", "date", "status", "状态"}:
                statuses.append((name, value.get("text") or "(empty)"))
    return dates, statuses


def main() -> int:
    token = os.environ.get("PROJECTS_READ_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    if not token:
        print("PROJECTS_READ_TOKEN is unavailable; token value was not read or printed.")
        return 1
    if "/" not in repository:
        print("GITHUB_REPOSITORY is unavailable or malformed.")
        return 1

    owner = repository.split("/", 1)[0]
    try:
        projects = all_account_projects(token, owner)
        matches = [project for project in projects if project.get("title") == EXPECTED_PROJECT_TITLE]
        if len(matches) != 1:
            if not matches:
                print(f"Project not found in personal account {owner}: {EXPECTED_PROJECT_TITLE}")
                print("Check the Project title and confirm the token can read user-owned Projects.")
                return 1
            print(f"Found {len(matches)} Projects with the exact expected title; refusing to guess.")
            return 1

        selected = matches[0]
        project, fields, items = get_project_details(token, selected["id"])
    except ProjectReadError as error:
        print(str(error))
        return 1

    print("PROJECT READ TEST: SUCCESS")
    print("Owner type: User (personal account)")
    print(f"Project title: {project['title']}")
    print(f"Project ID: {project['id']}")
    print(f"Project number: {project['number']}")
    print(f"Project URL: {project['url']}")
    print("Field definitions:")
    for field in fields:
        name = field.get("name") or "(unnamed field)"
        field_type = field.get("dataType") or field.get("__typename", "Unknown")
        options = field.get("options") or []
        option_names = ", ".join(option.get("name", "") for option in options)
        suffix = f"; options: {option_names}" if option_names else ""
        print(f"- {name} [{field_type}]{suffix}")

    found_days: dict[int, list[dict[str, Any]]] = {}
    print(f"Items read: {len(items)}")
    for item in items:
        title, content_type, issue_number = title_and_type(item)
        dates, statuses = item_field_values(item)
        record = {
            "id": item["id"],
            "title": title,
            "content_type": content_type,
            "issue_number": issue_number,
            "dates": dates,
            "statuses": statuses,
        }
        number = day_number(title)
        if number is not None:
            found_days.setdefault(number, []).append(record)
        print(
            "ITEM "
            + json.dumps(
                {
                    "project_item_id": record["id"],
                    "title": record["title"],
                    "learning_date": dates,
                    "status": statuses,
                    "content_type": content_type,
                    "issue_number": issue_number,
                },
                ensure_ascii=False,
            )
        )

    print("Expected Day 01–Day 07 recognition:")
    all_days_present = True
    for number in EXPECTED_DAYS:
        matches_for_day = found_days.get(number, [])
        state = "FOUND" if matches_for_day else "NOT FOUND"
        if len(matches_for_day) > 1:
            state = f"DUPLICATE ({len(matches_for_day)} items)"
            all_days_present = False
        elif not matches_for_day:
            all_days_present = False
        print(f"- Day {number:02d}: {state}")

    date_field_names = sorted({name for item in items for name, _ in item_field_values(item)[0]})
    status_field_names = sorted({name for item in items for name, _ in item_field_values(item)[1]})
    print(f"Date-valued field names in items: {date_field_names or 'none populated'}")
    print(f"Single-select/status field names in items: {status_field_names or 'none populated'}")
    print(f"Day 01–07 all uniquely recognized: {'YES' if all_days_present else 'NO'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
