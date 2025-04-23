#!/bin/sh
alembic upgrade head
echo "migration done"
uvicorn main:app --host 127.0.0.1 --port 8000