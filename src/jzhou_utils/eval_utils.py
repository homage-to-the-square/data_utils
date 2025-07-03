import numpy as np
from scipy.stats import norm

def normal_CI_2_sided_multiplier(alpha: float) -> float:
    """
    Given significance level alpha (e.g., 0.05), return the confidence interval multiplier.
    """
    return norm.ppf(1 - alpha / 2)

    
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