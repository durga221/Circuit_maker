from crewai import Agent, Task
from crewai.tools import BaseTool
import litellm
import os
from typing import Any, Dict, List

from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


os.environ["GEMINI_API_KEY"] = API_KEY



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



class CommonSourceAnalysisTool(BaseTool):
    name: str = "Common Source Small Signal Analysis Tool"
    description: str = ("Analyzes Common Source MOSFET amplifier configurations using small signal models "
                        "to calculate gain, input/output impedance, bandwidth, and other performance metrics.")
    
    def _run(self, circuit_design: Dict[str, Any]) -> Dict[str, Any]:
        # Extract component values and circuit parameters
        component_values = circuit_design.get("component_values", {})
        transistor_params = circuit_design.get("transistor_parameters", {})
        
        # Get required parameters
        gm = transistor_params.get("gm", 0)  # Transconductance
        rd = transistor_params.get("rd", float('inf'))  # Drain-source resistance
        Rd = component_values.get("drain_resistor", 0)  # Drain resistor
        Rg = component_values.get("gate_resistor", 0)  # Gate resistor
        Cgs = transistor_params.get("Cgs", 0)  # Gate-source capacitance
        Cgd = transistor_params.get("Cgd", 0)  # Gate-drain capacitance
        
        # Perform small signal analysis
        small_signal_analysis = {
            "topology": "Common Source",
            "small_signal_model": {
                "elements": [
                    {"name": "gm*vgs", "from": "drain", "to": "source", "value": f"{gm} S * vgs"},
                    {"name": "rd", "from": "drain", "to": "source", "value": f"{rd} Ω"},
                    {"name": "Rd", "from": "drain", "to": "vdd", "value": f"{Rd} Ω"},
                    {"name": "Rg", "from": "gate", "to": "gnd", "value": f"{Rg} Ω"},
                    {"name": "Cgs", "from": "gate", "to": "source", "value": f"{Cgs} F"},
                    {"name": "Cgd", "from": "gate", "to": "drain", "value": f"{Cgd} F"}
                ]
            },
            "performance_metrics": {}
        }
        
        # Calculate key performance metrics
        # Voltage gain (Av)
        voltage_gain = -1 * gm * (Rd * rd) / (Rd + rd)
        voltage_gain_db = 20 * (voltage_gain if voltage_gain > 0 else -voltage_gain)
        
        # Input impedance
        input_impedance = Rg
        
        # Output impedance
        output_impedance = Rd * rd / (Rd + rd)
        
        # Bandwidth calculation (simplified)
        # For low frequency cutoff
        input_capacitance = Cgs + Cgd * (1 + abs(voltage_gain))  # Miller effect
        low_cutoff_freq = 1 / (2 * 3.14159 * Rg * input_capacitance)
        
        # Store calculated metrics
        small_signal_analysis["performance_metrics"] = {
            "voltage_gain": voltage_gain,
            "voltage_gain_db": f"{voltage_gain_db} dB",
            "input_impedance": f"{input_impedance} Ω",
            "output_impedance": f"{output_impedance} Ω",
            "bandwidth": {
                "low_cutoff": f"{low_cutoff_freq} Hz"
            },
            "formulas": {
                "voltage_gain": "Av = -gm * (Rd || rd)",
                "input_impedance": "Zin = Rg",
                "output_impedance": "Zout = Rd || rd",
                "miller_capacitance": "Cin = Cgs + Cgd*(1+|Av|)"
            }
        }
        
        return small_signal_analysis


