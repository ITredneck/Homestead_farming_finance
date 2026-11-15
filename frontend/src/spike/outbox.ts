import { type DBSchema, type IDBPDatabase, openDB } from 'idb';

import { newUuid } from './uuid';

/** An entry made on this device, waiting to be sent or already sent. */
export interface OutboxEntry {
  uuid: string;
  note: string;
  clientCreatedAt: string;
  status: 'pending' | 'sent';
  attempts: number;
  lastError?: string;
  sentAt?: string;
  serverStatus?: 'created' | 'duplicate';
}

interface SpikeDatabase extends DBSchema {
  outbox: { key: string; value: OutboxEntry; indexes: { byStatus: string } };
}

export const OUTBOX_DB_NAME = 'homestead-finance-spike';

const byCreated = (a: OutboxEntry, b: OutboxEntry) =>
  a.clientCreatedAt.localeCompare(b.clientCreatedAt);

/** Entries kept in IndexedDB, so they survive reloads and the app being closed. */
export class Outbox {
  private readonly db: IDBPDatabase<SpikeDatabase>;

  private constructor(db: IDBPDatabase<SpikeDatabase>) {
    this.db = db;
  }

  static async open(name = OUTBOX_DB_NAME): Promise<Outbox> {
    const db = await openDB<SpikeDatabase>(name, 1, {
      upgrade(database) {
        const store = database.createObjectStore('outbox', { keyPath: 'uuid' });
        store.createIndex('byStatus', 'status');
      },
    });
    return new Outbox(db);
  }

  async add(note: string, uuid = newUuid(), now = new Date()): Promise<OutboxEntry> {
    const entry: OutboxEntry = {
      uuid,
      note,
      clientCreatedAt: now.toISOString(),
      status: 'pending',
      attempts: 0,
    };
    await this.db.put('outbox', entry);
    return entry;
  }

  async all(): Promise<OutboxEntry[]> {
    return (await this.db.getAll('outbox')).sort(byCreated);
  }

  async pending(): Promise<OutboxEntry[]> {
    return (await this.db.getAllFromIndex('outbox', 'byStatus', 'pending')).sort(byCreated);
  }

  async markSent(uuid: string, serverStatus: 'created' | 'duplicate', now = new Date()) {
    await this.update(uuid, (entry) => {
      entry.status = 'sent';
      entry.serverStatus = serverStatus;
      entry.sentAt = now.toISOString();
      entry.attempts += 1;
      delete entry.lastError;
    });
  }

  async markFailed(uuid: string, error: string) {
    await this.update(uuid, (entry) => {
      entry.attempts += 1;
      entry.lastError = error;
    });
  }

  async clear() {
    await this.db.clear('outbox');
  }

  close() {
    this.db.close();
  }

  private async update(uuid: string, change: (entry: OutboxEntry) => void) {
    const tx = this.db.transaction('outbox', 'readwrite');
    const entry = await tx.store.get(uuid);
    if (entry) {
      change(entry);
      await tx.store.put(entry);
    }
    await tx.done;
  }
}
