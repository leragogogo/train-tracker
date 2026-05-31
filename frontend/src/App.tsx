import { useEffect, useState } from "react";
import { fetchDepartures, type DeparturesResponse } from "./api/departures";
import { SearchInput } from "./components/SearchInput";
import { StationCard } from "./components/StationCard";
import "./App.css";

const DEBOUNCE_MS = Number(import.meta.env.VITE_DEBOUNCE_MS);
const MIN_QUERY_LENGTH = Number(import.meta.env.VITE_MIN_QUERY_LENGTH);

export default function App() {
  const [query, setQuery] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);
  const [results, setResults] = useState<DeparturesResponse | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");

  useEffect(() => {
    if (query.length < MIN_QUERY_LENGTH) {
      setResults(null);
      setStatus("idle");
      return;
    }

    const controller = new AbortController();

    const timer = setTimeout(async () => {
      setStatus("loading");
      try {
        const data = await fetchDepartures(query, controller.signal);
        setResults(data);
        setStatus("idle");
      } catch (err) {
        if ((err as Error).name === "AbortError") return;
        setStatus("error");
      }
    }, DEBOUNCE_MS);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query, refreshKey]);

  const noResults =
    status === "idle" && results !== null && results.stations.length === 0;

  return (
    <main className="app">
      <h1 className="app-title">Train Tracker</h1>
      <SearchInput
        value={query}
        onChange={setQuery}
        onRefresh={() => setRefreshKey((k) => k + 1)}
      />

      {status === "loading" && <p className="status-text">Searching…</p>}
      {status === "error" && (
        <p className="status-text error">Something went wrong. Try again.</p>
      )}
      {noResults && (
        <p className="status-text">
          No departures found for "{results!.query}".
        </p>
      )}

      {results && results.stations.length > 0 && (
        <div className="results">
          {results.stations.map((s) => (
            <StationCard key={s.station} station={s} />
          ))}
        </div>
      )}
    </main>
  );
}
