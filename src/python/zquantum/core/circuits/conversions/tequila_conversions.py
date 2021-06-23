import operator
from functools import reduce

import tequila as tq
import tequila.circuit.gates

from .. import _circuit, _gates, _operations

# TODO: figure out how to handle I & RH gates


def _tequila_gate_name(zquantum_gate_name):
    return zquantum_gate_name.lower().capitalize()


ZQUANTUM_TEQUILA_MAP = {
    **{
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
    },
    **{
        name: getattr(tq.circuit.gates, _tequila_gate_name(name))
        for name in [
            "RX",
            "RY",
            "RZ",
            # "RH",
            "PHASE",
        ]
    },
    "PHASE": lambda angle, qubit: tq.circuit.gates.Phase(
        target=qubit,
        control=None,
        angle=angle,
    ),
    "U3": tq.circuit.gates.u3,
}


def export_to_tequila(circuit: _circuit.Circuit) -> tq.QCircuit:
    tq_gate_circuits = [_export_operation(op) for op in circuit.operations]
    return reduce(operator.add, tq_gate_circuits, tq.QCircuit())


def _export_operation(operation: _operations.Operation) -> tq.QCircuit:
    if not isinstance(operation, _gates.GateOperation):
        raise TypeError(f"Can't export {type(operation)} to tequila")

    gate_factory = ZQUANTUM_TEQUILA_MAP[operation.gate.name]
    return gate_factory(*operation.params, *operation.qubit_indices)
