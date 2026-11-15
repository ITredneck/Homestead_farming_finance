"""Constants shared by the tests."""

from __future__ import annotations

#: The ingress gateway (the Supervisor) and an address that is not it.
GATEWAY = ("172.30.32.2", 50000)
OUTSIDER = ("10.0.0.5", 50000)

#: Identity headers as HA ingress sends them.
USER_HEADERS = {
    "X-Remote-User-Id": "8d1c0e3f0c2a4b6e9f1a2b3c4d5e6f70",
    "X-Remote-User-Name": "farmer",
    "X-Remote-User-Display-Name": "Farmer Jo",
}
