#!/bin/sh
# Compatibility entry point: export only reviewed pages selected in site.yml.
set -eu
if [ "$#" -ne 0 ]; then
  echo 'Usage: ./generate-jupyter.sh (select reviewed pages in site.yml; recursive directory export is retired)' >&2
  exit 2
fi
cd "$(dirname "$0")"
npm run site:static
printf '%s\n' 'Notebook exports: build/static-site/course-rom/_attachments/labs/'
