import pytest
import tequila as tq
import tequila.circuit.gates
from zquantum.core import circuits
from zquantum.core.circuits.conversions import tequila_conversions

EQUIVALENT_CIRCUITS = [
    (circuits.Circuit([]), tq.circuit.QCircuit()),
    (circuits.Circuit([circuits.X(0)]), tq.circuit.gates.X(0)),
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
]


@pytest.mark.parametrize("zquantum_circuit,tequila_circuit", EQUIVALENT_CIRCUITS)
class TestCircuitEquivalence:
    def test_exporting_matches_equivalent_circuit(
        self, zquantum_circuit, tequila_circuit
    ):
        assert (
            tequila_conversions.export_to_tequila(zquantum_circuit) == tequila_circuit
        )
