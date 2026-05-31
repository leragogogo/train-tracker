import type { Departure } from "../api/departures";

interface Props {
  departures: Departure[];
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function Delay({ minutes }: { minutes: number }) {
  if (minutes === 0) return <span className="delay on-time">On time</span>;
  return <span className="delay delayed">+{minutes} min</span>;
}

export function DepartureTable({ departures }: Props) {
  return (
    <table className="departure-table">
      <thead>
        <tr>
          <th>Train</th>
          <th>Destination</th>
          <th>Scheduled</th>
          <th>Delay</th>
        </tr>
      </thead>
      <tbody>
        {departures.map((dep, i) => (
          <tr key={i}>
            <td className="mono">{dep.train_number}</td>
            <td>{dep.destination}</td>
            <td className="mono">{formatTime(dep.scheduled_departure)}</td>
            <td>
              <Delay minutes={dep.delay_minutes} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
