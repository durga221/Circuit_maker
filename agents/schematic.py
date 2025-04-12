from crewai import Agent, Task
import litellm
import os


class GeminiLLM:
    def _init_(self,model_name="google/gemini-2.0-flash-lite" ):
        self.model_name = model_name

    def generate(self, messages):
        response = litellm.completion(
            model=self.model_name,
            messages=messages
        )
        return response.choices[0].message.content
        
    def chat(self, messages):
        return self.generate(messages)



schematic_agent = Agent(
    role="Circuit Schematic Visualizer",
    goal="Create clear, visually appealing circuit schematics from SPICE netlists using matplotlib and networkx",
    backstory="You're an expert in electronic circuit visualization with deep knowledge of both circuit design and data visualization. You specialize in transforming text-based SPICE netlists into intuitive graphical representations. Your visualizations are known for their clarity, accurate component placement, and proper connection routing that helps engineers understand circuit topology at a glance. You have extensive experience with matplotlib and networkx for creating professional-grade circuit diagrams.",
    allow_delegation=False,
    verbose=True,
    llm=GeminiLLM()
)

schematic_task = Task(
    description=(
        
        "1. Parse the SPICE netlist to identify:\n"
        "   - Components (resistors, capacitors, transistors, voltage/current sources)\n"
        "   - Nodes and connections\n"
        "   - Component values\n\n"
        "2. Generate a circuit schematic visualization using matplotlib and networkx:\n"
        "   - Represent resistors as rectangles (color: light blue)\n"
        "   - Represent capacitors as circles (color: light green)\n"
        "   - Represent MOSFETs/transistors with appropriate symbols (color: light orange)\n"
        "   - Represent voltage/current sources with appropriate symbols (color: light red)\n"
        "   - Display component values next to each component\n"
        "   - Draw connections as lines between components\n"
        "   - Highlight ground nodes\n"
        "   - Highlight input and output nodes\n\n"
        "3. Apply a clean layout algorithm to position components logically\n\n"
        "4. Add clear labels for all components and nodes\n\n"
        "5. Include a title showing the circuit type/function\n\n"
        "6. Generate and return Python code that produces this visualization\n\n"
        "IMPORTANT: Your output should ONLY be the complete Python code using matplotlib and networkx that generates the schematic visualization. The code must be fully functional and ready to run."
    ),
    expected_output=(
        "Complete Python code using matplotlib and networkx that parses a SPICE netlist and generates a "
        "visually appealing circuit schematic with proper component representation, connections, and labels. "
        "The code should be fully executable, well-commented, and produce a professional-looking circuit diagram "
        "that accurately reflects the netlist provided."
    ),
    agent=schematic_agent
)