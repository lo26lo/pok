#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tcgdex_images_dl.py — Download all card images for a given set (by *name* or *id*) from TCGdex.

Usage examples:
  python tcgdex_images_dl.py --set "Surging Sparks"                # resolve by name (EN), high .jpg
  python tcgdex_images_dl.py --set sv08                            # resolve by id directly
  python tcgdex_images_dl.py --set "151" --lang en --ext png       # png output
  python tcgdex_images_dl.py --set "Obsidian Flames" --quality low # low quality
  python tcgdex_images_dl.py --set sv08 --out image_sv08 --lang fr # French asset path
"""
import os, csv, re, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote
import requests

API_BASE = "https://api.tcgdex.net/v2"
ASSET_TIP = "See https://tcgdex.dev/assets for image extensions (png/webp/jpg) and qualities (high/low)"

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^A-Za-z0-9 \\-_.]+', '_', name).strip().strip('.')

def backoff_sleep(attempt: int):
    time.sleep(min(1.0 * (2 ** attempt), 10.0))

def http_get(session: requests.Session, url: str, timeout=20):
    attempts = 0
    while True:
        try:
            r = session.get(url, timeout=timeout)
        except requests.RequestException:
            if attempts >= 4:
                raise
            attempts += 1
            backoff_sleep(attempts)
            continue
        if r.status_code in (429, 500, 502, 503, 504):
            if attempts >= 4:
                r.raise_for_status()
            attempts += 1
            retry_after = r.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                time.sleep(int(retry_after))
            else:
                backoff_sleep(attempts)
            continue
        r.raise_for_status()
        return r

def resolve_set(lang: str, set_query: str):
    session = requests.Session()
    # Try direct id first (letters/numbers and dot allowed)
    import re as _re
    if _re.fullmatch(r'[A-Za-z0-9.]+', set_query):
        url = f"{API_BASE}/{lang}/sets/{quote(set_query)}"
        try:
            r = http_get(session, url)
            return r.json()
        except Exception:
            pass
    # Try strict equality
    url_eq = f"{API_BASE}/{lang}/sets?name=eq:{quote(set_query)}"
    r = http_get(session, url_eq)
    arr = r.json()
    if isinstance(arr, list) and arr:
        for s in arr:
            if s.get('name','').lower() == set_query.lower():
                sid = s.get('id')
                if sid:
                    r2 = http_get(session, f"{API_BASE}/{lang}/sets/{quote(sid)}")
                    return r2.json()
    # Fallback laxist
    url_like = f"{API_BASE}/{lang}/sets?name={quote(set_query)}"
    r = http_get(session, url_like)
    arr = r.json()
    if not isinstance(arr, list) or not arr:
        raise SystemExit(f"Aucun set trouvé pour: {set_query}")
    best = None
    for s in arr:
        if s.get('name','').lower() == set_query.lower():
            best = s; break
    if best is None:
        best = arr[0]
    sid = best.get('id')
    if not sid:
        raise SystemExit("Set trouvé mais sans id utilisable.")
    r2 = http_get(session, f"{API_BASE}/{lang}/sets/{quote(sid)}")
    return r2.json()

def build_card_url(base_url: str, quality: str, ext: str) -> str:
    base_url = base_url.rstrip('/')
    return f"{base_url}/{quality}.{ext}"

def download_one(session, url, out_path):
    attempts = 0
    while True:
        try:
            r = session.get(url, timeout=30, stream=True)
        except requests.RequestException:
            if attempts >= 3:
                return False
            attempts += 1
            backoff_sleep(attempts)
            continue
        if r.status_code == 404:
            return False
        if r.status_code in (429, 500, 502, 503, 504):
            if attempts >= 3:
                return False
            attempts += 1
            retry_after = r.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                time.sleep(int(retry_after))
            else:
                backoff_sleep(attempts)
            continue
        if r.status_code != 200:
            return False
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1<<16):
                if chunk:
                    f.write(chunk)
        return True

def run(set_query: str, lang: str="en", out_dir="images", ext="png", quality="high", workers=8, progress_callback=None):
    """
    Download TCGdex set images.
    
    Args:
        set_query: Set name or ID
        lang: Language code (en, fr, de, etc.)
        out_dir: Output directory
        ext: Image extension (jpg, png, webp)
        quality: Image quality (high, low)
        workers: Number of parallel downloads
        progress_callback: Optional callback(message, current, total)
    
    Returns:
        Tuple (success_count, fail_count, total_count)
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.csv"

    if progress_callback:
        progress_callback(f"Resolving set '{set_query}' in lang '{lang}' ...", 0, 0)
    
    set_obj = resolve_set(lang, set_query)
    sid = set_obj.get("id")
    sname = set_obj.get("name")
    cards = set_obj.get("cards") or []
    
    if not cards:
        if progress_callback:
            progress_callback("No cards found for this set.", 0, 0)
        return 0, 0, 0
    
    total = len(cards)
    if progress_callback:
        progress_callback(f"Found set: {sname} (id={sid}) — {total} cards", 0, total)

    session = requests.Session()
    jobs = []
    for c in cards:
        base = c.get("image")
        localId = str(c.get("localId"))
        cid = c.get("id")
        name = c.get("name","")
        if not base:
            continue
        url = build_card_url(base, quality, ext)
        # New format: {set_id}_{local_id}_{lang}.{ext}
        fname = f"{sid}_{localId}_{lang}.{ext}"
        out_path = out_dir / fname
        jobs.append((url, out_path, cid, localId, name))

    ok, fail = 0, 0
    rows = []

    def worker(job):
        url, out_path, cid, localId, name = job
        if out_path.exists():
            return True, url, out_path, cid, localId, name
        res = download_one(session, url, out_path)
        return res, url, out_path, cid, localId, name

    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futures = [ex.submit(worker, j) for j in jobs]
        for i, fut in enumerate(as_completed(futures), 1):
            res, url, out_path, cid, localId, name = fut.result()
            rows.append((cid, localId, name, str(out_path), url))
            if res:
                ok += 1
                if progress_callback:
                    progress_callback(f"[OK] {out_path.name}", ok + fail, total)
            else:
                fail += 1
                if progress_callback:
                    progress_callback(f"[FAIL] {out_path.name}", ok + fail, total)

    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        import csv as _csv
        w = _csv.writer(f)
        w.writerow(["id","localId","name","file","source_url"])
        w.writerows(rows)

    if progress_callback:
        progress_callback(f"Done. Downloaded: {ok}, Failed: {fail}. Manifest: {manifest_path}", total, total)
    
    return ok, fail, total

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Download TCGdex set images into a folder.")
    ap.add_argument("--set", required=True, help="Set name (e.g., 'Surging Sparks') or set id (e.g., sv08)")
    ap.add_argument("--lang", default="en", help="Assets language path (en, fr, de, it, es, pt...). Default: en")
    ap.add_argument("--ext", default="png", choices=["jpg","png","webp"], help="Image extension. Default: png")
    ap.add_argument("--quality", default="high", choices=["high","low"], help="Image quality. Default: high")
    ap.add_argument("--out", default="images", help="Output directory. Default: ./images")
    ap.add_argument("--workers", type=int, default=8, help="Parallel downloads. Default: 8")
    args = ap.parse_args()
    ok, fail, total = run(args.set, args.lang, args.out, args.ext, args.quality, args.workers)
    print(f"Done. Downloaded: {ok}, Failed: {fail}, Total: {total}")
