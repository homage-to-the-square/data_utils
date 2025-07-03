import numpy as np

def compute_sharpe_w_cov(
    weights: np.ndarray, mu: np.ndarray, Sigma: np.ndarray
) -> list:
    """
    Given a 2d array of weights, where each column is a new set of weights, computes the
        Sharpe ratio with the mean and cov.
    """
    return [
        np.sum(weight * mu) / np.sqrt(weight @ Sigma @ weight.T) for weight in weights.T
    ]


def compute_port_utility(weight, gamma, mu, Sigma):
    return (weight.T @ mu) - gamma / 2 * (weight.T @ Sigma @ weight)