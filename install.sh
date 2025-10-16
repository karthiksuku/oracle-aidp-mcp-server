#!/bin/bash

# Oracle AIDP MCP Server - Installation Script
# This script sets up the Python environment and installs dependencies

set -e  # Exit on error

echo "======================================================================"
echo "Oracle AIDP MCP Server - Installation"
echo "======================================================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Installing to: $SCRIPT_DIR"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    PYTHON_CMD="python"
else
    echo "ERROR: Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Found Python $PYTHON_VERSION"

# Check if Python version is 3.8 or higher
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "ERROR: Python 3.8 or higher is required. Found $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python version is compatible"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

$PYTHON_CMD -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create config directory if it doesn't exist
echo "Setting up configuration..."
mkdir -p config
mkdir -p logs

# Check if config file exists
if [ ! -f "config/aidp_config.yaml" ]; then
    echo "⚠️  Configuration file not found!"
    echo ""
    echo "Please create config/aidp_config.yaml from config/aidp_config.example.yaml"
    echo "and update it with your AIDP instance details:"
    echo ""
    echo "  cp config/aidp_config.example.yaml config/aidp_config.yaml"
    echo ""
    echo "Then edit config/aidp_config.yaml with your:"
    echo "  - AIDP instance OCID"
    echo "  - OCI region"
    echo "  - Compartment OCID"
    echo "  - Object Storage namespace"
    echo ""
else
    echo "✓ Configuration file found"
fi

# Check OCI config
echo ""
echo "Checking OCI configuration..."
if [ -f "$HOME/.oci/config" ]; then
    echo "✓ OCI config found at ~/.oci/config"
else
    echo "⚠️  OCI config not found!"
    echo ""
    echo "Please configure OCI CLI:"
    echo "  oci setup config"
    echo ""
fi

# Make run script executable
echo ""
echo "Making run script executable..."
chmod +x run_server.sh
echo "✓ Run script is executable"

# Deactivate virtual environment
deactivate

echo ""
echo "======================================================================"
echo "Installation Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your AIDP instance (if not done already):"
echo "   cp config/aidp_config.example.yaml config/aidp_config.yaml"
echo "   # Then edit config/aidp_config.yaml with your details"
echo ""
echo "2. Test the server:"
echo "   ./run_server.sh"
echo ""
echo "3. Configure Claude Desktop:"
echo "   Edit: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "   Add:"
echo '   {'
echo '     "mcpServers": {'
echo '       "aidp": {'
echo "         \"command\": \"$SCRIPT_DIR/run_server.sh\""
echo '       }'
echo '     }'
echo '   }'
echo ""
echo "4. Restart Claude Desktop"
echo ""
echo "For detailed instructions, see README.md"
echo ""
