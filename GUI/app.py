
# Importing the necessary libraries
from shiny import render, reactive
from shiny.express import input, ui
from matplotlib import pyplot as plt
from outputs.export_doc import generate_docx

# importing functions from the notebook ---Remove when moving to .py file
# from importnb import Notebook
import pandas as pd
import sys
import os
import ast
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parser.parser import process_dxf
from calcs.calc_cable_size import table_data
from kernel import ground_grid
from plots.plots import plot_grid_with_lines_and_rods

# Extract conductor types (first column of table_data)
conductor_types = {row[0]: row[0] for row in table_data}

# with Notebook():
#     from Main import ground_grid, plot_grid_with_lines_and_rods  #Importing functions from the notebook

# TODO ####### To review the code and implement later ########
# Initialize the list to store cables
# new_cable_list = []
# new_rod_list = []
# app_state = {
#     "add_cable": False,
#     "last_added_cable": None,
#     "add_rod": False,
#     "last_added_rod": None
# }

# # File paths to save the data
# cable_file = os.path.join(os.path.dirname(__file__), 'cables.json')
# rod_file = os.path.join(os.path.dirname(__file__), 'rods.json')
# state_file = os.path.join(os.path.dirname(__file__), 'app_state.json')

# def save_data():
#     with open(cable_file, 'w') as f:
#         json.dump(new_cable_list, f)
#     with open(rod_file, 'w') as f:
#         json.dump(new_rod_list, f)
#     with open(state_file, 'w') as f:
#         json.dump(app_state, f)

# def load_data():
#     global new_cable_list, new_rod_list, app_state
#     if os.path.exists(cable_file):
#         with open(cable_file, 'r') as f:
#             new_cable_list = json.load(f)
#     if os.path.exists(rod_file):
#         with open(rod_file, 'r') as f:
#             new_rod_list = json.load(f)
#     if os.path.exists(state_file):
#         with open(state_file, 'r') as f:
#             app_state = json.load(f)

# # Load data when the app starts
# load_data()

ui.page_opts(title="Grounding Grid Quick Estimator", fillable=True)
with ui.sidebar(title="Main Inputs"):
    ui.input_file("DXF_file", label="Select a DXF file", accept=[".dxf"], multiple=False)
    ui.input_select(
        "Units",
        "DXF Drawing Units",
        {"m":"m","mm":"mm", "in":"in"},	
        )
    

    ui.input_text("Soil_Resistivity","Soil Resistivity (ohm-m)", value=100)
    ui.input_text("Crushed_rock_resistivity","Crushed Rock Resistivity (ohm-m)", value=2500)
    ui.input_text("Crushed_rock_depth", "Crushed Rock depth (m)", value=0.15)

    ui.input_select(
        "Conductor_Type",
        "Conductor Type",
        conductor_types,  # Use the dynamically extracted conductor types
    )

    ui.input_text("Short_Circuit_Sizing", "Short Circuit for Conductor Sizing (kA)", value=20)
    ui.input_text("Short_Circuit", "Short Circuit for GPR (kA)", value=20)
    ui.input_text("Split_Factor","Split Factor (-)", value=1)
    ui.input_text("Fault_duration","Fault Duration (s)", value=0.5)
    ui.input_select(
        "Person_Weight",
        "Person Weight (kg)",
        {"50":"50","70":"70"},
        )
    ui.input_text("Depth","Burying Depth (m)", value=0.45)
    ui.input_text("Rod_lenght","Rod Length (m)", value=3)
    ui.input_text("Rod_diameter","Rod Diameter (mm)", value=0.015875)
    ui.input_checkbox("Advanced_Options", "Advanced Options", False)
    with ui.panel_conditional("input.Advanced_Options"):
        ui.input_select("Rpt_model", "Grounding Resistance Model", {"Sverak": "Sverak", "Schwarz": "Schwarz", "Simplified 1": "Simplified 1", "Simplified 2": "Simplified 2"}, selected="Sverak")
        ui.input_text("Ambient_temp", "Ambient Temperature (Celsius)", value=40)

