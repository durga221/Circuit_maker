
"""
Interpreter Agent for executing Python code using Autogen.
This agent receives a block of Python code, calls the task function to execute it,
and returns the execution results.
"""

"""
Task functions for executing Python code via the interpreter.
"""

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



import autogen


class InterpreterAgent(autogen.AssistantAgent):
    """
    Agent responsible for executing Python code securely.
    """
    def __init__(self, name="interpreter_agent"):
        super().__init__(name=name)
    
    def execute_code(self, code: str) -> str:
        """
        Execute the provided Python code.

        Args:
            code (str): The Python code to execute.

        Returns:
            str: Combined output including stdout, stderr, and exit status.
        """
        return run_code(code)


### pyspice_agent.py
from crewai import Agent, Task
import os
import litellm




class GeminiLLM:
    def __init__(self, model_name="google/gemini-2.0-flash-lite"):
        self.model_name = model_name
    
    def generate(self, messages):
        response = litellm.completion(
            model=self.model_name,
            messages=messages
        )
        return response.choices[0].message.content
        
    def chat(self, messages):
        return self.generate(messages)

# Initialize the custom LLM for CrewAI
llm = GeminiLLM()

# Initialize the Autogen Interpreter Agent
interpreter_agent = InterpreterAgent()

# Execution Agent to run PySpice code
pyspice_simulation_expert = Agent(
    role="PySpice Code Execution Agent",
    goal="Execute PySpice circuit simulation code and return accurate simulation results, including plots and numerical outputs. and also to sent the netlist code to the next agent..",
    backstory="You're an expert Python execution engine with deep understanding of electrical circuit simulations using PySpice. Your task is to take a generated PySpice script, execute it flawlessly, and return clear simulation outputs, including numerical values and graphical results.",
    allow_delegation=False,
    verbose=True,
    llm=llm,
    coding_tools=[interpreter_agent]  # Add Autogen interpreter as a coding tool
)

# Define the execution task
pyspice_simulation_task = Task(
    description=(
        "1. Receive the fully functional PySpice Python script and netlist code  from the Netlist-to-PySpice Generator.\n"
        "2. Execute the PysPice script in a controlled Python environment using the Autogen Interpreter Agent. and jsut pass the netlist code to next agent \n"
        "3. Capture the simulation results, including:\n"
        "   - Numerical outputs such as node voltages and currents.\n"
        "   - Graphs such as transient response, AC frequency response, or Bode plots.\n"
        "4.and finllay pass the netlist code to the next agent.. [very important step]"
    ),
    expected_output="Successful execution of the PySpice script, producing valid simulation results, including numerical values and plotted graphs. and also finally pass the netlist code to the next agent.. note: netlist code that you got as input must be passed to the next agent..",
    agent=pyspice_simulation_expert
)
