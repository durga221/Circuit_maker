from crewai import Agent, Task
from crewai.tools import BaseTool
import json
import re
from typing import Any

class ConfigurationIdentifierTool(BaseTool):
    name: str = "MOSFET Configuration Identifierv "
    description: str = """
    Identifies the MOSFET amplifier configuration (CS, CG, CD) based on the user prompt.
    Can identify based on explicit mentions or infer from gain requirements.
    - Common Source (CS): High gain amplifier with phase inversion
    - Common Gate (CG): Current amplifier with good frequency response
    - Common Drain (CD): Buffer/follower with gain ≈ 1, high input impedance
    """
    
    def _run(self, user_prompt: str) -> str:
        config = {
            "type": "Unknown",
            "description": "",
            "identification_method": "Not identified"
        }
        
        # Check for explicit configuration mentions
        if any(term in user_prompt.lower() for term in ["common source", "cs", "source grounded"]):
            config["type"] = "Common Source (CS)"
            config["description"] = "Voltage amplifier with high voltage gain and phase inversion"
            config["identification_method"] = "Explicit mention"
        
        elif any(term in user_prompt.lower() for term in ["common gate", "cg", "gate grounded"]):
            config["type"] = "Common Gate (CG)"
            config["description"] = "Current amplifier with good high-frequency response"
            config["identification_method"] = "Explicit mention"
        
        elif any(term in user_prompt.lower() for term in ["common drain", "cd", "source follower", "drain grounded"]):
            config["type"] = "Common Drain (CD)"
            config["description"] = "Buffer amplifier with gain ≈ 1, high input impedance, low output impedance"
            config["identification_method"] = "Explicit mention"
        
        # If not explicitly mentioned, try to infer from gain requirements
        elif "gain" in user_prompt.lower():
            gain_match = re.search(r'gain\s*[=:]?\s*(\d+(?:\.\d+)?)', user_prompt.lower())
            if gain_match:
                gain_value = float(gain_match.group(1))
                
                if gain_value > 5:
                    config["type"] = "Common Source (CS)"
                    config["description"] = "Voltage amplifier with high voltage gain and phase inversion"
                    config["identification_method"] = "Inferred from high gain requirement"
                elif 0.9 <= gain_value <= 1.1:
                    config["type"] = "Common Drain (CD)"
                    config["description"] = "Buffer amplifier with gain ≈ 1, high input impedance, low output impedance"
                    config["identification_method"] = "Inferred from unity gain requirement"
                else:
                    config["type"] = "Common Source (CS)"
                    config["description"] = "Default choice for medium gain requirements"
                    config["identification_method"] = "Inferred from medium gain requirement"
        
        return json.dumps(config, indent=2)


