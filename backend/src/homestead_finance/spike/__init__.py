"""THROWAWAY: the M1 offline-outbox spike (#12). Removed in M2 (#119).

Receives entries that the spike page queues in IndexedDB and replays, and stores
each client UUID once, so tests in the HA app show whether replay is exactly-once.
"""
