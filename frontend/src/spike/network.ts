import { api } from '../api/client';
import type { OutboxEntry } from './outbox';
import type { SendResult } from './replay';

const SEND_TIMEOUT_MS = 10_000;
const PING_TIMEOUT_MS = 4_000;

/** Posts one entry. Classifies failures so the page can show why sending stopped. */
export async function sendEntry(entry: OutboxEntry): Promise<SendResult> {
  try {
    const { data, response } = await api.POST('/api/spike/entries', {
      body: { uuid: entry.uuid, note: entry.note, client_created_at: entry.clientCreatedAt },
      signal: AbortSignal.timeout(SEND_TIMEOUT_MS),
    });
    if (data) {
      return { ok: true, status: data.status };
    }
    const problem = response.status === 401 || response.status === 403 ? 'session' : 'server';
    return { ok: false, problem, message: `HTTP ${response.status}` };
  } catch (error) {
    // A web page instead of JSON usually means the Home Assistant session ran out.
    if (error instanceof SyntaxError) {
      return { ok: false, problem: 'session', message: 'got a web page instead of data' };
    }
    return { ok: false, problem: 'offline', message: describe(error) };
  }
}

/** Whether the app's server answers right now (navigator.onLine can be wrong). */
export async function canReachServer(): Promise<boolean> {
  try {
    const { response } = await api.GET('/api/health', {
      signal: AbortSignal.timeout(PING_TIMEOUT_MS),
    });
    return response.ok;
  } catch {
    return false;
  }
}

function describe(error: unknown): string {
  if (error instanceof DOMException && error.name === 'TimeoutError') {
    return 'timed out';
  }
  return error instanceof Error ? error.message : String(error);
}
