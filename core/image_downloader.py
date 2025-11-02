#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
image_downloader.py — Download Pokemon card images from TCGdex API

Provides a clean interface for downloading card sets with progress tracking.
"""
import os
import re
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote
import requests
from typing import Callable, Optional, Tuple

try:
    from .utils import safe_print
except ImportError:
    from utils import safe_print

API_BASE = "https://api.tcgdex.net/v2"

# Popular sets for quick access
POPULAR_SETS = [
    ("Surging Sparks", "sv08"),
    ("Stellar Crown", "sv07"),
    ("Shrouded Fable", "sv06.5"),
    ("Twilight Masquerade", "sv06"),
    ("Temporal Forces", "sv05"),
    ("Paldean Fates", "sv04.5"),
    ("Paradox Rift", "sv04"),
    ("Obsidian Flames", "sv03"),
    ("Paldea Evolved", "sv02"),
    ("Scarlet & Violet", "sv01"),
    ("Crown Zenith", "swsh12.5"),
    ("Silver Tempest", "swsh12"),
    ("Lost Origin", "swsh11"),
    ("Astral Radiance", "swsh10"),
    ("Brilliant Stars", "swsh9"),
    ("Fusion Strike", "swsh8"),
    ("Evolving Skies", "swsh7"),
    ("Chilling Reign", "swsh6"),
    ("Battle Styles", "swsh5"),
]

LANGUAGES = {
    "English": "en",
    "Français": "fr",
    "Deutsch": "de",
    "Italiano": "it",
    "Español": "es",
    "Português": "pt",
    "日本語": "ja",
    "한국어": "ko",
    "中文": "zh",
    "ไทย": "th",
}


def sanitize_filename(name: str) -> str:
    """Sanitize filename to be filesystem-safe"""
    return re.sub(r'[^A-Za-z0-9 \-_.]+', '_', name).strip().strip('.')


def backoff_sleep(attempt: int):
    """Exponential backoff for retries"""
    time.sleep(min(1.0 * (2 ** attempt), 10.0))


class ImageDownloader:
    """Download Pokemon card images from TCGdex"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        Initialize downloader.
        
        Args:
            progress_callback: Optional callback(message: str, current: int, total: int)
        """
        self.session = requests.Session()
        self.progress_callback = progress_callback
    
    def _log(self, message: str, current: int = 0, total: int = 0):
        """Log message via callback or print"""
        if self.progress_callback:
            self.progress_callback(message, current, total)
        else:
            safe_print(message)
    
    def _http_get(self, url: str, timeout: int = 20) -> requests.Response:
        """HTTP GET with retry logic"""
        attempts = 0
        while True:
            try:
                r = self.session.get(url, timeout=timeout)
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
    
    def resolve_set(self, set_query: str, lang: str = "en") -> dict:
        """
        Resolve set name or ID to full set data.
        
        Args:
            set_query: Set name (e.g., "Surging Sparks") or ID (e.g., "sv08")
            lang: Language code
        
        Returns:
            Set data dictionary
        
        Raises:
            Exception: If set not found
        """
        # Try direct ID lookup first
        if re.fullmatch(r'[A-Za-z0-9.]+', set_query):
            url = f"{API_BASE}/{lang}/sets/{quote(set_query)}"
            try:
                r = self._http_get(url)
                return r.json()
            except Exception:
                pass
        
        # Try exact name match
        url_eq = f"{API_BASE}/{lang}/sets?name=eq:{quote(set_query)}"
        r = self._http_get(url_eq)
        arr = r.json()
        
        if isinstance(arr, list) and arr:
            for s in arr:
                if s.get('name', '').lower() == set_query.lower():
                    sid = s.get('id')
                    if sid:
                        r2 = self._http_get(f"{API_BASE}/{lang}/sets/{quote(sid)}")
                        return r2.json()
        
        # Fallback: fuzzy search
        url_like = f"{API_BASE}/{lang}/sets?name={quote(set_query)}"
        r = self._http_get(url_like)
        arr = r.json()
        
        if not isinstance(arr, list) or not arr:
            raise Exception(f"No set found for: {set_query}")
        
        # Prefer exact match
        best = None
        for s in arr:
            if s.get('name', '').lower() == set_query.lower():
                best = s
                break
        
        if best is None:
            best = arr[0]
        
        sid = best.get('id')
        if not sid:
            raise Exception("Set found but has no usable ID")
        
        r2 = self._http_get(f"{API_BASE}/{lang}/sets/{quote(sid)}")
        return r2.json()
    
    def _build_image_url(self, base_url: str, quality: str, ext: str) -> str:
        """Build full image URL from base"""
        base_url = base_url.rstrip('/')
        return f"{base_url}/{quality}.{ext}"
    
    def _download_image(self, url: str, out_path: Path) -> bool:
        """Download single image with retry logic"""
        attempts = 0
        while True:
            try:
                r = self.session.get(url, timeout=30, stream=True)
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
            
            # Write file
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
            return True
    
    def download_set(
        self,
        set_query: str,
        output_dir: str = "images",
        lang: str = "en",
        quality: str = "high",
        ext: str = "png",
        workers: int = 8
    ) -> Tuple[int, int, int]:
        """
        Download all cards from a set.
        
        Args:
            set_query: Set name or ID
            output_dir: Output directory path
            lang: Language code (en, fr, de, etc.)
            quality: Image quality (high, low)
            ext: Image extension (png, jpg, webp)
            workers: Number of parallel downloads
        
        Returns:
            Tuple (success_count, fail_count, total_count)
        """
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Resolve set
        self._log(f"🔍 Resolving set '{set_query}' (language: {lang})...", 0, 0)
        
        try:
            set_obj = self.resolve_set(set_query, lang)
        except Exception as e:
            self._log(f"❌ Error: {e}", 0, 0)
            return 0, 0, 0
        
        set_id = set_obj.get("id")
        set_name = set_obj.get("name")
        cards = set_obj.get("cards") or []
        
        if not cards:
            self._log("⚠️ No cards found for this set", 0, 0)
            return 0, 0, 0
        
        total = len(cards)
        self._log(f"✅ Found: {set_name} (ID: {set_id}) — {total} cards", 0, total)
        
        # Prepare download jobs
        jobs = []
        for card in cards:
            base = card.get("image")
            if not base:
                continue
            
            local_id = str(card.get("localId", "000"))
            card_id = card.get("id", "unknown")
            name = card.get("name", "Unknown")
            
            url = self._build_image_url(base, quality, ext)
            safe_name = sanitize_filename(name)
            filename = f"{local_id.zfill(3)} - {safe_name} ({card_id}).{ext}"
            out_path = out_dir / filename
            
            jobs.append((url, out_path, card_id, local_id, name))
        
        # Download with thread pool
        success = 0
        failed = 0
        
        def worker(job):
            url, out_path, card_id, local_id, name = job
            # Skip if already exists
            if out_path.exists():
                return True, out_path, name
            result = self._download_image(url, out_path)
            return result, out_path, name
        
        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            futures = [executor.submit(worker, job) for job in jobs]
            
            for i, future in enumerate(as_completed(futures), 1):
                result, out_path, name = future.result()
                
                if result:
                    success += 1
                    self._log(f"✅ [{i}/{total}] {out_path.name}", i, total)
                else:
                    failed += 1
                    self._log(f"❌ [{i}/{total}] Failed: {name}", i, total)
        
        # Create manifest CSV
        manifest_path = out_dir / "manifest.csv"
        try:
            import csv
            with open(manifest_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "localId", "name", "file", "source_url"])
                for url, out_path, card_id, local_id, name in jobs:
                    writer.writerow([card_id, local_id, name, str(out_path), url])
        except Exception as e:
            self._log(f"⚠️ Could not create manifest: {e}", total, total)
        
        self._log(
            f"🎉 Complete! Success: {success}, Failed: {failed}, Total: {total}",
            total,
            total
        )
        
        return success, failed, total


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download Pokemon card images from TCGdex"
    )
    parser.add_argument(
        "--set",
        required=True,
        help="Set name (e.g., 'Surging Sparks') or ID (e.g., 'sv08')"
    )
    parser.add_argument(
        "--output",
        default="images",
        help="Output directory (default: images)"
    )
    parser.add_argument(
        "--lang",
        default="en",
        choices=list(LANGUAGES.values()),
        help="Language code (default: en)"
    )
    parser.add_argument(
        "--quality",
        default="high",
        choices=["high", "low"],
        help="Image quality (default: high)"
    )
    parser.add_argument(
        "--ext",
        default="png",
        choices=["png", "jpg", "webp"],
        help="Image extension (default: png)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Parallel downloads (default: 8)"
    )
    
    args = parser.parse_args()
    
    downloader = ImageDownloader()
    success, failed, total = downloader.download_set(
        set_query=args.set,
        output_dir=args.output,
        lang=args.lang,
        quality=args.quality,
        ext=args.ext,
        workers=args.workers
    )
    
    print(f"\nDownload complete: {success} succeeded, {failed} failed, {total} total")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
