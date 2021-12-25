from ObjectOrientedApproach.gomory_method import GomoryMethod
import pandas as pd


if __name__ == '__main__':
    objective_function = ('maximize', '8x_1 + 6x_2')
    constraints = ['2x_1 + 5x_2 <= 19', '4x_1 + 1x_2 <= 16']
    gomory = GomoryMethod(num_vars=2, constraints=constraints, objective_function=objective_function)
    gomory.integer_solve()
    history = gomory.simplex_history
    basic_vars_history = gomory.basic_vars_history

    print('Gomory method steps:')
    for step, table in history.items():
        print(step)
        simplex_table = pd.DataFrame(
            table,
            columns=[f'x{i+1}' if i < len(table[0])-1 else 'b' for i in range(len(table[0]))],
            index=[f'x{basic_vars_history[step][i]+1}' if i != 0 else 'f(x)' for i in range(len(basic_vars_history[step]))]
        )
        print(simplex_table)
        print()
    print('Optimal point:')
    for var, value in gomory.get_solution().items():
        print(var, value)

