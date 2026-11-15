import { describe, expect, it } from 'vitest';

import { newUuid } from './uuid';

const UUID_V4 = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

describe('newUuid', () => {
  it('uses crypto.randomUUID when the page is secure', () => {
    const source = {
      randomUUID: () => '11111111-2222-4333-8444-555555555555' as const,
      getRandomValues: crypto.getRandomValues.bind(crypto),
    };

    expect(newUuid(source)).toBe('11111111-2222-4333-8444-555555555555');
  });

  it('falls back to getRandomValues on plain-HTTP pages', () => {
    const source = { getRandomValues: crypto.getRandomValues.bind(crypto) };

    expect(newUuid(source)).toMatch(UUID_V4);
  });

  it('fallback ids are unique', () => {
    const source = { getRandomValues: crypto.getRandomValues.bind(crypto) };

    const ids = new Set(Array.from({ length: 500 }, () => newUuid(source)));

    expect(ids.size).toBe(500);
  });
});
