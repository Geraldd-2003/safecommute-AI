#!/usr/bin/env bash
# SafeCommute AI - macOS / Linux launcher:  bash run_app.sh
cd "$(dirname "$0")"
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/python -m pip install -q -r requirements.txt
.venv/bin/python -m streamlit run app.py
