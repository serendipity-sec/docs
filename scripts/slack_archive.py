"""Store native Slack connector results. Codex performs collection and summarization.

No Slack/OpenAI API credentials, HTTP requests, or model calls are made here.
The ingest command accepts a complete, paginated channel capture exported by Codex.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import unquote

KST = timezone(timedelta(hours=9))
CHANNEL_ID = re.compile(r"^[CG][A-Z0-9]+$")
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ArchiveError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def config_at(root):
    return load(root / "slack/config.json")


def records(root):
    for path in sorted((root / "slack/raw").glob("*/*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                yield path, json.loads(line)


def connector_data(result):
    """Inspect structured payloads without discarding the original MCP envelope."""
    if not isinstance(result, dict) or result.get("isError"):
        raise ArchiveError("Slack connector returned an error or invalid result")
    content = result.get("content", [])
    values = []
    if isinstance(result.get("structuredContent"), dict):
        values.append(result["structuredContent"])
    for block in content:
        if block.get("type") == "text":
            try:
                value = json.loads(block["text"])
            except (ValueError, KeyError):
                continue
            if isinstance(value, dict):
                values.append(value)
    if not content and not values:
        raise ArchiveError("Slack connector result is empty")
    for value in values:
        if value.get("ok") is False or value.get("error") or value.get("error_code"):
            raise ArchiveError("Slack API reported a failure")
    for block in content:
        if block.get("type") == "text" and block.get("text", "").startswith("execution_failed:"):
            raise ArchiveError("Slack connector reported a failure")
    return values


def native_cursor(result):
    for value in connector_data(result):
        meta = value.get("response_metadata") or {}
        if "next_cursor" in meta:
            return meta["next_cursor"] or ""
        if "next_cursor" in value:
            return value["next_cursor"] or ""
    return None  # Markdown-only responses require the observed cursor from Codex.


def validate_pages(pages, channel_id, thread_ts=None):
    if not isinstance(pages, list) or not pages:
        raise ArchiveError("Capture must include at least one native page")
    expected_cursor = ""
    expected_tool = "slack_read_thread" if thread_ts else "slack_read_channel"
    for index, page in enumerate(pages):
        if page.get("tool") != expected_tool:
            raise ArchiveError("Unexpected Slack tool in capture")
        args = page.get("arguments", {})
        if args.get("channel_id") != channel_id:
            raise ArchiveError("Page channel does not match the authorized channel")
        if thread_ts and args.get("message_ts") != thread_ts:
            raise ArchiveError("Page belongs to a different thread")
        if (args.get("cursor") or "") != expected_cursor:
            raise ArchiveError("Pagination cursor chain is incomplete")
        if "next_cursor" not in page or not isinstance(page["next_cursor"], str):
            raise ArchiveError("Each page must record its observed next_cursor")
        observed = native_cursor(page.get("result"))
        if observed is not None and observed != page["next_cursor"]:
            raise ArchiveError("Recorded cursor differs from native Slack result")
        for value in connector_data(page["result"]):
            if value.get("has_more") is True and not page["next_cursor"]:
                raise ArchiveError("Slack reported uncollected pages")
        expected_cursor = page["next_cursor"]
        if index < len(pages) - 1 and not expected_cursor:
            raise ArchiveError("Pages continue after an already completed result")
    if expected_cursor:
        raise ArchiveError("Final page still has a pagination cursor")


def seen_threads(pages):
    parents = set()
    for page in pages:
        for value in connector_data(page["result"]):
            messages = value.get("messages", [])
            if isinstance(messages, str):
                # The live connector can return formatted history as JSON text.
                for block in re.split(r"(?=^=== Message from )", messages, flags=re.M):
                    ts = re.search(r"^Message TS: (\d+\.\d+)$", block, flags=re.M)
                    replies = re.search(r"^Thread: ([1-9]\d*) replies", block, flags=re.M)
                    if ts and replies:
                        parents.add(ts.group(1))
                continue
            if not isinstance(messages, list):
                raise ArchiveError("Unexpected Slack message representation")
            for message in messages:
                if not isinstance(message, dict):
                    raise ArchiveError("Invalid structured Slack message")
                if message.get("reply_count", 0) > 0 and message.get("ts"):
                    parents.add(message["ts"])
    return parents


def validate_reply_counts(history, threads):
    """A terminal cursor alone cannot prove replies were returned by the connector."""
    counts = {}
    for page in history:
        for value in connector_data(page["result"]):
            messages = value.get("messages", [])
            if isinstance(messages, str):
                for block in re.split(r"(?=^=== Message from )", messages, flags=re.M):
                    ts = re.search(r"^Message TS: (\d+\.\d+)$", block, re.M)
                    count = re.search(r"^Thread: (\d+) replies", block, re.M)
                    if ts and count:
                        counts[ts.group(1)] = max(counts.get(ts.group(1), 0), int(count.group(1)))
            elif isinstance(messages, list):
                for message in messages:
                    if message.get("ts") and message.get("reply_count", 0):
                        counts[message["ts"]] = max(counts.get(message["ts"], 0), message["reply_count"])
    for thread in threads:
        returned = set()
        for page in thread["pages"]:
            for value in connector_data(page["result"]):
                messages = value.get("messages", [])
                if isinstance(messages, str):
                    returned.update(re.findall(r"^Message TS: (\d+\.\d+)$", messages, re.M))
                elif isinstance(messages, list):
                    returned.update(m["ts"] for m in messages if m.get("ts"))
        returned.discard(thread["ts"])
        if len(returned) < counts.get(thread["ts"], 0):
            raise ArchiveError("Thread contains fewer replies than channel history reported")


def ingest(root, batch):
    config = config_at(root)
    workspace = batch.get("workspace", {})
    if workspace.get("name") != config["workspace_name"]:
        raise ArchiveError("Workspace name does not match the configured source")
    if not config.get("workspace_id") or workspace.get("id") != config["workspace_id"]:
        raise ArchiveError("Connect and verify the configured Slack workspace first")
    captured = datetime.fromisoformat(batch["captured_at"])
    if captured.tzinfo is None:
        raise ArchiveError("captured_at must have an explicit timezone")
    day = captured.astimezone(KST).date().isoformat()
    channel = batch.get("channel", {})
    cid = channel.get("id", "")
    if not CHANNEL_ID.fullmatch(cid):
        raise ArchiveError("Invalid Slack channel ID")
    if channel.get("team_id") != workspace["id"]:
        raise ArchiveError("Channel membership must be verified for this workspace")
    if channel.get("is_im") or channel.get("is_mpim"):
        raise ArchiveError("Direct messages are outside this archive")
    if config["channel_scope"] == "public_channels":
        if channel.get("is_private") is not False:
            raise ArchiveError("Only verified public channels are authorized")
    elif cid not in config["channel_ids"]:
        raise ArchiveError("Channel is outside the configured allowlist")
    if batch.get("complete") is not True:
        raise ArchiveError("Incomplete capture cannot advance the checkpoint")
    history = batch.get("history", [])
    validate_pages(history, cid)
    threads = batch.get("threads", [])
    required = set(batch.get("thread_parents", [])) | seen_threads(history)
    supplied = {thread.get("ts") for thread in threads}
    if required != supplied:
        raise ArchiveError("Thread replies are missing or undeclared")
    for thread in threads:
        validate_pages(thread.get("pages"), cid, thread["ts"])
    validate_reply_counts(history, threads)

    # Validate the entire batch before writing anything or advancing progress.
    existing = {row["fingerprint"] for _, row in records(root)}
    additions = []
    units = [(None, page) for page in history]
    units += [(thread["ts"], page) for thread in threads for page in thread["pages"]]
    for thread_ts, page in units:
        fp = digest({"workspace_id": workspace["id"], "channel_id": cid,
                     "thread_ts": thread_ts, "tool": page["tool"], "result": page["result"]})
        if fp in existing:
            continue
        existing.add(fp)
        additions.append({"schema_version": 1, "fingerprint": fp,
                          "captured_at": batch["captured_at"], "workspace": workspace,
                          "channel": channel, "thread_ts": thread_ts,
                          "tool": page["tool"], "arguments": page["arguments"],
                          "result": page["result"]})
    target = root / f"slack/raw/{day}/{cid}.jsonl"
    if additions:
        target.parent.mkdir(parents=True, exist_ok=True)
        previous = target.read_text(encoding="utf-8") if target.exists() else ""
        temp = target.with_suffix(".jsonl.tmp")
        temp.write_text(previous + "".join(canonical(row) + "\n" for row in additions), encoding="utf-8")
        temp.replace(target)
    checkpoint = root / f"slack/state/channels/{cid}.json"
    # Identical successful rereads do not create commits just to change a timestamp.
    if additions or not checkpoint.exists():
        write_json(checkpoint, {"workspace_id": workspace["id"], "channel_id": cid,
                               "channel_name": channel.get("name"),
                               "last_changed_capture_at": batch["captured_at"],
                               "thread_parents": sorted(required), "complete": True})
    return {"channel_id": cid, "new_pages": len(additions), "complete": True}


def bind(root, workspace):
    config = config_at(root)
    if workspace.get("name") != config["workspace_name"]:
        raise ArchiveError("Workspace name does not match")
    if not re.fullmatch(r"T[A-Z0-9]+", workspace.get("id", "")):
        raise ArchiveError("Invalid workspace ID")
    if config.get("expected_workspace_id") and workspace["id"] != config["expected_workspace_id"]:
        raise ArchiveError("Workspace ID differs from the verified Slack browser URL")
    if config.get("workspace_id") not in (None, workspace["id"]):
        raise ArchiveError("A different workspace is already pinned")
    config["workspace_id"] = workspace["id"]
    config["connection_status"] = "WORKSPACE_VERIFIED"
    write_json(root / "slack/config.json", config)
    return {"workspace_id": workspace["id"], "workspace_verified": True}


def summary_plan(root):
    plans = []
    for raw_path in sorted((root / "slack/raw").glob("*/*.jsonl")):
        day, cid = raw_path.parent.name, raw_path.stem
        source_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()
        receipt = root / f"slack/state/summaries/{day}/{cid}.json"
        summary = root / f"slack/summaries/{day}/{cid}.md"
        if receipt.exists() and summary.exists():
            saved = load(receipt)
            if (saved.get("source_sha256") == source_hash and
                    saved.get("summary_sha256") == hashlib.sha256(summary.read_bytes()).hexdigest()):
                continue
        plans.append({"day": day, "channel_id": cid,
                      "source": raw_path.relative_to(root).as_posix(),
                      "source_sha256": source_hash,
                      "summary": f"slack/summaries/{day}/{cid}.md"})
    return plans


def save_summary(root, day, cid, text):
    if not DAY.fullmatch(day) or not CHANNEL_ID.fullmatch(cid):
        raise ArchiveError("Invalid summary date or channel")
    datetime.strptime(day, "%Y-%m-%d")
    source = root / f"slack/raw/{day}/{cid}.jsonl"
    if not source.exists():
        raise ArchiveError("Cannot summarize a missing raw source")
    required_link = f"../../raw/{day}/{cid}.jsonl"
    if required_link not in text or "## 수집 범위" not in text:
        raise ArchiveError("Summary must declare coverage and link the raw source")
    target = root / f"slack/summaries/{day}/{cid}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.rstrip() + "\n", encoding="utf-8")
    write_json(root / f"slack/state/summaries/{day}/{cid}.json",
               {"source": source.relative_to(root).as_posix(),
                "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "summary_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                "generator": "Codex in the scheduled chat; no separate API key"})
    return {"summary": target.relative_to(root).as_posix()}


ORGANIZATION_PREFIXES = ("meetings/slack/", "research/slack/", "proposals/slack/")


def raw_hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((root / "slack/raw").glob("*/*.jsonl"))}


def organization_document(root, name):
    if not isinstance(name, str) or "\\" in name:
        raise ArchiveError("Invalid classification path")
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or path.suffix != ".md":
        raise ArchiveError("Invalid classification path")
    if name != "slack/INDEX.md" and not name.startswith(ORGANIZATION_PREFIXES):
        raise ArchiveError("Classification is outside repository categories")
    target = (root / path).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ArchiveError("Classification path leaves the checkout")
    return target


def organization_plan(root):
    sources = raw_hashes(root)
    if not sources:
        return {"needed": False, "sources": {}, "documents": []}
    receipt_path = root / "slack/state/organization.json"
    previous = load(receipt_path) if receipt_path.exists() else {}
    documents = previous.get("documents", {})
    needed = previous.get("sources") != sources or not documents
    for name, saved_hash in documents.items():
        path = organization_document(root, name)
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != saved_hash:
            needed = True
    return {"needed": needed, "sources": sources, "documents": sorted(documents)}


def save_organization(root, manifest):
    sources = raw_hashes(root)
    if not sources or manifest.get("sources") != sources:
        raise ArchiveError("Classification source snapshot is missing or stale")
    documents = manifest.get("documents")
    if not isinstance(documents, list) or "slack/INDEX.md" not in documents:
        raise ArchiveError("Classification requires the source navigation index")
    if len(documents) != len(set(documents)):
        raise ArchiveError("Duplicate classification documents")
    hashes, linked = {}, set()
    for name in documents:
        path = organization_document(root, name)
        text = path.read_text(encoding="utf-8")
        if "## 수집 범위" not in text:
            raise ArchiveError("Classification must declare source coverage")
        local_sources = set()
        for link in re.findall(r"\]\(([^)]+)\)", text):
            link = unquote(link.strip("<>").split("#", 1)[0])
            if ":" in link or not link:
                continue
            target = (path.parent / link).resolve()
            if target.is_relative_to(root.resolve()):
                relative = target.relative_to(root.resolve()).as_posix()
                if relative.startswith("slack/raw/"):
                    if relative not in sources:
                        raise ArchiveError("Classification links a missing raw source")
                    local_sources.add(relative)
        if not local_sources:
            raise ArchiveError("Classification must link an archived raw source")
        linked.update(local_sources)
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    if linked != set(sources):
        raise ArchiveError("Classification index does not cover all archived channels and days")
    write_json(root / "slack/state/organization.json", {
        "schema_version": 1, "sources": sources, "documents": hashes,
        "generator": "Codex in the scheduled chat; no separate API key"})
    return {"documents": sorted(hashes), "source_files": len(sources)}


def status(root):
    config = config_at(root)
    rows = list(records(root))
    return {"workspace_name": config["workspace_name"],
            "workspace_verified": bool(config.get("workspace_id")),
            "connection_status": config["connection_status"],
            "archived_native_pages": len(rows),
            "archived_channels": sorted({row["channel"]["id"] for _, row in rows}),
            "pending_summaries": len(summary_plan(root)),
            "pending_organization": organization_plan(root)["needed"],
            "live_collection_confirmed": bool(rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("summary-plan")
    sub.add_parser("organization-plan")
    organizer = sub.add_parser("save-organization")
    organizer.add_argument("--manifest", required=True, type=Path)
    binder = sub.add_parser("bind-workspace")
    binder.add_argument("--source", required=True, type=Path)
    collector = sub.add_parser("ingest")
    collector.add_argument("--batch", required=True, type=Path)
    summary = sub.add_parser("save-summary")
    summary.add_argument("--day", required=True)
    summary.add_argument("--channel", required=True)
    summary.add_argument("--text-file", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "status":
            result = status(args.root)
        elif args.command == "summary-plan":
            result = summary_plan(args.root)
        elif args.command == "organization-plan":
            result = organization_plan(args.root)
        elif args.command == "save-organization":
            result = save_organization(args.root, load(args.manifest))
        elif args.command == "bind-workspace":
            result = bind(args.root, load(args.source))
        elif args.command == "ingest":
            result = ingest(args.root, load(args.batch))
        else:
            result = save_summary(args.root, args.day, args.channel,
                                  args.text_file.read_text(encoding="utf-8-sig"))
        print(json.dumps(result, ensure_ascii=True))
    except (ArchiveError, OSError, ValueError, KeyError) as exc:
        # Do not echo raw payloads or credential-bearing contents on errors.
        print(f"Archive failed: {type(exc).__name__}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
