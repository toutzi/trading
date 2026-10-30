#!/usr/bin/env bash
# Emits the OpenAPI contract to contracts/auth-v1.yaml (deterministic).
# Run from anywhere; the script locates its own repo root.
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTRACTS_DIR="${BACKEND_DIR}/../contracts"
OUT="${CONTRACTS_DIR}/auth-v1.yaml"

mkdir -p "${CONTRACTS_DIR}"

cd "${BACKEND_DIR}"
python - "${OUT}" <<'PY'
import sys

import yaml

from app.main import app

spec = app.openapi()
out = sys.argv[1]
with open(out, "w") as fh:
    yaml.safe_dump(spec, fh, sort_keys=True, allow_unicode=True)
print(f"wrote {out}")
PY
