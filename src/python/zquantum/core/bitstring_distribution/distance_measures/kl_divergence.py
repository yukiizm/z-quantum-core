import numpy as np
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from zquantum.core.bitstring_distribution import BitstringDistribution


def compute_rbf_kernel(x_i: np.array, y_j: np.array, sigma: float) -> np.ndarray:
    """ Compute the gaussian (RBF) kernel matrix K, with K_ij = exp(-gamma |x_i - y_j|^2) and gamma = 1/(2*sigma).

        Args:
            x_i (np.array): Samples A (integers).
            y_j (np.array): Samples B (integers).
            sigma (float): The bandwidth of the gaussian kernel.

        Returns:
            np.ndarray: The gaussian kernel matrix.
    """
    exponent = np.abs(x_i[:, None] - y_j[None, :]) ** 2
    try:
        gamma = 1.0 / (2 * sigma)
    except ZeroDivisionError as error:
        print("Handling run-time error:", error)
        raise
    kernel_matrix = np.exp(-gamma * exponent)
    return kernel_matrix


def compute_multi_rbf_kernel(x_i: np.array, y_j: np.array, sigmas: List) -> np.ndarray:
    """ Compute the multi-gaussian (RBF) kernel matrix K, with K_ij = 1/N * Sum_n [exp(-gamma_n |x_i - y_j|^2)] with n = 1,...,N and gamma = 1/(2*sigma).

        Args:
            x_i (np.array): Samples A (integers).
            y_j (np.array): Samples B (integers).
            sigmas (np.array): The list of bandwidths of the multi-gaussian kernel.

        Returns:
            np.ndarray: The gaussian kernel matrix.
    """
    exponent = np.abs(x_i[:, None] - y_j[None, :]) ** 2
    kernel_matrix = 0.0
    for sigma in sigmas:
        try:
            gamma = 1.0 / (2 * sigma)
        except ZeroDivisionError as error:
            print("Handling run-time error:", error)
            raise
        kernel_matrix = kernel_matrix + np.exp(-gamma * exponent)
    return kernel_matrix / len(sigmas)


def compute_kl_divergence(
    target_distribution: "BitstringDistribution",
    measured_distribution: "BitstringDistribution",
    distance_measure_parameters: Dict,
) -> float:
    """ Compute the squared Maximum Mean Discrepancy (MMD) distance measure between between a target bitstring distribution
    and a measured bitstring distribution.
    Reference: arXiv.1804.04168.

        Args:
            target_distribution (BitstringDistribution): The target bitstring probability distribution.
            measured_distribution (BitstringDistribution): The measured bitstring probability distribution.

            distance_measure_parameters (dict):
                - sigma (float/np.array): the bandwidth parameter used to compute the single/multi gaussian kernel. The default value is 1.0.

        Returns:
            float: The value of the maximum mean discrepancy.
    """

    print("target_distribution")
    print(target_distribution)
    print("measured_distribution")
    print(measured_distribution)
    print("distance_measure_parameters")
    print(distance_measure_parameters)
    sigma = distance_measure_parameters.get("sigma", 1.0)
    target_keys = target_distribution.distribution_dict.keys()
    measured_keys = measured_distribution.distribution_dict.keys()
    all_keys = set(target_keys).union(measured_keys)

    target_values = []
    measured_values = []
    for bitstring in all_keys:
        # Add 0 to the values list whenever a bistrings isn't found among the keys.
        target_values.append(target_distribution.distribution_dict.get(bitstring, 0))
        measured_values.append(
            measured_distribution.distribution_dict.get(bitstring, 0)
        )

    basis = np.asarray([int(item, 2) for item in all_keys])  # bitstring to int
    if not hasattr(sigma, "__len__"):
        kernel_matrix = compute_rbf_kernel(basis, basis, sigma)
    else:
        kernel_matrix = compute_multi_rbf_kernel(basis, basis, sigma)

    diff = np.array(target_values) - np.array(measured_values)
    return diff.dot(kernel_matrix.dot(diff))
