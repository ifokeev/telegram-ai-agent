#!/bin/bash

# Run pre-commit on all files
echo "Running pre-commit checks..."
pre-commit run --all-files

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "All checks passed!"
else
    echo "Some checks failed. Please fix the issues and try again."
fi

exit $exit_code
