#!/bin/bash
set -e

# Check if API token is provided
if [ -z "$1" ]; then
    echo "Error: API token is required"
    echo "Usage: $0 <api_token>"
    echo "Example: $0 pypi-xxx..."
    exit 1
fi

API_TOKEN=$1

# Clean up any previous builds
rm -rf dist/

# Build the package
poetry build

# Configure PyPI repository with the provided token
poetry config pypi-token.pypi $API_TOKEN

# Upload to PyPI
poetry publish

echo "Package published to PyPI successfully!"
echo "You can install it using:"
echo "pip install synmetrix-python-client"
