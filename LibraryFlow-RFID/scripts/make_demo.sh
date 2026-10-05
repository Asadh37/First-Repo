#!/usr/bin/env bash
set -euo pipefail
python -m app.seed
python scripts/generate_sample_migration.py
printf '\nDemo data prepared. Start the app with: uvicorn app.main:app --reload\n'
