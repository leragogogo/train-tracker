import { render, screen, act, fireEvent } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach, afterEach } from "vitest";
import App from "../src/App";
import { fetchDepartures } from "../src/api/departures";

vi.mock("../src/api/departures");

const mockData = {
  query: "Bru",
  stations: [
    {
      station: "Bruges",
      departures: [
        {
          train_number: "BE.NMBS.IC1234",
          destination: "Ghent",
          scheduled_departure: "2024-01-15T14:30:00",
          delay_minutes: 0,
        },
      ],
    },
  ],
};

describe("App", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it("does not fetch when query is shorter than 3 chars", async () => {
    render(<App />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "Br" } });
    await act(async () => {
      await vi.runAllTimersAsync();
    });
    expect(fetchDepartures).not.toHaveBeenCalled();
  });

  it("fetches after the debounce fires with 3+ chars", async () => {
    vi.mocked(fetchDepartures).mockResolvedValue(mockData);
    render(<App />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "Bru" } });
    await act(async () => {
      await vi.runAllTimersAsync();
    });
    expect(fetchDepartures).toHaveBeenCalledWith(
      "Bru",
      expect.any(AbortSignal),
    );
  });

  it("shows Searching… while fetching", async () => {
    vi.mocked(fetchDepartures).mockReturnValue(new Promise(() => {}));
    render(<App />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "Bru" } });
    await act(async () => {
      vi.advanceTimersByTime(300);
    });
    expect(screen.getByText(/searching/i)).toBeInTheDocument();
  });

  it("renders station cards when fetch resolves", async () => {
    vi.mocked(fetchDepartures).mockResolvedValue(mockData);
    render(<App />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "Bru" } });
    await act(async () => {
      await vi.runAllTimersAsync();
    });
    expect(screen.getByText("Bruges")).toBeInTheDocument();
  });

  it('shows "No departures found" when stations array is empty', async () => {
    vi.mocked(fetchDepartures).mockResolvedValue({
      query: "Zzz",
      stations: [],
    });
    render(<App />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "Zzz" } });
    await act(async () => {
      await vi.runAllTimersAsync();
    });
    expect(screen.getByText(/no departures found/i)).toBeInTheDocument();
  });

  it("shows error message when fetch throws", async () => {
    vi.mocked(fetchDepartures).mockRejectedValue(new Error("Network error"));
    render(<App />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "Bru" } });
    await act(async () => {
      await vi.runAllTimersAsync();
    });
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
  });

  it("re-fetches when refresh is clicked without changing the query", async () => {
    vi.mocked(fetchDepartures).mockResolvedValue(mockData);
    render(<App />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "Bru" } });
    await act(async () => {
      await vi.runAllTimersAsync();
    });
    expect(fetchDepartures).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole("button", { name: /refresh/i }));
    await act(async () => {
      await vi.runAllTimersAsync();
    });

    expect(fetchDepartures).toHaveBeenCalledTimes(2);
    expect(screen.getByRole("textbox")).toHaveValue("Bru");
  });
});
