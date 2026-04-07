"""
Jira Issue Sync Script

Fetches issues from a Jira project and converts them into Markdown files
for the Secondary Brain task directories.

Handles Jira's Atlassian Document Format (ADF) and converts it to Markdown.

Usage:
    Set environment variables (JIRA_USERNAME, JIRA_API_TOKEN, JIRA_BASE_URL,
    JIRA_PROJECT_KEY) and run: python scripts/jira_sync.py
"""

import os
import re
import requests

JIRA_USERNAME = os.environ["JIRA_USERNAME"]
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
JIRA_BASE_URL = os.environ["JIRA_BASE_URL"].rstrip("/")
JIRA_PROJECT_KEY = os.environ["JIRA_PROJECT_KEY"]

HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
AUTH = (JIRA_USERNAME, JIRA_API_TOKEN)

STATUS_MAP_ACTIVE = {"In Progress", "In Review", "In Development", "Selected for Development"}
STATUS_MAP_COMPLETED = {"Done", "Closed", "Resolved", "Released"}


def adf_to_markdown(node: dict | list | None, depth: int = 0) -> str:
    """Convert Atlassian Document Format (ADF) JSON to Markdown."""
    if node is None:
        return ""
    if isinstance(node, list):
        return "".join(adf_to_markdown(child, depth) for child in node)
    if not isinstance(node, dict):
        return str(node)

    node_type = node.get("type", "")
    content = node.get("content", [])
    text = node.get("text", "")
    marks = node.get("marks", [])

    if node_type == "doc":
        return adf_to_markdown(content, depth)

    if node_type == "text":
        result = text
        for mark in marks:
            mark_type = mark.get("type", "")
            if mark_type == "strong":
                result = f"**{result}**"
            elif mark_type == "em":
                result = f"*{result}*"
            elif mark_type == "code":
                result = f"`{result}`"
            elif mark_type == "strike":
                result = f"~~{result}~~"
            elif mark_type == "link":
                href = mark.get("attrs", {}).get("href", "")
                result = f"[{result}]({href})"
        return result

    if node_type == "paragraph":
        inner = adf_to_markdown(content, depth)
        return f"{inner}\n\n"

    if node_type == "heading":
        level = node.get("attrs", {}).get("level", 1)
        inner = adf_to_markdown(content, depth)
        return f"{'#' * level} {inner}\n\n"

    if node_type == "bulletList":
        items = ""
        for child in content:
            items += adf_to_markdown(child, depth)
        return items

    if node_type == "orderedList":
        items = ""
        for i, child in enumerate(content, 1):
            items += adf_to_markdown(child, depth, )
        return items

    if node_type == "listItem":
        inner = adf_to_markdown(content, depth + 1).strip()
        indent = "  " * depth
        lines = inner.split("\n")
        result = f"{indent}- {lines[0]}\n"
        for line in lines[1:]:
            if line.strip():
                result += f"{indent}  {line}\n"
        return result

    if node_type == "codeBlock":
        lang = node.get("attrs", {}).get("language", "")
        inner = adf_to_markdown(content, depth)
        return f"```{lang}\n{inner.strip()}\n```\n\n"

    if node_type == "blockquote":
        inner = adf_to_markdown(content, depth)
        lines = inner.strip().split("\n")
        return "\n".join(f"> {line}" for line in lines) + "\n\n"

    if node_type == "rule":
        return "---\n\n"

    if node_type == "hardBreak":
        return "\n"

    if node_type == "table":
        return adf_table_to_markdown(node)

    if node_type == "mention":
        return f"@{node.get('attrs', {}).get('text', 'unknown')}"

    if node_type == "emoji":
        return node.get("attrs", {}).get("text", "")

    if node_type == "inlineCard":
        url = node.get("attrs", {}).get("url", "")
        return f"[{url}]({url})"

    if node_type == "mediaGroup" or node_type == "mediaSingle":
        return "[Media attachment]\n\n"

    return adf_to_markdown(content, depth)


def adf_table_to_markdown(table_node: dict) -> str:
    """Convert ADF table node to Markdown table."""
    rows = table_node.get("content", [])
    if not rows:
        return ""

    md_rows = []
    for row in rows:
        cells = row.get("content", [])
        cell_texts = []
        for cell in cells:
            cell_content = adf_to_markdown(cell.get("content", []))
            cell_texts.append(cell_content.strip().replace("\n", " "))
        md_rows.append(cell_texts)

    if not md_rows:
        return ""

    col_count = max(len(row) for row in md_rows)
    for row in md_rows:
        while len(row) < col_count:
            row.append("")

    result = "| " + " | ".join(md_rows[0]) + " |\n"
    result += "| " + " | ".join(["---"] * col_count) + " |\n"
    for row in md_rows[1:]:
        result += "| " + " | ".join(row) + " |\n"
    return result + "\n"


