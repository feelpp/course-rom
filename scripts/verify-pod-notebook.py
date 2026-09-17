"""Run the exported POD chapter with only its downloadable image in a clean folder.

Run with the course Python environment after an Antora build. Keeps an executed
notebook in build/course-release for inspection; student exports remain editable.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import hashlib
import json
import shutil
import sys

import nbformat
from nbclient import NotebookClient

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--site', default='public')
args = parser.parse_args()
site = root / args.site
notebook_path = site / 'rom/_attachments/reduction/pod.ipynb'
image_path = site / 'rom/_attachments/data/melencolia-magic-square.png'
notebook = nbformat.read(notebook_path, as_version=4)
nbformat.validate(notebook)
source = root / 'materials/modules/ROOT/pages/reduction/pod.adoc'
assert notebook.metadata.course.source_sha256 == hashlib.sha256(source.read_bytes()).hexdigest()
assert len([c for c in notebook.cells if c.cell_type == 'code']) == 5
with TemporaryDirectory() as tmp:
    # Resolve the kernel inside this interpreter's environment, without installing
    # anything in the user's persistent Jupyter configuration.
    kernel = Path(tmp) / 'kernel'
    kernel.mkdir()
    (kernel / 'kernel.json').write_text(json.dumps({
        'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
        'display_name': 'POD verification', 'language': 'python',
    }))
    from jupyter_client.kernelspec import KernelSpecManager
    class LocalKernelSpecManager(KernelSpecManager):
        def find_kernel_specs(self):
            return {'python3': str(kernel)}
    from jupyter_client import KernelManager
    class LocalKernelManager(KernelManager):
        def __init__(self, **kwargs):
            super().__init__(kernel_spec_manager=LocalKernelSpecManager(), **kwargs)
    shutil.copy2(image_path, Path(tmp) / image_path.name)
    NotebookClient(notebook, timeout=60, kernel_manager_class=LocalKernelManager,
                   resources={'metadata': {'path': tmp}}).execute()
outputs = [o for c in notebook.cells if c.cell_type == 'code' for o in c.outputs]
assert not any(o.output_type == 'error' for o in outputs)
plots = [o for o in outputs if 'image/png' in o.get('data', {})]
assert len(plots) == 2, f'Expected two executed figures, got {len(plots)}'
text = '\n'.join(o.get('text', '') for o in outputs)
assert 'Verified: measured reconstruction errors match the singular-value tails.' in text
assert 'Correlation POD: weighted projection error squared' in text
out = root / 'build/course-release/pod-executed.ipynb'
out.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(notebook, out)
print(text)
print(f'POD notebook: all five cells executed with only the downloaded image; two figures.\n{out}')
