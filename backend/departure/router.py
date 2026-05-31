"""
GET /departures?q=<station-fragment>

Returns upcoming departures (within 15 minutes) from stations that fuzzy-match
the query. Both the English name and the local standardname are scored with
partial_ratio; a station is included if either score >= 80. Results are ordered
from best match to worst.

Response — 200 OK:
  {
    "query": "Bru",
    "stations": [
      {
        "station": {
          "id": "BE.NMBS.008813003",
          "name": "Brussels-Central",
          "standardname": "Brussel-Centraal"
        },
        "departures": [
          {
            "train_number": "BE.NMBS.IC1234",
            "destination": {
              "id": "BE.NMBS.008892007",
              "name": "Ghent-Sint-Pieters",
              "standardname": "Gent-Sint-Pieters"
            },
            "scheduled_departure": "2024-01-15T14:30:00",
            "delay_minutes": 5
          }
        ]
      }
    ]
  }

  Stations with no upcoming departures in the 15-minute window are excluded.

Response — 400 Bad Request (q shorter than 3 characters):
  {
    "detail": {
      "error": "QUERY_TOO_SHORT",
      "message": "Query must be at least 3 characters long.",
      "min_length": 3,
      "received_length": <int>
    }
  }
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

import httpx
from departure.models import (
    Departure,
    DepartureOut,
    DeparturesResponse,
    Station,
    StationDeparturesOut,
    StationsResponse,
)
from departure.StationsCache import stations_cache
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import TypeAdapter
from rapidfuzz import fuzz

load_dotenv(Path(__file__).parent / ".env")

IRAIL_BASE_URL = os.getenv("IRAIL_BASE_URL")
DEPARTURE_WINDOW_SECONDS = int(os.getenv("DEPARTURE_WINDOW_SECONDS"))

router = APIRouter(prefix="/departures", tags=["departures"])


async def _fetch_departures(
    client: httpx.AsyncClient, station_id: str, now: datetime
) -> list[Departure]:
    try:
        response = await client.get(
            f"{IRAIL_BASE_URL}/liveboard/",
            params={
                "id": station_id,
                "date": now.strftime("%d%m%y"),
                "time": now.strftime("%H%M"),
                "format": "json",
                "lang": "en",
                "alerts": "false",
            },
        )
        response.raise_for_status()
        data = response.json()
        raw = data.get("departures")
        if not raw or not isinstance(raw, dict):
            return []
        departure_list = raw.get("departure") or []
        if not departure_list:
            return []
        return TypeAdapter(list[Departure]).validate_python(departure_list)
    except Exception:
        return []


def _filter_window(departures: list[Departure], now: datetime) -> list[Departure]:
    result = []
    for dep in departures:
        diff = (datetime.fromtimestamp(dep.time) - now).total_seconds()
        if 0 <= diff <= DEPARTURE_WINDOW_SECONDS:
            result.append(dep)
    return result


def _to_departure_out(dep: Departure) -> DepartureOut:
    return DepartureOut(
        train_number=dep.vehicle,
        destination=dep.stationinfo,
        scheduled_departure=datetime.fromtimestamp(dep.time),
        delay_minutes=dep.delay,
    )


def _get_matching_stations(q: str, stations: list[Station]) -> list[Station]:
    q_lower = q.lower()
    scored = [
        (
            max(
                fuzz.partial_ratio(q_lower, s.name.lower()),
                fuzz.partial_ratio(q_lower, s.standardname.lower()),
            ),
            s,
        )
        for s in stations
    ]
    filtered = [(score, s) for score, s in scored if score >= 80]
    return [s for _, s in sorted(filtered, key=lambda x: x[0], reverse=True)]


@router.get("/", response_model=DeparturesResponse)
async def get_departures(q: str) -> DeparturesResponse:
    if len(q) < 3:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "QUERY_TOO_SHORT",
                "message": "Query must be at least 3 characters long.",
                "min_length": 3,
                "received_length": len(q),
            },
        )

    now = datetime.now()

    async with httpx.AsyncClient(follow_redirects=True) as client:
        stations = stations_cache.get_stations()
        if not stations:
            resp = await client.get(
                f"{IRAIL_BASE_URL}/stations/",
                params={"format": "json", "lang": "en"},
            )
            resp.raise_for_status()
            stations = StationsResponse.model_validate(resp.json()).station
            stations_cache.set_stations(stations)

        matching = _get_matching_stations(q, stations)

        tasks = [_fetch_departures(client, s.id, now) for s in matching]
        all_departures = await asyncio.gather(*tasks)

    station_results = []
    for station, departures in zip(matching, all_departures):
        within_window = _filter_window(departures, now)
        if within_window:
            station_results.append(
                StationDeparturesOut(
                    station=station,
                    departures=[_to_departure_out(d) for d in within_window],
                )
            )

    return DeparturesResponse(query=q, stations=station_results)
