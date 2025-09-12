#!/bin/bash

# Activar entorno virtual y ejecutar backend
cd /home/giovanemere/ia-ops/ia-ops-dev-core
source venv/bin/activate
cd api
uvicorn docs_backend:app --host 0.0.0.0 --port 8846 --reload
