"""Package the built course and verified opening practical for teaching backup."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
output = root / "build/course-release"
site = root / "public"
notebook = site / "course-rom/_attachments/labs/session01-digital-twins.ipynb"
preview = output / "session01-starter.html"
for required in (site / "course-rom/index.html", notebook, preview):
    if not required.is_file():
        raise SystemExit(f"Missing {required}; build the site and run verify-session01.py first.")

readme = """M2 ROM & Data-Driven ROM — opening session, 10 September 2026, 13:30–15:30 CEST

Student experiment:
  Open session01-digital-twins.ipynb in JupyterLab.
  Use requirements-course.txt for the tested Python environment (Python >= 3.12).
  All experiment data are generated in the notebook; no network is needed to run
  it after the environment is installed.

Teaching website:
  From this extracted directory run:
    python3 -m http.server 8080 --bind 127.0.0.1 --directory site
  Open http://127.0.0.1:8080/course-rom/index.html
  The page includes build-time Python results and embedded plots.
  MathJax is normally loaded from a CDN; use the PDF companion when offline.

Fallback:
  session01-starter.html contains the executed starter notebook and plots.
  introduction-2024.pdf is a historical slide companion, not the current timetable.
  The course page and session 1 page contain the current 2026 instructions.

This package contains student material only; instructor checks/solutions are excluded.
"""
archive = output / "course-rom-session01-20260910.zip"
with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
    bundle.writestr("README.txt", readme)
    bundle.write(notebook, notebook.name)
    bundle.write(root / "requirements-course.txt", "requirements-course.txt")
    bundle.write(preview, preview.name)
    bundle.write(site / "course-rom/_attachments/lecture-rbobm-beamer-l1-2024.pdf", "introduction-2024.pdf")
    for file in sorted(site.rglob("*")):
        if file.is_file():
            bundle.write(file, "site/" + file.relative_to(site).as_posix())
print(archive)
print(f"{archive.stat().st_size / 1024**2:.1f} MiB; website, notebook, requirements, executed preview and PDF companion.")
