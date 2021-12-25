from warnings import warn
import copy
from FunctionalApproach.table_tools import sum_rows, multiply_const_row
from FunctionalApproach.utils import construct_simplex_table, update_objective_function, create_solution


def simplex_solve(num_vars: int, constraints: list, objective_function: tuple):
    """
    Solve the problem of linear programming by the simplex method.
    In the method body of each iteration of the loop, the optimality condition of the objective function is
    checked under the specified constraints, if this condition is true, the problem is considered solved and the
    iterations stop, otherwise one step of the simplex method is performed

    :param num_vars: number of variables
    :param constraints: list of constraints
        (for example ['1x_1 + 2x_2 >= 4', '2x_3 + 3x_1 <= 5', 'x_3 + 3x_2 = 6'])
    :param objective_function: tuple in which two string values are specified: objective function
        (for example, '2x_1 + 4x_3 + 5x_2') optimization direction ('min' or 'max')
    :return:
    optimum (float) – the optimal value of the objective function obtained by the simplex method
    optimal_plane (dict) - optimal plan obtained by simplex method (solution of linear programming problem)
    simplex_history (list): list containing the steps of simplex table conversion
    basic_vars_history (list): list containing the steps of basic_vars conversion
    """
    simplex_table, r_rows, num_s_vars, num_r_vars = construct_simplex_table(constraints, num_vars)
    objective, objective_function = objective_function[0], objective_function[1]
    basic_vars = [0 for _ in range(len(simplex_table))]
    simplex_table, basic_vars, simplex_history = phase1(simplex_table, basic_vars, r_rows, num_vars, num_s_vars)
    r_index = num_r_vars + num_s_vars
    for i in basic_vars:
        if i > r_index:
            raise ValueError("Infeasible solution")
    simplex_table = delete_r_vars(simplex_table, num_vars, num_s_vars)
    simplex_table = update_objective_function(simplex_table, objective_function, objective)

    simplex_history = {}
    basic_vars_history = {}
    for row, column in enumerate(basic_vars[1:]):
        if simplex_table[0][column] != 0:
            const = -simplex_table[0][column]
            result = multiply_const_row(const, simplex_table[row])
            simplex_table[0] = sum_rows(simplex_table[0], result)
    simplex_history['Initial Simplex-method'] = copy.deepcopy(simplex_table)
    basic_vars_history['Initial Simplex-method'] = copy.deepcopy(basic_vars)
    step = 1
    while not check_condition(simplex_table):
        key_column = find_key_column(simplex_table)
        key_row = find_key_row(simplex_table, key_column)
        simplex_table, basic_vars = simplex_step(simplex_table, basic_vars, key_column, key_row)
        simplex_history[f'Simplex-method step {step}'] = copy.deepcopy(simplex_table)
        basic_vars_history[f'Simplex-method step {step}'] = copy.deepcopy(basic_vars)
        step += 1
    optimum = simplex_table[0][-1]
    optimal_plane = create_solution(simplex_table, basic_vars, num_vars)
    return optimum, optimal_plane, simplex_history, basic_vars_history


def check_condition(simplex_table: list):
    """
    Checks the optimality condition of the objective function for the current simplex table
     (all values in the row of the objective function are negative or equal to zero)
    :param simplex_table: current simplex table
    :return: condition (bool): True if the optimality condition is met, False otherwise
    """
    F = simplex_table[0]
    negative_values = list(filter(lambda x: x <= 0, F))
    condition = len(negative_values) == len(F)
    return condition


def find_key_column(simplex_table: list):
    """
    Find the resolving column in the current simplex table
    :param simplex_table: current simplex table
    :return: key_column (int):  index of the resolving column
    """
    key_columns = 0
    for i in range(0, len(simplex_table[0]) - 1):
        if abs(simplex_table[0][i]) >= abs(simplex_table[0][key_columns]):
            key_columns = i

    return key_columns


