"""
processing/verify_sample.py
----------------------------
Standalone verifier for the Coriolis NLP pipeline (Step 2).

Reads the first 5 posts from mastodon_stream_test_output.json, adds 5
synthetic posts with explicit location references (to ensure the NER +
geocoder are exercised well), processes all 10, and prints + saves a
Markdown comparison table.

No database connection required.

Usage
-----
    # From the project root:
    python -m processing.verify_sample
"""

from __future__ import annotations

import json
import logging
import textwrap
from pathlib import Path

from processing.nlp_processor import load_models, process_post

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("coriolis.verify")


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SAMPLE_JSON = _PROJECT_ROOT / "mastodon_stream_test_output.json"
_OUTPUT_MD = Path(__file__).resolve().parent / "verification_results.md"

# ---------------------------------------------------------------------------
# 5 synthetic posts with known geographic references for comprehensive testing
# ---------------------------------------------------------------------------
SYNTHETIC_POSTS = [
    {
        "source": "synthetic",
        "text": "Massive flooding reported across Bangladesh and parts of West Bengal today. Thousands displaced.",
        "raw_location": None,
    },
    {
        "source": "synthetic",
        "text": "The tech conference in Berlin was amazing! Great talks on AI and open-source. Definitely flying back to London next year.",
        "raw_location": None,
    },
    {
        "source": "synthetic",
        "text": "Tokyo just announced a major expansion of its metro network. Great news for commuters in Japan.",
        "raw_location": "Tokyo, Japan",
    },
    {
        "source": "synthetic",
        "text": "Wildfires spreading rapidly in California. Authorities in Los Angeles have issued emergency evacuation orders.",
        "raw_location": None,
    },
    {
        "source": "synthetic",
        "text": "The election results from Nairobi are in — a historic moment for Kenya and East Africa as a whole.",
        "raw_location": None,
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _truncate(s: str, n: int = 70) -> str:
    """Truncate *s* to *n* chars with ellipsis."""
    return s if len(s) <= n else s[: n - 1] + "…"


def _fmt_coords(lat, lon) -> str:
    if lat is None or lon is None:
        return "—"
    return f"({lat:.4f}, {lon:.4f})"


def _fmt_locations(locs: list[str]) -> str:
    if not locs:
        return "*(none)*"
    return ", ".join(locs[:4])  # cap at 4 for table readability


def _sentiment_emoji(label: str) -> str:
    return {"Positive": "😊 Positive", "Neutral": "😐 Neutral", "Negative": "😟 Negative"}.get(
        label, label
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    # --- load sample JSON -----------------------------------------------
    logger.info("Loading sample posts from %s", _SAMPLE_JSON)
    with open(_SAMPLE_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    json_posts: list[dict] = data.get("posts", [])
    logger.info("Found %d posts in JSON file.", len(json_posts))

    # Combine: real posts first, then synthetic
    all_posts: list[dict] = json_posts + SYNTHETIC_POSTS
    # Process up to 10
    posts_to_run = all_posts[:10]
    logger.info("Will process %d posts total.", len(posts_to_run))

    # --- load NLP models ------------------------------------------------
    logger.info("Loading NLP models…")
    load_models()
    logger.info("Models ready. Starting processing…")

    # --- process each post ----------------------------------------------
    results = []
    for i, post in enumerate(posts_to_run, start=1):
        source_tag = "[JSON]" if i <= len(json_posts) else "[SYN]"
        logger.info("Processing post %d/10 %s…", i, source_tag)
        result = process_post(post)
        results.append(
            {
                "num": i,
                "tag": source_tag,
                "raw_text": post.get("text", ""),
                "extracted_locations": result["extracted_locations"],
                "geocoded_location": result["geocoded_location"],
                "coordinates": _fmt_coords(result["latitude"], result["longitude"]),
                "sentiment_score": result["sentiment_score"],
                "sentiment_label": result["sentiment_label"],
            }
        )

    # --- build Markdown table -------------------------------------------
    logger.info("Building results table…")

    header = (
        "# Coriolis NLP Verification — 10 Sample Posts\n\n"
        "> **Run conditions**: 5 real Mastodon posts (fosstodon.org) + 5 synthetic posts.\n"
        "> Location extraction uses spaCy `en_core_web_sm` (GPE + LOC entities).\n"
        "> Geocoding via Nominatim / OpenStreetMap with local JSON cache.\n"
        "> Sentiment via VADER compound score.\n\n"
    )

    col_widths = {
        "num": 4,
        "src": 6,
        "text": 72,
        "loc": 30,
        "coords": 24,
        "sent": 20,
    }

    def row_md(num, tag, text, locs, coords, sentiment, score):
        return (
            f"| {num:<3} | {tag:<5} "
            f"| {_truncate(text, col_widths['text']):<72} "
            f"| {_fmt_locations(locs):<30} "
            f"| {coords:<24} "
            f"| {sentiment} ({score:+.3f}) |"
        )

    table_header = (
        "| #   | Src   "
        "| Raw Text (truncated to 72 chars)                                         "
        "| Extracted Locations           "
        "| Coordinates              "
        "| Sentiment           |\n"
        "|-----|-------|"
        "--------------------------------------------------------------------------|"
        "-------------------------------|"
        "--------------------------|"
        "---------------------|"
    )

    rows_md = [
        row_md(
            r["num"],
            r["tag"],
            r["raw_text"],
            r["extracted_locations"],
            r["coordinates"],
            _sentiment_emoji(r["sentiment_label"]),
            r["sentiment_score"],
        )
        for r in results
    ]

    # Summary stats
    geocoded_count = sum(1 for r in results if r["coordinates"] != "—")
    pos = sum(1 for r in results if r["sentiment_label"] == "Positive")
    neu = sum(1 for r in results if r["sentiment_label"] == "Neutral")
    neg = sum(1 for r in results if r["sentiment_label"] == "Negative")

    summary = textwrap.dedent(f"""
    ## Summary

    | Metric | Value |
    |--------|-------|
    | Posts processed | {len(results)} |
    | Posts with geocoded coordinates | {geocoded_count} / {len(results)} |
    | Positive sentiment | {pos} |
    | Neutral sentiment | {neu} |
    | Negative sentiment | {neg} |

    > [!NOTE]
    > Posts without extracted locations are typically general commentary or
    > technical posts with no geographic references. The raw `raw_location`
    > field from the Mastodon profile is used as a fallback geocoding hint.
    """).strip()

    full_md = header + table_header + "\n" + "\n".join(rows_md) + "\n\n" + summary + "\n"

    # --- print to terminal ----------------------------------------------
    print("\n" + "=" * 80)
    print("CORIOLIS NLP VERIFICATION RESULTS")
    print("=" * 80)
    for r in results:
        print(
            f"\n[{r['num']:02d}] {r['tag']} | {r['sentiment_label']:8s} ({r['sentiment_score']:+.3f})"
            f"\n     Text     : {_truncate(r['raw_text'], 90)}"
            f"\n     Locations: {_fmt_locations(r['extracted_locations'])}"
            f"\n     Coords   : {r['coordinates']}"
        )
    print(f"\n{'='*80}")
    print(f"Processed: {len(results)} | Geocoded: {geocoded_count} | "
          f"Pos: {pos} | Neu: {neu} | Neg: {neg}")
    print("=" * 80)

    # --- save Markdown artifact -----------------------------------------
    with open(_OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(full_md)
    logger.info("Results saved to %s", _OUTPUT_MD)
    print(f"\nMarkdown table saved → {_OUTPUT_MD}\n")


if __name__ == "__main__":
    main()
