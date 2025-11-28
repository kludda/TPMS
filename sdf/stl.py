import numpy as np

import logging
logger = logging.getLogger(__name__)

def write_binary(verts, faces, filename):
    from stl import mesh
    stl_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            stl_mesh.vectors[i][j] = verts[f[j], :]
    stl_mesh.save(filename)