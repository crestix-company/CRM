import { afterEach, describe, expect, it } from "vitest";
import {
  currentEncryptionKeyVersion,
  decryptSecret,
  encryptedSecretKeyVersion,
  encryptSecret,
} from "./security";

const originalKey = process.env.APP_ENCRYPTION_KEY;
const originalVersion = process.env.APP_ENCRYPTION_KEY_VERSION;

afterEach(() => {
  if (originalKey === undefined) delete process.env.APP_ENCRYPTION_KEY;
  else process.env.APP_ENCRYPTION_KEY = originalKey;
  if (originalVersion === undefined) delete process.env.APP_ENCRYPTION_KEY_VERSION;
  else process.env.APP_ENCRYPTION_KEY_VERSION = originalVersion;
});

describe("Google Calendar encryption envelope", () => {
  it("identifies existing v1 and new v2 tokens without decrypting", () => {
    process.env.APP_ENCRYPTION_KEY = "test-key";
    process.env.APP_ENCRYPTION_KEY_VERSION = "v1";
    const v1 = encryptSecret("test-token");
    process.env.APP_ENCRYPTION_KEY_VERSION = "v2";
    const v2 = encryptSecret("test-token");
    expect(encryptedSecretKeyVersion(v1)).toBe("v1");
    expect(encryptedSecretKeyVersion(v2)).toBe("v2");
    expect(currentEncryptionKeyVersion()).toBe("v2");
  });

  it("keeps unversioned and malformed payloads out of v2", () => {
    expect(encryptedSecretKeyVersion("abc.def.ghi")).toBe("legacy");
    expect(encryptedSecretKeyVersion("not-a-token")).toBe("legacy");
    expect(encryptedSecretKeyVersion(null)).toBeNull();
  });

  it("does not decrypt an existing token using a different secret key", () => {
    process.env.APP_ENCRYPTION_KEY_VERSION = "v1";
    process.env.APP_ENCRYPTION_KEY = "old-test-secret";
    const old = encryptSecret("keep-existing-token");
    process.env.APP_ENCRYPTION_KEY = "new-test-secret";
    process.env.APP_ENCRYPTION_KEY_VERSION = "v2";
    expect(decryptSecret(old)).toBeNull();
    expect(encryptedSecretKeyVersion(old)).toBe("v1");
  });
});
