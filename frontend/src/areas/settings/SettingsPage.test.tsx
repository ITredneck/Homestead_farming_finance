import { screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { renderApp } from '../../test/render';

function stubApi(responses: Record<string, unknown>) {
  const fetchMock = vi.fn((request: Request) => {
    const body = responses[new URL(request.url).pathname];
    return Promise.resolve(
      body === undefined ? new Response('Not found', { status: 404 }) : Response.json(body),
    );
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('settings page', () => {
  it('shows the version and signed-in user from the API', async () => {
    const fetchMock = stubApi({
      '/api/health': { status: 'ok', version: '0.1.0', schema_revision: '0002', database: 'ok' },
      '/api/me': { user_id: 'u1', name: 'farmer', display_name: 'Farmer Jo', ingress_path: null },
    });

    renderApp('/settings');

    expect(await screen.findByText('Farmer Jo')).toBeInTheDocument();
    expect(await screen.findByText('0.1.0')).toBeInTheDocument();
    expect(screen.getByText('ok (schema 0002)')).toBeInTheDocument();
    const paths = fetchMock.mock.calls.map(([request]) => new URL(request.url).pathname);
    expect(paths).toEqual(expect.arrayContaining(['/api/health', '/api/me']));
  });

  it('says so when the server cannot be reached', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.reject(new TypeError('Failed to fetch'))),
    );

    renderApp('/settings');

    expect(await screen.findByText(/Couldn't reach the app's server/)).toBeInTheDocument();
  });

  it('links to the offline entry test', () => {
    stubApi({});

    renderApp('/settings');

    expect(screen.getByRole('link', { name: 'Offline entry test' })).toBeInTheDocument();
  });
});
