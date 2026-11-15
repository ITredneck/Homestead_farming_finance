import type { Outbox, OutboxEntry } from './outbox';

export type Problem = 'offline' | 'session' | 'server';

export type SendResult =
  { ok: true; status: 'created' | 'duplicate' } | { ok: false; problem: Problem; message: string };

export type Sender = (entry: OutboxEntry) => Promise<SendResult>;

export interface ReplayReport {
  sent: number;
  duplicates: number;
  failed?: { problem: Problem; message: string };
}

/**
 * Sends waiting entries oldest first. Stops at the first failure, so entries keep their
 * order and a dropped connection doesn't burn through every retry at once.
 */
export async function replayPending(outbox: Outbox, send: Sender): Promise<ReplayReport> {
  const report: ReplayReport = { sent: 0, duplicates: 0 };
  for (const entry of await outbox.pending()) {
    const result = await send(entry);
    if (!result.ok) {
      await outbox.markFailed(entry.uuid, `${result.problem}: ${result.message}`);
      report.failed = { problem: result.problem, message: result.message };
      return report;
    }
    await outbox.markSent(entry.uuid, result.status);
    report.sent += 1;
    if (result.status === 'duplicate') {
      report.duplicates += 1;
    }
  }
  return report;
}