class CommonDrainAnalysisTool(BaseTool):
    name: str = "Common Drain Small Signal Analysis Tool"
    description: str = ("Analyzes Common Drain (Source Follower) MOSFET amplifier configurations using small signal models "
                        "to calculate gain, input/output impedance, bandwidth, and other performance metrics.")
    
    def _run(self, circuit_design: Dict[str, Any]) -> Dict[str, Any]:
        # Extract component values and circuit parameters
        component_values = circuit_design.get("component_values", {})
        transistor_params = circuit_design.get("transistor_parameters", {})
        
        # Get required parameters
        gm = transistor_params.get("gm", 0)  # Transconductance
        rd = transistor_params.get("rd", float('inf'))  # Drain-source resistance
        Rs = component_values.get("source_resistor", 0)  # Source resistor
        Rg = component_values.get("gate_resistor", 0)  # Gate resistor
        Cgs = transistor_params.get("Cgs", 0)  # Gate-source capacitance
        Cgd = transistor_params.get("Cgd", 0)  # Gate-drain capacitance
        
        # Perform small signal analysis
        small_signal_analysis = {
            "topology": "Common Drain",
            "small_signal_model": {
                "elements": [
                    {"name": "gm*vgs", "from": "source", "to": "drain", "value": f"{gm} S * vgs"},
                    {"name": "rd", "from": "drain", "to": "source", "value": f"{rd} Ω"},
                    {"name": "Rs", "from": "source", "to": "gnd", "value": f"{Rs} Ω"},
                    {"name": "Rg", "from": "gate", "to": "gnd", "value": f"{Rg} Ω"},
                    {"name": "Cgs", "from": "gate", "to": "source", "value": f"{Cgs} F"},
                    {"name": "Cgd", "from": "gate", "to": "drain", "value": f"{Cgd} F"}
                ]
            },
            "performance_metrics": {}
        }
        
        # Calculate key performance metrics
        # Voltage gain (Av)
        gm_Rs_parallel_rd = (gm * Rs * rd) / (Rs + rd)
        voltage_gain = gm_Rs_parallel_rd / (1 + gm_Rs_parallel_rd)
        voltage_gain_db = 20 * (voltage_gain if voltage_gain > 0 else -voltage_gain)
        
        # Input impedance
        input_impedance = Rg
        
        # Output impedance
        output_impedance = Rs * rd / (Rs + rd + gm * Rs * rd)
        
        # Bandwidth calculation
        effective_capacitance = Cgs + Cgd * (1 - voltage_gain)
        low_cutoff_freq = 1 / (2 * 3.14159 * Rg * effective_capacitance)
        
        # Store calculated metrics
        small_signal_analysis["performance_metrics"] = {
            "voltage_gain": voltage_gain,
            "voltage_gain_db": f"{voltage_gain_db} dB",
            "input_impedance": f"{input_impedance} Ω",
            "output_impedance": f"{output_impedance} Ω",
            "bandwidth": {
                "low_cutoff": f"{low_cutoff_freq} Hz"
            },
            "formulas": {
                "voltage_gain": "Av = gm*Rs*rd/(Rs+rd) / (1 + gm*Rs*rd/(Rs+rd))",
                "input_impedance": "Zin = Rg",
                "output_impedance": "Zout = Rs || (rd/(1+gm*rd))",
                "effective_capacitance": "Ceff = Cgs + Cgd*(1-Av)"
            }
        }
        
        return small_signal_analysis


class CommonGateAnalysisTool(BaseTool):
    name: str = "Common Gate Small Signal Analysis Tool"
    description: str = ("Analyzes Common Gate MOSFET amplifier configurations using small signal models "
                        "to calculate gain, input/output impedance, bandwidth, and other performance metrics.")
    
    def _run(self, circuit_design: Dict[str, Any]) -> Dict[str, Any]:
        # Extract component values and circuit parameters
        component_values = circuit_design.get("component_values", {})
        transistor_params = circuit_design.get("transistor_parameters", {})
        
        # Get required parameters
        gm = transistor_params.get("gm", 0)  # Transconductance
        rd = transistor_params.get("rd", float('inf'))  # Drain-source resistance
        Rd = component_values.get("drain_resistor", 0)  # Drain resistor
        Rs = component_values.get("source_resistor", 0)  # Source resistor
        Cgs = transistor_params.get("Cgs", 0)  # Gate-source capacitance
        Cgd = transistor_params.get("Cgd", 0)  # Gate-drain capacitance
        
        # Perform small signal analysis
        small_signal_analysis = {
            "topology": "Common Gate",
            "small_signal_model": {
                "elements": [
                    {"name": "gm*vgs", "from": "drain", "to": "source", "value": f"{gm} S * vgs"},
                    {"name": "rd", "from": "drain", "to": "source", "value": f"{rd} Ω"},
                    {"name": "Rd", "from": "drain", "to": "vdd", "value": f"{Rd} Ω"},
                    {"name": "Rs", "from": "source", "to": "gnd", "value": f"{Rs} Ω"},
                    {"name": "Cgs", "from": "gate", "to": "source", "value": f"{Cgs} F"},
                    {"name": "Cgd", "from": "gate", "to": "drain", "value": f"{Cgd} F"}
                ]
            },
            "performance_metrics": {}
        }
        
        # Calculate key performance metrics
        # Voltage gain (Av)
        voltage_gain = gm * (Rd * rd) / (Rd + rd)
        voltage_gain_db = 20 * (voltage_gain if voltage_gain > 0 else -voltage_gain)
        
        # Input impedance
        input_impedance = 1 / gm
        
        # Output impedance
        output_impedance = Rd * rd / (Rd + rd)
        
        # Bandwidth calculation
        source_capacitance = Cgs
        low_cutoff_freq = 1 / (2 * 3.14159 * Rs * source_capacitance)
        
        # Store calculated metrics
        small_signal_analysis["performance_metrics"] = {
            "voltage_gain": voltage_gain,
            "voltage_gain_db": f"{voltage_gain_db} dB",
            "input_impedance": f"{input_impedance} Ω",
            "output_impedance": f"{output_impedance} Ω",
            "bandwidth": {
                "low_cutoff": f"{low_cutoff_freq} Hz"
            },
            "formulas": {
                "voltage_gain": "Av = gm * (Rd || rd)",
                "input_impedance": "Zin = 1/gm",
                "output_impedance": "Zout = Rd || rd",
                "source_capacitance": "Cs = Cgs"
            }
        }
        
        return small_signal_analysis


