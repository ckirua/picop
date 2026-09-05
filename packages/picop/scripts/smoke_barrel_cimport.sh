#!/usr/bin/env bash
# Smoke: out-of-tree extension with barrel cimport against installed picop
# (and deprecated cypy shim).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXT="${ROOT}/examples/cimport_ext"

PYTHON="${PYTHON:-python3.14}"
"$PYTHON" -c "import picop; print('picop', picop.__version__)"

cd "${EXT}"
rm -f demo.c demo*.so demo*.pyd
"$PYTHON" setup.py build_ext --inplace
"$PYTHON" -c "import demo; assert demo.check_barrel(); assert demo.check_submodule() == 2; assert demo.check_uuid(); print('barrel cimport ok')"
