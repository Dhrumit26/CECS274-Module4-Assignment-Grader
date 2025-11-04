import random

def build_math_expr(n: int, single_char=True, extra=""):
    if single_char:
        variables = [chr(i) for i in range(65, 91)]
    else:
        greeks = ['alpha', 'beta', 'omega', 'tau', 'epsilon', 'lambda', 'eta', 'pi']
        variables = [x + str(i) for x in greeks for i in range(0, 21)]

    expression = generate_balanced_expr(n, variables)

    if extra == '':  # generate balanced expression
        return expression
    elif extra == ')':  # generate expression with extra )
        indices = [i for i, ltr in enumerate(expression) if ltr == ')']  # indices of all ) in the balanced expression
        idx = random.randint(0, len(indices) - 1)  # index of randomly chosen existing )
        expression = expression[:idx] + ')' + expression[idx:]  # inserting extra )
        return expression
    elif extra == '(':
        indices = [i for i, ltr in enumerate(expression) if ltr == '(']  # indices of all ( in the balanced expression
        idx = random.randint(0, len(indices) - 1)  # index of randomly chosen existing (
        expression = expression[:idx] + '(' + expression[idx:]  # inserting extra (
        return expression
    else:
        raise ValueError(f"Incorrect value given. Parameter 'extra' expects character ')' or '(' only.")


def generate_balanced_expr(n: int, var_pool):
    op = ['+', '-', '*', '/']
    if n == 0:
        return
    elif n == 1:
        k = len(var_pool) - 1
        left = var_pool[random.randint(0, k)]
        right = var_pool[random.randint(0, k)]
        operator = op[random.randint(0, len(op) - 1)]
        return f"({left}{operator}{right})"
    else:
        r = random.randint(1, 2)
        if r == 1:
            return f"({generate_balanced_expr(n - 1, var_pool)}{op[random.randint(0, len(op) - 1)]}{generate_balanced_expr(1, var_pool)})"
        else:
            return f"({generate_balanced_expr(1, var_pool)}{op[random.randint(0, len(op) - 1)]}{generate_balanced_expr(n - 1, var_pool)})"