def get_description_markdown(fields: dict) -> str:
    """Extract and convert the description field to Markdown."""
    desc = fields.get("description")
    if desc is None:
        return "No description provided."
    if isinstance(desc, str):
        return desc
    return adf_to_markdown(desc).strip() or "No description provided."


def get_subtasks(fields: dict) -> str:
    """Extract subtasks into a Markdown checklist."""
    subtasks = fields.get("subtasks", [])
    if not subtasks:
        return "[No subtasks]"

    lines = []
    for st in subtasks:
        status = st.get("fields", {}).get("status", {}).get("name", "")
        done = "x" if status in STATUS_MAP_COMPLETED else " "
        summary = st.get("fields", {}).get("summary", st.get("key", ""))
        key = st.get("key", "")
        lines.append(f"- [{done}] {key}: {summary}")
    return "\n".join(lines)


def issue_to_markdown(issue: dict) -> str:
    """Convert a Jira issue dict into the Secondary Brain task Markdown format."""
    fields = issue["fields"]
    key = issue["key"]
    summary = fields.get("summary", "Untitled")
    status = fields.get("status", {}).get("name", "Unknown")
    issue_type = fields.get("issuetype", {}).get("name", "Task")
    priority = fields.get("priority", {}).get("name", "None")
    assignee = (fields.get("assignee") or {}).get("displayName", "Unassigned")
    reporter = (fields.get("reporter") or {}).get("displayName", "Unknown")
    created = fields.get("created", "")
    updated = fields.get("updated", "")
    description = get_description_markdown(fields)
    subtasks = get_subtasks(fields)

    return f"""# {key}: {summary}

**Status:** {status}
**Type:** {issue_type}
**Priority:** {priority}
**Assignee:** {assignee}
**Reporter:** {reporter}
**Created:** {created}
**Last Updated:** {updated}
**Jira Link:** [{key}]({JIRA_BASE_URL}/browse/{key})

## Description

{description}

## Subtasks

{subtasks}

## Acceptance Criteria

[Manually add acceptance criteria after sync, or populate from Jira custom fields]

## Test Scenarios

[Manually add test scenarios after sync]

## Dependencies

- **Depends on:** [Add dependencies]
- **Blocks:** [Add what this blocks]

## Related Files

[Add relevant codebase files after sync]

## AI Agent Instructions for this Task

- **Focus:** Address the core problem described in the Description section.
- **Context:** Refer to `AI_CONTEXT/project-context.md` and `AI_CONTEXT/rules.md` for overall project guidelines. Check `AI_CONTEXT/known-issues.md` for relevant gotchas.
- **Deliverables:** [Specify expected deliverables after sync]
- **Definition of Done:** All acceptance criteria met, tests passing, PR approved, docs updated.
"""


def determine_directory(status: str) -> str:
    """Map Jira status to the appropriate tasks subdirectory."""
    if status in STATUS_MAP_COMPLETED:
        return "tasks/completed"
    elif status in STATUS_MAP_ACTIVE:
        return "current-focus"
    else:
        return "tasks/backlog"


def fetch_all_issues() -> list:
    """Fetch all issues from the Jira project using pagination."""
    all_issues = []
    start_at = 0
    max_results = 50

    while True:
        url = f"{JIRA_BASE_URL}/rest/api/3/search"
        params = {
            "jql": f'project = "{JIRA_PROJECT_KEY}" ORDER BY updated DESC',
            "startAt": start_at,
            "maxResults": max_results,
            "fields": "summary,description,status,assignee,reporter,priority,"
                      "issuetype,created,updated,subtasks",
        }
        resp = requests.get(url, headers=HEADERS, auth=AUTH, params=params)
        resp.raise_for_status()
        data = resp.json()
        issues = data.get("issues", [])
        all_issues.extend(issues)
        if len(issues) < max_results:
            break
        start_at += max_results

    return all_issues


def save_issue(issue: dict) -> None:
    """Save a single issue as a Markdown file in the appropriate directory."""
    key = issue["key"]
    status = issue["fields"]["status"]["name"]
    target_dir = determine_directory(status)
    summary_slug = re.sub(r"[^a-zA-Z0-9]+", "-", issue["fields"]["summary"]).strip("-").lower()
    filename = f"{key}-{summary_slug}.md"

    os.makedirs(target_dir, exist_ok=True)
    filepath = os.path.join(target_dir, filename)

    markdown = issue_to_markdown(issue)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Saved {filename} -> {target_dir}")


def main():
    print(f"Fetching issues for project: {JIRA_PROJECT_KEY}")
    issues = fetch_all_issues()
    print(f"Found {len(issues)} issues")

    for issue in issues:
        save_issue(issue)

    print("Sync complete.")


if __name__ == "__main__":
    main()
