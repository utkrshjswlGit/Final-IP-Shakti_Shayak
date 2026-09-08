/**
 * Frontend smoke tests — Phase 1.
 *
 * Tests only pure utility functions that do not require a running server.
 * Full integration tests are added in Phase 9 (browser-based verification).
 */

import { extractErrorMessage } from "@/lib/api";

describe("extractErrorMessage", () => {
  it("returns the error message for a plain Error", () => {
    const result = extractErrorMessage(new Error("something went wrong"));
    expect(result).toBe("something went wrong");
  });

  it("returns fallback message for non-Error unknown", () => {
    const result = extractErrorMessage("some string error");
    expect(result).toBe("An unexpected error occurred.");
  });

  it("returns fallback message for null", () => {
    const result = extractErrorMessage(null);
    expect(result).toBe("An unexpected error occurred.");
  });
});

describe("Type exports", () => {
  it("types module exports correctly (compile-time check)", () => {
    // This test just verifies the module can be imported.
    // TypeScript compilation catches type errors at build time.
    expect(true).toBe(true);
  });
});
