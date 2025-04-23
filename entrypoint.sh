#!/bin/sh
alembic upgrade head
echo "migration done"
uvicorn main:app --host 0.0.0.0 --port 8000