import pandas as pd


def print_history_table(table_history, basic_vars_history, solution):
    """
    Printing history of method
    :param table_history: history of changing simplex table
    :param basic_vars_history: list containing the steps of simplex table conversion
    :param solution: list containing the steps of basic_vars conversion
    :return: None
    """
    for step, table in table_history.items():
        print(step)
        simplex_table = pd.DataFrame(
            table,
            columns=[f'x{i + 1}' if i < len(table[0]) - 1 else 'b' for i in range(len(table[0]))],
            index=[f'x{basic_vars_history[step][i] + 1}' if i != 0 else 'f(x)' for i in
                   range(len(basic_vars_history[step]))]
        )
        print(simplex_table)
        print()
    print('Optimal point:')
    for var, value in solution.items():
        print(var, value)