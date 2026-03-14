"""
processing/
-----------
Data Processing & NLP Layer for the Coriolis pipeline.

Modules
-------
nlp_processor  — spaCy NER, Nominatim geocoding, VADER sentiment, local cache.
worker         — DB worker: pulls pending rows, processes them, writes results.
verify_sample  — Standalone verifier against mastodon_stream_test_output.json.
"""