class SmallSignalAnalyzer(BaseTool):
    name: str = "MOSFET Small Signal Analyzer Tool"
    description: str = ("Comprehensive tool that analyzes MOSFET amplifier configurations "
                        "using small signal models to predict performance characteristics "
                        "across Common Source, Common Drain, and Common Gate topologies.")
    
    cs_tool: CommonSourceAnalysisTool = Field(default_factory=CommonSourceAnalysisTool)
    cd_tool: CommonDrainAnalysisTool = Field(default_factory=CommonDrainAnalysisTool)
    cg_tool: CommonGateAnalysisTool = Field(default_factory=CommonGateAnalysisTool)
    

    def _run(self, circuit_design: Dict[str, Any]) -> Dict[str, Any]:
        topology = circuit_design.get("topology", "")
        
        # Select appropriate analysis tool based on topology
        if topology == "Common Source":
            small_signal_analysis = self.cs_tool._run(circuit_design)
        elif topology == "Common Drain":
            small_signal_analysis = self.cd_tool._run(circuit_design)
        elif topology == "Common Gate":
            small_signal_analysis = self.cg_tool._run(circuit_design)
        else:
            return {
                "error": "Invalid topology specified. Must be one of: Common Source, Common Drain, or Common Gate"
            }
        
        # Generate comprehensive analysis report
        result = {
            "circuit_information": {
                "topology": topology,
                "component_values": circuit_design.get("component_values", {}),
                "transistor_parameters": circuit_design.get("transistor_parameters", {})
            },
            "small_signal_analysis": small_signal_analysis,
            "summary": {
                "key_characteristics": {
                    "voltage_gain": small_signal_analysis["performance_metrics"]["voltage_gain"],
                    "voltage_gain_db": small_signal_analysis["performance_metrics"]["voltage_gain_db"],
                    "input_impedance": small_signal_analysis["performance_metrics"]["input_impedance"],
                    "output_impedance": small_signal_analysis["performance_metrics"]["output_impedance"],
                    "bandwidth": small_signal_analysis["performance_metrics"]["bandwidth"],
                },
                "applications": get_applications_for_topology(topology, small_signal_analysis["performance_metrics"]),
                "trade_offs": get_tradeoffs_for_topology(topology, small_signal_analysis["performance_metrics"])
            }
        }
        
        return result


def get_applications_for_topology(topology: str, metrics: Dict[str, Any]) -> List[str]:
    """Helper function to provide appropriate applications based on topology and metrics"""
    applications = []
    
    if topology == "Common Source":
        applications = [
            "Voltage amplification stages",
            "Audio pre-amplifiers",
            "Sensor interfaces requiring high gain",
            "Signal conditioning circuits"
        ]
    elif topology == "Common Drain":
        applications = [
            "Buffer stages with low output impedance",
            "Level shifters",
            "Impedance matching circuits",
            "Driving low-impedance loads"
        ]
    elif topology == "Common Gate":
        applications = [
            "RF amplifiers requiring good isolation",
            "Cascode configurations",
            "Current sensing applications",
            "High-frequency circuits"
        ]
    
    return applications


