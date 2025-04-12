
from typing import Any
from crewai import Agent, Task
import litellm
import os



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


# Create the Circuit Visualization Code Generator Agent
circuit_code_generator = Agent(
    role="Circuit Visualization Code Generator",
    goal="Generate Python code that visualizes circuit diagrams from SPICE netlists using matplotlib and networkx",
    backstory="You're a specialized circuit visualization code expert who creates Python scripts that transform SPICE netlists into visual representations. Your expertise in electrical engineering, Python programming, and data visualization allows you to write code that produces clear circuit diagrams showing component values, connections, and circuit topology. Engineers rely on your code to quickly visualize circuits before simulation.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)




# Create the code generation task
circuit_code_generation_task = Task(
    description=(
            """Parse the given SPICE netlist and extract components, connections, and node labels.
        Generate Python code that:
        Uses matplotlib and networkx for circuit visualization.
        Creates a clear, simple, and accurate circuit diagram with minimal clutter.
        Uses a structured layout to position circuit elements logically.
        Labels components (R, C, L, MOSFETs, etc.) with their values.
        Maintains readability and symmetry in visualization.
        Ensures correct connectivity between circuit nodes.
        Optimize the diagram’s style:
        Consistent spacing for clarity.
        Rounded nodes with easy-to-read text.
        Minimal overlaps between wires and elements.
        Ensure the generated code is:
        Executable in any Python environment (e.g., IDLE, Jupyter Notebook).
        Reusable for different netlists with minor modifications.
        Efficient, using clean and modular functions.
        Provide a working example netlist and a sample execution to ensure correctness.


        """
         ),
    expected_output="""Fully functional Python code that, when executed, generates a clean, simple, and accurate circuit diagram like the provided image.
        The code should be:
        Commented and structured for readability.
        Accurate in circuit representation without excessive complexity.
        Easy to modify for different netlists.
        The generated image should be identical in clarity to the reference image, with:
        Properly labeled nodes and components.
        A neat, professional look without excessive clutter.
        An organized layout that visually represents the actual circuit topology.

        the output must be like the given below example..
        import matplotlib.pyplot as plt
        import networkx as nx
        from typing import Dict, List, Tuple

        class CircuitVisualizer:
            def __init__(self):
                self.graph = nx.Graph()
                self.component_positions = {}
                self.component_labels = {}
                
            def create_common_source_amplifier(self):
                # Define nodes
                nodes = ['VDD', 'Drain', 'Gate', 'Source', 'GND', 'Vin', 'Vout']
                
                # Add nodes to graph
                for node in nodes:
                    self.graph.add_node(node)
                
                # Add components
                # VDD power supply
                self.graph.add_edge('VDD', 'GND', component='VDD', label='VDD: 5V')
                
                # Drain resistor
                self.graph.add_edge('VDD', 'Drain', component='RD', label='RD: 1kΩ')
                
                # Gate resistor for biasing
                self.graph.add_edge('VDD', 'Gate', component='RG1', label='RG1: 100kΩ')
                
                # Gate to ground resistor (voltage divider)
                self.graph.add_edge('Gate', 'GND', component='RG2', label='RG2: 100kΩ')
                
                # Source resistor
                self.graph.add_edge('Source', 'GND', component='RS', label='RS: 200Ω')
                
                # MOSFET connections
                self.graph.add_edge('Drain', 'Gate', component='M1_DG', label='NMOS')
                self.graph.add_edge('Gate', 'Source', component='M1_GS', label='W/L=10')
                
                # Input coupling capacitor
                self.graph.add_edge('Vin', 'Gate', component='Cin', label='Cin: 1μF')
                
                # Output coupling capacitor
                self.graph.add_edge('Drain', 'Vout', component='Cout', label='Cout: 1μF')
                
                # Set node positions manually for a clear visual layout
                self.component_positions = {
                    'VDD': (2, 3),
                    'Drain': (2, 2),
                    'Gate': (1, 1.5),
                    'Source': (2, 1),
                    'GND': (2, 0),
                    'Vin': (0, 1.5),
                    'Vout': (4, 2)
                }
                
            def visualize_circuit(self, 
                                title="Common Source Amplifier Circuit",
                                node_color="lightgreen",
                                node_size=800,
                                edge_color="blue",
                                edge_width=1.5,
                                font_size=10,
                                figsize=(10, 8)):
                
                plt.figure(figsize=figsize)
                
                # Draw nodes
                nx.draw_networkx_nodes(self.graph, self.component_positions, 
                                    node_color=node_color, node_size=node_size)
                
                # Draw edges
                nx.draw_networkx_edges(self.graph, self.component_positions, 
                                    edge_color=edge_color, width=edge_width)
                
                # Draw node labels
                nx.draw_networkx_labels(self.graph, self.component_positions, font_size=font_size)
                
                # Draw edge labels
                edge_labels = {}
                for u, v, data in self.graph.edges(data=True):
                    if 'label' in data and data['label']:
                        edge_labels[(u, v)] = data['label']
                
                nx.draw_networkx_edge_labels(self.graph, self.component_positions, 
                                            edge_labels=edge_labels, font_size=font_size)
                
                plt.title(title)
                plt.axis('off')
                plt.tight_layout()
                plt.show()
                
            def calculate_circuit_values(self):
                # Circuit parameters
                VDD = 5.0  # supply voltage in volts
                RD = 1000  # drain resistor in ohms
                RG1 = 100000  # upper gate resistor in ohms
                RG2 = 100000  # lower gate resistor in ohms
                RS = 200  # source resistor in ohms
                
                # MOSFET parameters (NMOS)
                K = 0.5e-3  # transconductance parameter in A/V^2
                VT = 1.0  # threshold voltage in volts
                
                # Calculate DC bias point
                VG = VDD * RG2 / (RG1 + RG2)  # gate voltage from voltage divider
                
                # Guess initial value for ID
                ID = 1e-3  # initial guess for drain current in amps
                
                # Iteratively solve for the drain current
                for _ in range(10):
                    VS = ID * RS  # source voltage
                    VGS = VG - VS  # gate-source voltage
                    ID_new = K * (VGS - VT)**2 if VGS > VT else 0  # drain current
                    ID = (ID + ID_new) / 2  # update with average for better convergence
                
                # Calculate remaining voltages
                VS = ID * RS  # source voltage
                VGS = VG - VS  # gate-source voltage
                VD = VDD - ID * RD  # drain voltage
                VDS = VD - VS  # drain-source voltage
                
                # Calculate small-signal parameters
                gm = 2 * K * (VGS - VT) if VGS > VT else 0  # transconductance
                gain = -gm * RD  # voltage gain
                
                # Print circuit analysis
                print("DC Analysis:")
                print(f"Gate Voltage (VG): {VG:.2f} V")
                print(f"Source Voltage (VS): {VS:.2f} V")
                print(f"Drain Voltage (VD): {VD:.2f} V")
                print(f"Gate-Source Voltage (VGS): {VGS:.2f} V")
                print(f"Drain-Source Voltage (VDS): {VDS:.2f} V")
                print(f"Drain Current (ID): {ID*1000:.2f} mA")
                print("\nSmall-Signal Analysis:")
                print(f"Transconductance (gm): {gm*1000:.2f} mS")
                print(f"Voltage Gain (Av): {gain:.2f}")

        if __name__ == "__main__":
            # Create circuit visualizer
            visualizer = CircuitVisualizer()
            
            # Create common source amplifier circuit
            visualizer.create_common_source_amplifier()
            
            # Visualize the circuit
            visualizer.visualize_circuit()
            
            # Calculate and print the circuit values
            visualizer.calculate_circuit_values()

                
        
        
        
        """,
    agent=circuit_code_generator
)

# Example of how you would execute the task
"""
# Example call
result = circuit_code_generation_task.execute()
print(result)
"""