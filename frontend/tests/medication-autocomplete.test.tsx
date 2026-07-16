import { delay, http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";

import { MedicationCheck } from "@/features/medications/medication-check";
import { API_URL } from "@/tests/mocks/handlers";
import { server } from "@/tests/mocks/server";
import { renderWithProfile, screen, userEvent, waitFor } from "@/tests/test-utils";

function suggestionResponse(query: string, suggestions: Array<{ rxcui: string; name: string; rank: number }>) {
  return HttpResponse.json({
    success: true,
    data: { query, suggestions },
    message: "Medication suggestions retrieved successfully.",
  });
}

describe("medication autocomplete", () => {
  it("does not request suggestions for fewer than two characters", async () => {
    const request = vi.fn();
    server.use(http.get(`${API_URL}/medications/suggestions`, () => {
      request();
      return suggestionResponse("a", []);
    }));
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);

    await user.type(screen.getByRole("combobox", { name: "Medication name" }), "a");
    await new Promise((resolve) => setTimeout(resolve, 450));

    expect(request).not.toHaveBeenCalled();
  });

  it("debounces the backend request", async () => {
    const request = vi.fn();
    server.use(http.get(`${API_URL}/medications/suggestions`, ({ request: incoming }) => {
      request();
      const query = new URL(incoming.url).searchParams.get("q") ?? "";
      return suggestionResponse(query, [{ rxcui: "723", name: "amoxicillin", rank: 1 }]);
    }));
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);

    await user.type(screen.getByRole("combobox", { name: "Medication name" }), "am");
    expect(request).not.toHaveBeenCalled();
    expect(await screen.findByRole("option", { name: /amoxicillin/ })).toBeVisible();
    expect(request).toHaveBeenCalledTimes(1);
  });

  it("shows multiple suggestions and never more than eight", async () => {
    const suggestions = Array.from({ length: 10 }, (_, index) => ({
      rxcui: String(700 + index),
      name: `amoxicillin option ${index + 1}`,
      rank: index + 1,
    }));
    server.use(http.get(`${API_URL}/medications/suggestions`, () => suggestionResponse("am", suggestions)));
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);

    await user.type(screen.getByRole("combobox", { name: "Medication name" }), "am");

    await screen.findByRole("option", { name: /amoxicillin option 1/ });
    expect(screen.getAllByRole("option")).toHaveLength(8);
  });

  it("selects a suggestion with Arrow Down and Enter", async () => {
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);
    const input = screen.getByRole("combobox", { name: "Medication name" });

    await user.type(input, "Fic");
    await screen.findByRole("option", { name: /Fictional medicine, RxCUI 900/ });
    await user.keyboard("{ArrowDown}{Enter}");

    expect(input).toHaveValue("Fictional medicine");
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("supports Arrow Up, Escape, and mouse selection", async () => {
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);
    const input = screen.getByRole("combobox", { name: "Medication name" });

    await user.type(input, "Fic");
    const second = await screen.findByRole("option", { name: /Fictional medicine extended release/ });
    await user.keyboard("{ArrowUp}");
    expect(second).toHaveAttribute("aria-selected", "true");
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();

    await user.click(input);
    await user.click(await screen.findByRole("option", { name: /Fictional medicine extended release/ }));
    expect(input).toHaveValue("Fictional medicine extended release");
  });

  it("shows a helpful empty result without blocking manual input", async () => {
    server.use(http.get(`${API_URL}/medications/suggestions`, () => suggestionResponse("zz", [])));
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);
    const input = screen.getByRole("combobox", { name: "Medication name" });

    await user.type(input, "zz");

    expect(await screen.findByText(/No RxNorm suggestions found/)).toBeVisible();
    expect(input).toHaveValue("zz");
  });

  it("shows RxNorm timeout as a non-blocking suggestion error", async () => {
    server.use(http.get(`${API_URL}/medications/suggestions`, () => HttpResponse.json({ detail: "RxNorm did not respond before the timeout" }, { status: 504 })));
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);
    const input = screen.getByRole("combobox", { name: "Medication name" });

    await user.type(input, "am");

    expect(await screen.findByText(/Suggestions are temporarily unavailable/)).toBeVisible();
    expect(input).toHaveValue("am");
  });

  it("shows a network failure without blocking manual input", async () => {
    server.use(http.get(`${API_URL}/medications/suggestions`, () => HttpResponse.error()));
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);
    const input = screen.getByRole("combobox", { name: "Medication name" });

    await user.type(input, "am");

    expect(await screen.findByText(/Suggestions are temporarily unavailable/)).toBeVisible();
    expect(input).toHaveValue("am");
  });

  it("ignores an older request after the user types again", async () => {
    server.use(http.get(`${API_URL}/medications/suggestions`, async ({ request }) => {
      const query = new URL(request.url).searchParams.get("q") ?? "";
      if (query === "am") {
        await delay(800);
        return suggestionResponse(query, [{ rxcui: "111", name: "stale medicine", rank: 1 }]);
      }
      return suggestionResponse(query, [{ rxcui: "723", name: "amoxicillin", rank: 1 }]);
    }));
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);
    const input = screen.getByRole("combobox", { name: "Medication name" });

    await user.type(input, "am");
    await waitFor(() => expect(screen.getByRole("listbox")).toBeInTheDocument());
    await user.type(input, "o");

    expect(await screen.findByRole("option", { name: /amoxicillin/ })).toBeVisible();
    await new Promise((resolve) => setTimeout(resolve, 850));
    expect(screen.queryByText("stale medicine")).not.toBeInTheDocument();
  });

  it("allows a manually entered medication to use the existing search", async () => {
    server.use(http.get(`${API_URL}/medications/suggestions`, () => suggestionResponse("custom medicine", [])));
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);

    await user.type(screen.getByRole("combobox", { name: "Medication name" }), "custom medicine");
    await user.click(screen.getByRole("button", { name: "View medication details" }));

    expect(await screen.findByText("Fictional medicine 10 MG")).toBeVisible();
  });

  it("exposes an accessible combobox and listbox relationship", async () => {
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);
    const input = screen.getByRole("combobox", { name: "Medication name" });

    expect(input).toHaveAttribute("aria-autocomplete", "list");
    expect(input).toHaveAttribute("aria-expanded", "false");
    await user.type(input, "Fic");
    const listbox = await screen.findByRole("listbox", { name: "Medication suggestions" });

    expect(input).toHaveAttribute("aria-expanded", "true");
    expect(input).toHaveAttribute("aria-controls", listbox.id);
  });
});