def get_tradeoffs_for_topology(topology: str, metrics: Dict[str, Any]) -> Dict[str, str]:
    """Helper function to provide appropriate trade-offs based on topology and metrics"""
    tradeoffs = {}
    
    if topology == "Common Source":
        tradeoffs = {
            "gain_vs_bandwidth": "Higher gain reduces bandwidth due to Miller effect",
            "gain_vs_linearity": "Higher gain typically reduces linearity",
            "output_impedance": "High output impedance limits ability to drive loads"
        }
    elif topology == "Common Drain":
        tradeoffs = {
            "gain_limitation": "Gain is always less than 1",
            "linearity_vs_power": "Good linearity but requires higher power consumption",
            "impedance_matching": "Excellent for impedance transformation but limited gain"
        }
    elif topology == "Common Gate":
        tradeoffs = {
            "input_impedance": "Low input impedance may require additional matching",
            "noise_figure": "Higher noise figure than Common Source",
            "bandwidth_vs_gain": "Good bandwidth but moderate gain"
        }
    
    return tradeoffs


# Create the tool
small_signal_analyzer_tool = SmallSignalAnalyzer()


# Create the agent
small_signal_analysis_agent = Agent(
    role="MOSFET Small Signal Analysis Expert",
    goal="Analyze MOSFET amplifier circuits using small signal models to determine exact performance characteristics and provide comprehensive insights for design optimization",
    backstory="You are a highly specialized analog IC designer with extensive experience in MOSFET small signal analysis. With a PhD in Microelectronics and 15 years of industry experience, you've developed proprietary techniques for accurately predicting circuit performance using advanced small signal modeling. Your methodology has been adopted by leading semiconductor companies for analyzing amplifier stages in critical applications from medical devices to aerospace systems. Your ability to extract maximum performance from transistor configurations through precise small signal analysis has made you a sought-after consultant for challenging analog design problems.",
    allow_delegation=False,
    verbose=True,
    tools=[small_signal_analyzer_tool],
    llm=GeminiLLM()
)

small_signal_analysis_task = Task(
    description=(
        "1. Analyze the MOSFET circuit configuration using small signal models to determine "
        "key performance characteristics including:\n"
        "   - Voltage gain (magnitude and phase)\n"
        "   - Input and output impedance\n"
        "   - Bandwidth limitations\n"
        "   - Noise performance\n"
        "   - Linearity considerations\n"
        "2. Create a comprehensive small signal model identifying all relevant components and their effects\n"
        "3. Derive and calculate all critical formulas for the specific topology\n"
        "4. Identify potential performance bottlenecks and provide optimization recommendations\n"
        "5. Generate a complete JSON report containing all analytical results\n"
        "\n"
        "Input format example:\n"
        "{{\n"  # Note the doubled braces
        "  \"topology\": \"Common Source\",\n"
        "  \"component_values\": {{\n"  # Note the doubled braces
        "    \"drain_resistor\": 10000,\n"
        "    \"gate_resistor\": 1000000,\n"
        "    \"source_resistor\": 0,\n"
        "    \"input_capacitor\": 1e-6\n"
        "  }},\n"  # Note the doubled braces
        "  \"transistor_parameters\": {{\n"  # Note the doubled braces
        "    \"gm\": 0.002,\n"
        "    \"rd\": 50000,\n"
        "    \"Cgs\": 5e-12,\n"
        "    \"Cgd\": 1e-12\n"
        "  }},\n"  # Note the doubled braces
        "  \"requirements\": {{\n"  # Note the doubled braces
        "    \"min_gain_db\": 20,\n"
        "    \"min_bandwidth\": 100000,\n"
        "    \"max_input_impedance\": 1000000\n"
        "  }}\n"
        "}}\n"  # Note the doubled braces
    ),
    expected_output=(
        "A comprehensive JSON document containing detailed small signal analysis results including: "
        "circuit model, performance metrics with formulas, component values, impedance characteristics, "
        "bandwidth calculations, and optimization recommendations specific to the MOSFET configuration."
    ),
    agent=small_signal_analysis_agent
)