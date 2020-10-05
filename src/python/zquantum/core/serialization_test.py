"""Test cases for serialization module."""
import json
import numpy as np
from .history.recorder import HistoryEntry, HistoryEntryWithArtifacts
from .utils import convert_array_to_dict, ValueEstimate
from .interfaces.optimizer import optimization_result
from .serialization import ZapataEncoder
from .bitstring_distribution import BitstringDistribution


def test_zapata_encoder_can_handle_numpy_arrays():
    dict_to_serialize = {
        "array_1": np.array([1, 2, 3]),
        "array_2": np.array([0.5 + 1j, 0.5 - 0.25j]),
        "list_of_arrays": [np.array([0.5, 0.4, 0.3]), np.array([1, 2, 3])],
    }

    deserialized_dict = json.loads(json.dumps(dict_to_serialize, cls=ZapataEncoder))
    expected_deserialized_dict = {
        "array_1": convert_array_to_dict(dict_to_serialize["array_1"]),
        "array_2": convert_array_to_dict(dict_to_serialize["array_2"]),
        "list_of_arrays": [
            convert_array_to_dict(arr) for arr in dict_to_serialize["list_of_arrays"]
        ],
    }
    assert deserialized_dict == expected_deserialized_dict


def test_zapata_encoder_can_handle_optimization_result():
    # The result constructed below does not make sense.
    # It does not matter though, as we are only testing serialization and it contains variety
    # of data to be serialized.
    result_to_serialize = optimization_result(
        opt_value=0.5,
        opt_params=np.array([0, 0.5, 2.5]),
        nit=3,
        fev=10,
        history=[
            HistoryEntry(
                call_number=0,
                params=np.array([0.1, 0.2, 0.3j]),
                value=ValueEstimate(0.5, precision=6),
            ),
            HistoryEntry(call_number=1, params=np.array([1, 2, 3]), value=-10.0),
            HistoryEntryWithArtifacts(
                call_number=2,
                params=np.array([-1, -0.5, -0.6]),
                value=-20.0,
                artifacts={
                    "bitstring": "0111",
                    "bitstring_distribution": BitstringDistribution({"111": 0.25, "010": 0.75}),
                },
            ),
        ],
    )

    expected_deserialized_result = {
        "opt_value": 0.5,
        "opt_params": convert_array_to_dict(np.array([0, 0.5, 2.5])),
        "nit": 3,
        "fev": 10,
        "history": [
            {
                "call_number": 0,
                "params": convert_array_to_dict(np.array([0.1, 0.2, 0.3j])),
                "value": ValueEstimate(0.5, precision=6).to_dict(),
            },
            {
                "call_number": 1,
                "params": convert_array_to_dict(np.array([1, 2, 3])),
                "value": -10.0,
            },
            {
                "call_number": 2,
                "params": convert_array_to_dict(np.array([-1, -0.5, -0.6])),
                "value": -20.0,
                "artifacts": {
                    "bitstring": "0111",
                    "bitstring_distribution": {"111": 0.25, "010": 0.75},
                },
            },
        ],
    }

    deserialized_result = json.loads(json.dumps(result_to_serialize, cls=ZapataEncoder))

    assert deserialized_result == expected_deserialized_result