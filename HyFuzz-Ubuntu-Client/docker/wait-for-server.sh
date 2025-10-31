#!/usr/bin/env bash
set -euo pipefail
until curl -fsS http://server:8000/health; do sleep 1; done