class MOSFETParametersTool(BaseTool):
    name: str = "MOSFET Parameters Analyzer"
    description: str = """
    Extracts or sets MOSFET parameters based on the user prompt. 
    If parameters are not specified, provides default NMOS values:
    - Threshold Voltage (V_th) = 0.7V
    - Channel Length Modulation (λ) = 0.02 V^(-1)
    - Process Transconductance Parameter (μ_n C_ox) = 100 µA/V²
    - Oxide Capacitance per unit area (C_ox) = 5 fF/µm²
    - Electron Mobility (μ_n) = 500 cm²/V·s
    - Aspect Ratio (W/L) = 5
    """
    
    def _run(self, user_prompt: str) -> str:
        # Default NMOS parameters
        mosfet_params = {
            "type": "NMOS",
            "threshold_voltage": "0.7V",
            "channel_length_modulation": "0.02 V^(-1)",
            "transconductance_parameter": "100 µA/V²",
            "oxide_capacitance": "5 fF/µm²",
            "electron_mobility": "500 cm²/V·s",
            "aspect_ratio": "5",
            "parameters_source": "Default values used"
        }
        
        # Check if any parameters are specified
        parameters_specified = False
        
        # Check if MOSFET type is specified
        if any(term in user_prompt.lower() for term in ["pmos", "p-type", "p-channel"]):
            mosfet_params["type"] = "PMOS"
            parameters_specified = True
        elif any(term in user_prompt.lower() for term in ["nmos", "n-type", "n-channel"]):
            mosfet_params["type"] = "NMOS"  # Already the default, but mark as specified
            parameters_specified = True
        
        # Check for threshold voltage
        vth_match = re.search(r'(threshold|vth|v_th)\s*[=:]?\s*([\d.]+\s*[a-zA-Z]*)', user_prompt.lower())
        if vth_match:
            mosfet_params["threshold_voltage"] = vth_match.group(2).strip()
            parameters_specified = True
        
        # Check for channel length modulation (lambda)
        lambda_match = re.search(r'(channel length modulation|lambda|λ)\s*[=:]?\s*([\d.]+\s*[a-zA-Z^()-]*)', user_prompt.lower())
        if lambda_match:
            mosfet_params["channel_length_modulation"] = lambda_match.group(2).strip()
            parameters_specified = True
        
        # Check for transconductance parameter
        trans_match = re.search(r'(transconductance|μ_n c_ox)\s*[=:]?\s*([\d.]+\s*[a-zA-Z/²]*)', user_prompt.lower())
        if trans_match:
            mosfet_params["transconductance_parameter"] = trans_match.group(2).strip()
            parameters_specified = True
        
        # Check for oxide capacitance
        cox_match = re.search(r'(oxide capacitance|c_ox)\s*[=:]?\s*([\d.]+\s*[a-zA-Z/²]*)', user_prompt.lower())
        if cox_match:
            mosfet_params["oxide_capacitance"] = cox_match.group(2).strip()
            parameters_specified = True
        
        # Check for electron mobility
        mobility_match = re.search(r'(electron mobility|μ_n)\s*[=:]?\s*([\d.]+\s*[a-zA-Z/·²]*)', user_prompt.lower())
        if mobility_match:
            mosfet_params["electron_mobility"] = mobility_match.group(2).strip()
            parameters_specified = True
          
        # Check for aspect ratio or W/L
        wl_match = re.search(r'(aspect ratio|w/l)\s*[=:]?\s*([\d.]+)', user_prompt.lower())
        if wl_match:
            mosfet_params["aspect_ratio"] = wl_match.group(2).strip()
            parameters_specified = True
        
        if parameters_specified:
            mosfet_params["parameters_source"] = "Some parameters specified by user, others set to default"
        
        return json.dumps(mosfet_params, indent=2)


class ComponentValuesTool(BaseTool):
    name: str = "Component Values Extractor"
    description: str = """
    Extracts all component values mentioned in the user prompt. 
    Detects resistors, capacitors, voltage sources, current sources, and gain requirements.
    Does not assume any values not explicitly provided by the user.
    Identifies DC and AC voltage specifications if mentioned.
    """
    
    def _run(self, user_prompt: str) -> str:
        components = {
            "resistors": [],
            "capacitors": [],
            "voltage_sources": [],
            "current_sources": [],
            "performance_requirements": {}
        }
        
        # Extract resistors (R1, R2, Rs, Rd, etc.)
        resistor_matches = re.findall(r'(?:resistor|r\d*|r_[a-z]+)\s*[=:]?\s*([\d.]+\s*[kMG]?(?:ohm|Ω)?)', user_prompt, re.IGNORECASE)
        for match in resistor_matches:
            components["resistors"].append(match.strip())
        
        # Extract capacitors (C1, C2, Cc, etc.)
        capacitor_matches = re.findall(r'(?:capacitor|c\d*|c_[a-z]+)\s*[=:]?\s*([\d.]+\s*[pnuµm]?F)', user_prompt, re.IGNORECASE)
        for match in capacitor_matches:
            components["capacitors"].append(match.strip())
        
        # Extract voltage sources (VDD, VSS, Vin, etc.)
        voltage_matches = re.findall(r'(?:voltage|v(?:dd|ss|cc)?)\s*[=:]?\s*([\d.]+\s*[mµ]?V(?:\s*(?:AC|DC))?)', user_prompt, re.IGNORECASE)
        for match in voltage_matches:
            components["voltage_sources"].append(match.strip())
        
        # Extract input voltage specifically
        input_voltage_match = re.search(r'input\s*(?:voltage|v)?\s*(?:of|is|=|:)?\s*([\d.]+\s*[mµ]?V(?:\s*(?:AC|DC))?)', user_prompt, re.IGNORECASE)
        if input_voltage_match:
            input_voltage = input_voltage_match.group(1).strip()
            if not any(input_voltage in vs for vs in components["voltage_sources"]):
                components["voltage_sources"].append(f"Input: {input_voltage}")
        
        # Extract current sources
        current_matches = re.findall(r'(?:current|i\d*)\s*[=:]?\s*([\d.]+\s*[mµ]?A)', user_prompt, re.IGNORECASE)
        for match in current_matches:
            components["current_sources"].append(match.strip())
        
        # Extract performance requirements
        # Gain
        gain_match = re.search(r'gain\s*(?:of|is|=|:)?\s*([\d.]+)', user_prompt, re.IGNORECASE)
        if gain_match:
            components["performance_requirements"]["gain"] = gain_match.group(1).strip()
        
        # Bandwidth
        bw_match = re.search(r'bandwidth\s*(?:of|is|=|:)?\s*([\d.]+\s*[kMG]?Hz)', user_prompt, re.IGNORECASE)
        if bw_match:
            components["performance_requirements"]["bandwidth"] = bw_match.group(1).strip()
        
        # Power consumption
        power_match = re.search(r'power\s*(?:of|is|=|:)?\s*([\d.]+\s*[mµ]?W)', user_prompt, re.IGNORECASE)
        if power_match:
            components["performance_requirements"]["power"] = power_match.group(1).strip()
        
        return json.dumps(components, indent=2)


