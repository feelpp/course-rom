"""Check the teaching routes, local resources and executed page outputs."""
from html.parser import HTMLParser
from html import unescape
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

REPO = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--static', action='store_true', help='Verify build/static-site without executed outputs')
args = parser.parse_args()
ROOT = REPO / ('build/static-site' if args.static else 'public')
BASE = "https://feelpp.github.io/course-rom/"
release = json.loads((REPO / "teaching/course-release.json").read_text())
PAGES = release["pages"] + ["course-rom/" + lab["source"].replace(".adoc", ".html") for lab in release["labs"]]



class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids, self.images, self.notebook_links = [], set(), [], []
        self.proof_blocks = []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "proof" in attrs.get("class", "").split():
            self.proof_blocks.append((tag, attrs))
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
# Audit every published article, including archives and contributor pages, rather
# than limiting internal-source checks to the current teaching release list.
audited_articles = 0
private_source = re.compile(
    r'\b[\w./-]+\.tex\b|\brbm/|\bSlides/rbm/|'
    r'\brbm_tiny_lab\.ipynb\b|\bPS[24]_Python\.zip\b|\bplotsolution\.m\b'
)
for path in ROOT.rglob('*.html'):
    article = re.search(r'<article\b[^>]*class="doc"[^>]*>(.*?)</article>', path.read_text(), re.DOTALL)
    if article:
        audited_articles += 1
        for tag, attrs in Page(article.group(1)).proof_blocks:
            if tag != "details" or "open" in attrs:
                failures.append(f"Proof must be collapsible and closed by default: {path.relative_to(ROOT)}")
        text = unescape(re.sub(r'<[^>]+>', '', article.group(1)))
        if match := private_source.search(text):
            failures.append(f"Inaccessible source reference: {path.relative_to(ROOT)}: {match.group()}")

for relative in PAGES:
    path = ROOT / relative
    if not path.is_file():
        failures.append(f"Missing page: {relative}")
        continue
    html = path.read_text()
    # A swallowed inline-math boundary can pull the next stem macro and prose
    # into one MathJax expression (e.g. paired AsciiDoc '+' passthrough markers).
    for math in re.findall(r'\\\((.*?)\\\)', html, re.DOTALL):
        if 'stem:[' in math:
            failures.append(f"Unprocessed stem macro inside inline math: {relative}")
    parsed = Page(html)
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

for spec in release["labs"]:
    lab = ROOT / "course-rom" / spec["source"].replace(".adoc", ".html")
    if not lab.is_file():
        continue
    html = lab.read_text()
    parsed = Page(html)
    plots = [im for im in parsed.images if im.get("src", "").startswith("data:image/png;base64,")]
    if len(plots) != (0 if args.static else spec["plots"]):
        failures.append(f"{spec['source']}: unexpected plot count {len(plots)}")
    if any(not im.get("alt") for im in plots):
        failures.append(f"{spec['source']}: missing plot alternative text")
    if len(parsed.notebook_links) != 1 or not parsed.notebook_links[0].endswith(spec["source"].replace(".adoc", ".ipynb")):
        failures.append(f"{spec['source']}: notebook toolbar download is missing or incorrect")
    if args.static and "Static preview: Python cells have not been executed" not in html:
        failures.append(f"{spec['source']}: missing static preview label")
    if not args.static and "Static preview: Python cells have not been executed" in html:
        failures.append(f"{spec['source']}: executable release labeled as static")
    for output in spec["results"]:
        if not args.static and output not in html:
            failures.append(f"{spec['source']}: missing executed result: {output}")

manifest_path = ROOT / "course-rom/_attachments/generated/asciidoc-notebook-manifest.json"
if not manifest_path.is_file():
    failures.append("Missing Feel++ notebook provenance manifest")
else:
    entries = json.loads(manifest_path.read_text())["entries"]
    if {entry['source_path'] for entry in entries} != {spec['source'] for spec in release['labs']}:
        failures.append("Notebook exports do not match the reviewed course release")
    for entry in entries:
        notebook_path = ROOT / "course-rom/_attachments" / entry["notebook_path"]
        page_path = REPO / "docs/modules/ROOT/pages" / entry["source_path"]
        if hashlib.sha256(notebook_path.read_bytes()).hexdigest() != entry["notebook_sha256"]:
            failures.append("Notebook hash does not match its manifest")
        notebook = json.loads(notebook_path.read_text())
        for cell in notebook['cells']:
            if cell['cell_type'] != 'markdown':
                continue
            source = cell['source'] if isinstance(cell['source'], str) else ''.join(cell['source'])
            for link in re.findall(r'\]\(([^)]+)\)', source):
                if '::' in link or link.startswith('attachment$') or (link.endswith('.ipynb') and not link.startswith('https://')):
                    failures.append(f'Unresolved notebook reference: {entry["source_path"]}: {link}')
                if link.startswith(BASE):
                    target_url = urlsplit(link)
                    target = ROOT / unquote(target_url.path.removeprefix('/course-rom/'))
                    if not target.is_file():
                        failures.append(f'Missing notebook reference: {entry["source_path"]}: {link}')
        if hashlib.sha256(page_path.read_bytes()).hexdigest() != entry["source_sha256"]:
            failures.append("Page source hash does not match its manifest")

