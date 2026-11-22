import json
import logging
import math
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query

from backend.schemas import EnvironmentalTelemetry, GeoSearchResult

logger = logging.getLogger("kshetra.geo")
router = APIRouter(prefix="/geo", tags=["Geospatial & Environmental Telemetry"])

# In-memory caches to prevent redundant calls and respect rate limits
_GEO_SEARCH_CACHE: Dict[str, List[Dict[str, Any]]] = {}
_GEO_REVERSE_CACHE: Dict[str, Dict[str, Any]] = {}
_ENV_CACHE: Dict[str, Dict[str, Any]] = {}
_LAST_OSM_CALL = 0.0

def check_network_connectivity() -> bool:
    """
    Returns True to allow outbound queries to live open data providers (Open-Meteo, Nominatim).
    Can be disabled by setting KSHETRA_DISABLE_REMOTE_NETWORK=1.
    """
    return os.environ.get("KSHETRA_DISABLE_REMOTE_NETWORK", "0") != "1"
