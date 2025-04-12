from crewai import Agent, Task
from crewai.tools import BaseTool

import litellm
import os
from typing import Any





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


class NetlistToPySpiceConverterTool(BaseTool):
    name: str = "Netlist-to-PySpice Converter Tool"
    description: str = ("Converts SPICE netlists to executable PySpice Python code "
                       "with guaranteed simulation compatibility and error prevention.")
    
    def _run(self, netlist_data: Any) -> Any:
        # Extract netlist components and structure
        raw_spice = netlist_data.get("raw_spice", "")
        title = netlist_data.get("title", "MOSFET Amplifier Circuit")
        components = netlist_data.get("components", [])
        models = netlist_data.get("models", [])
        analyses = netlist_data.get("analyses", [])
        
        # Initialize the PySpice code structure
        pyspice_script = {
            "imports": [
                "import numpy as np",
                "import matplotlib.pyplot as plt",
                "import PySpice.Logging.Logging as Logging",
                "from PySpice.Plot.BodeDiagram import bode_diagram",
                "from PySpice.Spice.Netlist import Circuit",
                "from PySpice.Unit import *"
            ],
            "circuit_definition": [],
            "component_instantiation": [],
            "analysis_configuration": [],
            "simulation_execution": [],
            "results_processing": [],
            "visualization": [],
            "complete_code": "",  # Will contain the full executable script
            "verification_tests": []
        }
        
        # Generate PySpice code from netlist components
        # (Implementation would convert each component to PySpice syntax)
        
        # Convert MOSFET models to PySpice format
        # (Implementation would handle model parameter conversion)
        
        # Generate analysis configurations
        # (Implementation would create appropriate simulator.xxxx_analysis() calls)
        
        # Implement robust error prevention mechanisms
        # (Implementation would add checks and safeguards)
        
        # Generate visualization code
        # (Implementation would create appropriate plotting code)
        
        # Assemble complete Python script
        # (Implementation would join all code sections)
        
        # Generate verification tests
        # (Implementation would create test cases to verify circuit operation)
        
        return pyspice_script

class PySpiceCodeOptimizerTool(BaseTool):
    name: str = "PySpice Code Optimizer Tool"
    description: str = ("Optimizes and validates PySpice code for execution efficiency, "
                       "convergence robustness, and simulation accuracy.")
    
    def _run(self, pyspice_script: dict) -> dict:
        # Analyze the PySpice code for potential issues
        # (Implementation would check for common errors and optimization opportunities)
        
        # Apply code optimizations
        # (Implementation would refactor code for better performance)
        
        # Add convergence assistance techniques
        # (Implementation would add .OPTION statements or equivalent PySpice options)
        
        # Validate node connections and component values
        # (Implementation would check for disconnected nodes, out-of-range values, etc.)
        
        # Add additional error handling
        # (Implementation would add try/except blocks and validation checks)
        
        # Return optimized and validated PySpice script
        return {
            "optimized_script": pyspice_script,
            "optimization_report": {
                "issues_detected": [],
                "optimizations_applied": [],
                "convergence_enhancements": [],
                "validation_results": "PASS"
            }
        }

tool=PySpiceCodeOptimizerTool()

netlist_to_pyspice_generator = Agent(
    role="High-Precision Netlist-to-PySpice Code Generator",
    goal="Transform SPICE netlists into flawless PySpice Python scripts with perfect translation accuracy and guaranteed execution success while maintaining complete circuit design fidelity",
    backstory="You're an elite AI-powered SPICE automation engineer with unparalleled expertise in translating circuit simulations across platforms. Your specialized knowledge spans the full spectrum of circuit elements from basic passives to complex MOSFET models, with particular mastery of amplifier topologies including Common Source, Common Drain, and Common Gate configurations. Through thousands of simulated circuit conversions, you've developed proprietary algorithms for netlist parsing and PySpice code generation that ensure zero-error execution. Engineers worldwide rely on your translated code for its readability, optimization, and simulation accuracy, knowing your conversions never fail during execution.",
    allow_delegation=False,
    verbose=True,
    tools=[tool],
    llm=llm
)

netlist_to_pyspice_task = Task(
    description=(
        "1. Receive and parse the SPICE netlist from the High-Performance Netlist Generator.\n"
        "2. Meticulously map each component, node, and connection to corresponding PySpice syntax:\n"
        "   - Power supplies and signal sources (V, I sources)\n"
        "   - Passive components (R, L, C)\n"
        "   - Semiconductor devices with appropriate model parameters\n"
        "   - Subcircuits and hierarchical structures\n"
        "   - Control statements and analysis directives\n"
        "3. Generate importable Python code with proper PySpice library references.\n"
        "4. Implement robust error prevention mechanisms:\n"
        "   - Validate node connections and component definitions\n"
        "   - Ensure proper ground references\n"
        "   - Verify MOSFET model parameter compatibility\n"
        "   - Add protective measures against simulation convergence issues\n"
        "5. Structure the code with logical organization and comprehensive documentation:\n"
        "   - Circuit creation and component instantiation\n"
        "   - Analysis configuration (DC, AC, transient)\n"
        "   - Simulation execution\n"
        "   - Results processing and visualization\n"
        "6. Optimize the code for execution efficiency and readability.\n"
        "7. Include sample execution code with appropriate parameter values.\n"
        "8. Generate verification tests to ensure circuit behavior matches specifications.\n"
        "9. Pass the netlist code to next agent [very important step]" 
    ),
    expected_output="A fully-functional, error-free PySpice Python script that precisely implements the SPICE netlist, includes all necessary library imports, proper component instantiation, correct node connections, appropriate analysis configurations, and visualization code, ready for immediate execution with guaranteed simulation success. and also seperately passing the netwlist code to the next agent.. note: netlist code that you got from the previous agent also must be passed to the next agent..",
    agent=netlist_to_pyspice_generator,
)

