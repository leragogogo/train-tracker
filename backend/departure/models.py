from datetime import datetime

from pydantic import BaseModel, field_validator


class Station(BaseModel):
    id: str
    name: str
    standardname: str


class StationsResponse(BaseModel):
    station: list[Station]


class Departure(BaseModel):
    id: int
    stationinfo: Station  # destination station with name and standardname
    time: int  # unix timestamp
    delay: int  # delay in minutes (converted from seconds by validator)
    vehicle: str

    @field_validator("delay", mode="before")
    @classmethod
    def convert_delay_to_minutes(cls, v):
        return int(v) // 60


class DepartureOut(BaseModel):
    train_number: str
    destination: Station
    scheduled_departure: datetime
    delay_minutes: int


class StationDeparturesOut(BaseModel):
    station: Station
    departures: list[DepartureOut]


class DeparturesResponse(BaseModel):
    query: str
    stations: list[StationDeparturesOut]
