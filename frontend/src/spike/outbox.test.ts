import 'fake-indexeddb/auto';

import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { Outbox } from './outbox';

let name: string;
let outbox: Outbox;

beforeEach(async () => {
  name = `outbox-test-${crypto.randomUUID()}`;
  outbox = await Outbox.open(name);
});

afterEach(() => {
  outbox.close();
});

describe('Outbox', () => {
  it('keeps entries waiting in the order they were made', async () => {
    await outbox.add('second', 'b', new Date('2026-11-14T10:00:02Z'));
    await outbox.add('first', 'a', new Date('2026-11-14T10:00:01Z'));

    const pending = await outbox.pending();

    expect(pending.map((entry) => entry.note)).toEqual(['first', 'second']);
    expect(pending.every((entry) => entry.status === 'pending')).toBe(true);
  });

  it('survives closing and reopening (like an app restart)', async () => {
    await outbox.add('eggs', 'a');
    outbox.close();

    outbox = await Outbox.open(name);

    expect((await outbox.pending()).map((entry) => entry.uuid)).toEqual(['a']);
  });

  it('moves sent entries out of the waiting list', async () => {
    await outbox.add('eggs', 'a');

    await outbox.markSent('a', 'created');

    expect(await outbox.pending()).toEqual([]);
    const [entry] = await outbox.all();
    expect(entry).toMatchObject({ status: 'sent', serverStatus: 'created', attempts: 1 });
  });

  it('records failed attempts and keeps the entry waiting', async () => {
    await outbox.add('eggs', 'a');

    await outbox.markFailed('a', 'offline: Failed to fetch');
    await outbox.markFailed('a', 'offline: Failed to fetch');

    const [entry] = await outbox.pending();
    expect(entry).toMatchObject({ attempts: 2, lastError: 'offline: Failed to fetch' });
  });

  it('clears everything', async () => {
    await outbox.add('eggs', 'a');

    await outbox.clear();

    expect(await outbox.all()).toEqual([]);
  });
});
