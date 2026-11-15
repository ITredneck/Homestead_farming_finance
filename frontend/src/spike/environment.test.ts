import { describe, expect, it } from 'vitest';

import { classifyHost } from './environment';

describe('classifyHost', () => {
  it.each([
    ['homeassistant.local', 'local'],
    ['localhost', 'local'],
    ['homeassistant', 'local'],
    ['192.168.1.20', 'local'],
    ['10.0.0.8', 'local'],
    ['172.20.1.4', 'local'],
    ['127.0.0.1', 'local'],
    ['abc123.ui.nabu.casa', 'remote'],
    ['ha.example.org', 'remote'],
    ['203.0.113.7', 'remote'],
    ['172.32.0.1', 'remote'],
  ])('%s is %s', (host, kind) => {
    expect(classifyHost(host)).toBe(kind);
  });
});
