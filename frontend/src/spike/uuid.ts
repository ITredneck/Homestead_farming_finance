/**
 * A random version-4 UUID.
 *
 * `crypto.randomUUID` only exists on secure pages (HTTPS or localhost), and Home Assistant
 * is often opened over plain HTTP at home, so this falls back to `getRandomValues`, which
 * works everywhere.
 */
export function newUuid(
  source: Pick<Crypto, 'getRandomValues'> & Partial<Crypto> = crypto,
): string {
  if (typeof source.randomUUID === 'function') {
    return source.randomUUID();
  }
  const bytes = source.getRandomValues(new Uint8Array(16));
  bytes[6] = ((bytes[6] ?? 0) & 0x0f) | 0x40; // version 4
  bytes[8] = ((bytes[8] ?? 0) & 0x3f) | 0x80; // RFC 4122 variant
  const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
  return [
    hex.slice(0, 8),
    hex.slice(8, 12),
    hex.slice(12, 16),
    hex.slice(16, 20),
    hex.slice(20),
  ].join('-');
}
