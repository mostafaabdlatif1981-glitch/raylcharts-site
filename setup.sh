#!/bin/bash
# يركّب أدوات تقارير القطاعات في /home/claude (من فرع rayl-tools)
set -e
SRC="$(cd "$(dirname "$0")" && pwd)/home"
cp -rn "$SRC"/. /home/claude/ 2>/dev/null || true
cp -r "$SRC"/. /home/claude/
pip install --break-system-packages -q playwright websocket-client requests 2>/dev/null || true
python3 -m playwright install chromium >/dev/null 2>&1 || true
echo SETUP_OK
