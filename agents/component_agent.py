from crewai import Agent, Task
from crewai.tools import BaseTool
import os
from typing import Dict, Any

import litellm




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


class CommonSourceComponentTool(BaseTool):
    name: str = "Common Source Component Identification Tool"
    description: str = "Identifies required components for Common Source MOSFET amplifier configurations."
    
    def _run(self, is_rs_present: bool) -> Dict:
        """
        Identifies required components for Common Source MOSFET amplifier configurations.
        
        Args:
            is_rs_present: Boolean indicating if source resistor and bypass capacitor are present.
        
        Returns:
            Dictionary with required components and their naming conventions.
        """
        components = {
            "configuration": "Common Source",
            "bias_type": "Voltage Divider Bias",
            "description": "The Common Source amplifier is a fundamental MOSFET amplifier configuration that provides voltage gain. It is widely used in analog circuits for signal amplification.",
            "required_components": {
                "active_components": [
                    {
                        "name": "M1",
                        "type": "MOSFET",
                        "description": "Main amplifying MOSFET that provides voltage gain."
                    }
                ],
                "resistors": [
                    {
                        "name": "RD",
                        "description": "Drain resistor that determines gain and DC operating point."
                    },
                    {
                        "name": "R1",
                        "description": "Upper resistor in the voltage divider bias network, sets gate voltage."
                    },
                    {
                        "name": "R2",
                        "description": "Lower resistor in the voltage divider bias network, forms a stable bias point."
                    }
                ],
                "capacitors": [
                    {
                        "name": "CIN",
                        "description": "Input coupling capacitor to block DC and pass AC signals. Ensures DC isolation between stages."
                    },
                    {
                        "name": "COUT",
                        "description": "Output coupling capacitor to block DC while allowing amplified AC signals to pass. Prevents DC bias shifting in the next stage."
                    }
                ],
                "voltage_sources": [
                    {
                        "name": "VDD",
                        "description": "Power supply voltage that provides the necessary drain current for operation."
                    },
                    {
                        "name": "VIN",
                        "description": "Input signal voltage source that provides the AC signal to be amplified."
                    }
                ]
            }
        }

        if is_rs_present:
            components["required_components"]["resistors"].append({
                "name": "RS",
                "description": "Source resistor for degeneration, improving biasing stability and linearity."
            })
            
            components["required_components"]["capacitors"].append({
                "name": "CS",
                "description": "Source bypass capacitor that increases AC gain by bypassing RS at high frequencies."
            })
        
        return components


class CommonDrainComponentTool(BaseTool):
    name: str = "Common Drain Component Identification Tool"
    description: str = "Identifies required components for Common Drain (Source Follower) MOSFET configurations."
    
    def _run(self) -> Dict:
        """
        Identifies required components for Common Drain (Source Follower) MOSFET configurations.
        
        Returns:
            Dictionary with required components and their naming conventions.
        """
        components = {
            "configuration": "Common Drain (Source Follower)",
            "bias_type": "Voltage Divider Bias",
            "description": "The Common Drain (Source Follower) configuration provides voltage buffering with near-unity gain. It is mainly used for impedance matching and driving low-impedance loads.",
            "required_components": {
                "active_components": [
                    {
                        "name": "M1",
                        "type": "MOSFET",
                        "description": "Main MOSFET for source follower configuration, providing high input impedance and low output impedance."
                    }
                ],
                "resistors": [
                    {
                        "name": "RS",
                        "description": "Source resistor that sets bias current and serves as the output load."
                    },
                    {
                        "name": "R1",
                        "description": "Upper resistor in the voltage divider bias network, helps set gate voltage."
                    },
                    {
                        "name": "R2",
                        "description": "Lower resistor in the voltage divider bias network, helps set stable gate bias."
                    }
                ],
                "capacitors": [
                    {
                        "name": "CIN",
                        "description": "Input coupling capacitor that blocks DC while allowing AC signals to pass. Ensures proper signal transfer from the previous stage."
                    },
                    {
                        "name": "COUT",
                        "description": "Output coupling capacitor that blocks DC from appearing at the output, ensuring only the AC signal is transferred."
                    },
                    {
                        "name": "CS",
                        "description": "Source bypass capacitor to improve AC performance by reducing variations in source voltage, stabilizing signal gain."
                    }
                ],
                "voltage_sources": [
                    {
                        "name": "VDD",
                        "description": "Power supply voltage that provides necessary biasing for MOSFET operation."
                    },
                    {
                        "name": "VIN",
                        "description": "Input signal voltage source that provides the AC signal for buffering."
                    }
                ]
            }
        }
        
        return components


