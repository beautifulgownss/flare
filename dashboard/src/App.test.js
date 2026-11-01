import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import App from "./App";

beforeEach(() => {
  global.fetch = jest.fn(() =>
    Promise.resolve({ json: () => Promise.resolve([]) })
  );
});

afterEach(() => {
  delete global.fetch;
});

test("renders the dashboard header and every tab", async () => {
  render(<App />);
  expect(screen.getByRole("heading", { name: /gtm enrichment pipeline/i })).toBeInTheDocument();
  for (const label of [
    "Account prioritization",
    "Email sequences",
    "Live signals",
    "Run history",
    "HubSpot sync",
    "Pitch pages",
  ]) {
    expect(screen.getByRole("button", { name: label })).toBeInTheDocument();
  }
  await waitFor(() => expect(global.fetch).toHaveBeenCalledWith("/companies_final.json"));
});

test("switching tabs does not crash with empty data", async () => {
  render(<App />);
  for (const label of ["Email sequences", "Live signals", "Run history", "HubSpot sync", "Pitch pages"]) {
    fireEvent.click(screen.getByRole("button", { name: label }));
  }
  await waitFor(() => expect(global.fetch).toHaveBeenCalledTimes(6));
});
