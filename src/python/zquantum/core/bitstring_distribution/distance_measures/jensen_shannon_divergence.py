from typing import TYPE_CHECKING, Dict

from .clipped_negative_log_likelihood import compute_clipped_negative_log_likelihood

if TYPE_CHECKING:
    from zquantum.core.bitstring_distribution import BitstringDistribution


def compute_jensen_shannon_divergence(
    target_distribution: "BitstringDistribution",
    measured_distribution: "BitstringDistribution",
    distance_measure_parameters: Dict,
) -> float:
    """Computes the symmetrized version of the clipped negative log likelihood between a target bitstring distribution
    and a measured bitstring distribution
    See Equation (4) in https://advances.sciencemag.org/content/5/10/eaaw9918?rss=1

    Args:
        target_distribution (BitstringDistribution): The target bitstring probability distribution.
        measured_distribution (BitstringDistribution): The measured bitstring probability distribution.

        distance_measure_parameters (dict):
            - epsilon (float): The small parameter needed to regularize log computation when argument is zero. The default value is 1e-9.

    Returns:
        float: The value of the symmetrized version
    """

    value = (
        compute_clipped_negative_log_likelihood(
            target_distribution, measured_distribution, distance_measure_parameters
        )
        / 2
        + compute_clipped_negative_log_likelihood(
            measured_distribution, target_distribution, distance_measure_parameters
        )
        / 2
    )

    return value
