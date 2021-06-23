import pytest
import tequila as tq
from zquantum.core import circuits
from zquantum.core.circuits.conversions import tequila_conversions

EQUIVALENT_CIRCUITS = [
    (circuits.Circuit([]), tq.circuit.QCircuit()),
]


@pytest.mark.parametrize("zquantum_circuit,tequila_circuit", EQUIVALENT_CIRCUITS)
class TestCircuitEquivalence:
    def test_exporting_matches_equivalent_circuit(
        self, zquantum_circuit, tequila_circuit
    ):
        assert (
            tequila_conversions.export_to_tequila(zquantum_circuit) == tequila_circuit
        )
