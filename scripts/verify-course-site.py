"""Check the opening route, local resources and executed page outputs."""
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1] / "public"
BASE = "https://feelpp.github.io/course-rom/"
PAGES = [
    "course-rom/index.html", "course-rom/syllabus.html", "course-rom/setup.html",
    "course-rom/archive.html", "course-rom/sessions/01-digital-twins.html",
    "course-rom/labs/session01-digital-twins.html", "rom/index.html",
    "rom/digital-twins.html",
]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids, self.images, self.notebook_links = [], set(), [], []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
            if "jupyter-download" in attrs.get("class", ""):
                self.notebook_links.append(attrs["href"])
        if tag in {"img", "script"} and attrs.get("src"):
            self.links.append(attrs["src"])
        if tag == "img":
            self.images.append(attrs)
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.links.append(attrs["href"])


failures = []
for relative in PAGES:
    path = ROOT / relative
    if not path.is_file():
        failures.append(f"Missing page: {relative}")
        continue
    parsed = Page(path.read_text())
    for link in parsed.links:
        url = urlsplit(urljoin(BASE + relative, link))
        if url.scheme != "https" or url.netloc != "feelpp.github.io":
            continue
        if not url.path.startswith("/course-rom/"):
            failures.append(f"Link escapes site prefix: {relative}: {link}")
            continue
        target = ROOT / unquote(url.path.removeprefix("/course-rom/"))
        if target.is_dir():
            target /= "index.html"
        if not target.is_file():
            failures.append(f"Missing target: {relative}: {link}")
        elif url.fragment and target.suffix == ".html":
            if unquote(url.fragment) not in Page(target.read_text()).ids:
                failures.append(f"Missing fragment: {relative}: {link}")

lab = ROOT / "course-rom/labs/session01-digital-twins.html"
if lab.is_file():
    html = lab.read_text()
    parsed = Page(html)
    plots = [im for im in parsed.images if im.get("src", "").startswith("data:image/png;base64,")]
    if len(plots) != 3:
        failures.append(f"Expected three executed Matplotlib images, found {len(plots)}")
    if any(not im.get("alt") for im in plots):
        failures.append("An executed plot is missing alternative text")
    if len(parsed.notebook_links) != 1 or not parsed.notebook_links[0].endswith("labs/session01-digital-twins.ipynb"):
        failures.append("Notebook toolbar download is missing or incorrect")
    # These are calculated results, not the Python source strings on the page.
    for output in ("mean=0.418756", "mean=0.138904", "mean=0.039674", "mean=0.008249"):
        if output not in html:
            failures.append(f"Missing executed result: {output}")

manifest_path = ROOT / "course-rom/_attachments/generated/asciidoc-notebook-manifest.json"
if not manifest_path.is_file():
    failures.append("Missing Feel++ notebook provenance manifest")
else:
    entries = json.loads(manifest_path.read_text())["entries"]
    if len(entries) != 1:
        failures.append(f"Expected one selected notebook export, found {len(entries)}")
    for entry in entries:
        notebook_path = ROOT / "course-rom/_attachments" / entry["notebook_path"]
        page_path = ROOT.parent / "docs/modules/ROOT/pages" / entry["source_path"]
        if hashlib.sha256(notebook_path.read_bytes()).hexdigest() != entry["notebook_sha256"]:
            failures.append("Notebook hash does not match its manifest")
        if hashlib.sha256(page_path.read_bytes()).hexdigest() != entry["source_sha256"]:
            failures.append("Page source hash does not match its manifest")

if failures:
    raise SystemExit("\n".join(failures))
print(f"Verified {len(PAGES)} opening pages, local links/assets, notebook toolbar and three executed plots.")
