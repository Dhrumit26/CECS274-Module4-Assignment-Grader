import random
import re

import expr_generator as expr_gen


def generate_input():
    # INPUT FOR CALCULATOR OPTION 1 & 2:
    # STORE VAR/VAL & DISPLAY
    map = {}
    n = random.randint(2, 3)
    while len(map) < n:
        var = chr(random.randint(97, 122))
        if var not in map:
            map[var] = round(random.randint(-10, 10) + random.random(), 2)
    f = open("calc_in_1.txt", 'w')
    f.write("1\n1\n")
    variables = list(map.keys())
    for var in variables:
        f.write(f"{var}\n{map[var]}\n")
        del map[var]
        if len(map) > 0:
            f.write("Y\n")
        else:
            f.write("N\n")
    f.write("2\nQ\nQ")
    f.close()

    # INPUT FOR CALCULATOR OPTION 1 & 2:
    # REPLACING AN EXISTING VALUE
    map = {}
    n = random.randint(2, 3)
    while len(map) < n:
        var = chr(random.randint(97, 122))
        if var not in map:
            map[var] = random.randint(-10, 10) + round(random.random(), 2)
    f = open("calc_in_2.txt", 'w')
    f.write("1\n1\n")
    variables = list(map.keys())
    for var in variables:
        f.write(f"{var}\n{map[var]}\n")
        del map[var]
        if len(map) > 0:
            f.write("Y\n")
        else:
            f.write("N\n")

    f.write("2\n1\n")
    var = variables[random.randint(0, len(variables) - 1)]
    val = random.randint(20, 30)
    f.write(f"{var}\n{val}\nY\nN\n2\nQ\nQ")
    f.close()

    # INPUT FOR CALCULATOR OPTION 3: PRINT EXPRESSION
    expression = expr_gen.build_math_expr(2, False)
    variables = [x for x in re.split(r'\W+', expression) if x.isalnum()]
    map = {}
    n = random.randint(2, 3)
    while len(map) < n:
        var = variables[random.randint(0, len(variables) - 1)]
        if var not in map:
            map[var] = round(random.randint(-10, 10) + random.random(), 2)
    f = open("calc_in_3.txt", 'w')
    f.write("1\n1\n")
    vars = list(map.keys())
    for var in vars:
        f.write(f"{var}\n{map[var]}\n")
        del map[var]
        if len(map) > 0:
            f.write("Y\n")
        else:
            f.write("N\n")
    f.write(f"2\n3\n{expression}\nQ\nQ")
    f.close()

    # INPUT FOR BOOKSTORE SEARCH BY KEY
    i = random.randint(1, 15)
    catalog = f"books_{i}.txt"

    f = open(catalog, encoding="utf8")
    lines = f.readlines()
    num_books = len(lines)
    key = lines[random.randint(0, num_books - 1)].split("^")[0]
    f.close()

    file1 = open("store_input.txt", 'w')
    file1.write(f"2\n1\n{catalog}\n2\n4\n3\n{key}\nq\nq\nq")
    file1.close()


generate_input()