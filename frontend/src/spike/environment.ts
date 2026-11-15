/** What the spike page reports about where it runs. Nothing here identifies the install. */

export type OriginKind = 'local' | 'remote';

export interface EnvironmentInfo {
  origin: OriginKind;
  secureContext: boolean;
  randomUuid: boolean;
  storageApi: boolean;
  androidWebView: boolean;
}

const PRIVATE_IPV4 = [
  (a: number) => a === 10,
  (a: number) => a === 127,
  (a: number, b: number) => a === 192 && b === 168,
  (a: number, b: number) => a === 172 && b >= 16 && b <= 31,
  (a: number, b: number) => a === 169 && b === 254,
];

/** Home network address (e.g. homeassistant.local, 192.168.x.x) or a remote one. */
export function classifyHost(hostname: string): OriginKind {
  const host = hostname.toLowerCase();
  if (host === 'localhost' || host.endsWith('.local') || !host.includes('.')) {
    return 'local';
  }
  const ipv4 = /^(\d+)\.(\d+)\.\d+\.\d+$/.exec(host);
  if (ipv4) {
    const a = Number(ipv4[1]);
    const b = Number(ipv4[2]);
    return PRIVATE_IPV4.some((isPrivate) => isPrivate(a, b)) ? 'local' : 'remote';
  }
  return 'remote';
}

export function describeEnvironment(): EnvironmentInfo {
  return {
    origin: classifyHost(window.location.hostname),
    secureContext: window.isSecureContext,
    randomUuid: 'randomUUID' in crypto,
    storageApi: 'storage' in navigator,
    androidWebView: navigator.userAgent.includes('Android') && /\bwv\b/.test(navigator.userAgent),
  };
}
