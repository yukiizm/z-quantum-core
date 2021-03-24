import numpy as np
from zquantum.core.gradients import finite_differences_gradient
from zquantum.core.interfaces.functions import FunctionWithGradient
from zquantum.core.interfaces.optimizer_test import (
    OptimizerTests,
    rosenbrock_function,
    sum_x_squared,
)
from .scipy_optimizer import ScipyOptimizer
from .layerwise_ansatz_optimizer import LayerwiseAnsatzOptimizer
import pytest
import networkx as nx
from zquantum.qaoa.farhi_ansatz import QAOAFarhiAnsatz
from zquantum.qaoa.maxcut import get_random_maxcut_hamiltonians
from qequlacs import QulacsSimulator
from zquantum.core.cost_function import AnsatzBasedCostFunction
from zquantum.core.estimator import ExactEstimator


@pytest.fixture(
    params=[
        {"method": "BFGS"},
        {"method": "L-BFGS-B"},
        {"method": "Nelder-Mead"},
        {"method": "SLSQP"},
        {"method": "COBYLA", "options": {"maxiter": 50000, "tol": 1e-7}},
    ]
)
def optimizer(request):
    return ScipyOptimizer(**request.param)


class TestLayerwiseAnsatzOptimizer:
    def test_SLSQP_with_equality_constraints(self):
        # Given
        while True:
            H = get_random_maxcut_hamiltonians(
                {"type_graph": "complete"},
                number_of_instances=1,
                possible_number_of_qubits=5,
            )[0]

            if str(H) != "0":
                break

        ansatz = QAOAFarhiAnsatz(1, cost_hamiltonian=H)
        backend = QulacsSimulator()
        # backend = ForestSimulator("4q-qvm", n_samples=10000)
        # optimizer = GridSearchOptimizer(grid)
        optimizer = ScipyOptimizer(method="L-BFGS-B")
        estimator = ExactEstimator()
        cost_function = AnsatzBasedCostFunction(H, ansatz, backend, estimator=estimator)
        lbl_optimizer = LayerwiseAnsatzOptimizer(optimizer)

        # When
        results = lbl_optimizer.minimize_lbl(
            cost_function, 4, 4, [0, 0]*4, [np.pi, np.pi / 2]*4
        )

        # # Then
        # assert results.opt_value == pytest.approx(target_value, abs=1e-3)
        # assert results.opt_params == pytest.approx(target_params, abs=1e-3)

    def test_SLSQP_with_inequality_constraints(self):
        # Given
        cost_function = FunctionWithGradient(
            rosenbrock_function, finite_differences_gradient(rosenbrock_function)
        )
        constraints = {"type": "ineq", "fun": lambda x: x[0] + x[1] - 3}
        optimizer = ScipyOptimizer(method="SLSQP")
        initial_params = np.array([0, 0])

        # When
        results_without_constraints = optimizer.minimize(
            cost_function, initial_params=initial_params
        )
        optimizer.constraints = constraints
        results_with_constraints = optimizer.minimize(
            cost_function, initial_params=initial_params
        )

        # Then
        assert results_without_constraints.opt_value == pytest.approx(
            results_with_constraints.opt_value, abs=1e-1
        )
        assert results_with_constraints.opt_params.sum() >= 3
