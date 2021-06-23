import numpy as np
import numpy.testing
import pytest
import tequila as tq
import tequila.circuit.gates
from zquantum.core import circuits
from zquantum.core.circuits.conversions import tequila_conversions

EQUIVALENT_CIRCUITS = [
    # empty
    (circuits.Circuit([]), tq.circuit.QCircuit()),
    # simplest case - single gate circuit
    (circuits.Circuit([circuits.X(0)]), tq.circuit.gates.X(0)),
    # all ZQuantum single-qubit, non-parametric gates
    (
        circuits.Circuit(
            [
                circuits.X(1),
                circuits.Y(0),
                circuits.Z(4),
                circuits.H(3),
                # circuits.I(1),
                circuits.S(1),
                circuits.T(1),
            ]
        ),
        (
            tq.gates.X(1)
            + tq.circuit.gates.Y(0)
            + tq.circuit.gates.Z(4)
            + tq.circuit.gates.H(3)
            + tq.circuit.gates.S(1)
            + tq.circuit.gates.T(1)
        ),
    ),
    # all ZQuantum single-qubit, parametric gates
    *[
        (
            circuits.Circuit(
                [
                    circuits.RX(angle)(1),
                    circuits.RY(angle)(0),
                    circuits.RZ(angle)(4),
                    # circuits.RH(angle)(0),
                    circuits.PHASE(angle)(1),
                    circuits.U3(angle, angle + 0.1, angle - 0.3)(0),
                ]
            ),
            (
                tq.circuit.gates.Rx(angle, 1)
                + tq.circuit.gates.Ry(angle, 0)
                + tq.circuit.gates.Rz(angle, 4)
                + tq.circuit.gates.Phase(1, None, angle)
                + tq.circuit.gates.u3(angle, angle + 0.1, angle - 0.3, 0)
            ),
        )
        for angle in [0.0, 0.1, np.pi, 2 * np.pi, np.pi / 5, 10 * np.pi]
    ],
    # all ZQuantum two-qubit, non-parametric gates
    (
        circuits.Circuit(
            [
                circuits.CNOT(0, 1),
                circuits.CZ(0, 3),
                circuits.SWAP(3, 1),
            ]
        ),
        (
            tq.gates.CNOT(control=0, target=1)
            + tq.circuit.gates.CZ(control=0, target=3)
            + tq.circuit.gates.SWAP(3, 1)
        ),
    ),
]


class TestCircuitEquivalence:
    @pytest.mark.parametrize("zquantum_circuit,tequila_circuit", EQUIVALENT_CIRCUITS)
    def test_exporting_matches_equivalent_circuit(
        self, zquantum_circuit, tequila_circuit
    ):
        assert (
            tequila_conversions.export_to_tequila(zquantum_circuit) == tequila_circuit
        )

    # TODO: compare matrices after the export
