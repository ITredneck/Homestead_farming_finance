import { Button, Card, Stack, Table, Text, Title } from '@mantine/core';
import { IconFlask } from '@tabler/icons-react';
import { Link } from 'react-router';

import { useHealth, useMe } from '../../api/hooks';
import { BackLink } from '../../components/BackLink';

export function SettingsPage() {
  const health = useHealth();
  const me = useMe();

  const rows: [string, string][] = [
    ['Signed in as', me.data ? (me.data.display_name ?? me.data.name ?? 'Unknown') : '…'],
    ['Version', health.data?.version ?? '…'],
    [
      'Database',
      health.data ? `${health.data.database} (schema ${health.data.schema_revision ?? '?'})` : '…',
    ],
  ];

  return (
    <Stack>
      <BackLink />
      <Title order={2}>Settings</Title>
      <Card withBorder>
        <Title order={3} size="h4" mb="sm">
          About
        </Title>
        {health.isError || me.isError ? (
          <Text c="red">Couldn't reach the app's server. Check your connection and reload.</Text>
        ) : (
          <Table variant="vertical" layout="fixed" withTableBorder={false}>
            <Table.Tbody>
              {rows.map(([label, value]) => (
                <Table.Tr key={label}>
                  <Table.Th w={140}>{label}</Table.Th>
                  <Table.Td>{value}</Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        )}
      </Card>
      <Card withBorder>
        <Title order={3} size="h4" mb="xs">
          Diagnostics
        </Title>
        <Text mb="md">Tools for testing this early version.</Text>
        <Button component={Link} to="/spike" variant="light" leftSection={<IconFlask />}>
          Offline entry test
        </Button>
      </Card>
    </Stack>
  );
}
