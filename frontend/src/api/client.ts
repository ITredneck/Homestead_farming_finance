import createClient from 'openapi-fetch';

import type { paths } from './generated/schema';

/**
 * The API is served next to the page, under Home Assistant's ingress path (which changes
 * per install), so its base URL is derived from the page URL at runtime, never hardcoded.
 */
export function apiBaseUrl(pageUrl: string = window.location.href): string {
  const url = new URL(pageUrl);
  let path = url.pathname.replace(/index\.html$/, '');
  if (!path.endsWith('/')) {
    path += '/';
  }
  return `${url.origin}${path}`.replace(/\/$/, '');
}

export const api = createClient<paths>({
  baseUrl: apiBaseUrl(),
  // Look up fetch per request (not once at startup) so tests can stub it.
  fetch: (request) => globalThis.fetch(request),
});