class CommonGateComponentTool(BaseTool):
    name: str = "Common Gate Component Identification Tool"
    description: str = "Identifies required components for Common Gate MOSFET configurations."
    
    def _run(self) -> Dict:
        """
        Identifies required components for Common Gate MOSFET configurations.
        
        Returns:
            Dictionary with required components and their naming conventions.
        """
        components = {
            "configuration": "Common Gate",
            "bias_type": "Voltage Divider Bias",
            "description": "The Common Gate configuration provides voltage gain with low input impedance and high output impedance. It's useful for high-frequency applications and impedance matching.",
            "required_components": {
                "active_components": [
                    {
                        "name": "M1",
                        "type": "MOSFET",
                        "description": "Main MOSFET for common gate configuration, with signal applied to source and output taken from drain."
                    }
                ],
                "resistors": [
                    {
                        "name": "RD",
                        "description": "Drain resistor that determines gain and DC operating point."
                    },
                    {
                        "name": "RS",
                        "description": "Source resistor for input impedance and bias current setting."
                    },
                    {
                        "name": "R1",
                        "description": "Upper resistor in the voltage divider bias network for gate bias voltage."
                    },
                    {
                        "name": "R2",
                        "description": "Lower resistor in the voltage divider bias network for stable gate bias."
                    }
                ],
                "capacitors": [
                    {
                        "name": "CIN",
                        "description": "Input coupling capacitor to block DC and pass AC signals to the source terminal."
                    },
                    {
                        "name": "COUT",
                        "description": "Output coupling capacitor to block DC while allowing amplified AC signals to pass."
                    },
                    {
                        "name": "CG",
                        "description": "Gate bypass capacitor to hold gate voltage constant at AC frequencies."
                    }
                ],
                "voltage_sources": [
                    {
                        "name": "VDD",
                        "description": "Power supply voltage that provides necessary biasing for MOSFET operation."
                    },
                    {
                        "name": "VIN",
                        "description": "Input signal voltage source that provides the AC signal to the source terminal."
                    }
                ]
            }
        }
        
        return components


class ComponentIdentificationTool(BaseTool):
    name: str = "Component Identification Tool"
    description: str = "Identifies required components for MOSFET amplifier configuration based on circuit analysis."
    
    def _run(self, circuit_analysis: Dict) -> Dict:
        """
        Identifies required components based on the circuit analysis.
        
        Args:
            circuit_analysis: Dictionary containing circuit analysis results
            
        Returns:
            Dictionary with required components and their naming conventions
        """
        # Extract circuit type from analysis
        circuit_type = circuit_analysis.get("circuit_type", "Not identified")
        
        # Determine which component tool to use based on circuit type
        if "Common Source (CS)" in circuit_type:
            # Check if it has source resistor
            is_rs_present = "with Rs" in circuit_type
            cs_tool = CommonSourceComponentTool()
            return cs_tool._run(is_rs_present)
            
        elif "Common Drain (CD)" in circuit_type or "Source Follower" in circuit_type:
            cd_tool = CommonDrainComponentTool()
            return cd_tool._run()
            
        elif "Common Gate (CG)" in circuit_type:
            cg_tool = CommonGateComponentTool()
            return cg_tool._run()
            
        else:
            # Default to common source without Rs as fallback
            cs_tool = CommonSourceComponentTool()
            return cs_tool._run(False)


# Create the Component Identification Specialist agent
component_selection_specialist = Agent(
    role="MOSFET Component Identification Specialist",
    goal="Identify all required components and their standard naming conventions for different MOSFET amplifier configurations",
    backstory="You're an expert in MOSFET circuit design with decades of experience in identifying the required components for different amplifier topologies. Your specialty lies in understanding the standard naming conventions and component requirements for common source, common drain, and common gate configurations with various biasing arrangements.",
    allow_delegation=False,
    verbose=True,
    tools=[ComponentIdentificationTool()],
    llm=llm
)

# Create the task for component identification
component_selection_task = Task(
    description=(
        "1. Review the circuit analysis from the previous agent.\n"
        "2. Identify the MOSFET configuration (Common Source, Common Drain, Common Gate).\n"
        "3. Determine all required components for the identified configuration with standard naming conventions.\n"
        "4. Assume voltage divider bias if no specific biasing is mentioned in the analysis.\n"
        "5. Generate a complete list of required components without assigning specific values."
    ),
    expected_output="A JSON format response containing the circuit configuration, bias type, description, and a complete list of required components with standard naming conventions organized by component type (active components, resistors, capacitors, voltage sources). and also include that values for the components that are recieved from the previous agents(i.e the specifications which are mentioned in the user propmpt)..final meaning is combining the both agents responses but in well structured format.. in json format..",
    agent=component_selection_specialist
)