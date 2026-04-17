#!/usr/bin/env sh

# Minimal Husky bootstrap for local git hooks.
if [ "${HUSKY:-1}" = "0" ]; then
  exit 0
fi
