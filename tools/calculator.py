def calculator(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Example:
        calculator("125 * 87")
    """

    try:
        # Basic calculator for our first prototype.
        allowed = "0123456789+-*/().% "

        if not all(char in allowed for char in expression):
            return "Error: expression contains unsupported characters."

        result = eval(expression, {"__builtins__": {}}, {})

        return str(result)

    except Exception as e:
        return f"Calculator error: {e}"
