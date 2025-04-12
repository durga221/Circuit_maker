"""
Helper functions for executing Python code securely using the interpreter.
"""

import os
import subprocess
import tempfile

def run_python_code(code: str, timeout: int = 10) -> str:
    """
    Run the provided Python code in an isolated environment using a temporary file,
    capture stdout, stderr, and the exit code, and return a formatted result.

    Args:
        code (str): The Python code to execute.
        timeout (int, optional): Maximum allowed time for code execution (in seconds).

    Returns:
        str: Combined output containing the input code, stdout, stderr, and exit status.
    """
    temp_file_name = None
    try:
        # Write code to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file.flush()
            temp_file_name = temp_file.name

        # Execute the temporary Python file using a subprocess
        result = subprocess.run(
            ["python", temp_file_name],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout.strip()
        errors = result.stderr.strip()
        exit_code = result.returncode

        formatted_result = (
            f"--- Input Code ---\n{code}\n\n"
            f"--- Execution Output ---\n{output}\n\n"
            f"--- Errors ---\n{errors}\n\n"
            f"--- Exit Code ---\n{exit_code}"
        )
    except subprocess.TimeoutExpired:
        formatted_result = "Error: Code execution timed out."
    except Exception as e:
        formatted_result = f"Error during code execution: {e}"
    finally:
        # Clean up the temporary file if it was created
        if temp_file_name and os.path.exists(temp_file_name):
            try:
                os.remove(temp_file_name)
            except Exception as cleanup_error:
                formatted_result += f"\nWarning: Could not remove temporary file: {cleanup_error}"

    return formatted_result