with ui.layout_column_wrap(width=1/2):

    with ui.card(title="Grounding Grid Quick Estimator", full_screen=False, width=1/4):
        ui.input_action_button("Calculate", "Calculate Grounding")

        # Download "button"
        @render.download(label="Download Output", filename="results.docx")
        # @reactive.event(input.Calculate, input.DXF_file)
        def download_results():
            # Proceed with generating the file for download
            a, b, c = Calc_results()
            
            if a is None and b is None and c is None:
                a={"No results available": "No results available"}
                b={"No results available": "No results available"}
                c={"No results available": "No results available"}
                
            df1, df2 = results_to_pd(a, b)
            path = generate_docx(df1, df2, c, filename="results.docx")
            with open(path, "rb") as f:
                yield f.read()

        @render.ui
        @reactive.event(input.Calculate, input.DXF_file, input.Units, ignore_init=False)
        def showing_results_markdown():
            if not input.DXF_file():
                return ui.markdown("""No DXF file uploaded\nPlease upload a file to view results.""")
            else:
                resultsx, _, _ = Calc_results()
                if resultsx:
                    last_two_entries = list(resultsx.items())[-3:]
                    compliance= last_two_entries[0][1]
                    first_entry=last_two_entries[1]
                    second_entry=last_two_entries[2]

                    # Format the first entry for display
                    if compliance is False:
                        # Print first_entry in red if compliance is False
                        formatted_result2 = f'<span style="color: red; font-weight: bold;">**{second_entry[0]}:** {second_entry[1]}</span>'
                    else:
                        # Print first_entry normally if compliance is True
                        formatted_result2 = f"**{second_entry[0]}:** {second_entry[1]}"
                    formatted_result1 = f"**{first_entry[0]}:** {first_entry[1]}"

                    
                    # Return the formatted result as Markdown
                    return ui.markdown(f"### Result \n{formatted_result2} <br> {formatted_result1}")
                else:
                    return ui.markdown("### No results available")


    with ui.card(title="Results", full_screen=False):
        # Show the column_wrap only if a DXF file is uploaded
        # with ui.panel_conditional("input.DXF_file"):
        with ui.layout_column_wrap(width=1/2):  # Use column wrap to display cards in parallel
            with ui.card(title="Results1", full_screen=False, width=1/4, height="400px"):
                @render.data_frame
                @reactive.event(
                    input.Calculate,
                    input.DXF_file,
                    input.Units,
                    input.Soil_Resistivity,
                    input.Crushed_rock_resistivity,
                    input.Crushed_rock_depth,
                    input.Conductor_Type,
                    input.Short_Circuit_Sizing,
                    input.Short_Circuit,
                    input.Split_Factor,
                    input.Fault_duration,
                    input.Person_Weight,
                    input.Depth,
                    input.Rod_lenght,
                    input.Rod_diameter,
                    input.Advanced_Options,
                    input.Rpt_model,
                    input.Ambient_temp,
                    ignore_init=True,
                )
                def showing_results1():
                    resultsx,filepath,_= Calc_results()
                    results1,_=results_to_pd(resultsx, filepath)
                    return results1

            with ui.card(title="Results2", full_screen=False, width=1/4, height="400px"):
                @render.data_frame
                @reactive.event(
                    input.Calculate,
                    input.DXF_file,
                    input.Units,
                    input.Soil_Resistivity,
                    input.Crushed_rock_resistivity,
                    input.Crushed_rock_depth,
                    input.Conductor_Type,
                    input.Short_Circuit_Sizing,
                    input.Short_Circuit,
                    input.Split_Factor,
                    input.Fault_duration,
                    input.Person_Weight,
                    input.Depth,
                    input.Rod_lenght,
                    input.Rod_diameter,
                    input.Advanced_Options,
                    input.Rpt_model,
                    input.Ambient_temp,
                    ignore_init=True,
                )
                def showing_results2():
                    resultsx,filepath,_= Calc_results()
                    _,results2=results_to_pd(resultsx, filepath)
                    # Exclude the last entry of results2
                    results2 = results2.iloc[:-1]  # Remove the last row
                    return results2


with ui.card(full_screen=False, fill=True):
    @render.plot
    @reactive.event(input.Calculate, input.DXF_file, input.Units)
    def render_plot_grid():
        print(f"DXF File Input: {input.DXF_file()}")

        if not input.DXF_file():
            print("No file uploaded.")
            return None
        
        filepath = input.DXF_file()[0]["datapath"] if input.DXF_file() else None  # Path to the uploaded DXF file
        fileunits = input.Units()  # DXF Drawing Units
        print(f"File Units: {fileunits}")

        if not filepath:
            return None
        
        fig = plot_grid_with_lines_and_rods(filepath, fileunits)            

        return fig
    
