import time
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from departure.StationsCache import stations_cache
from main import app
from starlette.testclient import TestClient

tc = TestClient(app)

STATIONS_JSON = {
    "station": [
        {"id": "001", "name": "Brussels-Central", "standardname": "Brussel-Centraal"},
        {"id": "002", "name": "Bruges", "standardname": "Brugge"},
        {
            "id": "003",
            "name": "Ghent-Sint-Pieters",
            "standardname": "Gent-Sint-Pieters",
        },
    ]
}


def _departure(
    dep_id,
    destination,
    offset_seconds,
    delay_seconds=0,
    vehicle="BE.NMBS.IC1234",
    standardname=None,
):
    """Build a fake iRail departure dict with a timestamp relative to now."""
    return {
        "id": str(dep_id),
        "stationinfo": {
            "id": f"BE.NMBS.00{dep_id}",
            "name": destination,
            "standardname": standardname or destination,
        },
        "time": str(int(time.time() + offset_seconds)),
        "delay": str(delay_seconds),
        "vehicle": vehicle,
    }


def _liveboard(departures):
    """Wrap a list of departure dicts in iRail liveboard response shape."""
    if not departures:
        return {"departures": ""}
    return {"departures": {"departure": departures}}


def _build_mock_client(stations_json, liveboard_map):
    """
    Return a patched AsyncClient mock.

    stations_json: dict returned for GET /stations/
    liveboard_map: {station_id: [departure_dicts]} for GET /liveboard/
    """

    async def mock_get(url, **kwargs):
        class _Resp:
            status_code = 200

            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

            def raise_for_status(self):
                pass

        if "/stations/" in url:
            return _Resp(stations_json)

        station_id = (kwargs.get("params") or {}).get("id", "")
        return _Resp(_liveboard(liveboard_map.get(station_id, [])))

    mock = AsyncMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    mock.get = AsyncMock(side_effect=mock_get)
    return mock


@pytest.fixture(autouse=True)
def clear_station_cache():
    stations_cache.set_stations([])
    yield
    stations_cache.set_stations([])


class TestQueryValidation:
    def test_empty_query_returns_400(self):
        r = tc.get("/departures/", params={"q": ""})
        assert r.status_code == 400
        detail = r.json()["detail"]
        assert detail["error"] == "QUERY_TOO_SHORT"
        assert detail["min_length"] == 3
        assert detail["received_length"] == 0

    def test_one_char_query_returns_400(self):
        r = tc.get("/departures/", params={"q": "B"})
        assert r.status_code == 400
        assert r.json()["detail"]["received_length"] == 1

    def test_three_char_query_is_accepted(self):
        mock = _build_mock_client(STATIONS_JSON, {})
        with patch("departure.router.httpx.AsyncClient", return_value=mock):
            r = tc.get("/departures/", params={"q": "Xyz"})
        assert r.status_code == 200

    def test_missing_q_param_returns_422(self):
        r = tc.get("/departures/")
        assert r.status_code == 422


class TestStationMatching:
    def test_no_matching_stations_returns_empty_list(self):
        mock = _build_mock_client(STATIONS_JSON, {})
        with patch("departure.router.httpx.AsyncClient", return_value=mock):
            r = tc.get("/departures/", params={"q": "Zzz"})
        assert r.status_code == 200
        data = r.json()
        assert data["query"] == "Zzz"
        assert data["stations"] == []

    def test_partial_name_match(self):
        """'ent' matches 'Ghent-Sint-Pieters' only."""
        deps = [_departure(0, "Brussels", offset_seconds=5 * 60)]
        mock = _build_mock_client(STATIONS_JSON, {"003": deps})
        with patch("departure.router.httpx.AsyncClient", return_value=mock):
            r = tc.get("/departures/", params={"q": "ent"})
        data = r.json()
        assert r.status_code == 200
        assert len(data["stations"]) == 1
        assert "Ghent" in data["stations"][0]["station"]["name"]

    def test_case_insensitive_lower(self):
        deps = [_departure(0, "Antwerp", offset_seconds=5 * 60)]
        mock = _build_mock_client(STATIONS_JSON, {"001": deps, "002": deps})
        with patch("departure.router.httpx.AsyncClient", return_value=mock):
            r = tc.get("/departures/", params={"q": "bru"})
        station_names = {s["station"]["name"] for s in r.json()["stations"]}
        assert "Brussels-Central" in station_names
        assert "Bruges" in station_names

    def test_case_insensitive_upper(self):
        deps = [_departure(0, "Antwerp", offset_seconds=5 * 60)]
        mock = _build_mock_client(STATIONS_JSON, {"001": deps, "002": deps})
        with patch("departure.router.httpx.AsyncClient", return_value=mock):
            r = tc.get("/departures/", params={"q": "BRU"})
        station_names = {s["station"]["name"] for s in r.json()["stations"]}
        assert "Brussels-Central" in station_names
        assert "Bruges" in station_names


