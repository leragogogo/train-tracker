import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import type { Departure } from "../../src/api/departures";
import { DepartureTable } from "../../src/components/DepartureTable";

function makeDep(overrides: Partial<Departure> = {}): Departure {
  return {
    train_number: "BE.NMBS.IC1234",
    destination: { id: "003", name: "Ghent-Sint-Pieters", standardname: "Gent-Sint-Pieters" },
    scheduled_departure: "2024-01-15T14:30:00",
    delay_minutes: 0,
    ...overrides,
  };
}

describe("DepartureTable", () => {
  it('shows "On time" when delay is 0', () => {
    render(<DepartureTable departures={[makeDep({ delay_minutes: 0 })]} />);
    expect(screen.getByText("On time")).toBeInTheDocument();
  });

  it('shows "+N min" when delay is positive', () => {
    render(<DepartureTable departures={[makeDep({ delay_minutes: 5 })]} />);
    expect(screen.getByText("+5 min")).toBeInTheDocument();
  });

  it("shows standardname and (name) when destination names differ", () => {
    render(<DepartureTable departures={[makeDep()]} />);
    expect(screen.getByText("Gent-Sint-Pieters")).toBeInTheDocument();
    expect(screen.getByText("(Ghent-Sint-Pieters)")).toBeInTheDocument();
  });

  it("shows only standardname when destination names are identical", () => {
    render(
      <DepartureTable
        departures={[makeDep({ destination: { id: "003", name: "Bruges", standardname: "Bruges" } })]}
      />,
    );
    expect(screen.getByText("Bruges")).toBeInTheDocument();
    expect(screen.queryByText(/\(/)).not.toBeInTheDocument();
  });

  it("formats scheduled_departure as HH:MM time", () => {
    render(
      <DepartureTable
        departures={[makeDep({ scheduled_departure: "2024-01-15T14:30:00" })]}
      />,
    );
    expect(screen.getByText(/\d{1,2}:\d{2}/)).toBeInTheDocument();
  });
});