class CompleteCircuitAnalysisTool(BaseTool):
    name: str = "Complete Circuit Analysis Tool"
    description: str = """
    Performs complete analysis of MOSFET amplifier circuits from user prompts.
    Identifies configuration (CS, CG, CD), extracts or sets MOSFET parameters,
    and extracts all component values. Returns a comprehensive JSON output
    with all circuit details properly organized.
    """
    
    def _run(self, user_prompt: str) -> str:
        # Use the individual tools internally
        config_tool = ConfigurationIdentifierTool()
        mosfet_tool = MOSFETParametersTool()
        component_tool = ComponentValuesTool()
        
        # Get results from each tool
        config_result = json.loads(config_tool._run(user_prompt))
        mosfet_result = json.loads(mosfet_tool._run(user_prompt))
        component_result = json.loads(component_tool._run(user_prompt))
        
        # Combine all results
        final_result = {
            "circuit_configuration": config_result,
            "mosfet_parameters": mosfet_result,
            "circuit_components": component_result,
            "analysis_summary": {
                "configuration_type": config_result["type"],
                "mosfet_type": mosfet_result["type"],
                "specified_gain": component_result["performance_requirements"].get("gain", "Not specified"),
                "components_specified": {
                    "resistors": len(component_result["resistors"]),
                    "capacitors": len(component_result["capacitors"]),
                    "voltage_sources": len(component_result["voltage_sources"]),
                    "current_sources": len(component_result["current_sources"])
                }
            }
        }
        
        return json.dumps(final_result, indent=4)


# LLM client - simplified

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



# Define a single agent with all tools
senior_circuit_analyzer = Agent(
    role="MOSFET Circuit Analysis Expert",
    goal="Analyze MOSFET amplifier configurations and extract all circuit parameters",
    backstory="""Expert analog circuit designer with decades of experience in MOSFET amplifier design.
    Specializes in identifying circuit topologies, selecting appropriate components, and optimizing
    circuit performance for various applications.""",
    tools=[
        ConfigurationIdentifierTool(),
        MOSFETParametersTool(),
        ComponentValuesTool(),
        CompleteCircuitAnalysisTool()
    ],
    llm=GeminiLLM(),
    verbose=True
)

# Define the task as requested
circuit_analysis_task = Task(
    description="Analyze user input for circuit specs and topology for the given prompt {prompt}",
    expected_output="""to generate the best analysis on the all the given components and the type of topology(which type of amplifier)..
    expected output format in this type of format..
    dictionary format.. with all well described values and components and evrythin related to circuit..
    note: Dont't assume any values your self if user not given.Leave it as it has to be calculated..
    if nothing mentioned about the mosfet it should take the constant values like:
            
    Threshold Voltage (V_th) = 0.7V  # Minimum gate voltage to turn ON NMOS
    Channel Length Modulation (λ) = 0.02 V^(-1)  # Defines drain voltage effect on current
    Process Transconductance Parameter (μ_n C_ox) = 100 µA/V²  # Affects current-driving capability
    Oxide Capacitance per unit area (C_ox) = 5 fF/µm²  # Gate oxide capacitance
    Electron Mobility (μ_n) = 500 cm²/V·s  # Speed of electrons in the channel
    Aspect Ratio (W/L) = 5  # Ratio of MOSFET width to length

    at maximum always make use of this mosfet..
    """,
    agent=senior_circuit_analyzer
)

# Example of how to run the task (assuming you have a CrewAI crew set up)
# from crewai import Crew
# crew = Crew(
#     agents=[senior_circuit_analyzer],
#     tasks=[circuit_analysis_task],
#     verbose=True
# )
# result = crew.kickoff(inputs={"prompt": "I need a CS amplifier with gain 10 using resistors and capacitors with input voltage of 0.2V AC and 25V DC supply"})