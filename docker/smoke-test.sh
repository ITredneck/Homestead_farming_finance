#!/bin/sh
# Smoke-tests a built app image: it starts, reports health with the right version,
# serves the frontend with relative URLs only, and refuses connections that don't
# come from the ingress gateway.
# Usage: docker/smoke-test.sh <image:tag> <expected version>
set -eu
image=$1
version=$2
name="hf-smoke-$$"

cleanup() {
  docker rm -f "$name" > /dev/null 2>&1 || true
}
trap cleanup EXIT

# Default settings: the gateway and loopback (inside the container) are trusted, anyone
# else gets 403. A short health interval lets us see Docker's health status quickly.
docker run -d --name "$name" --health-interval=3s --health-start-period=60s "$image" > /dev/null

# Prints the HTTP status, then the body.
probe='import sys, urllib.error, urllib.request
try:
    with urllib.request.urlopen(sys.argv[1], timeout=3) as response:
        print(response.status)
        print(response.read().decode())
except urllib.error.HTTPError as error:
    print(error.code)
'
fetch() {
  docker exec "$name" python -c "$probe" "$1"
}

echo "Waiting for the app to start..."
tries=0
until fetch http://127.0.0.1:8099/api/health 2> /dev/null | head -n 1 | grep -q '^200$'; do
  tries=$((tries + 1))
  if [ "$tries" -ge 45 ]; then
    echo "The app did not start."
    docker logs "$name"
    exit 1
  fi
  sleep 2
done

health=$(fetch http://127.0.0.1:8099/api/health | tail -n +2)
echo "Health: $health"
echo "$health" | grep -q "\"version\":\"$version\"" || { echo "Wrong version, expected $version"; exit 1; }
echo "$health" | grep -q '"database":"ok"' || { echo "The database check failed"; exit 1; }

page=$(fetch http://127.0.0.1:8099/ | tail -n +2)
echo "$page" | grep -q 'src="./assets/' || { echo "index.html lacks relative asset URLs"; exit 1; }
if echo "$page" | grep -qE '(src|href)="/'; then
  echo "index.html has absolute URLs, which break under ingress"
  exit 1
fi

echo "Waiting for Docker's HEALTHCHECK to report healthy..."
tries=0
until [ "$(docker inspect -f '{{.State.Health.Status}}' "$name")" = "healthy" ]; do
  tries=$((tries + 1))
  if [ "$tries" -ge 30 ]; then
    echo "The container never became healthy:"
    docker inspect -f '{{json .State.Health}}' "$name"
    exit 1
  fi
  sleep 2
done

address=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$name")
status=$(docker run --rm --entrypoint python "$image" -c "$probe" "http://$address:8099/api/health" | head -n 1)
if [ "$status" != "403" ]; then
  echo "Expected 403 for a connection from outside the gateway, got $status"
  exit 1
fi

echo "--- app log"
docker logs "$name" 2>&1 | tail -n 20
echo "Smoke test passed."
