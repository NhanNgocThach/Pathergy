import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AuthShell } from "@/components/auth-shell";
import { MedicationResultPanel } from "@/features/medications/medication-result-panel";
import { messages } from "@/i18n/messages";
import { renderWithProviders, userEvent } from "@/tests/test-utils";
import type { MedicationCheckResult } from "@/types/health";

const noRecordedMatch: MedicationCheckResult = {
  history_id: 1,
  patient_id: 10,
  medication_query: "Tylenol",
  normalized_medication_name: "acetaminophen",
  medication_rxcui: "161",
  active_ingredients: [{ rxcui: "161", name: "acetaminophen" }],
  result: "NO_RECORDED_MATCH_FOUND",
  matches: [],
  message: "No recorded match found.",
  disclaimer: "Third-party text is not rendered as the product safety notice.",
};

describe("language selection", () => {
  it("keeps the Vietnamese and Chinese dictionaries complete", () => {
    const englishKeys = Object.keys(messages.en).sort();
    expect(Object.keys(messages.vi).sort()).toEqual(englishKeys);
    expect(Object.keys(messages["zh-CN"]).sort()).toEqual(englishKeys);
  });

  it("switches the shared interface to Vietnamese and persists the choice", async () => {
    const user = userEvent.setup();
    renderWithProviders(<AuthShell><div>content</div></AuthShell>);

    await user.selectOptions(screen.getByRole("combobox", { name: "Language" }), "vi");

    expect(screen.getByRole("heading", { name: "Quản lý sức khỏe cá nhân rõ ràng" })).toBeInTheDocument();
    await waitFor(() => expect(document.documentElement.lang).toBe("vi"));
    expect(window.localStorage.getItem("pathergy.locale")).toBe("vi");
  });

  it("switches the shared interface to Simplified Chinese", async () => {
    const user = userEvent.setup();
    renderWithProviders(<AuthShell><div>content</div></AuthShell>);

    await user.selectOptions(screen.getByRole("combobox", { name: "Language" }), "zh-CN");

    expect(screen.getByRole("heading", { name: "清晰管理个人健康" })).toBeInTheDocument();
  });

  it("translates medication screening results without changing clinical data", async () => {
    const user = userEvent.setup();
    renderWithProviders(<AuthShell><MedicationResultPanel result={noRecordedMatch} /></AuthShell>);

    await user.selectOptions(screen.getByRole("combobox", { name: "Language" }), "vi");

    expect(screen.getByText("Không tìm thấy trùng khớp đã ghi nhận")).toBeInTheDocument();
    expect(screen.getByText(/chỉ xác định khái niệm thuốc/i)).toBeInTheDocument();
    expect(screen.queryByText(noRecordedMatch.disclaimer)).not.toBeInTheDocument();
  });
});
