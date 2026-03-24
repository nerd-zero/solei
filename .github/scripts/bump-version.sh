#!/usr/bin/env bash
set -euo pipefail

# CalVer auto-increment: YYYY.MM.NNN
# - Same month: increments patch (001 → 002)
# - New month/year: resets patch to 001
# Must be run from the repo root.
# Outputs the new version to stdout.

VERSION_FILE="VERSION"

YEAR=$(date +%Y)
MONTH=$(date +%m)

CURRENT=$(tr -d '[:space:]' < "$VERSION_FILE")
IFS='.' read -r CUR_YEAR CUR_MONTH CUR_PATCH <<< "$CURRENT"

if [[ "$CUR_YEAR" == "$YEAR" && "$CUR_MONTH" == "$MONTH" ]]; then
  NEW_PATCH=$(printf '%03d' $((10#$CUR_PATCH + 1)))
else
  NEW_PATCH="001"
fi

NEW_VERSION="${YEAR}.${MONTH}.${NEW_PATCH}"
printf '%s\n' "$NEW_VERSION" > "$VERSION_FILE"
echo "$NEW_VERSION"
