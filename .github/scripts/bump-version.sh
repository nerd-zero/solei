#!/usr/bin/env bash
set -euo pipefail

# CalVer auto-increment: YYYY.MM.NNN
# - Same month: increments patch (001 → 002)
# - New month/year: resets patch to 001
# Must be run from the repo root.
# Outputs the new version to stdout.
#
# Usage:
#   ./bump-version.sh <component>
# Example:
#   ./bump-version.sh api

VERSION_FILE="VERSION"
COMPONENT="${1:-}"

if [[ -z "$COMPONENT" ]]; then
  echo "Usage: $0 <component>" >&2
  exit 1
fi

YEAR=$(date +%Y)
MONTH=$(date +%m)

LINE=$(grep -E "^${COMPONENT}=" "$VERSION_FILE" || true)
if [[ -z "$LINE" ]]; then
  echo "Component not found in $VERSION_FILE: $COMPONENT" >&2
  exit 1
fi

CURRENT="${LINE#*=}"
IFS='.' read -r CUR_YEAR CUR_MONTH CUR_PATCH <<< "$CURRENT"

if [[ "$CUR_YEAR" == "$YEAR" && "$CUR_MONTH" == "$MONTH" ]]; then
  NEW_PATCH=$(printf '%03d' $((10#$CUR_PATCH + 1)))
else
  NEW_PATCH="001"
fi

NEW_VERSION="${YEAR}.${MONTH}.${NEW_PATCH}"

TMP_FILE="$(mktemp)"
awk -v comp="$COMPONENT" -v ver="$NEW_VERSION" '
  $0 ~ "^"comp"=" { print comp"="ver; next }
  { print }
' "$VERSION_FILE" > "$TMP_FILE"
mv "$TMP_FILE" "$VERSION_FILE"

echo "$NEW_VERSION"