def find_key_row(simplex_table: list, key_column: int):
    """
    Search for a permissive row in the permissive column of the current simplex table.
    :param simplex_table: current simplex table
    :param key_column: index of the resolving column
    :return: key_row (int): index of the resolving row
    """
    min_val = float("inf")
    key_row = 0
    for i in range(1, len(simplex_table)):
        if simplex_table[i][key_column] > 0:
            val = simplex_table[i][-1] / simplex_table[i][key_column]
            if val < min_val:
                min_val = val
                key_row = i
    if min_val == float("inf"):
        raise ValueError("Unbounded solution")
    if min_val == 0:
        warn("Dengeneracy")
    return key_row


def simplex_step(simplex_table: list, basic_vars: list, key_column: int, key_row: int):
    """
    Performs one step of the simplex algorithm:
        - input of new basic variables and output of old variables from the basis,
        - search for a permissive element,
        - normalization of the permissive row to the permissive element,
        - zeroing of the permissive column.
    :param simplex_table: current simplex table
    :param basic_vars: current basic variables
    :param key_column: index of the permissive column
    :param key_row: index of the permissive row
    :return:
    simplex_table (list): new simplex table
    basic_vars (list): new basic variables
    """
    basic_vars[key_row] = key_column
    pivot = simplex_table[key_row][key_column]
    simplex_table = normalize_to_pivot(simplex_table, key_row, pivot)
    simplex_table = make_key_column_zero(simplex_table, key_column, key_row)
    return simplex_table, basic_vars


def normalize_to_pivot(simplex_table: list, key_row: int, pivot: int):
    """
    Divides the resolving row of the current simplex table by the resolving element
    :param simplex_table: current simplex table
    :param key_row: index of the permissive row
    :param pivot: resolving element
    :return:
    """
    for i in range(len(simplex_table[0])):
        simplex_table[key_row][i] /= pivot
    return simplex_table


def make_key_column_zero(simplex_table: list, key_column: int, key_row: int):
    """
    Zeroes the elements of the resolving column of the current simplex table
    with the exception of the element standing in the resolving row by the Jordano-Gauss method
    :param simplex_table: current simplex table
    :param key_column: index of the permissive column
    :param key_row: index of the permissive row
    :return:
    simplex_table (list): new simplex table
    """
    num_columns = len(simplex_table[0])
    for i in range(len(simplex_table)):
        if i != key_row:
            factor = simplex_table[i][key_column]
            for j in range(num_columns):
                simplex_table[i][j] -= simplex_table[key_row][j] * factor
    return simplex_table


def delete_r_vars(simplex_table: list, num_vars: int, num_s_vars: int):
    for i in range(len(simplex_table)):
        non_r_length = num_vars + num_s_vars + 1
        length = len(simplex_table[i])
        while length != non_r_length:
            del simplex_table[i][non_r_length-1]
            length -= 1
    return simplex_table


def phase1(simplex_table: list, basic_vars: list, r_rows: list, num_vars: int, num_s_vars: int):
    # Objective function here is minimize r1+ r2 + r3 + ... + rn
    simplex_history = []
    r_index = num_vars + num_s_vars
    for i in range(r_index, len(simplex_table[0]) - 1):
        simplex_table[0][i] = -1
    for i in r_rows:
        simplex_table[0] = sum_rows(simplex_table[0], simplex_table[i])
        basic_vars[i] = r_index
        r_index += 1
    s_index = num_vars
    for i in range(1, len(basic_vars)):
        if basic_vars[i] == 0:
            basic_vars[i] = s_index
            s_index += 1
    while not check_condition(simplex_table):
        key_column = find_key_column()
        key_row = find_key_row(key_column=key_column)
        simplex_table, basic_vars = simplex_step(key_column, key_row)
        simplex_history.append(copy.deepcopy(simplex_table))
    return simplex_table, basic_vars, simplex_history