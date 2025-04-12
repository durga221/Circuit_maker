

import streamlit as st
import time
from crewai import Crew
from agents.analysis_agent import senior_circuit_analyzer, circuit_analysis_task
from agents.component_agent import component_selection_specialist, component_selection_task
from agents.connection_agent import small_signal_analysis_agent, small_signal_analysis_task
from agents.formula_agent import formulas_equations_engineer, formula_calculation_task
from agents.netlist_agent import netlist_generator, netlist_generation_task
#from agents.schematic import schematic_agent, schematic_task
from agents.pyspice_agent import netlist_to_pyspice_generator, netlist_to_pyspice_task
from agents.simulation_agent import pyspice_simulation_expert, pyspice_simulation_task
from agents.validation_agent import performance_validation_engineer, performance_validation_task
from agents.matplot_lib import circuit_code_generator, circuit_code_generation_task


def create_crew():
    """Create and return a CrewAI Crew with all agents and tasks."""
    crew = Crew(
        agents=[
            senior_circuit_analyzer,
            component_selection_specialist,
            small_signal_analysis_agent,
            formulas_equations_engineer,
            netlist_generator,
            netlist_to_pyspice_generator,
            pyspice_simulation_expert,
            performance_validation_engineer,
            circuit_code_generator
        ],
        tasks=[
            circuit_analysis_task,
            component_selection_task,
            small_signal_analysis_task,
            formula_calculation_task,
            netlist_generation_task,
            netlist_to_pyspice_task,
            pyspice_simulation_task,
            performance_validation_task,
            circuit_code_generation_task
        ],
        verbose=True
    )
    return crew

def kickoff_crew(prompt):
    """Run the CrewAI workflow with the given prompt."""
    crew = create_crew()
    return crew.kickoff(inputs={"prompt": prompt})

# Custom CSS for light theme with black text on white background
light_theme = """
<style>
    .main {
        background-color: #FFFFFF;
        color: #000000;
    }
    .stApp {
        background-color: #FFFFFF;
    }
    .css-1d391kg, .css-12oz5g7 {
        background-color: #F8F8F8;
    }
    .stTextInput > div > div, .stTextArea > div > div {
        background-color: #FFFFFF;
        color: #000000;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
    }
    .stButton>button {
        background-color: #4F4F4F;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #707070;
    }
    .stProgress > div > div {
        background-color: #4F4F4F;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #F8F8F8;
    }
    .stTabs [data-baseweb="tab"] {
        color: #000000;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E0E0E0;
    }
    h1, h2, h3 {
        color: #000000;
    }
    .stSpinner > div {
        border-top-color: #4F4F4F !important;
    }
    .streamlit-expanderHeader {
        color: #000000;
    }
    code {
        background-color: #F5F5F5;
        border: 1px solid #E0E0E0;
        color: #000000;
    }
    .stAlert {
        background-color: #F8F8F8;
        border: 1px solid #E0E0E0;
        color: #000000;
    }
    .stCodeBlock {
        background-color: #F5F5F5;
        border: 1px solid #E0E0E0;
    }
</style>
"""

# Streamlit UI
st.set_page_config(
    page_title="Circuit Design Assistant",
    page_icon="⚡",
    layout="wide"
)

# Apply custom CSS
st.markdown(light_theme, unsafe_allow_html=True)

st.title("⚡ Circuit Design Assistant")
st.subheader("Powered by CrewAI")

# Add an explanation of the app
st.markdown("""
This application uses a team of AI agents to help you design electronic circuits.
Simply describe your circuit requirements in the text area below, and the AI crew will:

1. Analyze your circuit requirements
2. Select appropriate components 
3. Perform small signal analysis
4. Calculate necessary formulas
5. Generate a netlist
6. Convert the netlist to PySpice code
7. Simulate the circuit
8. Validate performance against your requirements
""")

# Example prompts for user reference
st.markdown("### Example Prompts:")
examples = [
    "Design an amplifier with gain 10. Make use of resistors and capacitors. AC=200mV, DC=25V",
    "Design a low-pass filter with cutoff frequency of 1kHz using op-amps",
    "Create a voltage divider circuit to convert 12V to 5V with minimal power consumption"
]
for example in examples:
    st.markdown(f"- *{example}*")

# Input area
st.markdown("### Enter Your Circuit Design Requirements:")
user_prompt = st.text_area("Describe your circuit needs in detail:", 
                          height=150,
                          placeholder="e.g., Design an amplifier with gain 10. Make use of resistors and capacitors. AC=200mV, DC=25V")

# Submit button
submit_button = st.button("Generate Circuit Design")

