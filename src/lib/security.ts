import { createCipheriv, createDecipheriv, createHash, randomBytes } from "node:crypto";

export function createOpaqueToken(bytes = 32) {
  return randomBytes(bytes).toString("base64url");
}

function tokenHashSecret() {
  return process.env.SESSION_SECRET ?? "local-development-session-secret";
}

export function hashToken(token: string) {
  return createHash("sha256")
    .update(tokenHashSecret())
    .update(":")
    .update(token)
    .digest("hex");
}

export function normalizeEmail(email: string) {
  return email.trim().toLowerCase();
}

export function normalizePhone(phone: string | null | undefined) {
  if (!phone) return null;
  const normalized = phone.replace(/[^\d+]/g, "");
  return normalized || null;
}

function encryptionKey() {
  const raw =
    process.env.APP_ENCRYPTION_KEY ??
    process.env.GOOGLE_CALENDAR_ENCRYPTION_KEY ??
    "local-development-calendar-token-key";
  return createHash("sha256").update(raw).digest();
}

export function currentEncryptionKeyVersion() {
  return process.env.APP_ENCRYPTION_KEY_VERSION ?? "v1";
}

export function encryptSecret(value: string | null | undefined) {
  if (!value) return null;
  const iv = randomBytes(12);
  const cipher = createCipheriv("aes-256-gcm", encryptionKey(), iv);
  const encrypted = Buffer.concat([
    cipher.update(value, "utf8"),
    cipher.final(),
  ]);
  const tag = cipher.getAuthTag();
  return [
    currentEncryptionKeyVersion(),
    iv.toString("base64url"),
    tag.toString("base64url"),
    encrypted.toString("base64url"),
  ].join(".");
}

/** Returns the stored token's key version without exposing its plaintext. */
export function encryptedSecretKeyVersion(value: string | null | undefined) {
  if (!value) return null;
  const parts = value.split(".");
  if (parts.length === 4 && /^v[0-9]+$/.test(parts[0])) return parts[0];
  // Earlier unversioned three-part payloads must not be silently treated as v2.
  return "legacy";
}

export function decryptSecret(value: string | null | undefined) {
  if (!value) return null;
  const parts = value.split(".");
  const [iv, tag, encrypted] =
    parts.length === 4 ? parts.slice(1) : parts;
  if (!iv || !tag || !encrypted) return null;
  try {
    const decipher = createDecipheriv(
      "aes-256-gcm",
      encryptionKey(),
      Buffer.from(iv, "base64url"),
    );
    decipher.setAuthTag(Buffer.from(tag, "base64url"));
    const decrypted = Buffer.concat([
      decipher.update(Buffer.from(encrypted, "base64url")),
      decipher.final(),
    ]);
    return decrypted.toString("utf8");
  } catch {
    return null;
  }
}

export function makeOrganizationSlug(name: string) {
  const base = name
    .normalize("NFKD")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 48);
  const suffix = randomBytes(3).toString("hex");

  return `${base || "organization"}-${suffix}`;
}