class TestDepartureWindow:
    def test_departure_inside_window_included(self):
        deps = [_departure(0, "Ghent", offset_seconds=5 * 60)]
        mock = _build_mock_client(STATIONS_JSON, {"001": deps})
        with patch("departure.router.httpx.AsyncClient", return_value=mock):
            r = tc.get("/departures/", params={"q": "Brussels"})
        assert len(r.json()["stations"][0]["departures"]) == 1

    def test_departure_outside_window_excluded(self):
        deps = [_departure(0, "Ghent", offset_seconds=20 * 60)]
        mock = _build_mock_client(STATIONS_JSON, {"001": deps})
        with patch("departure.router.httpx.AsyncClient", return_value=mock):
            r = tc.get("/departures/", params={"q": "Brussels"})
        assert r.json()["stations"] == []

    def test_empty_liveboard_response_handled(self):
        """iRail returns {"departures": ""} when no trains are scheduled."""
        mock = _build_mock_client(STATIONS_JSON, {"001": []})
        with patch("departure.router.httpx.AsyncClient", return_value=mock):
            r = tc.get("/departures/", params={"q": "Brussels"})
        assert r.status_code == 200
        assert r.json()["stations"] == []


class TestResponseShape:
    def _get_first_departure(self):
        deps = [
            _departure(
                0,
                "Ghent-Sint-Pieters",
                offset_seconds=5 * 60,
                vehicle="BE.NMBS.IC1234",
                standardname="Gent-Sint-Pieters",
            )
        ]
        mock = _build_mock_client(STATIONS_JSON, {"001": deps})
        with patch("departure.router.httpx.AsyncClient", return_value=mock):
            r = tc.get("/departures/", params={"q": "Brussels"})
        return r.json()["stations"][0]["departures"][0]

    def test_all_departure_fields_present(self):
        dep = self._get_first_departure()
        assert "train_number" in dep
        assert "scheduled_departure" in dep
        assert "delay_minutes" in dep
        assert "name" in dep["destination"]
        assert "standardname" in dep["destination"]

    def test_delay_converted_to_minutes(self):
        deps = [_departure(0, "Ghent", offset_seconds=5 * 60, delay_seconds=300)]
        mock = _build_mock_client(STATIONS_JSON, {"001": deps})
        with patch("departure.router.httpx.AsyncClient", return_value=mock):
            r = tc.get("/departures/", params={"q": "Brussels"})
        dep = r.json()["stations"][0]["departures"][0]
        assert dep["delay_minutes"] == 5

    def test_scheduled_departure_is_iso_datetime(self):
        dep = self._get_first_departure()
        dt = datetime.fromisoformat(dep["scheduled_departure"])
        assert dt is not None


class TestStationsCache:
    def test_stations_cached_after_first_request(self):
        mock = _build_mock_client(STATIONS_JSON, {})
        with patch("departure.router.httpx.AsyncClient", return_value=mock):
            tc.get("/departures/", params={"q": "Bru"})
        assert len(stations_cache.get_stations()) == 3

    def test_stations_api_not_called_when_cache_is_populated(self):
        from departure.models import Station

        stations_cache.set_stations(
            [
                Station(
                    id="001", name="Brussels-Central", standardname="Brussel-Centraal"
                )
            ]
        )

        mock = _build_mock_client(STATIONS_JSON, {"001": []})
        with patch("departure.router.httpx.AsyncClient", return_value=mock):
            tc.get("/departures/", params={"q": "Bru"})

        called_urls = [call.args[0] for call in mock.get.call_args_list]
        assert all("/stations/" not in url for url in called_urls)
