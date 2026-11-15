import { useQuery } from '@tanstack/react-query';

import { api } from './client';

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const { data, response } = await api.GET('/api/health');
      if (!response.ok) {
        throw new Error(`Health check failed (HTTP ${response.status})`);
      }
      return data;
    },
  });
}

export function useFarm() {
  return useQuery({
    queryKey: ['farm'],
    queryFn: async () => {
      const { data, response } = await api.GET('/api/farm');
      if (!response.ok) {
        throw new Error(`Could not load the farm (HTTP ${response.status})`);
      }
      return data;
    },
  });
}

export function useMe() {
  return useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const { data, response } = await api.GET('/api/me');
      if (!response.ok) {
        throw new Error(`Could not load the signed-in user (HTTP ${response.status})`);
      }
      return data;
    },
  });
}
