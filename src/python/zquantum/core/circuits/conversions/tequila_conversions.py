import operator
from functools import reduce

import tequila as tq

from .. import _circuit, _gates, _operations


def import_from_tequila(circuit: tq.QCircuit) -> _circuit.Circuit:
    pass


def export_to_tequila(circuit: _circuit.Circuit) -> tq.QCircuit:
    tq_gate_circuits = [_export_operation(op) for op in circuit.operations]
    return reduce(operator.add, tq_gate_circuits, tq.QCircuit())


def _export_operation(operation: _operations.Operation) -> tq.QCircuit:
    if not isinstance(operation, _gates.GateOperation):
        raise TypeError(f"Can't export {type(operation)} to tequila")

    op: _gates.GateOperation = operation
    if op.gate.name == "X":
        return tq.gates.X(op.qubit_indices[0])

    raise NotImplementedError()
