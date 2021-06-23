import operator
from functools import reduce

import tequila as tq
import tequila.circuit.gates

from .. import _circuit, _gates, _operations


def import_from_tequila(circuit: tq.QCircuit) -> _circuit.Circuit:
    pass


# TODO: figure out how to handle I gate

ZQUANTUM_NAME_TO_TEQUILA_GATE = {
    name: getattr(tq.circuit.gates, name)
    for name in [
        "X",
        "Y",
        "Z",
        "H",
        # "I",
        "S",
        "T",
    ]
}


def export_to_tequila(circuit: _circuit.Circuit) -> tq.QCircuit:
    tq_gate_circuits = [_export_operation(op) for op in circuit.operations]
    return reduce(operator.add, tq_gate_circuits, tq.QCircuit())


def _export_operation(operation: _operations.Operation) -> tq.QCircuit:
    if not isinstance(operation, _gates.GateOperation):
        raise TypeError(f"Can't export {type(operation)} to tequila")

    gate_factory = ZQUANTUM_NAME_TO_TEQUILA_GATE[operation.gate.name]
    return gate_factory(*operation.qubit_indices)
