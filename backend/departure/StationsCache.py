# must be a singleton
from departure.models import Station


class StationsCache:
    def __init__(self):
        self._stations: list[Station] = []

    def set_stations(self, stations: list[Station]):
        self._stations = stations

    def get_stations(self) -> list[Station]:
        return self._stations


stations_cache = StationsCache()
