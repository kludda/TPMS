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

def get_voxel_grid(t, a, res):
    res = complex(0, res) + 1j
    ext = 1
    x, y, z = np.mgrid[-ext:ext:res, -ext:ext:res, -ext:ext:res]
    return calc_gyroid(x, y, z, t, a)
