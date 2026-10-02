import { describe, expect, it } from "vitest";
import { uuidv7 } from "./uuidv7";

describe("uuidv7", () => {
  it("emits RFC4122 variant UUID version 7", () => {
    const id = uuidv7(1_791_000_000_000);
    expect(id).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/,
    );
  });
});
