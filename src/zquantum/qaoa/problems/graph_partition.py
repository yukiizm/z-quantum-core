import networkx as nx

from qiskit.optimization.applications.ising import graph_partition
from zquantum.core.openfermion import QubitOperator, qiskitpauli_to_qubitop


def get_graph_partition_hamiltonian(graph: nx.Graph):
    """Converts a graph partition instance, as described by a weighted graph, to an Ising
    Hamiltonian.

    Args:
        graph (networkx.Graph): undirected weighted graph describing the problem
        instance.

    Returns:
        zquantum.core.openfermion.QubitOperator object describing the Hamiltonian

    """
    weight_matrix = nx.linalg.graphmatrix.adjacency_matrix(graph)
    qiskit_hamiltonian = graph_partition.get_operator(weight_matrix)
    return qiskitpauli_to_qubitop(qiskit_hamiltonian)