# TODO Later ###Input additional rods and cables    
    # ui.input_switch("Add_cable", "Add Cable", app_state["add_cable"])
    # with ui.panel_conditional("input.Add_cable"):
    #     ui.input_text("Start_point", "Start Point", "(0,0)")
    #     ui.input_text("End_point", "End Point", "(0,0)")
    #     ui.input_action_button("Add_cable_button", "Add Cable")


    # ui.input_switch("Add_rod", "Add Rod", app_state["add_rod"])
    # with ui.panel_conditional("input.Add_rod"):
    #     ui.input_text("Coordinates", "Coordinates", "(0,0)")
    #     ui.input_action_button("Add_rod_button", "Add Rod")

    # with ui.accordion():
    #     with ui.accordion_panel("Delete Buttons"):
    #         ui.input_action_button("Delete_cables", "Delete Cables")
    #         ui.input_action_button("Delete_rods", "Delete Rods")

@reactive.effect
def units():
    selected_unit = input.Units()

    # Conversion dictionary for units
    unit_conversion = {
        "m": ("meters","m", "m", 1.0, 1),  # 1 meter = 1 meter
        "mm": ("millimeters","mm", "m", 0.001, 1.0),  # 1 mm = 0.001 meters
        "in": ("inches", "in", "in",  0.0254, 0.0254),  # 1 inch = 0.0254 meters
    }
    _,unit_label,unit_label_SI, conversion_factor, conversion_factor_SI = unit_conversion[selected_unit]
    ui.update_text("Crushed_rock_depth", label=f"Crushed Rock depth ({unit_label_SI})", value=round(0.15/conversion_factor_SI,1))
    ui.update_text("Depth",label=f"Burying Depth ({unit_label_SI})", value=round(0.45/conversion_factor_SI,2))
    ui.update_text("Rod_lenght",label=f"Rod Length ({unit_label_SI})", value=round(3/conversion_factor_SI,2))
    ui.update_text("Rod_diameter",label=f"Rod Diameter ({unit_label_SI})", value=round(0.015875/conversion_factor_SI,4))

    



# Functions definitions

def Calc_results():
    filepath = input.DXF_file()[0]["datapath"] if input.DXF_file() else None  # Path to the uploaded DXF file
    fileunits = input.Units()  # DXF Drawing Units
    conductor_type = input.Conductor_Type()  # Conductor Type
    short_circuit_conductor = float(input.Short_Circuit_Sizing())  # Short Circuit Current for the conductor (kA)
    short_circuit = float(input.Short_Circuit())   # Short circuit (kA)
    fault_duration = float(input.Fault_duration())  # Fault Duration (seconds)
    person_weight = float(input.Person_Weight())  # Person Weight (kg)
    cable_depth = float(input.Depth())  # Burying Depth (meters)
    depth_crushed_rock = float(input.Crushed_rock_depth())  # Crushed Rock Depth (meters)
    ro = float(input.Soil_Resistivity())  # Soil Resistivity (Ohm-m)
    ros = float(input.Crushed_rock_resistivity())  # Crushed Rock Resistivity (Ohm-m)
    ambient_temperature = 40  # Ambient Temperature (Celsius) - hardcoded as per the example
    split_factor = float(input.Split_Factor())  # Split Factor
    rod_length = float(input.Rod_lenght())  # Rod Length (meters)
    rod_diameter = float(input.Rod_diameter())  # Rod Diameter (meters)
    case = input.Rpt_model() if input.Advanced_Options() else "Sverak"  # Grounding Resistance Model

    # Ensure filepath is provided
    if not filepath:
        results={}
        return results, filepath, None
    
    inputs_collection=(filepath, fileunits, conductor_type, short_circuit_conductor, short_circuit, fault_duration, person_weight,cable_depth, depth_crushed_rock, ro, ros, ambient_temperature, split_factor, rod_length,rod_diameter,case)
    inputs_dict = {
    "Filepath": inputs_collection[0],
    "DXF Drawing Units": inputs_collection[1],
    "Conductor Type": inputs_collection[2],
    "Conductor Short Circuit": f"{inputs_collection[3]} kA",
    "Short Circuit Current": f"{inputs_collection[4]} kA",
    "Fault Duration": f"{inputs_collection[5]} seconds",
    "Person Weight": f"{inputs_collection[6]} kg",
    "Split Factor": inputs_collection[12],
    "Soil Resistivity": f"{inputs_collection[9]} Ohm-m",
    "Crushed Rock Resistivity": f"{inputs_collection[10]} Ohm-m",
    "Crushed Rock Depth": f"{inputs_collection[8]} meters",
    "Conductors Depth": f"{inputs_collection[7]} meters",
    "Rods Length": f"{inputs_collection[13]} meters",
    "Rods Diameter": f"{inputs_collection[14]} meters",
    "Ambient Temperature": f"{inputs_collection[11]} °C",
    "Grounding Resistance Model": inputs_collection[15],
    }

    # Call the ground_grid function
    results = ground_grid(
        filepath, fileunits, conductor_type, short_circuit_conductor, short_circuit,
        fault_duration, person_weight, cable_depth, depth_crushed_rock, ro, ros,
        ambient_temperature, split_factor, rod_length, rod_diameter, case
    )
    # Format the results for display in a tabulated way ---- TEXT----
    # formatted_results = "\n".join([f"{key:<30}: {value}" for key, value in results.items()])
    # return f"Calculation Results:\n{formatted_results}"

    return results, filepath, inputs_dict

    # print("tabledata",table_data)
    # return table_data

