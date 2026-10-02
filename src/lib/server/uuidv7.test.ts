import { describe, expect, it } from "vitest";

import { generateUuidV7 } from "./uuidv7";

describe("generateUuidV7", () => {
  it("generates an RFC 9562 UUIDv7 with the expected variant", () => {
    const id = generateUuidV7(1_700_000_000_000);

    expect(id).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/,
    );
  });

  it("encodes Unix epoch milliseconds in the first 48 bits", () => {
    const timestampMs = 1_700_000_000_123;
    const id = generateUuidV7(timestampMs);
    const encodedTimestampHex = id.replaceAll("-", "").slice(0, 12);

    expect(Number.parseInt(encodedTimestampHex, 16)).toBe(timestampMs);
  });

  it("sorts by generation time when timestamps differ", () => {
    const earlier = generateUuidV7(1_700_000_000_000);
    const later = generateUuidV7(1_700_000_000_001);

    expect(earlier < later).toBe(true);
  });

  it("rejects invalid timestamps", () => {
    expect(() => generateUuidV7(-1)).toThrow(RangeError);
    expect(() => generateUuidV7(Number.NaN)).toThrow(RangeError);
    expect(() => generateUuidV7(2 ** 48)).toThrow(RangeError);
  });
});
