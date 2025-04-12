from crewai import Agent, Task
from crewai.tools import BaseTool
from typing import Any, Dict

import litellm
import os
from typing import Any, Dict, List

from pydantic import Field






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

class CommonSourceFormulaTool(BaseTool):
    name: str = "Common Source MOSFET Formula Tool"
    description: str = "Provides formulas for Common Source MOSFET amplifier configuration analysis"
    
    def _run(self, query: str = "") -> Dict[str, Any]:
        formulas = {
            "dc_analysis": {
                "saturation_condition": "V_DS > V_GS - V_th",
                "drain_current": "I_D = (1/2) * k_n * (V_GS - V_th)^2",
                "gate_voltage": "V_G = V_DD * (R_2 / (R_1 + R_2))",
                "source_voltage": "V_S = I_D * R_S",
                "gate_source_voltage": "V_GS = V_G - V_S",
                "drain_voltage": "V_D = V_DD - I_D * R_D"
            },
            "ac_analysis": {
                "transconductance": "g_m = 2 * I_D / (V_GS - V_th)",
                "output_resistance": "r_o = 1 / (λ * I_D)"
            },
            "voltage_gain": {
                "without_rs": "A_v = - g_m * (R_D || R_L)",
                "with_rs": "A_v = - (g_m * (R_D || R_L)) / (1 + g_m * R_S)",
                "with_bypassed_rs": "A_v = - g_m * (R_D || R_L)"
            },
            "impedance": {
                "input_without_rs": "Z_in ≈ ∞ (for ideal MOSFET)",
                "input_with_rs": "Z_in = (1 + g_m * R_S) * Z_gs",
                "output": "Z_out = R_D || r_o"
            },
            "frequency": {
                "low_cutoff": "f_L = 1 / (2π * R_eq * C)",
                "gain_bandwidth": "f_T = g_m / (2π * C_gs)",
                "miller_effect": "C_gd' = C_gd * (1 - A_v)",
                "high_cutoff": "f_H = 1 / (2π * R_out * (C_gs + C_gd'))",
                "bandwidth": "BW = f_H - f_L"
            },
            "power": {
                "dissipation": "P_D = V_DD * I_D",
                "efficiency": "η = (P_AC Output / P_DC Input) * 100%"
            }
        }
        
        return {
            "topology": "Common Source",
            "formulas": formulas
        }


class CommonDrainFormulaTool(BaseTool):
    name: str = "Common Drain MOSFET Formula Tool"
    description: str = "Provides formulas for Common Drain (Source Follower) MOSFET amplifier configuration analysis"
    
    def _run(self, query: str = "") -> Dict[str, Any]:
        formulas = {
            "dc_analysis": {
                "saturation_condition": "V_DS > V_GS - V_th",
                "drain_current": "I_D = (1/2) * k_n * (V_GS - V_th)^2",
                "gate_voltage": "V_G = V_DD * (R_2 / (R_1 + R_2))",
                "source_voltage": "V_S = I_D * R_S",
                "gate_source_voltage": "V_GS = V_G - V_S",
                "drain_voltage": "V_D = V_DD - I_D * R_D"
            },
            "ac_analysis": {
                "transconductance": "g_m = 2 * I_D / (V_GS - V_th)",
                "output_resistance": "r_o = 1 / (λ * I_D)"
            },
            "voltage_gain": {
                "without_rs": "A_v = g_m * (R_S || R_L) / (1 + g_m * (R_S || R_L))",
                "with_rs": "A_v = (R_S || R_L) / (R_S || R_L + 1/g_m)",
                "approximate": "A_v ≈ 1 (for high g_m)"
            },
            "impedance": {
                "input": "Z_in = (1 + g_m * R_S) * (R_g || Z_gs)",
                "output": "Z_out = (R_S || r_o) / (1 + g_m * (R_S || r_o))"
            },
            "frequency": {
                "low_cutoff": "f_L = 1 / (2π * R_eq * C)",
                "gain_bandwidth": "f_T = g_m / (2π * C_gs)",
                "miller_effect": "C_gd' = C_gd * (1 - A_v)",
                "high_cutoff": "f_H = 1 / (2π * R_out * (C_gs + C_gd'))",
                "bandwidth": "BW = f_H - f_L"
            },
            "power": {
                "dissipation": "P_D = V_DD * I_D",
                "efficiency": "η = (P_AC Output / P_DC Input) * 100%"
            }
        }
        
        return {
            "topology": "Common Drain (Source Follower)",
            "formulas": formulas
        }


