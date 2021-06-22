import numpy as np


def rmse(y_true, y_train):
    n = len(y_true)
    sigma = ((y_true - y_train) ** 2).sum()
    return np.sqrt((1 / n) * sigma)
