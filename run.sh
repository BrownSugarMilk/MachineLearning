#!/usr/bin/env bash
# 一键运行完整实验（Linux / macOS）
set -euo pipefail
cd "$(dirname "$0")"

if [ -d "my_venv" ]; then
  source my_venv/bin/activate
fi

python run.py
