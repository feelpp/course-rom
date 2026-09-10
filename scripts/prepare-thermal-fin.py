"""Extract compact coarse thermal-fin matrices from the published teaching data."""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
import hashlib
import json
import numpy as np
from scipy.io import loadmat

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs/modules/ROOT/attachments/homework-2024-data.zip'
TARGET=ROOT/'docs/modules/ROOT/attachments/data/thermal-fin-coarse.npz'
with ZipFile(SOURCE) as bundle:
    def coarse(name):
        entry=next(p for p in bundle.namelist() if p.endswith('/'+name) or p==name)
        return loadmat(BytesIO(bundle.read(entry)),simplify_cells=True)[Path(name).stem]['coarse']
    stiffness=coarse('FE_matrix.mat'); mass=coarse('FE_matrix_mass.mat'); grid=coarse('FE_grid.mat')
    arrays={'f':stiffness['Fh'],'coordinates':grid['coor']}
    for name,matrix in [('M',mass['Mh'])]+[(f'A{i}',a) for i,a in enumerate(stiffness['Ahq'])]:
        matrix=matrix.tocsc()
        arrays.update({name+'_data':matrix.data,name+'_indices':matrix.indices,
                       name+'_indptr':matrix.indptr,name+'_shape':np.array(matrix.shape)})
    triangles=[]
    for cells in grid['theta'][:5]:
        cells=np.asarray(cells)
        if cells.shape[0]==3: cells=cells.T
        triangles.append(cells[:,:3].astype(int)-1)
    arrays['triangles']=np.vstack(triangles)
TARGET.parent.mkdir(parents=True,exist_ok=True)
np.savez_compressed(TARGET,**arrays)
manifest={'source':'homework-2024-data.zip','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'asset':TARGET.name,'sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),
          'nodes':int(len(arrays['f'])),'description':'Original coarse FE matrices; all conductivities one, A5 is the unscaled Robin boundary matrix; M is the mass matrix. Transient inputs are defined by each practical.'}
TARGET.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(TARGET, TARGET.stat().st_size)