# Published data must match the maintained source and its extraction manifest.
for asset in release.get('assets', []):
    published = ROOT / 'course-rom/_attachments' / asset
    maintained = REPO / 'docs/modules/ROOT/attachments' / asset
    if not published.is_file() or published.read_bytes() != maintained.read_bytes():
        failures.append(f'Missing or stale teaching data: {asset}')
if release.get('assets'):
    metadata = json.loads((REPO / 'docs/modules/ROOT/attachments/data/thermal-fin-coarse.json').read_text())
    for name, key in ((metadata['source'], 'source_sha256'), ('data/' + metadata['asset'], 'sha256')):
        path = REPO / 'docs/modules/ROOT/attachments' / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != metadata[key]:
            failures.append(f'Thermal-fin provenance mismatch: {name}')

# Reference-library chapters exported as executable notebooks.
reference_notebooks = {
    'reduction/pod.adoc': (5, 'Verified: thermal training errors match the singular-value tails.'),
    'certification/residual-bound.adoc': (1, 'Offline/online certification: verified norms, outputs, bounds and effectivities.'),
}
reference_manifest = ROOT / 'rom/_attachments/generated/asciidoc-notebook-manifest.json'
if not reference_manifest.is_file():
    failures.append('Missing reference notebook manifest')
else:
    entries = {entry['source_path']: entry for entry in json.loads(reference_manifest.read_text())['entries']}
    if set(entries) != set(reference_notebooks):
        failures.append('Reference notebook exports do not match the reviewed chapters')
    for relative, (plot_count, result) in reference_notebooks.items():
        export_path = relative.replace('.adoc', '.ipynb')
        export = ROOT / 'rom/_attachments' / export_path
        html_path = ROOT / 'rom' / relative.replace('.adoc', '.html')
        if not export.is_file() or not html_path.is_file():
            failures.append(f'Missing reference notebook/page: {relative}')
            continue
        notebook = json.loads(export.read_text())
        source = REPO / 'materials/modules/ROOT/pages' / relative
        entry = entries.get(relative, {})
        if entry.get('notebook_sha256') != hashlib.sha256(export.read_bytes()).hexdigest():
            failures.append(f'Reference notebook manifest mismatch: {relative}')
        if notebook['metadata']['course']['source_sha256'] != hashlib.sha256(source.read_bytes()).hexdigest():
            failures.append(f'Stale reference notebook source: {relative}')
        for cell in notebook['cells']:
            if cell['cell_type'] != 'markdown':
                continue
            text = cell['source'] if isinstance(cell['source'], str) else ''.join(cell['source'])
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if not link.startswith(('https://', '#')):
                    failures.append(f'Unresolved reference notebook link: {relative}: {link}')
                elif link.startswith(BASE):
                    target = ROOT / unquote(urlsplit(link).path.removeprefix('/course-rom/'))
                    if not target.is_file():
                        failures.append(f'Missing reference notebook target: {relative}: {link}')
        page = Page(html_path.read_text())
        if len(page.notebook_links) != 1 or not page.notebook_links[0].endswith(export_path):
            failures.append(f'Reference notebook download is missing: {relative}')
        figures = [im for im in page.images if im.get('src', '').startswith('data:image/png;base64,')]
        if len(figures) != (0 if args.static else plot_count) or any(not im.get('alt') for im in figures):
            failures.append(f'Reference figures missing or lacking alternative text: {relative}')
        if not args.static and result not in html_path.read_text():
            failures.append(f'Reference numerical verification output is missing: {relative}')
asset_root = REPO / 'materials/modules/ROOT/attachments/data'
metadata = json.loads((asset_root / 'melencolia-magic-square.json').read_text())
if hashlib.sha256((REPO / metadata['source']).read_bytes()).hexdigest() != metadata['source_sha256']:
    failures.append('POD image source PDF changed')
for asset in (asset_root / metadata['asset'], ROOT / 'rom/_attachments/data' / metadata['asset']):
    if not asset.is_file() or hashlib.sha256(asset.read_bytes()).hexdigest() != metadata['sha256']:
        failures.append(f'POD image provenance mismatch: {asset}')

if failures:
    raise SystemExit("\n".join(failures))
print(f"Verified {len(PAGES)} course/library pages, local links/assets, notebook provenance and {'static preview' if args.static else 'executed plots for all released practicals'}.")
print(f"Audited all {audited_articles} published articles for internal or unavailable source references.")
