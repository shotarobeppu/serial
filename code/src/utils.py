import numpy as np

def check_nan(x):
    return isinstance(x, float) and np.isnan(x)