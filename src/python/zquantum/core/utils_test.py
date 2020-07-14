import unittest
import os
import random
import numpy as np
from scipy.linalg import expm
from scipy.stats import unitary_group
import sympy

from openfermion.utils import qubit_operator_sparse
from .utils import (
    convert_array_to_dict,
    convert_dict_to_array,
    dec2bin,
    bin2dec,
    is_identity,
    is_unitary,
    compare_unitary,
    RNDSEED,
    ValueEstimate,
    save_value_estimate,
    load_value_estimate,
    save_list,
    load_list,
    create_object,
    get_func_from_specs,
    load_noise_model,
    save_noise_model,
    create_symbols_map,
)
from .interfaces.mock_objects import MockQuantumSimulator


class TestUtils(unittest.TestCase):
    def test_real_array_conversion(self):
        arr = np.array([[1.0, 2.0], [3.0, 4.0]])
        dictionary = convert_array_to_dict(arr)
        new_arr = convert_dict_to_array(dictionary)
        self.assertTrue(np.allclose(arr, new_arr))

    def test_complex_array_conversion(self):
        arr = np.array([[1.0, 2.0], [3.0, 4.0j]])
        dictionary = convert_array_to_dict(arr)
        new_arr = convert_dict_to_array(dictionary)
        self.assertTrue(np.allclose(arr, new_arr))

    def test_dec_bin_conversion(self):
        integer = random.randint(1, 10 ** 9)
        integer2 = bin2dec(dec2bin(integer, 30))
        self.assertEqual(integer, integer2)

    def test_is_identity(self):
        # Given
        matrix1 = np.eye(4)
        random.seed(RNDSEED)
        matrix2 = np.array(
            [[random.uniform(-1, 1) for x in range(0, 4)] for y in range(0, 4)]
        )
        # When/Then
        self.assertTrue(is_identity(matrix1))
        self.assertFalse(is_identity(matrix2))

    def test_is_unitary(self):
        # Given
        U = unitary_group.rvs(4)
        # When/Then
        self.assertTrue(is_unitary(U))

    def test_compare_unitary(self):
        # Given
        U1 = unitary_group.rvs(4)
        U2 = unitary_group.rvs(4)
        # When/Then
        self.assertFalse(compare_unitary(U1, U2))

    def test_sample_from_probability_distribution(self):
        pass

    def test_convert_bitstrings_to_tuples(self):
        pass

    def test_convert_tuples_to_bitstrings(self):
        pass

    def test_value_estimate_dict_conversion(self):
        pass

    def test_value_estimate_io(self):
        # Given
        value = -1.0
        precision = 0.1
        value_estimate_object = ValueEstimate(value, precision)

        # When
        save_value_estimate(value_estimate_object, "value_estimate.json")
        value_estimate_object_loaded = load_value_estimate("value_estimate.json")

        # Then
        self.assertEqual(
            value_estimate_object.value, value_estimate_object_loaded.value
        )
        self.assertEqual(
            value_estimate_object.precision, value_estimate_object_loaded.precision
        )

        # Given
        value_estimate_object = ValueEstimate(value)
        # When
        save_value_estimate(value_estimate_object, "value_estimate.json")
        value_estimate_object_loaded = load_value_estimate("value_estimate.json")
        # Then
        self.assertEqual(
            value_estimate_object.value, value_estimate_object_loaded.value
        )
        self.assertEqual(
            value_estimate_object.precision, value_estimate_object_loaded.precision
        )

        # Given
        value = np.float64(-1.0)
        precision = np.float64(0.1)
        value_estimate_object = ValueEstimate(value, precision)

        # When
        save_value_estimate(value_estimate_object, "value_estimate.json")
        value_estimate_object_loaded = load_value_estimate("value_estimate.json")

        # Then
        self.assertEqual(
            value_estimate_object.value, value_estimate_object_loaded.value
        )
        self.assertEqual(
            value_estimate_object.precision, value_estimate_object_loaded.precision
        )

        os.remove("value_estimate.json")

    def test_list_io(self):
        # Given
        initial_list = [0.1, 0.3, -0.3]
        # When
        save_list(initial_list, "list.json")
        loaded_list = load_list("list.json")
        # Then
        self.assertListEqual(initial_list, loaded_list)
        os.remove("list.json")

    def test_create_object(self):
        # Given
        n_samples = 100
        function_name = "MockQuantumSimulator"
        specs = {
            "module_name": "zquantum.core.interfaces.mock_objects",
            "function_name": function_name,
            "n_samples": n_samples,
        }

        # When
        mock_simulator = create_object(specs)

        # Then
        self.assertEqual(type(mock_simulator).__name__, function_name)
        self.assertEqual(mock_simulator.n_samples, n_samples)

    def test_get_func_from_specs(self):
        # Given
        function_name = "sum_x_squared"
        specs = {
            "module_name": "zquantum.core.interfaces.optimizer_test",
            "function_name": function_name,
        }
        data = np.array([1.0, 2.0])
        target_value = 5.0
        # When
        function = get_func_from_specs(specs)

        # Then
        self.assertEqual(function.__name__, function_name)
        self.assertEqual(function(data), target_value)

    def test_noise_model_io(self):
        # Given
        module_name = "zquantum.core.testing.mocks"
        function_name = "mock_create_noise_model"
        noise_model_data = {"testing": "data"}

        # When
        save_noise_model(
            noise_model_data, module_name, function_name, "noise_model.json",
        )
        noise_model = load_noise_model("noise_model.json")

        # Then
        self.assertEqual(noise_model, None)
        os.remove("noise_model.json")

    def test_create_symbols_map_with_correct_input(self):
        # Given
        symbol_1 = sympy.Symbol("alpha")
        symbol_2 = sympy.Symbol("beta")
        symbols = [symbol_1, symbol_2]
        params = np.array([1, 2])
        target_symbols_map = [(symbol_1, 1), (symbol_2, 2)]

        # When
        symbols_map = create_symbols_map(symbols, params)

        # Then
        self.assertEqual(symbols_map, target_symbols_map)

    def test_create_symbols_map_with_incorrect_input(self):
        # Given
        symbol_1 = sympy.Symbol("alpha")
        symbols = [symbol_1]
        params = np.array([1, 2])

        # When/Then
        with self.assertRaises(ValueError):
            symbols_map = create_symbols_map(symbols, params)
