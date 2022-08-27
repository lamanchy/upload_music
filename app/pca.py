import warnings

import numpy as np
from scipy import linalg


def normalize(data):
    max_values = np.max(data, axis=0)
    min_values = np.min(data, axis=0)

    diff = max_values - min_values
    if not np.all(diff):
        problematic_dimensions = ", ".join(str(i + 1) for i, v
                                           in enumerate(diff) if v == 0)
        warnings.warn("No data variation in dimensions: %s. You should "
                      "check your data or disable normalization."
                      % problematic_dimensions)

    data = (data - min_values) / (max_values - min_values)
    data[np.logical_not(np.isfinite(data))] = 0
    return data


def pca(data, dimensions=2):
    data = np.array(data)
    # mean center the data
    data -= data.mean(axis=0)
    # calculate the covariance matrix
    R = np.cov(data, rowvar=False)
    # calculate eigenvectors & eigenvalues of the covariance matrix
    # use 'eigh' rather than 'eig' since R is symmetric, 
    # the performance gain is substantial
    evals, evecs = linalg.eigh(R)
    # sort eigenvalue in decreasing order
    idx = np.argsort(evals)[::-1]
    evecs = evecs[:, idx]
    # sort eigenvectors according to same index
    evals = evals[idx]
    # select the first n eigenvectors (n is desired dimension
    # of rescaled data array, or dimensions)
    evecs = evecs[:, :dimensions]
    # carry out the transformation on the data using eigenvectors
    # and return the re-scaled data, eigenvalues, and eigenvectors
    return np.dot(evecs.T, data.T).T.tolist(), evals.tolist(), evecs.tolist()


if __name__ == '__main__':
    print(normalize(pca([[0.0, 1.0], [1.0, 2.0], [5.0, 0.0]])[0]))
