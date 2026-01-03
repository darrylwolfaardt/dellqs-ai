"""Geocoder implementation for location lookup and validation."""

import re
from dataclasses import dataclass, field
from typing import Any, Optional

from ..common.base import BaseTool, ToolResult, ToolStatus, ToolError
from ..common.schemas import LocationInfo


@dataclass
class GeocodingResult:
    """Result of geocoding operation."""
    location: LocationInfo
    source: str  # Which geocoding service was used
    raw_response: Optional[dict[str, Any]] = None
    match_quality: str = "exact"  # "exact", "partial", "approximate"

    def to_dict(self) -> dict[str, Any]:
        return {
            "location": self.location.to_dict(),
            "source": self.source,
            "match_quality": self.match_quality,
        }


class Geocoder(BaseTool):
    """
    Tool for geocoding addresses and postcodes.

    Supports multiple providers:
    - postcodes.io (UK postcodes, free)
    - Nominatim/OpenStreetMap (addresses, free with rate limits)
    - Google Maps Geocoding API (paid, most accurate)
    """

    # UK postcode regex
    UK_POSTCODE_PATTERN = re.compile(
        r"^([A-Z]{1,2}[0-9][0-9A-Z]?)\s*([0-9][A-Z]{2})$",
        re.IGNORECASE
    )

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(config)
        self.primary_provider = config.get("provider", "postcodes_io") if config else "postcodes_io"
        self.google_api_key = config.get("google_api_key") if config else None
        self.cache: dict[str, GeocodingResult] = {}

    @property
    def name(self) -> str:
        return "geocoder"

    @property
    def description(self) -> str:
        return "Geocodes addresses and postcodes to coordinates and regional information"

    def _normalize_postcode(self, postcode: str) -> Optional[str]:
        """Normalize UK postcode to standard format."""
        postcode = postcode.strip().upper()
        match = self.UK_POSTCODE_PATTERN.match(postcode)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        return None

    def _is_uk_postcode(self, text: str) -> bool:
        """Check if text looks like a UK postcode."""
        return bool(self.UK_POSTCODE_PATTERN.match(text.strip()))

    async def _geocode_postcodes_io(self, postcode: str) -> GeocodingResult:
        """Geocode UK postcode using postcodes.io API."""
        import aiohttp

        normalized = self._normalize_postcode(postcode)
        if not normalized:
            raise ValueError(f"Invalid UK postcode format: {postcode}")

        url = f"https://api.postcodes.io/postcodes/{normalized.replace(' ', '')}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    raise ValueError(f"Postcode not found: {normalized}")
                elif response.status != 200:
                    raise RuntimeError(f"Postcodes.io API error: {response.status}")

                data = await response.json()
                result = data.get("result", {})

                location = LocationInfo(
                    postcode=normalized,
                    latitude=result.get("latitude"),
                    longitude=result.get("longitude"),
                    local_authority=result.get("admin_district"),
                    region=result.get("region"),
                    country=result.get("country", "UK"),
                )

                return GeocodingResult(
                    location=location,
                    source="postcodes.io",
                    raw_response=result,
                    match_quality="exact",
                )

    async def _geocode_nominatim(self, address: str) -> GeocodingResult:
        """Geocode address using OpenStreetMap Nominatim."""
        import aiohttp

        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
            "countrycodes": "gb",  # Default to UK
        }
        headers = {
            "User-Agent": "QS-Agent-Geocoder/1.0",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    raise RuntimeError(f"Nominatim API error: {response.status}")

                data = await response.json()

                if not data:
                    raise ValueError(f"Address not found: {address}")

                result = data[0]
                address_parts = result.get("address", {})

                location = LocationInfo(
                    address=result.get("display_name"),
                    postcode=address_parts.get("postcode"),
                    latitude=float(result.get("lat")),
                    longitude=float(result.get("lon")),
                    local_authority=address_parts.get("city") or address_parts.get("town"),
                    region=address_parts.get("county") or address_parts.get("state"),
                    country=address_parts.get("country", "UK"),
                )

                # Determine match quality
                match_type = result.get("type", "")
                if match_type in ("house", "building", "address"):
                    quality = "exact"
                elif match_type in ("street", "road"):
                    quality = "partial"
                else:
                    quality = "approximate"

                return GeocodingResult(
                    location=location,
                    source="nominatim",
                    raw_response=result,
                    match_quality=quality,
                )

    async def _geocode_google(self, address: str) -> GeocodingResult:
        """Geocode address using Google Maps Geocoding API."""
        import aiohttp

        if not self.google_api_key:
            raise ValueError("Google API key not configured")

        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": self.google_api_key,
            "region": "gb",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise RuntimeError(f"Google API error: {response.status}")

                data = await response.json()

                if data.get("status") != "OK":
                    raise ValueError(f"Geocoding failed: {data.get('status')}")

                result = data["results"][0]
                geometry = result.get("geometry", {})
                location_data = geometry.get("location", {})

                # Extract address components
                components = {
                    c["types"][0]: c["long_name"]
                    for c in result.get("address_components", [])
                    if c.get("types")
                }

                location = LocationInfo(
                    address=result.get("formatted_address"),
                    postcode=components.get("postal_code"),
                    latitude=location_data.get("lat"),
                    longitude=location_data.get("lng"),
                    local_authority=components.get("postal_town") or components.get("locality"),
                    region=components.get("administrative_area_level_2"),
                    country=components.get("country", "UK"),
                )

                # Determine match quality from location_type
                loc_type = geometry.get("location_type", "")
                quality_map = {
                    "ROOFTOP": "exact",
                    "RANGE_INTERPOLATED": "partial",
                    "GEOMETRIC_CENTER": "approximate",
                    "APPROXIMATE": "approximate",
                }
                quality = quality_map.get(loc_type, "approximate")

                return GeocodingResult(
                    location=location,
                    source="google",
                    raw_response=result,
                    match_quality=quality,
                )

    async def execute(
        self,
        query: str,
        provider: Optional[str] = None,
    ) -> ToolResult[GeocodingResult]:
        """
        Geocode an address or postcode.

        Args:
            query: Address or postcode to geocode
            provider: Override default provider ("postcodes_io", "nominatim", "google")

        Returns:
            ToolResult containing GeocodingResult
        """
        import time
        start_time = time.time()

        query = query.strip()

        if not query:
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=[self._create_error(
                    "EMPTY_QUERY",
                    "No address or postcode provided",
                    recoverable=False,
                )],
            )

        # Check cache
        cache_key = f"{query.lower()}:{provider or self.primary_provider}"
        if cache_key in self.cache:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                data=self.cache[cache_key],
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        provider = provider or self.primary_provider
        warnings: list[str] = []

        try:
            # Determine best provider based on input
            if self._is_uk_postcode(query):
                # Use postcodes.io for UK postcodes
                if provider != "postcodes_io":
                    warnings.append(f"Using postcodes.io for UK postcode (requested: {provider})")
                    provider = "postcodes_io"

                result = await self._geocode_postcodes_io(query)

            elif provider == "postcodes_io":
                # Not a postcode but postcodes.io requested
                return ToolResult(
                    status=ToolStatus.FAILED,
                    errors=[self._create_error(
                        "INVALID_INPUT",
                        "postcodes.io requires a valid UK postcode",
                        recoverable=True,
                    )],
                    warnings=["Try using 'nominatim' or 'google' provider for addresses"],
                )

            elif provider == "google":
                if not self.google_api_key:
                    warnings.append("Google API key not configured, falling back to Nominatim")
                    result = await self._geocode_nominatim(query)
                else:
                    result = await self._geocode_google(query)

            else:  # nominatim or unknown
                result = await self._geocode_nominatim(query)

            # Cache result
            self.cache[cache_key] = result

            execution_time = (time.time() - start_time) * 1000

            # Add warning for non-exact matches
            if result.match_quality != "exact":
                warnings.append(f"Match quality: {result.match_quality}")

            return ToolResult(
                status=ToolStatus.SUCCESS,
                data=result,
                warnings=warnings,
                execution_time_ms=execution_time,
            )

        except ValueError as e:
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=[self._create_error(
                    "NOT_FOUND",
                    str(e),
                    recoverable=True,
                )],
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        except Exception as e:
            self.logger.error(f"Geocoding failed for '{query}': {e}")
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=[self._create_error(
                    "GEOCODING_ERROR",
                    f"Geocoding failed: {str(e)}",
                    recoverable=True,
                    details={"exception": str(type(e).__name__)},
                )],
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    async def validate_postcode(self, postcode: str) -> ToolResult[bool]:
        """
        Validate a UK postcode exists.

        Args:
            postcode: Postcode to validate

        Returns:
            ToolResult containing boolean validity
        """
        import time
        start_time = time.time()

        normalized = self._normalize_postcode(postcode)
        if not normalized:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                data=False,
                warnings=["Invalid postcode format"],
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        try:
            import aiohttp

            url = f"https://api.postcodes.io/postcodes/{normalized.replace(' ', '')}/validate"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return ToolResult(
                            status=ToolStatus.FAILED,
                            errors=[self._create_error(
                                "API_ERROR",
                                f"Validation API error: {response.status}",
                                recoverable=True,
                            )],
                        )

                    data = await response.json()
                    is_valid = data.get("result", False)

                    return ToolResult(
                        status=ToolStatus.SUCCESS,
                        data=is_valid,
                        execution_time_ms=(time.time() - start_time) * 1000,
                    )

        except Exception as e:
            return ToolResult(
                status=ToolStatus.FAILED,
                errors=[self._create_error(
                    "VALIDATION_ERROR",
                    f"Postcode validation failed: {str(e)}",
                    recoverable=True,
                )],
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    async def enrich_location(
        self,
        location: LocationInfo,
    ) -> ToolResult[LocationInfo]:
        """
        Enrich a LocationInfo object with additional data.

        If postcode is present, fetches coordinates and regional info.
        If only address, attempts geocoding.

        Args:
            location: LocationInfo to enrich

        Returns:
            ToolResult containing enriched LocationInfo
        """
        import time
        start_time = time.time()

        if not location.postcode and not location.address:
            return ToolResult(
                status=ToolStatus.PARTIAL,
                data=location,
                warnings=["No postcode or address to enrich from"],
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        query = location.postcode or location.address
        result = await self.execute(query)

        if not result.success or not result.data:
            return ToolResult(
                status=ToolStatus.PARTIAL,
                data=location,
                errors=result.errors,
                warnings=result.warnings + ["Could not enrich location"],
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        geocoded = result.data.location

        # Merge: keep original values if present, add geocoded ones
        enriched = LocationInfo(
            address=location.address or geocoded.address,
            postcode=location.postcode or geocoded.postcode,
            latitude=geocoded.latitude,
            longitude=geocoded.longitude,
            local_authority=location.local_authority or geocoded.local_authority,
            region=location.region or geocoded.region,
            country=location.country or geocoded.country,
            what3words=location.what3words,
        )

        return ToolResult(
            status=ToolStatus.SUCCESS,
            data=enriched,
            warnings=result.warnings,
            execution_time_ms=(time.time() - start_time) * 1000,
        )
