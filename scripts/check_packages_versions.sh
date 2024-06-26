#!/bin/bash

PYPROJECT_VERSION=$(grep '^version = ' pyproject.toml | awk -F'"' '{print $2}')
PACKAGE_JSON_VERSION=$(grep '"version":' frontend/package.json | awk -F'"' '{print $4}')

if [ "$PYPROJECT_VERSION" != "$PACKAGE_JSON_VERSION" ]; then
  echo "Version mismatch: pyproject.toml ($PYPROJECT_VERSION) != frontend/package.json ($PACKAGE_JSON_VERSION)"
  echo "The backend and the frontend are versioned together, that is, they should have the same version number."
  echo "Please update the version number in both files to match."
  exit 1
fi

echo "Versions match."
