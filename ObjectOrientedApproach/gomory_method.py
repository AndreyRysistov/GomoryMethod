from simplex_method import SimplexMethod
import copy


class GomoryMethod(SimplexMethod):

    def __init__(self, num_vars: int, constraints: list, objective_function: tuple):
        """
        The method calls the constructor of the SimplexMethod parent class and initializes the parameters of the simplex algorithm.
        In the method, the solution of the simplex method is formed for the given constraints and the objective function.
        :param num_vars: number of variables
        :param constraints: list of constraints
         (for example ['1x_1 + 2x_2 >= 4', '2x_3 + 3x_1 <= 5', 'x_3 + 3x_2 = 6'])
        :param objective_function: tuple in which two string values are specified: objective function
         (for example, '2x_1 + 4x_3 + 5x_2') optimization direction ('min' or 'max')
        """
        super().__init__(num_vars, constraints, objective_function)
        self.clipping_history = []
        self.simplex_vals, self.simplex_solution = self.solve()

    def integer_solve(self):
        """
        The method is designed to solve the problem of integer linear programming by given constraints and an objective function.
        Initially, the condition of the integer value of the solution obtained by the simplex method is checked,
        if the solution is integer– it is output in response.
        At each iteration of the loop, the condition of integer optimality of the objective function is checked.
        If this condition is met, the task is considered solved and iterations are stopped, the resulting integer optimal value of the function and the integer optimal plan are returned.
        Otherwise, one step of the algorithm of the cutting-off plane method (Gomory method) is performed:
        - forming a clipping and adding it to the current simplex table
        - performing one step of the simplex method
        :return:
        integer_optimum (float): the optimal integer value of the objective function obtained by the Gomory method
        integer_optimal_plane (list): the optimal integer plan obtained by the Gomory method
        """
        if self._check_integer_condition():
            return self.simplex_table[0][-1], self.simplex_solution
        self.simplex_history[f'Initial Gomory-method'] = copy.deepcopy(self.simplex_table.get_table())
        self.basic_vars_history[f'Initial Gomory-method'] = copy.deepcopy(self.basic_vars)
        step = 1
        while not self._check_integer_condition():
            self._add_clipping()
            key_row = self._get_key_row()
            key_column = self._get_key_column(key_row)
            self.simplex_step(key_column, key_row)
            self.simplex_history[f'Gomory method step {step}'] = copy.deepcopy(self.simplex_table.get_table())
            self.basic_vars_history[f'Gomory method step {step}'] = copy.deepcopy(self.basic_vars)
            step += 1
        integer_optimum = self.simplex_table[0][-1]
        integer_optimal_plane = self.get_solution()
        return integer_optimum, integer_optimal_plane

    def _check_integer_condition(self):
        """
        The method checks the condition of integer optimality of the objective function
        (all values in the row of the objective function of the current simplex table are negative or equal to 0 and are integer)
        :return: condition (bool): True or False, depending on the fulfillment of the integer optimality condition
        """
        B = [x[-1] for x in self.simplex_table[1:]]
        integer_values = list(filter(lambda x: x.denominator == 1, B))
        positive_values = list(filter(lambda x: x >= 0, B))
        condition1 = len(positive_values) == len(B)
        condition2 = len(integer_values) == len(B)
        condition = condition1 and condition2
        return condition

    def _find_max_fractional_index(self):
        """
        The method searches for the index of the row of the current simplex table in which the
        maximum value of the fractional part of the element is located
        :return: max_fractional_index (int): index of the row containing the element with the maximum fractional part
        """
        max_fractional_part_i = 1
        for i in range(1, len(self.simplex_table)):
            curr_fractional_part = abs(float(self.simplex_table[i][-1])) % 1
            max_fractional_part = abs(float(self.simplex_table[max_fractional_part_i][-1])) % 1
            if curr_fractional_part > max_fractional_part:
                max_fractional_part_i = i
        return max_fractional_part_i

    def _add_clipping(self):
        """
        The method forms a new clipping of the Gomori method:
        - searching for a string containing an element with the maximum fractional part,
        - compiling the Gomori clipping inequality based on the found string,
        - reducing the resulting inequality into equality by adding a new variable,
        - introducing a new variable into the basis and adding the clipping to the current simplex table
        :return: None
        """
        index = self._find_max_fractional_index()
        self.simplex_table.add_zero_row()
        for i in range(len(self.simplex_table)):
            if i == len(self.simplex_table)-1:
                self.simplex_table[i].insert(-1, 1)
            else:
                self.simplex_table[i].insert(-1, 0)
        clipping_coeffs = []
        for j, coeff in enumerate(self.simplex_table[index]):
            if coeff != 0:
                self.simplex_table.set_item(-1, j, -(coeff.numerator % coeff.denominator), coeff.denominator)
                clipping_coeffs.append(self.simplex_table[-1][j])
        self.clipping_history.append(clipping_coeffs[1:])
        self.basic_vars.append(len(self.simplex_table) - 1)

    def _get_key_row(self):
        beta = [x[-1] if x[-1] < 0 else 0 for x in self.simplex_table[1:]]
        key_row = 0
        for b in range(len(beta)):
            if abs(beta[b]) >= abs(beta[key_row]):
                key_row = b
        return key_row + 1

    def _get_key_column(self, key_row):
        tetha = [x / y if y < 0 else float('inf') for x, y in
                 zip(self.simplex_table[0][:-2], self.simplex_table[key_row][:-2])]
        key_column = 0
        for t in range(len(tetha)):
            if tetha[t] <= tetha[key_column]:
                key_column = t
        return key_column













