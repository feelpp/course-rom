"""Package the built course and verified opening practical for teaching backup."""
from pathlib import Path
import hashlib
import json
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
output = root / "build/course-release"
site = root / "public"
release = json.loads((root / "teaching/course-release.json").read_text())
student_artifacts = []
for spec in release["labs"]:
    name = Path(spec["source"]).stem
    notebook = site / "course-rom/_attachments" / spec["source"].replace(".adoc", ".ipynb")
    prefix = "session01" if name == "session01-digital-twins" else name
    preview = output / f"{prefix}-starter.html"
    report_path = output / ("verification.json" if prefix == "session01" else f"{prefix}-verification.json")
    for required in (notebook, preview, report_path):
        if not required.is_file():
            raise SystemExit(f"Missing {required}; build and verify all released practicals first.")
    report = json.loads(report_path.read_text())
    source_page = root / "docs/modules/ROOT/pages" / spec["source"]
    exported_source_hash = json.loads(notebook.read_text())["metadata"]["course"]["source_sha256"]
    if hashlib.sha256(source_page.read_bytes()).hexdigest() != exported_source_hash:
        raise SystemExit(f"Stale notebook export for {source_page.name}; rebuild and verify first.")
    if report.get("checks") != "passed":
        raise SystemExit(f"{name} has not passed verification.")
    for file, key in ((notebook, "notebook_sha256"), (preview, "preview_sha256"),
                      (root / "requirements-course.txt", "requirements_sha256")):
        if hashlib.sha256(file.read_bytes()).hexdigest() != report.get(key):
            raise SystemExit(f"Stale verification for {file.name}; rerun the release checks.")
    student_artifacts.extend([notebook, preview])

readme = """M2 ROM & Data-Driven ROM — teaching material for sessions 1–3

Student experiments:
  Open the three session*.ipynb files in JupyterLab.
  Use requirements-course.txt for the tested Python environment (Python >= 3.12).
  All experiment data are generated in the notebooks.
  session*-starter.html contains executed starter cells and plots.

Website, notes and homework:
  python3 -m http.server 8080 --bind 127.0.0.1 --directory site
  Open http://127.0.0.1:8080/course-rom/index.html
  Follow the session pages for required notes, practicals and homework.
  MathJax normally loads from a CDN. The historical introduction PDF is included
  as an opening-session companion; it does not cover every new web chapter.

Submission dates and grading arrangements are announced by the instructor.
This package contains student material only; instructor checks/solutions are excluded.
"""
archive = output / "course-rom-teaching-pack.zip"
with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
    bundle.writestr("README.txt", readme)
    for file in student_artifacts:
        bundle.write(file, file.name)
    bundle.write(root / "requirements-course.txt", "requirements-course.txt")
    bundle.write(site / "course-rom/_attachments/lecture-rbobm-beamer-l1-2024.pdf", "introduction-2024.pdf")
    for file in sorted(site.rglob("*")):
        if file.is_file():
            bundle.write(file, "site/" + file.relative_to(site).as_posix())
print(archive)
print(f"{archive.stat().st_size / 1024**2:.1f} MiB; website, three notebooks, requirements, executed starter previews and PDF companion.")
