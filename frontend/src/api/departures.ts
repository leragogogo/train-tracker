export interface Departure {
  train_number: string;
  destination: string;
  scheduled_departure: string;
  delay_minutes: number;
}

export interface StationDepartures {
  station: string;
  departures: Departure[];
}

export interface DeparturesResponse {
  query: string;
  stations: StationDepartures[];
}

export async function fetchDepartures(
  query: string,
  signal: AbortSignal,
): Promise<DeparturesResponse> {
  const response = await fetch(`/departures/?q=${encodeURIComponent(query)}`, {
    signal,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}
