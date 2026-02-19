#!/bin/bash
cd /ssd/prospector
source .venv/bin/activate
exec python mcp-server/server.py
