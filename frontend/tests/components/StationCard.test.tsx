import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import type { StationDepartures } from "../../src/api/departures";
import { StationCard } from "../../src/components/StationCard";

function makeStation(name: string, standardname: string): StationDepartures {
  return {
    station: { id: "001", name, standardname },
    departures: [],
  };
}

describe("StationCard", () => {
  it("shows 'standardname (name)' when they differ", () => {
    render(
      <StationCard
        station={makeStation("Brussels-Central", "Brussel-Centraal")}
      />,
    );
    expect(
      screen.getByText("Brussel-Centraal (Brussels-Central)"),
    ).toBeInTheDocument();
  });

  it("shows just the standardname when name and standardname are identical", () => {
    render(<StationCard station={makeStation("Bruges", "Bruges")} />);
    expect(screen.getByText("Bruges")).toBeInTheDocument();
    expect(screen.queryByText(/\(/)).not.toBeInTheDocument();
  });
});
