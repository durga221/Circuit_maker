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

netlist_generator = Agent(
    role="High-Performance Netlist Generator",
    goal="Convert previous agent's circuit design output into precise, simulator-ready SPICE netlists for PySpice",
    backstory="You're an AI-driven circuit compiler with specialized expertise in translating circuit designs into optimized netlists for simulation environments. You've been trained on thousands of successful MOSFET circuit simulations and understand the nuances of different simulators' syntax requirements. Your netlists are known for their accuracy, completeness, and compatibility with PySpice and other simulation tools. You're meticulous about including all component connections, proper MOSFET model parameters, and simulation directives necessary for accurate analysis.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

netlist_generation_task = Task(
    description=(
        "Generate a complete SPICE netlist from previous agent's circuit design specification:\n\n"
        "1. Extract from previous agent's output:\n"
        "   - Circuit topology\n"
        "   - Component values and connections\n"
        "   - MOSFET parameters\n"
        "   - Simulation requirements\n\n"
        "2. Generate a complete SPICE netlist including:\n"
        "   - Title and descriptive comments\n"
        "   - All components with proper connections and values\n"
        "   - MOSFET models with appropriate parameters\n"
        "   - DC operating point analysis\n"
        "   - AC analysis (if applicable)\n"
        "   - Transient analysis (if applicable)\n"
        "   - Load lines and bias points\n"
        "   - Proper ground references\n"
        "   - Input signal sources with appropriate parameters\n"
        "   - Output measurement nodes clearly labeled\n"
        "   - Detailed comments throughout the netlist\n\n"
        "3. Ensure the netlist follows correct SPICE syntax and is compatible with PySpice\n\n"
        "4. Specify output node(s) for measurement and analysis\n\n"
        "5. Format the netlist with proper indentation and organization\n\n"
        "IMPORTANT: Return ONLY the complete SPICE netlist code as your output."
    ),
    expected_output="A complete, ready-to-run SPICE netlist compatible with PySpice, containing all components, connections, MOSFET models, and simulation directives with proper formatting and commenting, and clearly defined output nodes for measurement.",
    agent=netlist_generator,
)