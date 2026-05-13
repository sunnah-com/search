#!/usr/bin/env bash
# Migrate Elasticsearch data from the ./data bind mount into a named Docker
# volume (es-data). Run from the repo root on the host where the prod stack
# lives.
#
#   ./scripts/migrate-es-data.sh           # migrate
#   DRY_RUN=1 ./scripts/migrate-es-data.sh # show what would happen
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
SRC_DIR="${SRC_DIR:-$(pwd)/data}"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "error: $COMPOSE_FILE not found — run this from the repo root" >&2
  exit 1
fi

if [[ ! -d "$SRC_DIR" ]]; then
  echo "error: source data dir $SRC_DIR does not exist" >&2
  exit 1
fi

echo "==> Stopping the stack"
${DRY_RUN:+echo} docker compose -f "$COMPOSE_FILE" down

echo "==> Creating es-data volume (no-op if it already exists)"
${DRY_RUN:+echo} docker compose -f "$COMPOSE_FILE" up --no-start elasticsearch

VOLUME_NAME="$(docker compose -f "$COMPOSE_FILE" config --format json \
  | python3 -c "import json,sys; svc=json.load(sys.stdin)['services']['elasticsearch']; print(next(v['source'] for v in svc['volumes'] if v['target']=='/usr/share/elasticsearch/data'))")"

echo "==> Resolved volume name: $VOLUME_NAME"

echo "==> Copying $SRC_DIR -> volume $VOLUME_NAME (this may take a while)"
${DRY_RUN:+echo} docker run --rm \
  -v "$SRC_DIR":/from:ro \
  -v "$VOLUME_NAME":/to \
  alpine sh -c 'cp -a /from/. /to/ && chown -R 1000:1000 /to'

echo "==> Starting the stack"
${DRY_RUN:+echo} docker compose -f "$COMPOSE_FILE" up -d

echo
echo "Migration complete. Verify with:"
echo "  docker compose -f $COMPOSE_FILE logs -f elasticsearch"
echo
echo "Once ES is healthy and data looks correct, you can remove the old"
echo "bind-mount directory:"
echo "  rm -rf $SRC_DIR"
