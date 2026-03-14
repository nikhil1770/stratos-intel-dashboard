# Coriolis NLP Verification — 10 Sample Posts

> **Run conditions**: 5 real Mastodon posts (fosstodon.org) + 5 synthetic posts.
> Location extraction uses spaCy `en_core_web_sm` (GPE + LOC entities).
> Geocoding via Nominatim / OpenStreetMap with local JSON cache.
> Sentiment via VADER compound score.

| #   | Src   | Raw Text (truncated to 72 chars)                                         | Extracted Locations           | Coordinates              | Sentiment           |
|-----|-------|--------------------------------------------------------------------------|-------------------------------|--------------------------|---------------------|
| 1   | [JSON] | would you rather have zeppelins that float around dropping leaflets tha… | *(none)*                       | —                        | 😊 Positive (+0.052) |
| 2   | [JSON] | Almost  # lunch  time, so off I go to meet up with my middle son at Old… | *(none)*                       | —                        | 😐 Neutral (+0.000) |
| 3   | [JSON] | spelling out my name over the phone is a nightmare, no one gets it righ… | *(none)*                       | —                        | 😟 Negative (-0.412) |
| 4   | [JSON] | 12 Beautiful Spring Bloomer Shrubs To Plant In March After the Last Fro… | *(none)*                       | —                        | 😊 Positive (+0.599) |
| 5   | [JSON] | Hello World experience in  # Java :  - install openjdk - javac HelloWor… | Gießen, Hessen                 | (50.5809, 8.6938)        | 😐 Neutral (+0.000) |
| 6   | [SYN] | Massive flooding reported across Bangladesh and parts of West Bengal to… | Bangladesh, West Bengal        | (24.4769, 90.2934)       | 😐 Neutral (+0.000) |
| 7   | [SYN] | The tech conference in Berlin was amazing! Great talks on AI and open-s… | Berlin, AI, London             | (52.5174, 13.3951)       | 😊 Positive (+0.898) |
| 8   | [SYN] | Tokyo just announced a major expansion of its metro network. Great news… | Tokyo, Japan, Tokyo, Japan     | (35.6769, 139.7639)      | 😊 Positive (+0.625) |
| 9   | [SYN] | Wildfires spreading rapidly in California. Authorities in Los Angeles h… | California, Los Angeles        | (36.7015, -118.7560)     | 😟 Negative (-0.382) |
| 10  | [SYN] | The election results from Nairobi are in — a historic moment for Kenya … | Nairobi, Kenya, East Africa    | (-1.2890, 36.8173)       | 😐 Neutral (+0.000) |

## Summary

| Metric | Value |
|--------|-------|
| Posts processed | 10 |
| Posts with geocoded coordinates | 6 / 10 |
| Positive sentiment | 4 |
| Neutral sentiment | 4 |
| Negative sentiment | 2 |

> [!NOTE]
> Posts without extracted locations are typically general commentary or
> technical posts with no geographic references. The raw `raw_location`
> field from the Mastodon profile is used as a fallback geocoding hint.
