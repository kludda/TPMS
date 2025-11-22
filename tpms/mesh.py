import numpy as np
from skimage import measure

import logging
logger = logging.getLogger(__name__)


def get_mesh(vol, spacing, shift=None):
    verts, faces, normals, values = measure.marching_cubes(vol, level=0, spacing=(spacing, spacing, spacing))

    if not spacing is None:
        # Move verts back
        verts = verts - shift
        
    return verts, faces

# ChatGPT, I have no idea what it is doing but it seems to genereate correct result
def mean_gradient_magnitude(vol, sizeunit_per_voxel):
    gx, gy, gz = np.gradient(vol, sizeunit_per_voxel, sizeunit_per_voxel, sizeunit_per_voxel)
    grad_mag = np.sqrt(gx**2 + gy**2 + gz**2)
    return np.mean(grad_mag[np.abs(vol) < 0.1])


# direction = 'sym', '+', '-'
# surfaces will have will negative facing each other
def voxel_offset(vol, distance, direction=None):
    if direction == 'sym':
        distance = distance / 2
        outer = vol - distance
        inner = -(vol + distance)
    elif direction == '+':
        outer = vol - distance
        inner = -vol
    elif direction == '-':
        outer = vol
        inner = -(vol + distance)
    else:
        return vol - distance

    return np.maximum(inner, outer)


# Caping the extreme surfaces is achieved by padding the grid
# This cause the mesh created by marching_cubes to shift in space.
# If spacing is defined, where spacing is the spacing passed to marching_cubes,
# the amont of shift will be returned.
def voxel_cap_extremes(vol, spacing=None):
    p = 2
    vol = np.pad(vol, pad_width=p, mode='constant', constant_values=+1.0)

    shift = 0
    if not spacing is None:
        shift = p * spacing

    return vol, shift