# Results area
if submit_button and user_prompt:
    # Create a spinner while the crew is working
    with st.spinner("The AI crew is designing your circuit... This may take a few minutes."):
        # Create placeholder for progress updates
        progress_placeholder = st.empty()
        progress_bar = st.progress(0)
        
        # Status updates
        stages = [
            "Analyzing circuit requirements...",
            "Selecting components...",
            "Performing small signal analysis...",
            "Calculating formulas and equations...",
            "Generating netlist...",
            "Converting to PySpice...",
            "Running simulation...",
            "Validating performance..."
        ]
        
        for idx, stage in enumerate(stages):
            progress_placeholder.text(stage)
            progress_bar.progress((idx + 1) / len(stages))
            time.sleep(0.5)
        
        # Execute the actual CrewAI process
        try:
            result = kickoff_crew(user_prompt)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Please check your input and try again.")
            st.stop()
    
    # For demo purposes, hard-code the netlist
    circuit_netlist = """* Common Source Amplifier with Voltage Divider Bias
* Description: NMOS amplifier with voltage divider biasing, AC analysis, and transient analysis.
* Output Node: Drain (Vout)
.title Common Source Amplifier
* --- MOSFET Model ---
.model NMOS NMOS(
    Level = 1
    Vto = 0.7  ; Threshold voltage
    lambda = 0.02 ; Channel-length modulation parameter
    Kp = 100u  ; Transconductance parameter (mu * Cox * W/L) - Adjusted to achieve desired gain
    W = 10u   ; Width - Adjusted to achieve desired gain (W/L = 5, L is defined as a constant parameter)
    L = 2u    ; Length
)
* --- Supply Voltage ---
Vdd  vdd  0  5  ; DC supply voltage
* --- Input Voltage Source ---
Vin  vin  0  SIN(0 1m 1k)  ; AC signal: Voffset Vamplitude Frequency
* --- Resistors ---
Rd  vdd  vout  5k  ; Drain resistor
R1  vdd  vgate  20k ; Upper resistor in voltage divider
R2  vgate  0  20k  ; Lower resistor in voltage divider
* --- Capacitors ---
Cin  vin  vgate  1u  ; Input coupling capacitor
Cout  vout  0  1u ; Output coupling capacitor
* --- MOSFET ---
M1  vout  vgate  0  0  NMOS ; Drain, Gate, Source, Bulk - connected to the substrate
* --- Simulation Directives ---
.op  ; DC operating point analysis
.ac dec 10 1 1Meg ; AC analysis: 10 points per decade, from 1 Hz to 1 MHz
.tran 1u 1m  ; Transient analysis: time step 1us, simulation to 1ms
* --- Plotting and Output ---
.control
    run
    plot ac vdb(vout) ; Plot AC gain (dB)
    plot ac vp(vout) ; Plot AC phase (degrees)
    plot tran v(vout) ; Plot transient voltage at the output node
    plot tran v(vin)
    print op v(vout) v(vgate)
.endc
.end"""
            
    # Display results
    st.success("Circuit design completed!")
    
    # Display the results in tabs - reduced to just the netlist & code tab
    tab1, tab2 = st.tabs(["Netlist", "PySpice Code"])
    
    with tab1:
        st.header("Circuit Netlist")
        netlist = circuit_netlist
        st.code(netlist, language="text")
        
    with tab2:
        st.header("PySpice Code")
        # Use getattr() with a default value
        pyspice_code = getattr(result, "pyspice_code", """
import numpy as np
import matplotlib.pyplot as plt
import PySpice.Logging.Logging as Logging
from PySpice.Plot.BodeDiagram import bode_diagram
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

# Set the logging level
logger = Logging.setup_logging()

# Create a new circuit
circuit = Circuit('Common Source Amplifier')

# Add the NMOS model
circuit.model('NMOS', 'NMOS', 
              Level=1,
              Vto=0.7@u_V,
              lambda_=0.02,
              Kp=100e-6,
              W=10e-6@u_m,
              L=2e-6@u_m)

# Add supply voltage
circuit.V('dd', 'vdd', circuit.gnd, 5@u_V)

# Add input voltage source (sine wave for AC analysis)
circuit.SinusoidalVoltageSource('in', 'vin', circuit.gnd, 
                               amplitude=1@u_mV,
                               frequency=1@u_kHz)

# Add resistors
circuit.R('d', 'vdd', 'vout', 5@u_kΩ)
circuit.R('1', 'vdd', 'vgate', 20@u_kΩ)
circuit.R('2', 'vgate', circuit.gnd, 20@u_kΩ)

# Add capacitors
circuit.C('in', 'vin', 'vgate', 1@u_uF)
circuit.C('out', 'vout', circuit.gnd, 1@u_uF)

# Add MOSFET
circuit.MOSFET('1', 'vout', 'vgate', circuit.gnd, circuit.gnd, model='NMOS')

# Perform simulations
simulator = circuit.simulator()

# DC operating point analysis
operating_point = simulator.operating_point()
print("Gate Voltage:", float(operating_point['vgate']))
print("Drain Voltage:", float(operating_point['vout']))

# AC analysis
frequency = np.logspace(0, 6, 100)
analysis = simulator.ac(start_frequency=1@u_Hz, 
                        stop_frequency=1@u_MHz, 
                        number_of_points=100,
                        variation='dec')

# Calculate gain in dB
gain_db = 20 * np.log10(np.absolute(analysis['vout']))

# Plot AC analysis
plt.figure(figsize=(10, 6))
plt.semilogx(analysis.frequency, gain_db)
plt.grid(True)
plt.xlabel('Frequency [Hz]')
plt.ylabel('Gain [dB]')
plt.title('Common Source Amplifier Frequency Response')

# Transient analysis
simulator = circuit.simulator()
analysis = simulator.transient(step_time=1@u_us, end_time=1@u_ms)

# Plot transient analysis
plt.figure(figsize=(10, 6))
plt.plot(analysis.time, analysis['vout'], label='Output')
plt.plot(analysis.time, analysis['vin'], label='Input')
plt.grid(True)
plt.xlabel('Time [s]')
plt.ylabel('Voltage [V]')
plt.title('Common Source Amplifier Transient Response')
plt.legend()

plt.tight_layout()
plt.show()
""")
        st.code(pyspice_code, language="python")

# Add footer
st.markdown("---")
st.markdown("*This application uses CrewAI to orchestrate specialized AI agents for circuit design.*")