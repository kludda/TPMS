import numpy as np
from numpy import sin, cos, pi

import logging
logger = logging.getLogger(__name__)


def gyroid(x, y, z, t, a):
    x = pi * a * x
    y = pi * a * y
    z = pi * a * z
    return np.sin(x)*np.cos(y) + \
        np.sin(y)*np.cos(z) +\
        np.sin(z)*np.cos(x) - t
