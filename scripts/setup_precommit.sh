#!/bin/bash

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit
fi

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Update hooks to latest version
echo "Updating pre-commit hooks..."
pre-commit autoupdate

# Run against all files
echo "Running pre-commit on all files..."
pre-commit run --all-files

echo "Pre-commit setup complete!"
