#!/bin/bash

# Oracle AIDP MCP Server - Startup Script
# This script activates the virtual environment and starts the MCP server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
export AIDP_CONFIG="$SCRIPT_DIR/config/aidp_config.yaml"

# Set instance name (default to first instance in config if not specified)
if [ -z "$AIDP_INSTANCE" ]; then
    export AIDP_INSTANCE="my-instance"
fi

# Start the server
exec python src/server.py
