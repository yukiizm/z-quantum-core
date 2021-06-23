import operator
from functools import reduce
from typing import Callable, Dict

import tequila as tq
import tequila.circuit.gates

from .. import _circuit, _gates, _operations

# TODO: figure out how to handle I & RH gates


ZQUANTUM_TEQUILA_MAP: Dict[str, Callable] = {
    # single-qubit, non-parametric
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
    # single-qubit, parametric
    **{
        name: getattr(tq.circuit.gates, name.lower().capitalize())
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
    # two-qubit, non-parametric
    **{
        name: getattr(tq.circuit.gates, name)
        for name in [
            "CNOT",
            "CZ",
            "SWAP",
        ]
    },
}


def export_to_tequila(circuit: _circuit.Circuit) -> tq.QCircuit:
    tq_gate_circuits = [_export_operation(op) for op in circuit.operations]
    return reduce(operator.add, tq_gate_circuits, tq.QCircuit())


def _export_operation(operation: _operations.Operation) -> tq.QCircuit:
    if not isinstance(operation, _gates.GateOperation):
        raise TypeError(f"Can't export {type(operation)} to tequila")

    gate_factory = ZQUANTUM_TEQUILA_MAP[operation.gate.name]
    return gate_factory(*operation.params, *operation.qubit_indices)
