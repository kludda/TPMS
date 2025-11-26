from . import gyroid
from .gyroid import *

from . import mesh
from .mesh import *

import logging
logger = logging.getLogger(__name__)

def save_stl(verts, faces, filename):
    from stl import mesh
    stl_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            stl_mesh.vectors[i][j] = verts[f[j], :]
    stl_mesh.save(filename)


def save_png(verts, faces, filename):
    if len(faces) > 100000:
        logger.warning("More than 100000 faces (" + str(len(faces)) + "). It will take some time for matplotlib to generate an image.")
    import matplotlib.pyplot as plt
    be = plt.get_backend()
    plt.switch_backend('agg') # temporarily switch to non-interactive backend to speed things up
    fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
    ax.plot_trisurf(verts[:, 0], verts[:, 1], faces, verts[:, 2], aa=False)
    ax.set_box_aspect((1,1,1))
    min = np.amin(verts)
    max = np.amax(verts)
    ax.set_xlim3d(min, max+5)
    ax.set_ylim3d(min-5, max)
    ax.set_zlim3d(min, max+5)
    fig.savefig(filename, dpi=300, bbox_inches='tight')
    plt.switch_backend(be) # switch back
    plt.close()

def show(verts, faces):
    if len(faces) > 20000:
        logger.warning("More than 2000 faces (" + str(len(faces)) + "). Even moderate number of faces cause performance issues for matplotlib, consider using a separate viewer instead.")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
    ax.plot_trisurf(verts[:, 0], verts[:, 1], faces, verts[:, 2], aa=False)
    ax.set_box_aspect((1,1,1))
    min = np.amin(verts)
    max = np.amax(verts)
    ax.set_xlim3d(min, max)
    ax.set_ylim3d(min, max)
    ax.set_zlim3d(min, max)
    plt.show()
    plt.close()
    


