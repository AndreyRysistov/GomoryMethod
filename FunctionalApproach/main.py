from FunctionalApproach.gomory_module import *
from table_printing import print_history_table


if __name__ == '__main__':
    objective_function = ('maximize', '8x_1 + 6x_2')
    constraints = ['2x_1 + 5x_2 <= 19', '4x_1 + 1x_2 <= 16']
    num_vars = 2
    gomory_vals, gomory_solution, gomory_history, basic_vars_history = gomory_solve(
        num_vars,
        constraints,
        objective_function
    )
    print('Gomory method steps:')
    print_history_table(gomory_history, basic_vars_history, gomory_solution)