class CommonGateFormulaTool(BaseTool):
    name: str = "Common Gate MOSFET Formula Tool"
    description: str = "Provides formulas for Common Gate MOSFET amplifier configuration analysis"
    
    def _run(self, query: str = "") -> Dict[str, Any]:
        formulas = {
            "dc_analysis": {
                "saturation_condition": "V_DS > V_GS - V_th",
                "drain_current": "I_D = (1/2) * k_n * (V_GS - V_th)^2",
                "gate_voltage": "V_G = Fixed (often 0V for small-signal AC)",
                "source_voltage": "V_S = I_D * R_S",
                "gate_source_voltage": "V_GS = V_G - V_S",
                "drain_voltage": "V_D = V_DD - I_D * R_D"
            },
            "ac_analysis": {
                "transconductance": "g_m = 2 * I_D / (V_GS - V_th)",
                "output_resistance": "r_o = 1 / (λ * I_D)"
            },
            "voltage_gain": {
                "without_rs": "A_v = g_m * (R_D || R_L)",
                "with_rs": "A_v = (g_m * (R_D || R_L)) / (1 + g_m * R_S)",
                "approximate": "A_v ≈ g_m * (R_D || R_L) (if R_S is small)"
            },
            "impedance": {
                "input": "Z_in ≈ 1 / g_m",
                "output": "Z_out = (R_D || r_o)"
            },
            "frequency": {
                "low_cutoff": "f_L = 1 / (2π * R_eq * C)",
                "gain_bandwidth": "f_T = g_m / (2π * C_gs)",
                "high_cutoff": "f_H = 1 / (2π * R_out * (C_gs + C_gd))",
                "bandwidth": "BW = f_H - f_L"
            },
            "power": {
                "dissipation": "P_D = V_DD * I_D",
                "efficiency": "η = (P_AC Output / P_DC Input) * 100%"
            }
        }
        
        return {
            "topology": "Common Gate",
            "formulas": formulas
        }


# Initialize the tools
common_source_tool = CommonSourceFormulaTool()
common_drain_tool = CommonDrainFormulaTool()
common_gate_tool = CommonGateFormulaTool()

# Create a MOSFET engineer agent that uses these tools
formulas_equations_engineer = Agent(
    role="MOSFET Circuit Design Engineer",
    goal="Design and analyze MOSFET amplifier circuits to meet user specifications",
    backstory="An expert in analog electronics with specialization in MOSFET amplifier design. You apply the right formulas to calculate component values and predict circuit performance.",
    tools=[common_source_tool, common_drain_tool, common_gate_tool],
    verbose=True,
    llm=llm
)

# Create a task for the MOSFET engineer
formula_calculation_task = Task(
    description=(
        "1. Identify the MOSFET circuit topology based on user requirements\n"
        "2. Retrieve the appropriate formulas using the relevant formula tool\n"
        "3. Apply the formulas to calculate all circuit parameters and component values\n"
        "4. Make reasonable assumptions for any unknown values\n"
        "5. Verify that the calculated values meet the specified requirements\n"
        "6. Output a comprehensive design with all parameters and analysis results"
    ),
    expected_output=(
        "A structured JSON containing the circuit topology, all calculated component values, "
        "performance metrics (gain, bandwidth, input/output impedance), and verification "
        "that the design meets the specified requirements."
    ),
    agent=formulas_equations_engineer
)

# Example usage
# result = circuit_design_task.execute()