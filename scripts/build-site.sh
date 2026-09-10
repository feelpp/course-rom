#!/bin/sh
set -eu

# The static preview never imports Python or overwrites the executable release.
if [ "${1:-}" = --static ]; then
  shift
  set -- --to-dir build/static-site --attribute 'dynamic-blocks!' \
    --attribute 'course-static-preview=true' "$@"
else
  course_python=${COURSE_PYTHON:-python3}
  course_python_path=$("$course_python" -c 'import sys; import IPython, numpy, matplotlib; print(sys.executable)')
  set -- --attribute "dynamic-python-interpreter=$course_python_path" "$@"
fi
mkdir -p docs/modules/ROOT/attachments/labs
cp requirements-course.txt docs/modules/ROOT/attachments/labs/requirements-course.txt
exec ./node_modules/.bin/antora --stacktrace generate --log-failure-level error \
  --cache-dir cache --clean \
  site.yml "$@"
