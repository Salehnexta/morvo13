#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# scripts/backup.sh
# ---------------------------------------------------------------------------
# Safely create a code + database checkpoint for the Morvo project.
#
# 1. Creates a Git commit (if there are staged changes).
# 2. Tags the commit with a timestamp.
# 3. Copies the SQLite test/prototype DB (if present) into backups/.
#
# Usage:
#   bash scripts/backup.sh "checkpoint message"
# ---------------------------------------------------------------------------
set -euo pipefail

MSG=${1:-"Automated backup"}
STAMP=$(date +"%Y%m%d_%H%M%S")
TAG="backup-${STAMP}"
BACKUP_DIR="backups"
DB_FILE="test.db"

# Ensure backup directory exists
mkdir -p "${BACKUP_DIR}"

# Stage any pending changes (optional: adjust to taste)
if [[ -n $(git status --porcelain) ]]; then
  git add -A
  git commit -m "${MSG}" || true
fi

# Tag the current commit
if ! git rev-parse "${TAG}" >/dev/null 2>&1; then
  git tag -a "${TAG}" -m "${MSG}"
fi

# Copy database if it exists
if [[ -f "${DB_FILE}" ]]; then
  cp "${DB_FILE}" "${BACKUP_DIR}/${DB_FILE%.*}_${STAMP}.db"
  echo "Database snapshot saved to ${BACKUP_DIR}/${DB_FILE%.*}_${STAMP}.db"
fi

echo "Backup complete: Git tag ${TAG}" 