import numpy as np
from numpy import sin, cos, pi

import logging
logger = logging.getLogger(__name__)


def calc_gyroid(x, y, z, t, a):
    x = pi * a * x
    y = pi * a * y
    z = pi * a * z
    return np.sin(x)*np.cos(y) + \
        np.sin(y)*np.cos(z) +\
        np.sin(z)*np.cos(x) - t


def get_voxel_grid(res, size=None):
    _res = [res] * 3
    if isinstance(size, np.ndarray):
        _res = [size[i] / size.max() * res for i in range(3)]
    _res = [complex(0, i) + 1j for i in _res]

    _ext = [1] * 3
    if isinstance(size, np.ndarray):
        _ext = [size[i] / size.max() for i in range(3)]

    x, y, z = np.mgrid[-_ext[0]:_ext[0]:_res[0], -_ext[1]:_ext[1]:_res[1], -_ext[2]:_ext[2]:_res[2]]
    return x, y, z


def get_gyroid(t, a, res, size=None):
    x, y, z = get_voxel_grid(res=res, size=size)
    return calc_gyroid(x, y, z, t, a)
