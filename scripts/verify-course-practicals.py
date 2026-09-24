"""Execute sessions 4–14 from exported student notebooks with independent checks.

Reference check cells stay under build/; only student cells enter previews.
The fresh kernels receive only the published notebook and published data.
"""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'build/course-release'
OUTPUT.mkdir(parents=True,exist_ok=True)
release=json.loads((ROOT/'teaching/course-release.json').read_text())
assets={}
for asset in release.get('assets',[]):
    source=ROOT/'public/course-rom/_attachments'/asset
    shutil.copyfile(source,OUTPUT/source.name)
    assets[asset]=hashlib.sha256(source.read_bytes()).hexdigest()
guided_spec=next(spec for spec in release['labs']
                 if spec['source']=='labs/galerkin-sampling.adoc')
guided_source=ROOT/'public/course-rom/_attachments/labs/galerkin-sampling.ipynb'
guided_notebook=nbformat.read(guided_source,as_version=4)
nbformat.validate(guided_notebook)
# The exercise functions are intentionally incomplete, but their definitions and
# supplied 1D model must run in a fresh kernel without calling those functions.
NotebookClient(guided_notebook,timeout=120,kernel_name='python3',
               resources={'metadata':{'path':str(OUTPUT)}}).execute()
guided_html,_=HTMLExporter(template_name='classic').from_notebook_node(guided_notebook)
guided_preview=OUTPUT/'galerkin-sampling-starter.html'
guided_preview.write_text(guided_html)
guided_plots=sum('image/png' in out.get('data',{}) for cell in guided_notebook.cells
                 for out in cell.get('outputs',[]))
assert guided_plots==guided_spec['plots'],guided_plots
guided_report={'checks':'passed','python':sys.version.split()[0],
               'plots':guided_plots,
               'notebook_sha256':hashlib.sha256(guided_source.read_bytes()).hexdigest(),
               'preview_sha256':hashlib.sha256(guided_preview.read_bytes()).hexdigest(),
               'requirements_sha256':hashlib.sha256((ROOT/'requirements-course.txt').read_bytes()).hexdigest()}
(OUTPUT/'galerkin-sampling-verification.json').write_text(json.dumps(guided_report,indent=2)+'\n')
print('galerkin-sampling: guided cells run in a fresh kernel; '
      f'{guided_plots} starter plot(s); exercise answers remain blank.',flush=True)
advanced_start=next(i for i,spec in enumerate(release['labs'])
                    if spec['source']=='labs/session04-greedy.adoc')
for spec in release['labs'][advanced_start:]:
    name=Path(spec['source']).stem
    source=ROOT/'public/course-rom/_attachments'/spec['source'].replace('.adoc','.ipynb')
    notebook=nbformat.read(source,as_version=4)
    nbformat.validate(notebook)
    student_cells=len(notebook.cells)
    check=(ROOT/'teaching/instructors/checks'/f'{name}.py').read_text()
    notebook.cells.append(nbformat.v4.new_code_cell(check))
    NotebookClient(notebook,timeout=120,kernel_name='python3',
                   resources={'metadata':{'path':str(OUTPUT)}}).execute()
    nbformat.write(notebook,OUTPUT/f'{name}-reference.ipynb')
    notebook.cells=notebook.cells[:student_cells]
    nbformat.write(notebook,OUTPUT/f'{name}-executed.ipynb')
    html,_=HTMLExporter(template_name='classic').from_notebook_node(notebook)
    preview=OUTPUT/f'{name}-starter.html'; preview.write_text(html)
    plots=sum('image/png' in out.get('data',{}) for cell in notebook.cells for out in cell.get('outputs',[]))
    assert plots==spec['plots'],(name,plots,spec['plots'])
    report={'checks':'passed','python':sys.version.split()[0],'plots':plots,
            'notebook_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'preview_sha256':hashlib.sha256(preview.read_bytes()).hexdigest(),
            'requirements_sha256':hashlib.sha256((ROOT/'requirements-course.txt').read_bytes()).hexdigest(),
            'assets_sha256':assets}
    (OUTPUT/f'{name}-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'{name}: {student_cells} student cells, {plots} plot(s), fresh kernel and independent checks passed.',flush=True)
