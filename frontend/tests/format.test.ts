import { describe, expect, it } from "vitest";

import { formatPersonName } from "@/lib/format";

describe("formatPersonName", () => {
  it("uses given-name-first order in English", () => {
    expect(formatPersonName("Phương Vy", "Nguyễn Thị", "en")).toBe(
      "Phương Vy Nguyễn Thị",
    );
  });

  it.each(["vi", "zh-CN"] as const)(
    "uses family-name-first order for %s",
    (locale) => {
      expect(formatPersonName("Phương Vy", "Nguyễn Thị", locale)).toBe(
        "Nguyễn Thị Phương Vy",
      );
    },
  );
});
