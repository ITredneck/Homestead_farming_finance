// THROWAWAY: the M1 offline-outbox spike (#12). Removed in M2 (#119).
import {
  Badge,
  Button,
  Card,
  Code,
  Group,
  ScrollArea,
  SimpleGrid,
  Stack,
  Switch,
  Table,
  Text,
  Textarea,
  Title,
} from '@mantine/core';
import { IconCopy, IconPlus, IconRefresh, IconTrash } from '@tabler/icons-react';
import { useCallback, useEffect, useRef, useState } from 'react';

import { api } from '../api/client';
import { BackLink } from '../components/BackLink';
import { describeEnvironment } from './environment';
import { canReachServer, sendEntry } from './network';
import { Outbox, type OutboxEntry } from './outbox';
import { replayPending } from './replay';

const AUTO_ADD_MS = 2_000;
const RETRY_MS = 10_000;
const PING_MS = 5_000;
const MAX_EVENTS = 200;

interface LogEvent {
  at: string;
  message: string;
}

interface ServerSummary {
  total: number;
  duplicates: number;
}

const clock = (iso: string) => new Date(iso).toLocaleTimeString();

export function OutboxSpikePage() {
  const outboxRef = useRef<Outbox | null>(null);
  const replayingRef = useRef(false);
  const lastFailureRef = useRef<string | null>(null);
  const reachableRef = useRef<boolean | null>(null);

  const [entries, setEntries] = useState<OutboxEntry[]>([]);
  const [online, setOnline] = useState(navigator.onLine);
  const [reachable, setReachable] = useState<boolean | null>(null);
  const [autoAdd, setAutoAdd] = useState(false);
  const [events, setEvents] = useState<LogEvent[]>([]);
  const [server, setServer] = useState<ServerSummary | null>(null);
  const [lastSent, setLastSent] = useState<string | null>(null);
  const [persisted, setPersisted] = useState<boolean | null>(null);
  const [copied, setCopied] = useState(false);
  const [environment] = useState(describeEnvironment);

  const log = useCallback((message: string) => {
    setEvents((current) =>
      [{ at: new Date().toISOString(), message }, ...current].slice(0, MAX_EVENTS),
    );
  }, []);

  const refreshEntries = useCallback(async () => {
    const outbox = outboxRef.current;
    if (outbox) {
      setEntries(await outbox.all());
    }
  }, []);

  const refreshServer = useCallback(async () => {
    try {
      const { data } = await api.GET('/api/spike/summary', { signal: AbortSignal.timeout(5_000) });
      if (data) {
        setServer({ total: data.total, duplicates: data.duplicates_received });
      }
    } catch {
      // Offline: keep showing the last known numbers.
    }
  }, []);

  const replay = useCallback(
    async (reason: string) => {
      const outbox = outboxRef.current;
      if (!outbox || replayingRef.current) {
        return;
      }
      replayingRef.current = true;
      try {
        if ((await outbox.pending()).length === 0) {
          return;
        }
        const report = await replayPending(outbox, sendEntry);
        if (report.sent > 0) {
          const dupes = report.duplicates > 0 ? `, ${report.duplicates} already on the server` : '';
          log(`Sent ${report.sent} (${reason})${dupes}`);
          setLastSent(new Date().toISOString());
          lastFailureRef.current = null;
        }
        if (report.failed) {
          const failure = `${report.failed.problem}: ${report.failed.message}`;
          if (failure !== lastFailureRef.current) {
            log(`Sending stopped (${failure})`);
            lastFailureRef.current = failure;
          }
        }
        await refreshEntries();
        await refreshServer();
      } finally {
        replayingRef.current = false;
      }
    },
    [log, refreshEntries, refreshServer],
  );

  const ping = useCallback(async () => {
    const ok = await canReachServer();
    if (reachableRef.current !== null && reachableRef.current !== ok) {
      log(ok ? 'Server reachable again' : 'Server unreachable');
    }
    reachableRef.current = ok;
    setReachable(ok);
  }, [log]);

  const addEntry = useCallback(
    async (note: string) => {
      const outbox = outboxRef.current;
      if (!outbox) {
        return;
      }
      await outbox.add(note);
      await refreshEntries();
      await replay('new entry');
    },
    [refreshEntries, replay],
  );

  const clearAll = useCallback(async () => {
    await outboxRef.current?.clear();
    try {
      await api.DELETE('/api/spike/entries');
      log('Test data cleared on this device and on the server');
    } catch {
      log('Cleared this device only: the server could not be reached');
    }
    await refreshEntries();
    await refreshServer();
  }, [log, refreshEntries, refreshServer]);

  // Open the outbox once; send anything left over from earlier visits.
  useEffect(() => {
    let cancelled = false;
    Outbox.open()
      .then(async (outbox) => {
        if (cancelled) {
          outbox.close();
          return;
        }
        outboxRef.current = outbox;
        log('Page opened');
        await refreshEntries();
        await ping();
        await refreshServer();
        await replay('page opened');
      })
      .catch((error: unknown) => {
        log(`Could not open the outbox: ${String(error)}`);
      });
    if ('storage' in navigator) {
      navigator.storage
        .persisted()
        .then(setPersisted)
        .catch(() => {
          setPersisted(null);
        });
    }
    return () => {
      cancelled = true;
      outboxRef.current?.close();
      outboxRef.current = null;
    };
  }, [log, ping, refreshEntries, refreshServer, replay]);

  // Connection signals from the browser and the page.
  useEffect(() => {
    const onOnline = () => {
      setOnline(true);
      log('Browser says: online');
      void replay('back online');
    };
    const onOffline = () => {
      setOnline(false);
      log('Browser says: offline');
    };
    const onVisibility = () => {
      if (document.visibilityState === 'visible') {
        log('Page visible again');
        void replay('page visible');
      }
    };
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    document.addEventListener('visibilitychange', onVisibility);
    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, [log, replay]);

  // Retry waiting entries and check the server on a timer.
  useEffect(() => {
    const retry = window.setInterval(() => void replay('timer'), RETRY_MS);
    const check = window.setInterval(() => void ping(), PING_MS);
    return () => {
      window.clearInterval(retry);
      window.clearInterval(check);
    };
  }, [ping, replay]);

  useEffect(() => {
    if (!autoAdd) {
      return;
    }
    let count = 0;
    const timer = window.setInterval(() => {
      count += 1;
      void addEntry(`auto ${count}`);
    }, AUTO_ADD_MS);
    return () => {
      window.clearInterval(timer);
    };
  }, [autoAdd, addEntry]);

  const pending = entries.filter((entry) => entry.status === 'pending');
  const sent = entries.filter((entry) => entry.status === 'sent');
  const yesNo = (value: boolean) => (value ? 'yes' : 'no');

  const status: [string, string][] = [
    ['Browser says', online ? 'online' : 'offline'],
    ['Server reachable', reachable === null ? 'checking…' : yesNo(reachable)],
    ['Address', environment.origin === 'local' ? 'home network' : 'remote'],
    ['Secure page (HTTPS)', yesNo(environment.secureContext)],
    ['Storage kept', persisted === null ? 'unknown' : persisted ? 'yes' : 'may be cleared'],
    ['Last sent', lastSent ? clock(lastSent) : 'not yet'],
  ];

  const report = JSON.stringify(
    {
      generatedAt: new Date().toISOString(),
      environment,
      persistedStorage: persisted,
      browserOnline: online,
      serverReachable: reachable,
      waiting: pending.length,
      sent: sent.length,
      duplicateAcks: sent.filter((entry) => entry.serverStatus === 'duplicate').length,
      server,
      events: events.slice(0, 50),
    },
    null,
    2,
  );

  const canCopy = window.isSecureContext && 'clipboard' in navigator;
  const copyReport = async () => {
    await navigator.clipboard.writeText(report);
    setCopied(true);
  };

  return (
    <Stack>
      <BackLink />
      <Title order={2}>Offline entry test</Title>
      <Text>
        Add test entries, also with no connection. They wait on this device and are sent when the
        connection is back. Each one should reach the server exactly once.
      </Text>

      <Card withBorder>
        <Group justify="space-between" mb="xs">
          <Title order={3} size="h4">
            Status
          </Title>
          <Badge size="xl" color={pending.length > 0 ? 'orange' : 'green'}>
            {pending.length} waiting
          </Badge>
        </Group>
        <Table variant="vertical" layout="fixed">
          <Table.Tbody>
            {status.map(([label, value]) => (
              <Table.Tr key={label}>
                <Table.Th w={170}>{label}</Table.Th>
                <Table.Td>{value}</Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </Card>

      <SimpleGrid cols={{ base: 1, sm: 2 }}>
        <Button leftSection={<IconPlus />} onClick={() => void addEntry('manual')}>
          Add test entry
        </Button>
        <Button variant="light" leftSection={<IconRefresh />} onClick={() => void replay('button')}>
          Send now
        </Button>
      </SimpleGrid>
      <Switch
        size="lg"
        checked={autoAdd}
        onChange={(event) => {
          setAutoAdd(event.currentTarget.checked);
        }}
        label="Add an entry every 2 seconds"
      />

      <Card withBorder>
        <Group justify="space-between">
          <Text>
            Server:{' '}
            {server
              ? `${server.total} stored, ${server.duplicates} duplicates received`
              : 'not loaded yet'}
          </Text>
          <Button size="sm" variant="subtle" onClick={() => void refreshServer()}>
            Refresh
          </Button>
        </Group>
      </Card>

      <Card withBorder>
        <Title order={3} size="h4" mb="xs">
          Waiting on this device
        </Title>
        {pending.length === 0 ? (
          <Text c="dimmed">Nothing waiting. {sent.length} sent so far.</Text>
        ) : (
          <Stack gap={4}>
            {pending.slice(0, 20).map((entry) => (
              <Text key={entry.uuid} size="sm">
                {clock(entry.clientCreatedAt)} · {entry.note} · tries: {entry.attempts}
                {entry.lastError ? ` · ${entry.lastError}` : ''}
              </Text>
            ))}
          </Stack>
        )}
      </Card>

      <Card withBorder>
        <Title order={3} size="h4" mb="xs">
          Event log
        </Title>
        <ScrollArea h={220}>
          <Code block>
            {events.map((event) => `${clock(event.at)}  ${event.message}`).join('\n') || '—'}
          </Code>
        </ScrollArea>
      </Card>

      <Card withBorder>
        <Title order={3} size="h4" mb="xs">
          Report for the issue
        </Title>
        <Text size="sm" mb="xs">
          No addresses or device details are included.
          {canCopy ? '' : ' Copying needs HTTPS: select the text and copy it by hand.'}
        </Text>
        <Textarea readOnly autosize minRows={4} maxRows={12} value={report} />
        {canCopy && (
          <Button
            mt="sm"
            variant="light"
            leftSection={<IconCopy />}
            onClick={() => void copyReport()}
          >
            {copied ? 'Copied' : 'Copy report'}
          </Button>
        )}
      </Card>

      <Button
        color="red"
        variant="light"
        leftSection={<IconTrash />}
        onClick={() => void clearAll()}
      >
        Clear test data
      </Button>
    </Stack>
  );
}
