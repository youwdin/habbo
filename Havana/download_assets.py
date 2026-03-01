#!/usr/bin/env python3
"""
Downloads missing furniture SWF and icon files from habbofurni.com API.
Uses curl under the hood (bypasses any Python TLS/header issues).
"""

import os
import json
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

API_TOKEN = "322|Cf92rA2mkRARFuJAsIVfzvfCqMapZig3YcyeoIWh6577182b"
BASE_URL  = "https://habbofurni.com/api/v1"
PER_PAGE  = 100

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SWF_DIR    = os.path.join(SCRIPT_DIR, "tools", "www", "dcr", "hof_furni")
ICON_DIR   = os.path.join(SCRIPT_DIR, "tools", "www", "c_images", "catalogue")

os.makedirs(SWF_DIR,  exist_ok=True)
os.makedirs(ICON_DIR, exist_ok=True)

CURL_HEADERS = [
    "-H", f"Authorization: Bearer {API_TOKEN}",
    "-H", "X-Hotel-ID: 1",
    "-H", "Accept: application/json",
]

def api_get(path):
    url = f"{BASE_URL}{path}"
    result = subprocess.run(
        ["curl", "-s", "--max-time", "20"] + CURL_HEADERS + [url],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

def download_file(url, dest):
    if os.path.exists(dest):
        return "skip"
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "30", "-o", dest, url],
            capture_output=True
        )
        if result.returncode != 0:
            return f"err:curl_exit_{result.returncode}"
        if os.path.exists(dest) and os.path.getsize(dest) < 50:
            os.remove(dest)
            return "empty"
        return "ok"
    except Exception as e:
        return f"err:{e}"

def collect_all_furniture():
    print("Fetching furniture list from API …")
    first     = api_get(f"/furniture?per_page={PER_PAGE}&page=1")
    total     = first["meta"]["total"]
    last_page = first["meta"]["last_page"]
    print(f"  Total items : {total:,}")
    print(f"  Total pages : {last_page:,}")

    items = first["data"]
    for page in range(2, last_page + 1):
        try:
            data = api_get(f"/furniture?per_page={PER_PAGE}&page={page}")
            items.extend(data["data"])
        except Exception as e:
            print(f"  [warn] page {page} failed: {e}")
        if page % 20 == 0:
            print(f"  … fetched page {page}/{last_page}  ({len(items):,} items so far)")
        time.sleep(0.05)

    print(f"  Collected {len(items):,} items total\n")
    return items

def build_task_list(items):
    tasks = []
    for item in items:
        hd        = item.get("hotelData") or {}
        classname = (hd.get("classname") or item.get("classname", "")).replace("*", "_")
        if not classname:
            continue

        swf_info  = hd.get("swf")  or {}
        icon_info = hd.get("icon") or {}

        if swf_info.get("exists") and swf_info.get("url"):
            dest = os.path.join(SWF_DIR, f"{classname}.swf")
            tasks.append((swf_info["url"], dest, "swf", classname))

        if icon_info.get("exists") and icon_info.get("url"):
            dest = os.path.join(ICON_DIR, f"{classname}_icon.png")
            tasks.append((icon_info["url"], dest, "icon", classname))

    return tasks

def run_downloads(tasks, workers=10):
    total   = len(tasks)
    done    = 0
    skipped = 0
    ok      = 0
    errors  = 0

    print(f"Downloading {total:,} files with {workers} workers …\n")

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {
            ex.submit(download_file, url, dest): (kind, classname)
            for url, dest, kind, classname in tasks
        }
        for future in as_completed(futures):
            kind, classname = futures[future]
            result = future.result()
            done += 1

            if result == "skip":
                skipped += 1
            elif result == "ok":
                ok += 1
            else:
                errors += 1
                if result != "empty":
                    print(f"  [error] {kind:4}  {classname}  →  {result}")

            if done % 1000 == 0 or done == total:
                pct = done / total * 100
                print(f"  [{pct:5.1f}%] {done:,}/{total:,}  new={ok:,}  skip={skipped:,}  err={errors}")

    print(f"\n✓ Finished!  new={ok:,}  already had={skipped:,}  errors={errors}")

if __name__ == "__main__":
    items = collect_all_furniture()
    tasks = build_task_list(items)
    run_downloads(tasks, workers=10)
