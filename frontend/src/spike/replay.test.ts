import 'fake-indexeddb/auto';

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { Outbox, type OutboxEntry } from './outbox';
import { replayPending, type Sender, type SendResult } from './replay';

let outbox: Outbox;

beforeEach(async () => {
  outbox = await Outbox.open(`replay-test-${crypto.randomUUID()}`);
  await outbox.add('one', 'a', new Date('2026-11-14T10:00:01Z'));
  await outbox.add('two', 'b', new Date('2026-11-14T10:00:02Z'));
  await outbox.add('three', 'c', new Date('2026-11-14T10:00:03Z'));
});

afterEach(() => {
  outbox.close();
});

const created = (): Promise<SendResult> => Promise.resolve({ ok: true, status: 'created' });

describe('replayPending', () => {
  it('sends waiting entries oldest first and marks them sent', async () => {
    const send = vi.fn<Sender>(created);

    const report = await replayPending(outbox, send);

    expect(send.mock.calls.map(([entry]) => entry.uuid)).toEqual(['a', 'b', 'c']);
    expect(report).toEqual({ sent: 3, duplicates: 0 });
    expect(await outbox.pending()).toEqual([]);
  });

  it('counts entries the server already had as sent duplicates', async () => {
    const send = vi.fn((entry: OutboxEntry): Promise<SendResult> =>
      Promise.resolve({ ok: true, status: entry.uuid === 'b' ? 'duplicate' : 'created' }),
    );

    const report = await replayPending(outbox, send);

    expect(report).toEqual({ sent: 3, duplicates: 1 });
  });

  it('stops at the first failure and keeps the rest waiting, in order', async () => {
    const send = vi.fn((entry: OutboxEntry): Promise<SendResult> =>
      entry.uuid === 'b'
        ? Promise.resolve({ ok: false, problem: 'offline', message: 'Failed to fetch' })
        : created(),
    );

    const report = await replayPending(outbox, send);

    expect(report).toEqual({
      sent: 1,
      duplicates: 0,
      failed: { problem: 'offline', message: 'Failed to fetch' },
    });
    expect(send).toHaveBeenCalledTimes(2);
    expect((await outbox.pending()).map((entry) => entry.uuid)).toEqual(['b', 'c']);
  });

  it('never resends an entry that was already sent', async () => {
    const send = vi.fn<Sender>(created);

    await replayPending(outbox, send);
    await replayPending(outbox, send);

    expect(send).toHaveBeenCalledTimes(3);
  });
});
