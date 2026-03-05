#!/bin/bash
set -e

echo "Installing pre-commit hook..."
mkdir -p .git/hooks
cp scripts/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
echo "Hook installed: .git/hooks/pre-commit"