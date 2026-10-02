import { randomBytes } from "node:crypto";

/**
 * Generate an RFC 9562 UUIDv7.
 *
 * - The most-significant 48 bits contain Unix epoch milliseconds.
 * - Version bits are set to 7.
 * - Variant bits are set to RFC 9562 variant 10xx.
 *
 * UUID ordering is NOT the business source of truth for chronology.
 * Always use created_at / createdAt for application ordering and reporting.
 */
export function generateUuidV7(nowMs: number = Date.now()): string {
  if (!Number.isSafeInteger(nowMs) || nowMs < 0 || nowMs >= 2 ** 48) {
    throw new RangeError("UUIDv7 timestamp must be an integer in the unsigned 48-bit range.");
  }

  const bytes = randomBytes(16);
  let timestamp = nowMs;

  for (let index = 5; index >= 0; index -= 1) {
    bytes[index] = timestamp % 256;
    timestamp = Math.floor(timestamp / 256);
  }

  bytes[6] = (bytes[6] & 0x0f) | 0x70;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;

  const hex = bytes.toString("hex");

  return [
    hex.slice(0, 8),
    hex.slice(8, 12),
    hex.slice(12, 16),
    hex.slice(16, 20),
    hex.slice(20),
  ].join("-");
}
