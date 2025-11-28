import numpy as np

import logging
logger = logging.getLogger(__name__)


def get(res, size=None):
    _res = [res] * 3
    _ext = [1] * 3

    if isinstance(size, list):
        _res = [size[i] / max(size) * res for i in range(3)]
        _ext = [size[i] / max(size) for i in range(3)]
        
    _res = [complex(0, i) + 1j for i in _res]

    x, y, z = np.mgrid[-_ext[0]:_ext[0]:_res[0], -_ext[1]:_ext[1]:_res[1], -_ext[2]:_ext[2]:_res[2]]
    return x, y, z


# log-sum-exp (LSE) smooth
# k = smooth factor, higher = sharper; 5–20 is typical
def smooth_min_lse(a, b, k):
    return -np.log(np.exp(-k*a) + np.exp(-k*b)) / k
    
def smooth_max_lse(a, b, k):
    return np.log(np.exp(k*a) + np.exp(k*b)) / k


# Calculate mean gradient magnitude for approximate offsets of surface
def mean_gradient_magnitude(vol, sizeunit_per_voxel):
    gx, gy, gz = np.gradient(vol, sizeunit_per_voxel, sizeunit_per_voxel, sizeunit_per_voxel)
    grad_mag = np.sqrt(gx**2 + gy**2 + gz**2)
    return np.mean(grad_mag[np.abs(vol) < 0.1])


# Offset iso surface in voxel grid.
# A new offset surface will be returned,
def offset(vol, distance):
    return vol - distance


# Offset iso surface in voxel grid.
# direction = 'sym', '+', '-', None
# Two surfaces with negative facing each other will be returned
def thicken(vol, distance, direction=None):
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
        raise ValueError("Unknown direction: " + direction)

    return np.maximum(inner, outer)

