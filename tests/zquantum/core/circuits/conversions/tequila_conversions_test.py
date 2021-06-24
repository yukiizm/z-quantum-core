import numpy as np
import numpy.testing
import pytest
import tequila as tq
import tequila.circuit.gates
from zquantum.core import circuits
from zquantum.core.circuits.conversions import tequila_conversions

# Example circuits that contain gates defined natively in both ZQuantum and Tequila,
# meaning:
# - the gate has an explicit named constructor
# - the gate has the same name as in the other framework
# - the gate has the same matrix as in the other framework (TODO: validate it)
NATIVE_GATES_EQUIVALENT_CIRCUITS = [
    # empty
    (circuits.Circuit([]), tq.circuit.QCircuit()),
    # simplest case - single gate circuit
    (circuits.Circuit([circuits.X(0)]), tq.circuit.gates.X(0)),
    # --- single-qubit, non-parametric gates ---
    (
        circuits.Circuit(
            [
                circuits.X(1),
                circuits.Y(0),
                circuits.Z(4),
                circuits.H(3),
            ]
        ),
        (
            tq.gates.X(1)
            + tq.circuit.gates.Y(0)
            + tq.circuit.gates.Z(4)
            + tq.circuit.gates.H(3)
        ),
    ),
    # --- single-qubit, parametric gates ---
    *[
        (
            circuits.Circuit(
                [
                    circuits.RX(angle)(1),
                    circuits.RY(angle)(0),
                    circuits.RZ(angle)(4),
                    circuits.PHASE(angle)(1),
                ]
            ),
            (
                tq.circuit.gates.Rx(angle, 1)
                + tq.circuit.gates.Ry(angle, 0)
                + tq.circuit.gates.Rz(angle, 4)
                + tq.circuit.gates.Phase(1, None, angle)
            ),
        )
        for angle in [0.0, 0.1, np.pi, 2 * np.pi, np.pi / 5, 10 * np.pi]
    ],
    # --- two-qubit, non-parametric gates ---
    (
        circuits.Circuit(
            [
                circuits.SWAP(3, 1),
            ]
        ),
        tq.circuit.gates.SWAP(3, 1),
    ),
]


def _normalize_gate_name(name: str):
    return name.lower()


@pytest.mark.parametrize(
    "zquantum_circuit,tequila_circuit", NATIVE_GATES_EQUIVALENT_CIRCUITS
)
class TestCircuitEquivalenceForNativeGates:
    class TestFixtureHealth:
        def test_gate_names_match(self, zquantum_circuit, tequila_circuit):
            for zquantum_op, tequila_gate in zip(
                zquantum_circuit.operations, tequila_circuit.gates
            ):
                assert _normalize_gate_name(
                    zquantum_op.gate.name
                ) == _normalize_gate_name(tequila_gate.name)

    class TestExporting:
        def test_matches_equivalent_circuit(self, zquantum_circuit, tequila_circuit):
            assert (
                tequila_conversions.export_to_tequila(zquantum_circuit)
                == tequila_circuit
            )


# Gates that are similar between ZQuantum and Tequila, but contain some implicit
# processing.
NON_NATIVE_EQUIVALENT_CIRCUITS = [
    # --- single-qubit, non-parametric gates ---
    # S and T gates are implicitly converted to phase by Tequila
    (
        circuits.Circuit(
            [
                circuits.S(2),
                circuits.T(1),
            ]
        ),
        tq.circuit.gates.S(2) + tq.circuit.gates.T(1),
    ),
    # --- single-qubit, parametric gates ---
    # u3 is implicitly decomposed to a circuit with RX+RY+RZ gates
    *[
        (
            circuits.Circuit(
                [
                    circuits.U3(angle, angle + 0.1, angle - 0.3)(0),
                ]
            ),
            tq.circuit.gates.u3(angle, angle + 0.1, angle - 0.3, 0),
        )
        for angle in [0.0, 0.1, np.pi, 2 * np.pi, np.pi / 5, 10 * np.pi]
    ],
    # --- two-qubit, non-parametric gates ---
    # CNOT is implicitly translated to X with control argument
    # CZ is implicitly translated to Z with control argument
    (
        circuits.Circuit(
            [
                circuits.CNOT(0, 1),
                circuits.CZ(0, 3),
            ]
        ),
        tq.gates.CNOT(control=0, target=1) + tq.circuit.gates.CZ(control=0, target=3),
    ),
    # --- two-qubit, parametric gates ---
    # Tequila has no explicit CPHASE gate
    *[
        (
            circuits.Circuit(
                [
                    circuits.CPHASE(angle)(1, 3),
                ]
            ),
            tq.circuit.gates.Phase(target=3, control=1, angle=angle),
        )
        for angle in [0.0, 0.1, np.pi, 2 * np.pi, np.pi / 5, 10 * np.pi]
    ],
]


@pytest.mark.parametrize(
    "zquantum_circuit,tequila_circuit", NON_NATIVE_EQUIVALENT_CIRCUITS
)
class TestCircuitEquivalenceForNonNativeGates:
    class TestExporting:
        def test_matches_equivalent_circuit(self, zquantum_circuit, tequila_circuit):
            assert (
                tequila_conversions.export_to_tequila(zquantum_circuit)
                == tequila_circuit
            )
