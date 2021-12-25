import copy
from FunctionalApproach.simplex_module import simplex_step, simplex_solve
from FunctionalApproach.utils import get_fraction, create_solution


def gomory_solve(num_vars: int, constraints: list, objective_function: tuple):
    """
    Solve the problem of integer linear programming by given constraints and an objective function.
    Initially, the condition of the integer value of the solution obtained by the simplex method is checked,
    if the solution is integer– it is output in response.
    At each iteration of the loop, the condition of integer optimality of the objective function is checked.
    If this condition is met, the task is considered solved and iterations are stopped, the resulting integer optimal value of the function and the integer optimal plan are returned.
    Otherwise, one step of the algorithm of the cutting-off plane method (Gomori method) is performed:
    - forming a clipping and adding it to the current simplex table
    - performing one step of the simplex method
    :param num_vars: number of variables
    :param constraints: list of constraints
         (for example ['1x_1 + 2x_2 >= 4', '2x_3 + 3x_1 <= 5', 'x_3 + 3x_2 = 6'])
    :param objective_function: tuple in which two string values are specified: objective function
         (for example, '2x_1 + 4x_3 + 5x_2') optimization direction ('min' or 'max')
    :return:
    integer_optimum (float): the optimal integer value of the objective function obtained by the Gomori method
    integer_optimal_plane (list): the optimal integer plan obtained by the Gomori method
    gomory_history (list): a list containing the steps of simplex table conversion
    basic_vars_history (list): a list containing the steps of basic_vars conversion
    """
    simplex_vals, simplex_solution, simplex_history, simplex_basic_vars_history = simplex_solve(
        num_vars,
        constraints,
        objective_function
    )
    simplex_table = list(simplex_history.values())[-1]
    basic_vars = list(simplex_basic_vars_history.values())[-1]

    gomory_history = simplex_history
    basic_vars_history = simplex_basic_vars_history
    if check_integer_condition(simplex_table):
        return simplex_table[0][-1], simplex_solution
    gomory_history[f'Initial Gomory-method'] = copy.deepcopy(simplex_table)
    basic_vars_history[f'Initial Gomory-method'] = copy.deepcopy(basic_vars)
    step = 1
    while not check_integer_condition(simplex_table):
        simplex_table, basic_vars = add_clipping(simplex_table, basic_vars)
        key_row = get_key_row(simplex_table)
        key_column = get_key_column(simplex_table, key_row)
        simplex_table, basic_vars = simplex_step(simplex_table, basic_vars, key_column, key_row)
        gomory_history[f'Gomory method step {step}'] = copy.deepcopy(simplex_table)
        basic_vars_history[f'Gomory method step {step}'] = copy.deepcopy(basic_vars)
        step += 1
    integer_optimum = simplex_table[0][-1]
    integer_optimal_plane = create_solution(simplex_table, basic_vars, num_vars)

    return integer_optimum, integer_optimal_plane, gomory_history, basic_vars_history


def check_integer_condition(simplex_table: list):
    """
    Checks the condition of integer optimality of the objective function
    (all values in the row of the objective function of the current simplex table are negative or equal to 0 and are integer)
    :param simplex_table: current simplex table
    :return: condition (bool): True or False, depending on the fulfillment of the integer optimality condition
    """
    B = [x[-1] for x in simplex_table[1:]]
    integer_values = list(filter(lambda x: x.denominator == 1, B))
    positive_values = list(filter(lambda x: x >= 0, B))
    condition1 = len(positive_values) == len(B)
    condition2 = len(integer_values) == len(B)
    condition = condition1 and condition2
    return condition


def find_max_fractional_index(simplex_table: list):
    """
    Searches for the index of the row of the current simplex table in which the
    maximum value of the fractional part of the element is located
    :param simplex_table: current simplex table
    :return: max_fractional_index (int): index of the row containing the element with the maximum fractional part
    """
    max_fractional_part_i = 1
    for i in range(1, len(simplex_table)):
        curr_fractional_part = abs(float(simplex_table[i][-1])) % 1
        max_fractional_part = abs(float(simplex_table[max_fractional_part_i][-1])) % 1
        if curr_fractional_part > max_fractional_part:
            max_fractional_part_i = i
    return max_fractional_part_i


def add_clipping(simplex_table: list, basic_vars: list):
    """
    Forms a new clipping of the Gomori method:
    - searching for a string containing an element with the maximum fractional part,
    - compiling the Gomori clipping inequality based on the found string,
    - reducing the resulting inequality into equality by adding a new variable,
    - introducing a new variable into the basis and adding the clipping to the current simplex table
    :param simplex_table: current simplex table
    :param basic_vars: current basic vars

    :return:
    simplex_table: new simplex table
    basic_vars: new basic variables
    """
    index = find_max_fractional_index(simplex_table)
    simplex_table.append([0 for _ in simplex_table[0]])
    for i in range(len(simplex_table)):
        if i == len(simplex_table) - 1:
            simplex_table[i].insert(-1, 1)
        else:
            simplex_table[i].insert(-1, 0)
    for j, coeff in enumerate(simplex_table[index]):
        if coeff != 0:
            simplex_table[-1][j] = get_fraction(-(coeff.numerator % coeff.denominator), coeff.denominator)
    basic_vars.append(len(simplex_table) - 1)
    return simplex_table, basic_vars


def get_key_row(simplex_table: list):
    beta = [x[-1] if x[-1] < 0 else 0 for x in simplex_table[1:]]
    key_row = 0
    for b in range(len(beta)):
        if abs(beta[b]) >= abs(beta[key_row]):
            key_row = b
    return key_row + 1


def get_key_column(simplex_table: list, key_row: int):
    tetha = [x / y if y < 0 else float('inf') for x, y in
             zip(simplex_table[0][:-2], simplex_table[key_row][:-2])]
    key_column = 0
    for t in range(len(tetha)):
        if tetha[t] <= tetha[key_column]:
            key_column = t
    return key_column






