def sum_rows(row1: list, row2: list):
    """
    Summarizes two rows of the current simplex table. The lines are set in the parameters
    :param row1: the first line is the summand
    :param row2: the second line is the summand
    :return: sum_rows (list): result summarizes
    """
    row_sum = [0 for i in range(len(row1))]
    for i in range(len(row1)):
        row_sum[i] = row1[i] + row2[i]
    return row_sum


def multiply_const_row(const: float, row: list):
    """
    Multiplies the row by a constant.
    The constant and index of the multiplied string are specified in the parameters
    :param const: the constant by which the string is multiplied
    :param row: row to be multiplied by a constant
    :return: mul_row (list): the result of multiplying a string by a constant
    """
    mul_row = []
    for i in row:
        mul_row.append(const*i)
    return mul_row

