"""Extract the original-image panel of the published POD slides as experiment data.

Requires Poppler and Pillow. No resizing, enhancement or reconstruction is used.
The supplied raster is a slide reproduction, not the unavailable original array.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import subprocess
from PIL import Image

root = Path(__file__).resolve().parents[1]
source = root / 'docs/modules/ROOT/attachments/lecture-rbobm-beamer-svd-pod.pdf'
output = root / 'materials/modules/ROOT/attachments/data'
output.mkdir(parents=True, exist_ok=True)
crop = (964, 692, 1533, 1242)  # Original panel, excluding title and adjacent approximations.
with TemporaryDirectory() as tmp:
    subprocess.run(['pdfimages', '-f', '19', '-l', '19', '-png', str(source),
                    str(Path(tmp) / 'slide')], check=True)
    candidates = [p for p in Path(tmp).glob('*.png')
                  if Image.open(p).size == (1632, 1310) and Image.open(p).mode == 'RGB']
    if len(candidates) != 1:
        raise RuntimeError('Expected exactly one RGB comparison figure on PDF page 19')
    image = Image.open(candidates[0]).crop(crop).convert('L')
    target = output / 'melencolia-magic-square.png'
    image.save(target)
metadata = {
    'asset': target.name,
    'artwork': 'Albrecht Dürer, Melencolia I (1514), magic-square detail',
    'source': source.relative_to(root).as_posix(),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'pdf_page': 19, 'source_figure_size': [1632, 1310], 'crop_xyxy': list(crop),
    'processing': 'Original panel only; Pillow grayscale L conversion; no resizing.',
    'width': image.width, 'height': image.height,
    'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
}
(output / 'melencolia-magic-square.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n')
print(f'{target}: {image.height} x {image.width} grayscale pixels')
