from crewai import Agent, Task
from crewai.tools import BaseTool
import litellm
import os
from typing import Any




class GeminiLLM:
    def __init__(self, model_name="gemini/gemini-2.0-flash-lite"):
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


class ValidationReportGeneratorTool(BaseTool):
    name: str = "Validation Report Generator Tool"
    description: str = ("Compares simulation results with requirements and flags if redirect is needed.")
    
    def _run(self, validation_results: dict, simulation_results: dict = None) -> dict:
        # Simple comparison between requirements and simulation results
        parameter_validation = validation_results.get("parameter_validation", {})
        
        # Check if results match requirements
        matches_requirements = True
        failed_parameters = []
        
        for param, validation in parameter_validation.items():
            required = validation.get("required")
            achieved = validation.get("achieved")
            
            if isinstance(required, (int, float)) and isinstance(achieved, (int, float)):
                # Check if parameter meets requirements
                if param in ["voltage_gain", "bandwidth", "phase_margin"]:
                    if achieved < required:
                        matches_requirements = False
                        failed_parameters.append(param)
                elif param in ["noise", "power_consumption", "distortion"]:
                    if achieved > required:
                        matches_requirements = False
                        failed_parameters.append(param)
        
        # Determine which agent to redirect to (simplified logic)
        redirect_to = None
        if not matches_requirements:
            if any(p in ["input_impedance", "output_impedance", "voltage_gain"] for p in failed_parameters):
                redirect_to = "Component_Selection_Specialist"
            elif any(p in ["bandwidth", "phase_margin"] for p in failed_parameters):
                redirect_to = "Formulas_Equations_Engineer"
            else:
                redirect_to = "PySpice_Simulation_Expert"
        
        return {
            "matches_requirements": matches_requirements,
            "failed_parameters": failed_parameters,
            "redirect_to": redirect_to
        }


tool = ValidationReportGeneratorTool()


performance_validation_engineer = Agent(
    role="Senior Circuit Testing Engineer",
    goal="Validate simulation results against requirements and flag for redirection if needed",
    backstory="You're an expert circuit validation engineer who examines if MOSFET amplifier designs meet requirements.",
    allow_delegation=False,
    verbose=True,
    tools=[tool],
    llm=llm
)

performance_validation_task = Task(
    description="\n 0. Take the netlist code from the previous agent \n1. Compare simulation results against user requirements.\n2. Determine if all requirements are met.\n3. If requirements are not met, flag which specialist should address the issues.\n4. Finally pass the netlist code as the output.\nNote: finally pass the netlist code as the output..",
    expected_output="The netlist code",
    agent=performance_validation_engineer,
)

