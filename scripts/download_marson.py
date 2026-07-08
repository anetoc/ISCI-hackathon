#!/usr/bin/env python3
"""Resumable unsigned S3 downloader for Marson Perturb-seq files -> data/marson/."""
import os, sys, urllib.request, time, hashlib

BUCKET = "genome-scale-tcell-perturb-seq"
BASE = f"https://{BUCKET}.s3.amazonaws.com"
KEY = "marson2025_data/GWCD4i.DE_stats.h5ad"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "marson", "GWCD4i.DE_stats.h5ad")
OUT = os.path.abspath(OUT)

def head_size(url):
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as r:
        return int(r.headers["Content-Length"])

def main():
    url = f"{BASE}/{KEY}"
    total = head_size(url)
    have = os.path.getsize(OUT) if os.path.exists(OUT) else 0
    if have >= total:
        print(f"COMPLETE already: {have/1e9:.2f} GB", flush=True)
        return
    print(f"Resuming from {have/1e9:.2f} / {total/1e9:.2f} GB", flush=True)
    req = urllib.request.Request(url, headers={"Range": f"bytes={have}-"})
    t0 = time.time(); last = t0; got = have
    with urllib.request.urlopen(req, timeout=120) as r, open(OUT, "ab") as f:
        while True:
            chunk = r.read(8 * 1024 * 1024)
            if not chunk:
                break
            f.write(chunk); got += len(chunk)
            now = time.time()
            if now - last > 20:
                rate = (got - have) / (now - t0) / 1e6
                print(f"  {got/1e9:6.2f}/{total/1e9:.2f} GB  {100*got/total:5.1f}%  {rate:5.1f} MB/s  eta {int((total-got)/max(rate*1e6,1))}s", flush=True)
                last = now
    final = os.path.getsize(OUT)
    print(f"DONE: {final/1e9:.2f} GB {'OK' if final>=total else 'INCOMPLETE'}", flush=True)

if __name__ == "__main__":
    main()
