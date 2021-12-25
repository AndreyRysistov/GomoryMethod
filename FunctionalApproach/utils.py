from fractions import Fraction


def construct_simplex_table(constraints, num_vars):
    """
    Builds an initial simplex table from the specified constraints and the objective function.
    :param constraints:
    :param num_vars:
    :return:
    """
    num_s_vars = 0  # number of slack and surplus variables
    num_r_vars = 0  # number of additional variables to balance equality and less than equal to
    for expression in constraints:
        if '>=' in expression:
            num_s_vars += 1
        elif '<=' in expression:
            num_s_vars += 1
            num_r_vars += 1
        elif '=' in expression:
            num_r_vars += 1
    total_vars = num_vars + num_s_vars + num_r_vars

    coeff_matrix = [[Fraction("0/1") for _ in range(total_vars + 1)] for _ in range(len(constraints) + 1)]
    s_index = num_vars
    r_index = num_vars + num_s_vars
    r_rows = []  # stores the non -zero index of r
    for i in range(1, len(constraints) + 1):
        constraint = constraints[i - 1].split(' ')

        for j in range(len(constraint)):

            if '_' in constraint[j]:
                coeff, index = constraint[j].split('_')
                if constraint[j - 1] == '-':
                    coeff_matrix[i][int(index) - 1] = Fraction("-" + coeff[:-1] + "/1")
                else:
                    coeff_matrix[i][int(index) - 1] = Fraction(coeff[:-1] + "/1")

            elif constraint[j] == '<=':
                coeff_matrix[i][s_index] = Fraction("1/1")  # add surplus variable
                s_index += 1

            elif constraint[j] == '>=':
                coeff_matrix[i][s_index] = Fraction("-1/1")  # slack variable
                coeff_matrix[i][r_index] = Fraction("1/1")  # r variable
                s_index += 1
                r_index += 1
                r_rows.append(i)

            elif constraint[j] == '=':
                coeff_matrix[i][r_index] = Fraction("1/1")  # r variable
                r_index += 1
                r_rows.append(i)

            coeff_matrix[i][-1] = Fraction(constraint[-1] + "/1")
    return coeff_matrix, r_rows, num_s_vars, num_r_vars


def update_objective_function(simplex_table, objective_function, objective):
    objective_function_coeffs = objective_function.split()
    for i in range(len(objective_function_coeffs)):
        if '_' in objective_function_coeffs[i]:
            coeff, index = objective_function_coeffs[i].split('_')
            if objective_function_coeffs[i-1] == '-':
                simplex_table[0][int(index)-1] = Fraction(int(coeff[:-1]), 1)
            else:
                simplex_table[0][int(index)-1] = Fraction(-int(coeff[:-1]), 1)
            if 'max' in objective:
                simplex_table[0][int(index)-1] *= -1
    return simplex_table


def create_solution(simplex_table, basic_vars, num_vars):
    solution = {}
    for i, var in enumerate(basic_vars[1:]):
        if var < num_vars:
            solution['x_' + str(var + 1)] = simplex_table[i + 1][-1]
    for i in range(0, num_vars):
        if i not in basic_vars[1:]:
            solution['x_' + str(i + 1)] = 0
    return solution

def get_fraction(numerator, denominator):
    return Fraction(numerator, denominator)