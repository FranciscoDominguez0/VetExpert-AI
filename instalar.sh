#!/usr/bin/env bash
set -e
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
echo "Instalación terminada. Edite .env y agregue GEMINI_API_KEY."

