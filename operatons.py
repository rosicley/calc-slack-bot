def do_operation(channel: dict):
    res = ""
    op = channel["op"]
    n1 = channel["n1"]
    n2 = channel["n2"]
    if op == "add":
        res = n1 + n2
    elif op == "sub":
        res = n1 - n2
    elif op == "mul":
        res = n1 * n2
    elif op == "div":
        try:
            res = n1 / n2
        except ZeroDivisionError:
            res = "NaN"

    return str(res)


def get_op_text(op):
    if op == "add":
        return "Addition"
    elif op == "sub":
        return "Subtraction"
    elif op == "mul":
        return "Multiplication"
    elif op == "div":
        return "Division"
