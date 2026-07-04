#!/usr/bin/env bash
# Lanceur Linux/macOS — équivalent de START.bat
# Utilise le venv du projet s'il existe, sinon python3 du système.
set -e
cd "$(dirname "$0")"

if [ -x ".venv/bin/python" ]; then
    PY=".venv/bin/python"
else
    PY="python3"
fi

exec "$PY" GUI_v3.1_modern.py "$@"
