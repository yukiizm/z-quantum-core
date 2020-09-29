import numpy as np
import sympy
import json
import copy
import warnings
from typing import Tuple, Union, Dict, TextIO
from collections import Counter
from ...utils import SCHEMA_VERSION


class Gate(object):
    """Class for storing information associated with a quantum gate.

    Attributes:
        matrix (sympy.Matrix): two-dimensional array defining the matrix representing the quantum operator
        qubits (tuple[int]): A list of qubit indices that the operator acts on
        symbolic_params (set(sympy.Symbol)): A set of the parameter names used in the gate. If the gate is not
            parameterized, this value is the empty set.
    """

    def __init__(self, matrix: sympy.Matrix, qubits: Tuple[int]):
        """Initialize a gate

        Args:
            matrix (sympy.Matrix): See class definition
            qubits (tuple(int)): See class definition
        """
        self._assert_is_valid_operator(matrix, qubits)
        self._assert_qubits_are_unique(qubits)

        copied_matrix = copy.deepcopy(matrix)
        for index, element in enumerate(copied_matrix):
            copied_matrix[index] = element.evalf()
        self.matrix = copied_matrix
        self.qubits = qubits

    def _assert_is_valid_operator(self, matrix: sympy.Matrix, qubits: Tuple[int]):
        """Check to make sure the the given operator is a valid Gate. This function asserts that
        the shape of the matrix is a 2**N by 2**N matrix and that the operator is a unitary (if the operator
        has parameters, the assertion that the operator is unitary is skipped).

        Args:
            matrix (sympy.Matrix): See class definition
            qubits (tuple(int)): See class definition
        """
        # Make sure matrix is square
        is_square = True
        shape = matrix.shape
        assert len(shape) == 2
        assert shape[0] == shape[1]

        # Make sure matrix is associated with correct number of qubits
        assert 2 ** len(qubits) == shape[0]

    def _assert_qubits_are_unique(self, qubits: Tuple[int]):
        """Check to make sure the the qubits used in the gate are unique.

        Args:
            qubits (tuple(int)): See class definition
        """
        assert len(set(qubits)) == len(qubits)

    @property
    def is_parameterized(self):
        """Boolean indicating if any symbolic parameters used in the gate"""
        for element in self.matrix:
            if isinstance(element, sympy.Expr):
                return True
        return False

    @property
    def symbolic_params(self):
        """A set containing all the sympy symbols used in the gate"""
        all_symbols = []
        for element in self.matrix:
            if isinstance(element, sympy.Expr):
                for symbol in element.free_symbols:
                    all_symbols.append(symbol)
        return set(all_symbols)

    def __eq__(self, another_gate):
        """Determine if two gates are equivalent.

        Args:
            another_gate (Gate): The gate with which to compare

        Returns:
            boolean
        """
        if len(self.qubits) != len(another_gate.qubits):
            return False
        for qubit, another_qubit in zip(self.qubits, another_gate.qubits):
            if qubit != another_qubit:
                return False

        if len(self.matrix) != len(another_gate.matrix):
            return False
        for element, another_element in zip(self.matrix, another_gate.matrix):
            if element != another_element:
                if isinstance(
                    element, (sympy.Number, sympy.Mul, sympy.Add)
                ) and isinstance(another_element, (sympy.Number, sympy.Mul, sympy.Add)):
                    if not np.isclose(
                        complex(sympy.re(element), sympy.im(element)),
                        complex(
                            sympy.re(another_element),
                            sympy.im(another_element),
                        ),
                    ):
                        return False
                else:
                    return False

        if self.symbolic_params != another_gate.symbolic_params:
            return False

        return True

    def __repr__(self):
        """String representation of the Gate object

        Returns:
            string
        """
        return f"zquantum.core.circuit.gate.Gate(matrix={self.matrix}, qubits={self.qubits})"

    def to_dict(self, serializable: bool = True):
        """Convert the Gate object into a dictionary

        Args:
            serializable (bool): If true, the returned dictionary is serializable so that it can be stored
                in JSON format

        Returns:
            Dict: keys are schema, qubits, matrix, and symbolic_params
        """
        gate_dict = {"schema": SCHEMA_VERSION + "-gate"}
        if serializable:
            gate_dict["qubits"] = list(self.qubits)
            gate_dict["matrix"] = []
            for i in range(self.matrix.shape[0]):
                gate_dict["matrix"].append({"elements": []})
                for element in self.matrix.row(i):
                    gate_dict["matrix"][-1]["elements"].append(str(element))
            gate_dict["symbolic_params"] = [
                str(param) for param in self.symbolic_params
            ]
        else:
            gate_dict["qubits"] = self.qubits
            gate_dict["matrix"] = self.matrix
            gate_dict["symbolic_params"] = self.symbolic_params
        return gate_dict

    def save(self, filename: str):
        """Save the Gate object to file in JSON format

        Args:
            filename (str): The path to the file to store the Gate
        """
        with open(filename, "w") as f:
            f.write(json.dumps(self.to_dict(serializable=True), indent=2))

    @classmethod
    def load(cls, data: Union[Dict, TextIO]):
        """Load a Gate object from either a file/file-like object or a dictionary

        Args:
            data (Union[Dict, TextIO]): The data to load into the gate object

        Returns:
            Gate
        """
        if isinstance(data, str):
            with open(data, "r") as f:
                data = json.load(f)
        elif not isinstance(data, dict):
            data = json.load(data)

        qubits = tuple(data["qubits"])

        if not isinstance(data["matrix"], sympy.Matrix):
            matrix = []
            for row_index, row in enumerate(data["matrix"]):
                new_row = []
                for element_index in range(len(row["elements"])):
                    new_row.append(sympy.sympify(row["elements"][element_index]))
                matrix.append(new_row)
            matrix = sympy.Matrix(matrix)
        else:
            matrix = data["matrix"]

        return cls(matrix, qubits)

    def evaluate(self, symbols_map: Dict):
        """Create a copy of the current Gate with the parameters in the gate evaluated to the values
        provided in the input symbols map

        Args:
            symbols_map (Dict): A map of the symbols/gate parameters to new values

        Returns:
            Gate
        """
        if not self.is_parameterized:
            warnings.warn(
                """Gate is not parameterized. evaluate will return a copy of the current gate"""
            )
            return copy.deepcopy(self)

        for symbol in symbols_map.keys():
            if symbol not in self.symbolic_params:
                warnings.warn(
                    """
                Trying to evaluate gate with symbols not existing in the gate:
                Symbols in circuit: {0}
                Symbols in the map: {1}
                """.format(
                        self.symbolic_params, symbols_map.keys()
                    ),
                    Warning,
                )

        gate_class = type(self)

        evaluated_matrix = copy.deepcopy(self.matrix)
        for index, element in enumerate(evaluated_matrix):
            new_element = element.subs(symbols_map).evalf()
            if isinstance(sympy.re(new_element), sympy.Number) and isinstance(
                sympy.im(new_element), sympy.Number
            ):
                new_element = complex(
                    round(sympy.re(new_element), 16), round(sympy.im(new_element), 16)
                )
            evaluated_matrix[index] = new_element

        evaluated_gate = gate_class(evaluated_matrix, self.qubits)
        return evaluated_gate