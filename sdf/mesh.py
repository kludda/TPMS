import numpy as np
from skimage import measure
from . import stl

import logging
logger = logging.getLogger(__name__)


# Create mesh form voxel grid
def generate(vol, spacing): #, shift=None):
    verts, faces, normals, values = measure.marching_cubes(vol, level=0, spacing=(spacing, spacing, spacing))
    return verts, faces


# translate verts by offset [X,Y,Z]
def translate(verts, offset):
    verts = verts + np.array(offset)
    return verts


def save(verts, faces, filename):
    stl.write_binary(verts, faces, filename)