def results_to_pd(results, filepath):

    # Ensure filepath is provided
    if not filepath:
        # Return empty DataFrames for both parts
        empty_df = pd.DataFrame([])
        return empty_df, empty_df
    
    # format the results for table display
    table_data = []
    table_data=pd.DataFrame([{"Parameter": key, "Value": value} for key, value in results.items()])

    table_data = table_data.iloc[:-2]  # Exclude the last two rows

    # Split the DataFrame into two parts
    table_part1 = table_data.iloc[:6]  # First 6 rows
    table_part2 = table_data.iloc[6:]  # Remaining rows

    return table_part1, table_part2    

def plot_grid():
    
    lines_list, rods_list = process_dxf('Grounding_Test.dxf')

    plt.figure()

     #plot cables
    for line in lines_list:
        x,y = zip(*line)
        plt.plot(x,y, 'k')

    #plot rods
    for rod in rods_list:
        plt.plot(rod[0], rod[1], 'ro')

    #TODO
    # # Plot new cables in red
    # for line in new_cable_list:
    #     x, y = zip(*line)
    #     plt.plot(x, y, color='red')

    # # Plot new rods in red
    # for rod in new_rod_list:
    #     plt.plot(rod[0], rod[1], color='blue')


#TODO ### Functions to add componentes. 

# @reactive.Effect
# def render_add_cable():
#     return add_cable()

# @reactive.Effect
# def render_add_rod():
#     return add_rod()

# @reactive.event(input.Delete_cables)
# def render_delete_cables():
#     delete_cables()

# @reactive.event(input.Delete_rods)
# def render_delete_rods():
#     print("Delete Rods within the reactive event")
#     delete_rods()


#TODO ##Funtions to review and implement later to add cables and rods from the interface
def add_cable():
    if input.Add_cable_button():
        start_point = ast.literal_eval(input.Start_point())
        end_point = ast.literal_eval(input.End_point())
        new_cable_list.append([start_point, end_point])
        app_state["add_cable"] = input.Add_cable()
        app_state["last_added_cable"] = [start_point, end_point]
        save_data()
        plot_grid()

def add_rod():
    if input.Add_rod_button():
        coordinates = ast.literal_eval(input.Coordinates())
        new_rod_list.append(coordinates)
        app_state["add_rod"] = input.Add_rod()
        app_state["last_added_rod"] = coordinates
        save_data()
        plot_grid()

def delete_cables():
    if input.Delete_cables():
        print("Delete Rods within the delete cables event")
        new_cable_list.clear()
        app_state["last_added_cable"] = None
        with open(cable_file, 'w') as f:
            json.dump([], f)
        save_data()
        plot_grid()

def delete_rods():  
    if input.Delete_rods():
        new_rod_list.clear()
        app_state["last_added_rod"] = None
        with open(rod_file, 'w') as f:
            json.dump([], f)
        save_data()
        plot_grid()



