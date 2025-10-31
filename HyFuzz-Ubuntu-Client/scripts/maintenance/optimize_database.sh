#!/usr/bin/env bash
set -euo pipefail
sqlite3 data/database/client.db 'VACUUM;'
