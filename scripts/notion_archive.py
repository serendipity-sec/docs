"""Validate and archive a Notion UI Markdown & CSV export, without executing it."""

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import stat
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote, urlsplit

ROOT_ID = "096c2d6e1537828d8e3a810d9a8976ac"
ROOT_URL = f"https://app.notion.com/p/{ROOT_ID}"
MAX_BYTES = 250 * 1024 * 1024
ID = re.compile(r"([0-9a-f]{32})(?:_all)?\.(md|csv)$")
LINK = re.compile(r"\]\(((?:[^()\n]|\([^()\n]*\))*)\)")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_changed(path, data):
    if path.is_symlink():
        raise ValueError(f"Refusing symlink: {path}")
    if path.exists() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True


def load_export(archive):
    with zipfile.ZipFile(archive) as z:
        infos = [item for item in z.infolist() if not item.is_dir()]
        if len(infos) > 20000 or sum(i.file_size for i in infos) > MAX_BYTES:
            raise ValueError("Export exceeds archive limits")
        data = {}
        seen = set()
        for item in infos:
            name = item.filename
            path = PurePosixPath(name)
            if (path.is_absolute() or ".." in path.parts or "\\" in name
                    or ":" in name or name.casefold() in seen
                    or any(part.endswith((".", " ")) for part in path.parts)
                    or stat.S_ISLNK(item.external_attr >> 16)):
                raise ValueError(f"Unsafe or duplicate export path: {name}")
            seen.add(name.casefold())
            data[name] = z.read(item)
    roots = [name for name in data if name.endswith(f" {ROOT_ID}.md")]
    if len(roots) != 1:
        raise ValueError("Expected exactly one authorized team root page")
    root = PurePosixPath(roots[0])
    child_prefix = str(root.parent / root.name.removesuffix(f" {ROOT_ID}.md")) + "/"
    if any(name != str(root) and not name.startswith(child_prefix) for name in data):
        raise ValueError("Export contains content outside the authorized root")
    return data, str(root)


def summarize(data):
    files, missing = [], []
    for name, raw in sorted(data.items()):
        path = PurePosixPath(name)
        match = ID.search(path.name)
        entry = {"path": name, "sha256": digest(raw), "bytes": len(raw)}
        if match:
            entry["notion_id"] = match.group(1)
            entry["notion_url"] = f"https://app.notion.com/p/{match.group(1)}"
        if path.suffix == ".csv":
            rows = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"))))
            entry["columns"] = rows[0] if rows else []
            entry["row_count"] = max(0, len(rows) - 1)
        if path.suffix == ".md":
            content = raw.decode("utf-8-sig")
            entry["title"] = next((line[2:] for line in content.splitlines()
                                   if line.startswith("# ")), path.stem)
            for found in LINK.finditer(content):
                target = found.group(1)
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path or target.startswith("#"):
                    continue
                parts = list(path.parent.parts)
                for part in PurePosixPath(unquote(url.path)).parts:
                    if part == "..":
                        if parts:
                            parts.pop()
                    elif part != ".":
                        parts.append(part)
                resolved = "/".join(parts)
                if resolved not in data:
                    missing.append({"source": name, "target": target,
                                    "resolved_export_path": resolved})
        files.append(entry)
    return files, missing


