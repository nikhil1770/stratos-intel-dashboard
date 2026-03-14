"""
test_mastodon_stream.py
-----------------------
Verification script — connects to the Mastodon public federated timeline
and prints the first 5 incoming posts as structured JSON.

Method: Uses the anonymous REST endpoint GET /api/v1/timelines/public,
which works without authentication on any Mastodon instance.

Note: WebSocket streaming (stream_public) requires an access token on
most major instances (e.g. mastodon.social) as of 2025+. The REST
approach is the correct anonymous verification method.

Usage
-----
    python test_mastodon_stream.py [--max N] [--instance URL]

Options
-------
--max N         Number of posts to fetch (default: 5, max 40)
--instance URL  Mastodon instance to connect to (default: https://mastodon.social)

The results are also saved to: mastodon_stream_test_output.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Patch sys.path so we can import from sibling packages
sys.path.insert(0, str(Path(__file__).parent))

from ingestion.mastodon_client import fetch_public_posts  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("mastodon_test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch N posts from the Mastodon public timeline via REST."
    )
    parser.add_argument(
        "--max", type=int, default=5, help="Number of posts to fetch (default: 5)"
    )
    parser.add_argument(
        "--instance",
        type=str,
        default=None,
        help="Mastodon instance URL (default: https://mastodon.social or from .env)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    max_posts: int = args.max
    instance: str | None = args.instance

    print(
        f"\n🌐  Fetching {max_posts} post(s) from Mastodon public timeline "
        f"({instance or 'mastodon.social'}) via REST…\n"
    )

    start = datetime.now(timezone.utc)
    posts = fetch_public_posts(limit=max_posts, api_base_url=instance)
    elapsed = (datetime.now(timezone.utc) - start).total_seconds()

    for idx, record in enumerate(posts, 1):
        print(f"\n{'═' * 60}")
        print(f"  POST #{idx}")
        print(f"{'═' * 60}")
        display = {k: v for k, v in record.items() if k != "_meta"}
        for key, value in display.items():
            print(f"  {key:18s}: {value}")
        meta = record.get("_meta", {})
        if meta:
            print(f"  {'[account]':18s}: {meta.get('account', '')}")
            print(f"  {'[url]':18s}: {meta.get('url', '')}")
            print(f"  {'[language]':18s}: {meta.get('language', '')}")

    # Summary
    print(f"\n{'─' * 60}")
    print(f"✅  Captured {len(posts)} post(s) in {elapsed:.1f}s")
    print(f"{'─' * 60}\n")

    # Save to JSON file
    output_path = Path(__file__).parent / "mastodon_stream_test_output.json"
    output: dict = {
        "meta": {
            "instance": instance or "mastodon.social",
            "method": "REST /api/v1/timelines/public (anonymous)",
            "posts_requested": max_posts,
            "posts_captured": len(posts),
            "elapsed_seconds": round(elapsed, 2),
            "run_at": datetime.now(timezone.utc).isoformat(),
        },
        "posts": posts,
    }
    output_path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    print(f"📄  Output saved to: {output_path}")


if __name__ == "__main__":
    main()
