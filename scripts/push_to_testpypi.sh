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

# Configure TestPyPI repository with the provided token
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi $API_TOKEN

# Upload to TestPyPI
poetry publish -r testpypi

echo "Package published to TestPyPI successfully!"
echo "You can install it using:"
echo "pip install --index-url https://test.pypi.org/simple/ synmetrix-python-client"