def ingest(archive, repo):
    data, root = load_export(archive)
    files, missing = summarize(data)
    dest = repo / "notion" / "export"
    if dest.is_symlink() or (repo / "notion").is_symlink():
        raise ValueError("Archive destination must not be a symlink")
    base = dest.resolve()
    # Validate all destinations before writing any exported content.
    for name in data:
        target = dest / name
        if not target.resolve().is_relative_to(base) or target.is_symlink():
            raise ValueError("Archive destination escapes notion/export")
    prior_path = repo / "notion" / "manifest.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8")) if prior_path.exists() else {}
    old_paths = {f["path"] for f in prior.get("files", [])}
    old_paths.update(prior.get("retained_not_in_latest_export", []))
    retained = sorted(old_paths - data.keys())
    pages = [f for f in files if f["path"].endswith(".md") and "notion_id" in f]
    databases = [f for f in files if f["path"].endswith(".csv") and not f["path"].endswith("_all.csv")]
    manifest = {
        "schema_version": 1, "root_id": ROOT_ID, "root_url": ROOT_URL,
        "collection_method": "notion_browser_markdown_csv_export",
        "export_options": {"database_view": "default", "content": "all",
                           "include_subpages": True, "create_subpage_folders": True},
        "content_fingerprint": digest(json_bytes(files)),
        "counts": {"files": len(files), "notion_pages": len(pages),
                   "databases": len(databases), "csv_files": sum(f["path"].endswith(".csv") for f in files),
                   "attachments": len(files) - len(pages) - sum(f["path"].endswith(".csv") for f in files)},
        "coverage": "export_contents_verified; known_export_limitations_apply",
        "missing_local_links": missing,
        "retained_not_in_latest_export": retained,
        "files": files,
    }
    changed = sum(write_changed(dest / name, raw) for name, raw in data.items())
    changed += write_changed(prior_path, json_bytes(manifest))
    lines = ["# 팀 Notion 원문", "", f"[Notion 원본]({ROOT_URL}) · [수집 절차](RUNBOOK.md) · [검증 범위](verification.md)", "",
             "브라우저의 공식 Markdown & CSV 내보내기를 저장합니다. 원본 파일의 바이트와 폴더 구조를 보존합니다.", "",
             f"- 파일 {len(files)}개 / Notion 페이지 {len(pages)}개 / 데이터베이스 {len(databases)}개",
             f"- 내보내기에 없는 로컬 링크 {len(missing)}개. 댓글·보기 설정·페이지 권한은 완전 백업 범위가 아닙니다.", "",
             f"[팀 홈 사본](export/{quote(root, safe='/')})", "", "## 페이지", "",
             "| 경로와 제목 | 원본 |", "|---|---|"]
    for f in pages:
        label = f["path"].replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")
        lines.append(f"| [{label}](export/{quote(f['path'], safe='/')}) | [Notion]({f['notion_url']}) |")
    lines += ["", "## 데이터베이스", "", "| 파일 | 행 수 |", "|---|---|"]
    for f in databases:
        label = PurePosixPath(f["path"]).name.replace("|", "\\|")
        lines.append(f"| [{label}](export/{quote(f['path'], safe='/')}) | {f['row_count']} |")
    lines += ["", "## 내보내기에 없는 링크", ""]
    lines.extend(f"- `{m['resolved_export_path']}`" for m in missing)
    if retained:
        lines += ["", "## 이번 내보내기에 없어 이전 사본을 보존한 파일", ""]
        lines.extend(f"- `{name}`" for name in retained)
    changed += write_changed(repo / "notion" / "INDEX.md", ("\n".join(lines) + "\n").encode("utf-8"))
    runtime = repo / ".runtime" / "notion-sync"
    runtime.mkdir(parents=True, exist_ok=True)
    archive_hash = digest(archive.read_bytes())
    preserved = runtime / f"{archive_hash}.zip"
    if not preserved.exists():
        shutil.copyfile(archive, preserved)
    record = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "archive_sha256": archive_hash,
              "content_fingerprint": manifest["content_fingerprint"], "changed_files": changed,
              "counts": manifest["counts"], "missing_local_links": len(missing)}
    (runtime / "last-run.json").write_bytes(json_bytes(record))
    return record


def verify(repo):
    manifest = json.loads((repo / "notion" / "manifest.json").read_text(encoding="utf-8"))
    errors = []
    for f in manifest["files"]:
        path = repo / "notion" / "export" / f["path"]
        if not path.is_file() or digest(path.read_bytes()) != f["sha256"]:
            errors.append(f["path"])
    result = {"verified_files": len(manifest["files"]) - len(errors), "errors": errors,
              "missing_local_links": len(manifest["missing_local_links"]), "counts": manifest["counts"]}
    if errors:
        raise ValueError(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["ingest", "verify"])
    parser.add_argument("--zip", type=Path)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    if args.action == "ingest" and not args.zip:
        parser.error("ingest requires --zip")
    result = ingest(args.zip, args.repo.resolve()) if args.action == "ingest" else verify(args.repo.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
