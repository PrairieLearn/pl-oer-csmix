import numpy as np


def rmse(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def accuracy(y_true, y_pred):
    return np.mean(y_true == y_pred)


def mae(y_true, y_pred):
    return np.mean(np.abs(y_true - y_pred))
