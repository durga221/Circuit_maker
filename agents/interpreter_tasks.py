"""
Task functions for executing Python code via the interpreter.
"""

from interpreter_tools import run_python_code

def run_code(code: str) -> str:
    """
    Execute the given Python code and return the output.

    Args:
        code (str): The Python code to execute.

    Returns:
        str: The formatted execution output.
    """
    execution_result = run_python_code(code)
    return execution_result
