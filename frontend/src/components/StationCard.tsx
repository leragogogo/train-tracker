import type { StationDepartures } from "../api/departures";
import { DepartureTable } from "./DepartureTable";

interface Props {
  station: StationDepartures;
}

export function StationCard({ station }: Props) {
  return (
    <section className="station-card">
      <h2 className="station-name">
        {station.station.standardname === station.station.name
          ? station.station.standardname
          : `${station.station.standardname} (${station.station.name})`}
      </h2>
      <DepartureTable departures={station.departures} />
    </section>
  );
}
