import { describe, expect, it } from 'vitest';

import { apiBaseUrl } from './client';

describe('apiBaseUrl', () => {
  it.each([
    [
      'https://ha.example/api/hassio_ingress/tok123/',
      'https://ha.example/api/hassio_ingress/tok123',
    ],
    [
      'https://ha.example/api/hassio_ingress/tok123/#/animals',
      'https://ha.example/api/hassio_ingress/tok123',
    ],
    [
      'https://ha.example/api/hassio_ingress/tok123',
      'https://ha.example/api/hassio_ingress/tok123',
    ],
    [
      'https://ha.example/api/hassio_ingress/tok123/index.html',
      'https://ha.example/api/hassio_ingress/tok123',
    ],
    [
      'http://homeassistant.local:8123/api/hassio_ingress/x/',
      'http://homeassistant.local:8123/api/hassio_ingress/x',
    ],
    ['http://localhost:5173/#/settings', 'http://localhost:5173'],
  ])('derives the API base from %s', (page, expected) => {
    expect(apiBaseUrl(page)).toBe(expected);
  });
});
