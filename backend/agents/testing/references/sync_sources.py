"""Download attributable source snapshots. No network is used during generation.

Run: python -m agents.testing.references.sync_sources
Unavailable pages remain explicit failures; they are never indexed as documents.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent


def extract_text(data: bytes, source: dict) -> str:
    if source.get("format") == "pdf":
        from pypdf import PdfReader
        text = "\n\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(data)).pages)
    elif b"<html" in data[:5000].lower() or b"<!doctype" in data[:5000].lower():
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(data, "html.parser")
        main = (soup.select_one("article") or soup.select_one("[role=main]")
                or soup.select_one("main") or soup.select_one("#wiki-body"))
        if main is None and source["id"] == "gnucobol":
            # The older official guide predates semantic HTML main/article elements.
            main = soup.body
        if main is None:
            raise ValueError("No document body found; refusing to index navigation or an app shell")
        for node in main.select("script,style,nav,header,footer,.sidebar,.related"):
            node.decompose()
        # Preserve code lines; HTML syntax highlighting wraps individual tokens in spans.
        # A newline separator on every text node corrupts those examples.
        for pre in main.find_all("pre"):
            pre.replace_with("\n\n" + pre.get_text("", strip=False) + "\n\n")
        for br in main.find_all("br"):
            br.replace_with("\n")
        for block in main.find_all(["p", "li", "h1", "h2", "h3", "h4", "tr", "dt", "dd"]):
            block.append("\n")
        text = main.get_text("", strip=False)
        text = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", text)
    else:
        text = data.decode("utf-8")
    if len(text.strip()) < 600:
        raise ValueError("Document body too short; may be a blocked page")
    return text.strip()


def sync_one(source: dict) -> dict:
    try:
        request = Request(source.get("download_url", source["url"]),
                          headers={"User-Agent": "LegacyCoder-reference-ingestion/1.0"})
        with urlopen(request, timeout=40) as response:
            data = response.read(20_000_001)
        if len(data) > 20_000_000:
            raise ValueError("Document exceeds 20 MB ingestion limit")
        text = extract_text(data, source)
        suffix = ".pdf" if source.get("format") == "pdf" else ".html" if b"<html" in data[:5000].lower() else ".txt"
        raw_path = ROOT / "raw" / (source["id"] + suffix)
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(data)
        record = dict(source, retrieved_at=datetime.now(timezone.utc).isoformat(),
                      sha256=hashlib.sha256(data).hexdigest(), text=text,
                      content_kind="downloaded_source", raw_file=str(raw_path.relative_to(ROOT)).replace("\\", "/"))
        path = ROOT / "snapshots" / (source["id"] + ".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"id": source["id"], "status": "downloaded", "characters": len(text)}
    except Exception as exc:
        return {"id": source["id"], "status": "failed", "error": str(exc)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args()
    sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    if args.only:
        sources = [s for s in sources if s["id"] in args.only]
    with ThreadPoolExecutor(max_workers=5) as pool:
        report = list(pool.map(sync_one, sources))
    report_path = ROOT / "sync_report.json"
    previous = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else []
    merged = {row["id"]: row for row in previous}
    merged.update({row["id"]: row for row in report})
    report_path.write_text(json.dumps(list(merged.values()), indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if any(row["status"] == "failed" for row in report):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
