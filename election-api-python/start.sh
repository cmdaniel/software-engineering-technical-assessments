#!/usr/bin/env bash

# Start a local Spark standalone cluster using Docker Compose.
#
# Usage:
#   ./start.sh            # starts with default of 3 workers
#   ./start.sh 5          # starts with 5 workers
#   ./start.sh down       # scales workers down to 0
#
# Notes:
# - This script uses the scalable 'spark-worker' service in docker-compose.spark.yml.
# - Worker scaling in Docker Compose is manual (not autoscaling).

set -euo pipefail

DEFAULT_WORKERS=3
ARG="${1:-$DEFAULT_WORKERS}"
COMPOSE_FILE="docker-compose.spark.yml"

if [[ "$ARG" == "down" ]]; then
  WORKERS=0
else
  WORKERS="$ARG"
  if ! [[ "$WORKERS" =~ ^[0-9]+$ ]] || [[ "$WORKERS" -lt 1 ]]; then
    echo "Error: worker count must be a positive integer or 'down'." >&2
    echo "Usage: ./start.sh [worker_count|down]" >&2
    exit 1
  fi
fi

if [[ "$WORKERS" -eq 0 ]]; then
  echo "Scaling Spark workers down to 0..."
else
  echo "Starting Spark cluster with $WORKERS worker(s)..."
fi

docker compose -f "$COMPOSE_FILE" up -d --scale spark-worker="$WORKERS"

echo "Spark master UI: http://localhost:8080"
echo "Workers running: $WORKERS"
