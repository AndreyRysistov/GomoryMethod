from fractions import Fraction


class SimplexTable:

    def __init__(self, num_vars: int, constraints: list, objective: str, objective_function: str):
        """
        The method builds an initial simplex table from the specified constraints and the objective function.
        :param constraints: list of constraints (list of strings, for example ['1x_1 + 2x_2 >= 4', '2x_3 + 3x_1 <= 5', 'x_3 + 3x_2 = 6'])
        :param num_vars: number of variables
        :param objective: optimization direction ('min' or 'max')
        :param objective_function: objective function (for example, '2x_1 + 4x_3 + 5x_2')
        """
        self._num_s_vars = 0  # number of slack and surplus variables
        self._num_r_vars = 0  # number of additional variables to balance equality and less than equal to
        for expression in constraints:
            if '>=' in expression:
                self._num_s_vars += 1
            elif '<=' in expression:
                self._num_s_vars += 1
                self._num_r_vars += 1
            elif '=' in expression:
                self._num_r_vars += 1
        total_vars = num_vars + self._num_s_vars + self._num_r_vars

        self._coeff_matrix = [[Fraction("0/1") for _ in range(total_vars + 1)] for _ in range(len(constraints) + 1)]
        s_index = num_vars
        r_index = num_vars + self._num_s_vars
        self._r_rows = []  # stores the non -zero index of r
        for i in range(1, len(constraints) + 1):
            constraint = constraints[i - 1].split(' ')

            for j in range(len(constraint)):

                if '_' in constraint[j]:
                    coeff, index = constraint[j].split('_')
                    if constraint[j - 1] == '-':
                        self._coeff_matrix[i][int(index) - 1] = Fraction("-" + coeff[:-1] + "/1")
                    else:
                        self._coeff_matrix[i][int(index) - 1] = Fraction(coeff[:-1] + "/1")

                elif constraint[j] == '<=':
                    self._coeff_matrix[i][s_index] = Fraction("1/1")  # add surplus variable
                    s_index += 1

                elif constraint[j] == '>=':
                    self._coeff_matrix[i][s_index] = Fraction("-1/1")  # slack variable
                    self._coeff_matrix[i][r_index] = Fraction("1/1")  # r variable
                    s_index += 1
                    r_index += 1
                    self._r_rows.append(i)

                elif constraint[j] == '=':
                    self._coeff_matrix[i][r_index] = Fraction("1/1")  # r variable
                    r_index += 1
                    self._r_rows.append(i)

            self._coeff_matrix[i][-1] = Fraction(constraint[-1] + "/1")
        self._update_objective_function(objective_function, objective)

    def _update_objective_function(self, objective_function: str, objective: str):
        """
        The method adds a row with the objective function to the initial simplex table.
        The simplex table string is formed from the string argument objective_function is added to the beginning of the simplex table.
        If the objective function is to be maximized (objective='max' parameter),
        then the simplex string with the objective function is multiplied by -1.
        :param objective_function: objective function (for example, '2x_1 + 4x_3 + 5x_2')
        :param objective: – optimization direction ('min' or 'max')
        :return: None
        """
        objective_function_coeffs = objective_function.split()
        for i in range(len(objective_function_coeffs)):
            if '_' in objective_function_coeffs[i]:
                coeff, index = objective_function_coeffs[i].split('_')
                if objective_function_coeffs[i-1] == '-':
                    self.set_item(0, int(index)-1, int(coeff[:-1]))
                else:
                    self.set_item(0, int(index) - 1, -int(coeff[:-1]))
                if 'max' in objective:
                    self._coeff_matrix[0][int(index)-1] *= -1

    def get_matrix_params(self):
        """
        The method returns additional parameters of the simplex table necessary for the implementation of the simplex method:
        :return:
        num_s_vars (int): the number of weak (redundant variables), the number of additional variables
        num_r_vars (int): which reduce the constraints of the "inequality" type to the constraints of the "equality" type
        r_rows (list): list of row indexes with additional variables
        """
        return self._r_rows, self._num_s_vars, self._num_r_vars

    def get_table(self):
        """
        The method returns the current simplex table.
        :return: coff_matrix(list): simplex table
        """
        return self._coeff_matrix

    def add_zero_row(self):
        """
        The method adds a string consisting of zeros to the current simplex table
        :return: None
        """
        zero_row = [0 for _ in self._coeff_matrix[1]]
        self._coeff_matrix.append(zero_row)

    def sum_rows_by_index(self, index_left: int, index_right: int):
        """
        The method summarizes two rows of the current simplex table by their indexes.
        The indexes of the summed rows are set in the parameters
        :param index_left: index of the first line of the term
        :param index_right: index of the second line of the term
        :return:
        """
        row_left = self._coeff_matrix[index_left]
        row_right = self._coeff_matrix[index_right]
        size = len(self._coeff_matrix[index_left])
        sum_rows = [
            row_left[i] + row_right[i] for i in range(size)
        ]
        return sum_rows

    def sum_rows(self, row_left: list, row_right: list):
        """
        The method summarizes two rows of the current simplex table. The lines are set in the parameters
        :param row_left: the first line is the summand
        :param row_right: the second line is the summand
        :return: sum_rows (list): result summarizes
        """
        size = len(row_left)
        sum_rows = [row_left[i] + row_right[i] for i in range(size)]
        return sum_rows

    def multiply_const_row(self, const: float, index: int):
        """
        The method multiplies the string by a constant.
        The constant and index of the multiplied string are specified in the parameters
        :param const: the constant by which the string is multiplied
        :param index: index of the string to be multiplied by a constant
        :return: result (list): the result of multiplying a string by a constant
        """
        result = [const * i for i in self._coeff_matrix[index + 1]]
        return result

    def set_item(self, row, col, value_numerator, value_denominator=1):
        self._coeff_matrix[row][col] = Fraction(value_numerator, value_denominator)

    def __setitem__(self, index, data):
        self._coeff_matrix[index] = data

    def __getitem__(self, index):
        return self._coeff_matrix[index]

    def __len__(self):
        return len(self._coeff_matrix)
