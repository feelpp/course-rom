"""Render original RB/POD teaching illustrations; no private slide assets needed."""
from pathlib import Path
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / 'materials/modules/ROOT/images/reduction'
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.size': 11, 'svg.fonttype': 'none', 'svg.hashsalt': 'rom-reduction'})

fig = plt.figure(figsize=(8, 4.4), layout='constrained')
ax = fig.add_subplot(111, projection='3d')
xp, yp = np.meshgrid(np.linspace(0, 1.2, 3), np.linspace(-1.1, 1.1, 3))
ax.plot_surface(xp, yp, 0*xp, color='#bad7cb', alpha=.3)
t = np.linspace(-1, 1, 200)
ax.plot(np.ones_like(t), t, .1*t*t, color='#275c9b', linewidth=2.5, label='Solution family')
ax.plot(np.ones_like(t), t, 0*t, color='#45816a', linestyle='--', label='Projection into the reduced plane')
ts = np.linspace(-1, 1, 7)
ax.scatter(np.ones_like(ts), ts, .1*ts*ts, color='#275c9b', s=25, label='Snapshots')
for t0 in ts:
    ax.plot([1,1], [t0,t0], [0,.1*t0*t0], color='#b65c32', alpha=.7)
ax.set(xlabel='State coordinate 1', ylabel='State coordinate 2', zlabel='State coordinate 3',
       xlim=(0,1.2), ylim=(-1.1,1.1), zlim=(0,.13))
ax.set_title('A family of states close to a linear reduced space', pad=12)
ax.view_init(elev=23, azim=-42)
ax.legend(loc='upper left', fontsize=8)
fig.savefig(OUT/'solution-family.svg',metadata={'Date':None})
fig.savefig('/tmp/rom-solution-family.png',dpi=130)
plt.close(fig)

def rotation(theta):
    c,s=np.cos(theta),np.sin(theta)
    return np.array([[c,-s],[s,c]])
U=rotation(np.deg2rad(25)); V=rotation(np.deg2rad(30))
sigma=np.array([2., .7]); Y=U@np.diag(sigma)@V.T
angle=np.linspace(0,2*np.pi,400)
circle=np.vstack([np.cos(angle),np.sin(angle)])
fig,axes=plt.subplots(1,2,figsize=(8,3.7),layout='constrained')
for ax,points,title in zip(axes,[circle,Y@circle],['Input: unit circle','Output: ellipse under Y']):
    ax.plot(*points,color='#275c9b',linewidth=2)
    ax.axhline(0,color='.8',linewidth=.7);ax.axvline(0,color='.8',linewidth=.7)
    ax.set_aspect('equal');ax.set_title(title);ax.grid(alpha=.15)
for i,color in enumerate(['#b65c32','#45816a']):
    v=V[:,i]; u=sigma[i]*U[:,i]
    for ax,tip,label in [(axes[0],v,rf'$v_{i+1}$'),(axes[1],u,rf'$\sigma_{i+1}u_{i+1}$')]:
        ax.annotate('',xy=tip,xytext=(0,0),arrowprops={'arrowstyle':'->','color':color,'lw':2})
        ax.text(*(tip*1.15),label,color=color)
axes[0].set(xlim=(-1.4,1.4),ylim=(-1.4,1.4))
axes[1].set(xlim=(-2.6,2.6),ylim=(-2.6,2.6))
fig.savefig(OUT/'svd-geometry.svg',metadata={'Date':None})
fig.savefig('/tmp/rom-svd-geometry.png',dpi=130)
plt.close(fig)
print('Rendered solution-family.svg and svd-geometry.svg')

# Matplotlib emits trailing spaces in SVG path data; normalize the checked-in XML.
for name in ('solution-family.svg', 'svd-geometry.svg'):
    path = OUT / name
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')

# Extract only the illustration regions from the public companion PDF.
source = OUT.parents[4] / 'docs/modules/ROOT/attachments/lecture-rbobm-beamer-approx.pdf'
for page, crop, name in [
    (11, (65, 355, 630, 350), 'snapshot-family-slides'),
    (43, (113, 210, 857, 726), 'heat-transfer-domain-slides'),
]:
    x, y, width, height = crop
    subprocess.run(['pdftoppm', '-f', str(page), '-l', str(page), '-scale-to', '1450',
                    '-x', str(x), '-y', str(y), '-W', str(width), '-H', str(height),
                    '-png', '-singlefile', str(source), str(OUT/name)], check=True)
print('Extracted the two public PDF illustrations with recorded page/crop coordinates.')
