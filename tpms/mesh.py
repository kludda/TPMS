import numpy as np
from skimage import measure

import logging
logger = logging.getLogger(__name__)

# log-sum-exp (LSE) smooth
# k = smooth factor, higher = sharper; 5–20 is typical
# Not tested to work properly
def smooth_min_lse(a, b, k):
    return -np.log(np.exp(-k*a) + np.exp(-k*b)) / k

# log-sum-exp (LSE) smooth
# k = smooth factor, higher = sharper; 5–20 is typical
def smooth_max_lse(a, b, k):
    return np.log(np.exp(k*a) + np.exp(k*b)) / k


# Inigo Quilez’s polynomial smooth
# k = smooth blending radius
# Not tested to work properly
def smooth_min_poly(a, b, k):
    h = np.clip(0.5 + 0.5*(b - a)/k, 0.0, 1.0)
    return b*(1-h) + a*h - k*h*(1-h)

# Inigo Quilez’s polynomial smooth
# k = smooth blending radius
# Not tested to work properly
def smooth_max_poly(a, b, k):
    h = np.clip(0.5 + 0.5 * (a - b) / k, 0.0, 1.0)
    return a * h + b * (1 - h) + k * h * (1 - h)

# Create mesh form voxel grid
def get_mesh(vol, spacing, shift=None):
    verts, faces, normals, values = measure.marching_cubes(vol, level=0, spacing=(spacing, spacing, spacing))

    if not shift is None:
        # Move verts back
        verts = verts - shift

    return verts, faces

# Calculate mean gradient magnitude for approximate offsets of surface
def mean_gradient_magnitude(vol, sizeunit_per_voxel):
    gx, gy, gz = np.gradient(vol, sizeunit_per_voxel, sizeunit_per_voxel, sizeunit_per_voxel)
    grad_mag = np.sqrt(gx**2 + gy**2 + gz**2)
    return np.mean(grad_mag[np.abs(vol) < 0.1])


# Offset iso surface in voxel grid.
# direction = 'sym', '+', '-', None
# If direction = None, a new offset surface will be returned,
# else two surfaces with negative facing each other will be returned
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
