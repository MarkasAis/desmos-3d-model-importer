default_functions = ["sin", "cos", "tan"]

table_variables = []
custom_variables = []
custom_functions = []


def reverse_insort(a, x, lo=0, hi=None):
    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if x > a[mid]:
            hi = mid
        else:
            lo = mid + 1
    a.insert(lo, x)


def find_closing_brace(equation, start):
    opening_symbol = equation[start]
    if opening_symbol == "(":
        closing_symbol = ")"
    elif opening_symbol == "[":
        closing_symbol = "]"
    else:
        return None

    bracket_balance = 0
    for i in range(len(equation)):
        if equation[i] == opening_symbol:
            bracket_balance += 1
        elif equation[i] == closing_symbol:
            bracket_balance -= 1
            if bracket_balance == 0:
                return i

    return None


def is_enclosed(equation):
    return find_closing_brace(equation, 0) == len(equation)-1


def remove_outer_brackets(equation):        #TODO: remove all outer braces
    if is_enclosed(equation):
        return equation[1:-1]

    return equation


def split_by(equation, delimiters):
    terms = []

    bracket_balance = 0
    last = 0
    for i in range(len(equation)):
        if equation[i] == "(":
            bracket_balance += 1
        elif equation[i] == ")":
            bracket_balance -= 1
        elif bracket_balance == 0:
            for d in delimiters:
                if equation[i] == d:
                    terms.append(equation[last:i])
                    terms.append(equation[i])
                    last = i + 1
                    break

    terms.append(equation[last:])
    return terms


def split_terms(equation):
    return split_by(equation, ["+", "-"])


def split_products(term):
    return split_by(term, ["*", "/"])


def split_exp(exp):
    return split_by(exp, ["^"])


def compile_name(name):
    if len(name) > 1:
        return name[0] + "_{" + name[1:] + "}"

    return name


def compile_multiplication(left, right_data):
    left += "\\cdot"
    if right_data[1]:
        right_data[0] = "(" + right_data[0] + ")"
    left += right_data[0]
    return left


def compile_division(left, right_data):
    left = "\\frac{" + left + "}{" + right_data[0] + "}"
    return left


def compile_power(left, right_data):
    left += "^"
    if right_data[1]:
        right_data[0] = "{\\left(" + right_data[0] + "\\right)}"
    left += "{" + right_data[0] + "}"
    return left


def check_for_name(term, start, name):
    for i in range(len(name)):
        if term[start-i] != name[-(i+1)]:
            return False

    return True


def compile_sqrt(term, start):
    if check_for_name(term, start-1, "sqrt"):
        end_brace = find_closing_brace(term, start)
        compiled = term[:start-4] + "\\sqrt{" + compile_equation_util(term[start+1:end_brace])[0] + "}"

        if end_brace < len(term)-1:
            compiled += compile_equation_util(term[end_brace+1:])[0]

        return [compiled, True]

    return [term, False]


def compile_function(term, start, name, is_default):
    if check_for_name(term, start-1, name):
        end_brace = find_closing_brace(term, start)

        compiled = term[:start - len(name)]
        if is_default:
            compiled += "\\" + name
        else:
            compiled += compile_name(name)

        compiled += "\\left(" + compile_equation_util(term[start+1:end_brace])[0] + "\\right)"

        if end_brace < len(term)-1:
            compiled += compile_equation_util(term[end_brace+1:])[0]

        return [compiled, True]

    return [term, False]


def compile_functions(term):
    start = None

    for i in range(len(term)):
        if term[i] == "(":                          # TODO: also check for [ when adding parameters to functions
            start = i
            break

    if start is None:
        return term

    term_data = compile_sqrt(term, start)
    for f in default_functions:
        if term_data[1]:
            return term_data[0]
        term_data = compile_function(term_data[0], start, f, True)

    for f in custom_functions:
        if term_data[1]:
            return term_data[0]
        term_data = compile_function(term_data[0], start, f, False)

    return term_data[0]


def compile_table_variable(term, start, name):
    if check_for_name(term, start-1, name):
        end_brace = find_closing_brace(term, start)

        compiled = term[:start - len(name)] + compile_name(name) + "\\left[" + \
                   compile_equation_util(term[start+1:end_brace])[0] + "\\right]"

        if end_brace < len(term)-1:
            compiled += compile_equation_util(term[end_brace+1:])[0]

        return [compiled, True]

    return [term, False]


def compile_table_variables(term):
    start = None

    for i in range(len(term)):
        if term[i] == "[":
            start = i
            break

    if start is None:
        return term
                                    #TODO: if is_variable_viable(term, name, start-len(name)):
    term_data = [term, False]
    for v in table_variables:
        term_data = compile_table_variable(term_data[0], start, v)
        if term_data[1]:
            return term_data[0]

    return term_data[0]


def is_variable_viable(term, start):
    if start != -1:
        for i in range(start-1, 0, -1):
            if term[i] == "{" and term[i-1] == "_":
                return term

            if term[i] == "(":
                break

        return True

    return False


def compile_custom_variable(term, name):
    start = term.find(name)

    if is_variable_viable(term, start):
        return term[:start] + compile_name(name) + term[start + len(name):]

    return term


def compile_custom_variables(term):
    for v in custom_variables:
        term = compile_custom_variable(term, v)

    return term


def compile_exp(exp):
    compiled_data = ["", False]

    exps = split_exp(exp)

    if len(exps) == 1:
        return [exp, False]

    for i in range(len(exps)-1, -1, -2):
        e_data = compile_equation_util(exps[i])

        if i == len(exps)-1:
            compiled_data[0] = e_data[0]
            compiled_data[1] = e_data[1]
        else:
            if i == 0 and (e_data[1] or e_data[2]):
                e_data[0] = "(" + e_data[0] + ")"

            compiled_data[0] = compile_power(e_data[0], compiled_data)
            compiled_data[1] = False

    return [compiled_data[0], True]


def compile_term(term):
    compiled = ""

    products = split_products(term)
    if len(products) == 1:
        e_data = compile_exp(term)
        if e_data[1]:
            return [e_data[0], False]
        compiled = compile_functions(e_data[0])
        compiled = compile_table_variables(compiled)
        compiled = compile_custom_variables(compiled)
        return [compiled, False]

    for i in range(0, len(products), 2):
        p_data = compile_equation_util(products[i])

        if i == 0:
            compiled = p_data[0]
        else:
            symbol = products[i-1]
            if symbol == "*":
                compiled = compile_multiplication(compiled, p_data)
            if symbol == "/":
                compiled = compile_division(compiled, p_data)

    return [compiled, True]


def compile_equation_util(equation):
    compiled = ""

    equation = remove_outer_brackets(equation)
    terms = split_terms(equation)
    multiple_products = False
    for i in range(0, len(terms), 2):
        t_data = compile_term(terms[i])
        if t_data[1]:
            multiple_products = True

        if i > 0:
            compiled += terms[i-1]

        compiled += t_data[0]

    return [compiled, len(terms) > 1, multiple_products]


def compile_equation(equation):
    equation = str(equation)

    equal = -1
    for i in range(len(equation)):
        if equation[i] == "=":
            equal = i
            break

    if equal == -1:
        return compile_equation_util(equation)[0]

    return compile_equation_util(equation[:equal])[0] + "=" + compile_equation_util(equation[equal+1:])[0]


def define_table_variable(name):
    reverse_insort(table_variables, name)


def define_custom_variable(name):
    reverse_insort(custom_variables, name)


def define_custom_function(name):
    reverse_insort(custom_functions, name)
