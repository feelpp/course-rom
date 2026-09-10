#!/bin/sh
set -eu

# Use an activated course environment, or set COURSE_PYTHON explicitly.
course_python=${COURSE_PYTHON:-python3}
course_python_path=$("$course_python" -c 'import sys; import IPython, numpy, matplotlib; print(sys.executable)')
mkdir -p docs/modules/ROOT/attachments/labs
cp requirements-course.txt docs/modules/ROOT/attachments/labs/requirements-course.txt
exec ./node_modules/.bin/antora --stacktrace generate --log-failure-level error \
  --cache-dir cache --clean \
  --attribute "dynamic-python-interpreter=$course_python_path" site.yml "$@"
