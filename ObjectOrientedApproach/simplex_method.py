from warnings import warn
import copy
from simplex_table import SimplexTable


class SimplexMethod(object):

    def __init__(self, num_vars: int, constraints: list, objective_function: str):
        """
        The method is designed to initialize the parameters of the simplex algorithm:
        - formation of the initial simplex table,
        - initialization of basic variables,
        - checking the solvability condition of the linear programming problem,
        - initialization of the dictionary for storing the history of changes in the simplex table and basic variables
        :param num_vars: number of variables
        :param constraints: list of constraints
         (for example ['1x_1 + 2x_2 >= 4', '2x_3 + 3x_1 <= 5', 'x_3 + 3x_2 = 6'])
        :param objective_function: tuple in which two string values are specified: objective function
         (for example, '2x_1 + 4x_3 + 5x_2') optimization direction ('min' or 'max')
        """
        self.simplex_history = {}
        self.basic_vars_history = {}
        self.num_vars = num_vars
        self.objective = objective_function[0]
        self.objective_function = objective_function[1]
        self.constraints = constraints
        self.simplex_table = SimplexTable(self.num_vars, self.constraints, self.objective, self.objective_function)
        self.r_rows, self.num_s_vars, self.num_r_vars = self.simplex_table.get_matrix_params()
        self.basic_vars = [0 for _ in range(len(self.simplex_table))]
        r_index = self.num_r_vars + self.num_s_vars
        for i in self.basic_vars:
            if i > r_index:
                raise ValueError("Infeasible solution")
        self._delete_r_vars()
        #self.simplex_vals, self.simplex_solution = self.solve()

    def solve(self):
        """
        The method is designed to solve the problem of linear programming by the simplex method.
        In the method body of each iteration of the loop, the optimality condition of the objective function is
        checked under the specified constraints, if this condition is true, the problem is considered solved and the
        iterations stop, otherwise one step of the simplex method is performed
        :return:
        optimum (float) – the optimal value of the objective function obtained by the simplex method
        optimal_plane (dict) - optimal plan obtained by simplex method (solution of linear programming problem)
        """
        for row, column in enumerate(self.basic_vars[1:]):
            if self.simplex_table[0][column] != 0:
                const = -self.simplex_table[0][column]
                result = self.simplex_table.multiply_const_row(const, row)
                self.simplex_table[0] = self.simplex_table.sum_rows(self.simplex_table[0], result)
        self.simplex_history['Initial Simplex-method table'] = (copy.deepcopy(self.simplex_table.get_table()))
        self.basic_vars_history['Initial Simplex-method table'] = copy.deepcopy(self.basic_vars)
        step = 1
        while not self._check_condition():
            key_column = self._find_key_column()
            key_row = self._find_key_row(key_column=key_column)
            self.simplex_step(key_column, key_row)
            self.simplex_history[f'Simplex-method step {step}'] = copy.deepcopy(self.simplex_table.get_table())
            self.basic_vars_history[f'Simplex-method step {step}'] = copy.deepcopy(self.basic_vars)

            step += 1
        optimum = self.simplex_table[0][-1]
        optimal_plane = self.get_solution()
        return optimum, optimal_plane

    def get_solution(self):
        """
        The method generates an optimal plan based on the current simplex table.
        :return: optimal_plane (dict) - optimal plan obtained by simplex method (solution of linear programming problem)
        """
        optimal_plane = {}
        for i, var in enumerate(self.basic_vars[1:]):
            if var < self.num_vars:
                optimal_plane['x_' + str(var + 1)] = self.simplex_table[i + 1][-1]
        for i in range(0, self.num_vars):
            if i not in self.basic_vars[1:]:
                optimal_plane['x_' + str(i + 1)] = 0
        return optimal_plane

    def simplex_step(self, key_column: int, key_row: int):
        """
        The method performs one step of the simplex algorithm:
        - input of new basic variables and output of old variables from the basis,
        - search for a permissive element,
        - normalization of the permissive row to the permissive element,
        - zeroing of the permissive column.
        :param key_column: index of the permissive column
        :param key_row: index of the permissive row
        :return:
        """
        self.basic_vars[key_row] = key_column
        pivot = self.simplex_table[key_row][key_column]
        self._normalize_to_pivot(key_row, pivot)
        self._make_key_column_zero(key_column, key_row)

    def _check_condition(self):
        """
        The method checks the optimality condition of the objective function for the current simplex table
         (all values in the row of the objective function are negative or equal to zero)
        :return: condition (bool): True if the optimality condition is met, False otherwise
        """
        F = self.simplex_table[0]
        negative_values = list(filter(lambda x: x <= 0, F))
        condition = len(negative_values) == len(F)
        return condition

    def _find_key_column(self):
        """
        The method is designed to find the resolving column in the current simplex table
        :return: key_column (int):  index of the resolving column
        """
        key_columns = 0
        for i in range(0, len(self.simplex_table[0]) - 1):
            if abs(self.simplex_table[0][i]) >= abs(self.simplex_table[0][key_columns]):
                key_columns = i

        return key_columns

    def _find_key_row(self, key_column: int):
        """
        The method is designed to search for a permissive row in the permissive column of the current simplex table.
        :param key_column: index of the resolving column
        :return: key_row (int): index of the resolving string
        """
        min_val = float("inf")
        key_row = 0
        for i in range(1, len(self.simplex_table)):
            if self.simplex_table[i][key_column] > 0:
                val = self.simplex_table[i][-1] / self.simplex_table[i][key_column]
                if val < min_val:
                    min_val = val
                    key_row = i
        if min_val == float("inf"):
            raise ValueError("Unbounded solution")
        if min_val == 0:
            warn("Dengeneracy")
        return key_row

    def _normalize_to_pivot(self, key_row: int, pivot: float):
        """
        The method divides the resolving row of the current simplex table by the resolving element
        :param key_row: index of the permissive row
        :param pivot: resolving element
        :return: None
        """
        for i in range(len(self.simplex_table[0])):
            self.simplex_table[key_row][i] /= pivot

    def _make_key_column_zero(self, key_column: int, key_row: int):
        """
        The method zeroes the elements of the resolving column of the current simplex table
        with the exception of the element standing in the resolving row by the Jordano-Gauss method
        :param key_column: index of the permissive column
        :param key_row: index of the permissive row
        :return: None
        """
        num_columns = len(self.simplex_table[0])
        for i in range(len(self.simplex_table)):
            if i != key_row:
                factor = self.simplex_table[i][key_column]
                for j in range(num_columns):
                    self.simplex_table[i][j] -= self.simplex_table[key_row][j] * factor

    def _delete_r_vars(self):
        for i in range(len(self.simplex_table)):
            non_r_length = self.num_vars + self.num_s_vars + 1
            length = len(self.simplex_table[i])
            while length != non_r_length:
                del self.simplex_table[i][non_r_length-1]
                length -= 1

    def _phase1(self):
        # Objective function here is minimize r1+ r2 + r3 + ... + rn
        r_index = self.num_vars + self.num_s_vars
        for i in range(r_index, len(self.simplex_table[0]) - 1):
            self.simplex_table.set_item(0, i, -1)
        for i in self.r_rows:
            self.simplex_table[0] = self.simplex_table.sum_rows_by_index(0, i)
            self.basic_vars[i] = r_index
            r_index += 1
        s_index = self.num_vars
        for i in range(1, len(self.basic_vars)):
            if self.basic_vars[i] == 0:
                self.basic_vars[i] = s_index
                s_index += 1
        step = 0
        while not self._check_condition():
            key_column = self._find_key_column()
            key_row = self._find_key_row(key_column=key_column)
            self.simplex_step(key_column, key_row)
            self.simplex_history[f'Simplex-method step {step}'] = copy.deepcopy(self.simplex_table.get_table())
            self.basic_vars_history[f'Simplex-method step {step}'] = copy.deepcopy(self.simplex_table.get_table())
            step += 1
