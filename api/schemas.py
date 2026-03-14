"""
api/schemas.py
--------------
Pydantic v2 models for the Coriolis API responses.

GeoJSON structures follow RFC 7946.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# GeoJSON building blocks
# ---------------------------------------------------------------------------

class GeoJsonGeometry(BaseModel):
    """GeoJSON Point geometry."""

    type: Literal["Point"] = "Point"
    coordinates: List[float] = Field(
        ...,
        description="[longitude, latitude] per RFC 7946",
        min_length=2,
        max_length=2,
    )


class ActivityProperties(BaseModel):
    """Properties carried inside each GeoJSON Feature."""

    id: str
    source: str
    topic: Optional[str] = None
    text: str
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    geocoded_location: Optional[str] = None
    extracted_locations: Optional[List[str]] = None
    timestamp: Optional[datetime] = None
    processed_at: Optional[datetime] = None


class GeoJsonFeature(BaseModel):
    """A single GeoJSON Feature wrapping one processed activity record."""

    type: Literal["Feature"] = "Feature"
    geometry: GeoJsonGeometry
    properties: ActivityProperties


class FeatureCollection(BaseModel):
    """Top-level GeoJSON FeatureCollection returned by /api/v1/activity."""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: List[GeoJsonFeature] = Field(default_factory=list)
    count: int = Field(0, description="Number of features in this response")


# ---------------------------------------------------------------------------
# Stats response
# ---------------------------------------------------------------------------

class StatsResponse(BaseModel):
    """Summary statistics returned by /api/v1/stats."""

    total_records: int = Field(..., description="Total rows in processed_activity")
    records_with_coords: int = Field(
        ..., description="Rows that have non-null latitude and longitude"
    )
    by_source: Dict[str, int] = Field(
        default_factory=dict,
        description="Record count grouped by data source",
    )
    avg_sentiment_by_source: Dict[str, Optional[float]] = Field(
        default_factory=dict,
        description="Average VADER compound score per source",
    )
    by_sentiment_label: Dict[str, int] = Field(
        default_factory=dict,
        description="Record count grouped by sentiment label",
    )
    by_topic: Dict[str, int] = Field(
        default_factory=dict,
        description="Record count grouped by topic",
    )
    top_geocoded_locations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Top 10 most-frequent geocoded place names with their counts",
    )
