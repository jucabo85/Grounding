import sys

from parser.parser import process_dxf, convert_units
from calcs.calc_cable_size import cable_sizing
from calcs.calc_tolerables import surface_correction, Etouch, Estep
from calcs.calc_gpr import gpr
from plots.plots import plot_grid_with_lines_and_rods

from calcs.class_grid import GroundingGrid
from calcs.class_geom_etry import Geom_etry

G_grid=None
Geo_Grid=None


# Defining Main calculation function

def ground_grid(filepath, fileunits,conductor_type, short_circuit_conductor,short_circuit, fault_duration, person_weight, cable_depth,
                depth_crushed_rock, ro, ros, ambient_temperature, split_factor, rod_length, rod_diameter, case, override_mesh, parallel_separ, nrods=None):
    
    # Parse the DXF file to get the lines and rods
    lines_list_raw, rods_list_raw = process_dxf(filepath)

    # Scale the lines and rods
    lines_list, rods_list =convert_units(lines_list_raw, rods_list_raw, fileunits)

    # Calculate the effective short-circuit current
    effective_short_circuit = short_circuit * split_factor  # Adjusting for the split factor

    # Instantiate the Geom_etry class
    Geo_Grid = Geom_etry(lines_list,rods_list)
    
    # Calculate the selected cable and cable diameter
    cable_area,selected_cable, cable_diameter=cable_sizing(conductor_type, short_circuit_conductor, fault_duration, 
                                                ambient_temperature)
    
    # Check if the mesh Size wants to be overrrided
    if override_mesh:
        D=parallel_separ
    else:
        D=Geo_Grid.max_separation


    # Call the debugging function for inputs
    # debug_inputs_ground_grid(filepath, lines_list_raw, rods_list_raw, lines_list, rods_list, Geo_Grid, cable_area, selected_cable, cable_diameter, rod_length, effective_short_circuit)     
    # Plot to debug the geometry
    # poly = Geo_Grid.polyg_on
    # plot_grid_with_lines_and_rods(filepath, fileunits, poly, title="Grounding Grid with Lines and Rods")

    # # TODO: Hide this, applicable only for benchmarking purposes
    # cable_diameter=10

    # Instantiate the GroundingGrid class
    G_grid = GroundingGrid(ro, cable_depth, cable_diameter/1000, len(rods_list), rod_length, rod_diameter,
                           case=case, location_rods=Geo_Grid.location_rods, D=D, shape=Geo_Grid.shape,
                            side1=Geo_Grid.side1, side2=Geo_Grid.side2, side3=Geo_Grid.side3, side4=Geo_Grid.side4,
                            A=Geo_Grid.area, Lc=Geo_Grid.line_lengths,Lp=Geo_Grid.perimeter, Dm=Geo_Grid.max_dist,
                            Lx=Geo_Grid.max_length_x, Ly=Geo_Grid.max_length_y)

    # Calculate the grounding grid resistance
    Rg=float(G_grid.Rpt)

    # Calculate the Ground Potential Rise (GPR)
    gpr_value = float(gpr(Rg, effective_short_circuit*1000))

    # Calculate the surface correction factor
    Cs = surface_correction(ro, ros, depth_crushed_rock)

    # Calculate tolerable values
    tolerable_touch = float(Etouch(ros, Cs, fault_duration, weight=person_weight))
    tolerable_step = float(Estep(ros, Cs, fault_duration, weight=person_weight))

    touch_status=""
    step_status=""

    # Compare the calculated GPR with the tolerable values
    if gpr_value > tolerable_touch and gpr_value > tolerable_step:
        pass
    else:
        touch_status="GPR is below the touch and step tolerable limits."
        step_status="GPR is below the touch and step tolerable limits."
        compliance=True
        # print(touch_status)
        results = {
        "Selected Cable": f"{selected_cable}",
        "Cable Diameter": f"{round(cable_diameter, 2)} mm",
        "Conductor Short Circuit": f"{round(short_circuit_conductor, 2)} kA",
        "Short Circuit Current": f"{round(short_circuit, 2)} kA",
        "Current through the grid": f"{round(effective_short_circuit * 1000, 2)} A",
        "Grounding Resistance": f"{round(Rg, 2)} Ohms",
        "GPR": f"{round(gpr_value, 2)} V",
        "Tolerable Touch Voltage": f"{round(tolerable_touch, 2)} V",
        "Tolerable Step Voltage": f"{round(tolerable_step, 2)} V",
        "Compliance": compliance,
        "Step Status": step_status,
        "Touch Status": touch_status,
        }
        return results
        sys.exit(0)


    # Calculate the touch and step potentials
    touch_potential = float(G_grid.Em(effective_short_circuit*1000))  
    step_potential = float(G_grid.Es(effective_short_circuit*1000))

    # Call the output debugging function
    # debug_outputs_ground_grid(G_grid, Rg, touch_potential, step_potential, tolerable_touch, tolerable_step, gpr_value)
    
    # Print the results
    if touch_potential > tolerable_touch:
        touch_status="Warning: Touch potential exceeds tolerable limits!"
        compliance=False
    else:
        touch_status="Touch potential is within tolerable limits."
        compliance=True
    # print(touch_status)

    if step_potential > tolerable_step:
        step_status="Warning: Step potential exceeds tolerable limits!"
        compliance=False
    else:
        step_status="Step potential is within tolerable limits."
    # print(step_status)

    

    results = {
        "Selected Cable": f"{selected_cable}",
        "Cable Diameter": f"{round(cable_diameter, 2)} mm",
        "Conductor Short Circuit": f"{round(short_circuit_conductor, 2)} kA",
        "Short Circuit Current": f"{round(short_circuit, 2)} kA",
        "Current through the grid": f"{round(effective_short_circuit * 1000, 2)} A",
        "Grounding Resistance": f"{round(Rg, 2)} Ohms",
        "GPR": f"{round(gpr_value, 2)} V",
        "Tolerable Touch Voltage": f"{round(tolerable_touch, 2)} V",
        "Tolerable Step Voltage": f"{round(tolerable_step, 2)} V",
        "Touch Voltage": f"{round(touch_potential, 2)} V",
        "Step Potential": f"{round(step_potential, 2)} V",
        "Compliance": compliance,
        "Step Status": step_status,
        "Touch Status": touch_status
    }

    # Formatting the results for better readability


    return results

def debug_inputs_ground_grid(filepath, lines_list_raw, rods_list_raw, lines_list, rods_list, Geo_Grid, cable_area, selected_cable, cable_diameter, rod_length, effective_short_circuit):
    """
    Debugging function to print the intermediate values and results of the ground grid calculation.
    """
    print(f"Filepath: {filepath}")
    print(f"Lines List Raw: {lines_list_raw}")
    print(f"Rods List Raw: {rods_list_raw}")
    print(f"Lines List: {lines_list}")
    print(f"Rods List: {rods_list}")
    print(f"Cable Area: {cable_area}, Selected Cable: {selected_cable}, Cable Diameter: {cable_diameter:.2f} mm")

    # Values to print and debug
    print(f"Largest Horizontal Line: {Geo_Grid.largest_horizontal}")
    print(f"Largest Vertical Line: {Geo_Grid.largest_vertical}")
    print("Shape:", Geo_Grid.shape)
    print("Side 1:", Geo_Grid.side1)
    print("Side 2:", Geo_Grid.side2)
    print("Side 3:", Geo_Grid.side3)
    print("Side 4:", Geo_Grid.side4)
    print("Total Area:", Geo_Grid.area)
    print("Perimeter:", Geo_Grid.perimeter)
    print("Lx (Max Length X):", Geo_Grid.max_length_x)
    print("Ly (Max Length Y):", Geo_Grid.max_length_y)
    print("D (Max Separation):", Geo_Grid.max_separation)
    print("Dm (Max Distance):", Geo_Grid.max_dist)
    print("Cable Diameter:", cable_diameter)
    print("Number of Rods:", len(rods_list))
    print("Lr (Total Rod Length):", rod_length * len(rods_list))
    print("Lc (Total Line Length):", Geo_Grid.line_lengths)
    print("Location of Rods:", Geo_Grid.location_rods)
    print(f"Effective Short-Circuit Current: {effective_short_circuit:.2f} kA")

def debug_outputs_ground_grid(G_grid, Rg, touch_potential, step_potential, tolerable_touch, tolerable_step, gpr_value):
        """
        Output debugging information for the grounding grid calculations.
        """
        print(f"Grounding Grid Resistance (Rg): {Rg:.2f} Ohms")
        print("Rpt.kh:", G_grid.kh)
        print("Rpt.km:", G_grid.km)
        print("Rpt.ki:", G_grid.ki)
        print("Rpt.Kii:", G_grid.kii)
        print("Rpt.Lm:", G_grid.Lm)
        print("Rpt.Lr:", G_grid.LR)
        print("Rpt.Lc:", G_grid.Lc)
        print("Rpt.Lp:", G_grid.Lp)
        print("Rpt.Lx:", G_grid.Lx)
        print("Rpt.Ly:", G_grid.Ly)
        print("Rpt.na:", G_grid.na)
        print("Rpt.nb:", G_grid.nb)
        print("Rpt.nc:", G_grid.nc)
        print("Rpt.nd:", G_grid.nd)
        print("Rpt.ncalc_:", G_grid.ncalc_val)
        print(f"Touch Potential: {touch_potential:.2f} V")
        print(f"Step Potential: {step_potential:.2f} V")
        print(f"Tolerable Touch Potential: {tolerable_touch:.2f} V")
        print(f"Tolerable Step Potential: {tolerable_step:.2f} V")
        print(f"Ground Potential Rise (GPR): {gpr_value:.2f} V")    


if __name__ == '__main__':
    
    # Benchmarking from IEEE 80
    # Example IEEE B1

    # inputs
    filepath = "Fig_B2__mm.dxf"
    fileunits="mm"
    conductor_type = "Copper, anealed soft-drawn"
    short_circuit_conductor = 30.814 # kA
    short_circuit = 3.18  # kA
    fault_duration = 0.5  # seconds
    person_weight = 70  # kg
    cable_depth = 0.5  # meters
    depth_crushed_rock = 0.102  # meters
    ro = 400  # Ohm-m
    ros = 2500  # Ohm-m
    ambient_temperature = 40  # Celsius
    split_factor = 0.6  # Unitless
    rod_length = 7.5 # meters
    rod_diameter = 0.02  # meters
    case="Sverak"
    override_mesh=False
    parallel_separ=8

    

    results = ground_grid(filepath, fileunits, conductor_type, short_circuit_conductor,short_circuit, fault_duration, person_weight, cable_depth,
                          depth_crushed_rock, ro, ros, ambient_temperature, split_factor, rod_length, rod_diameter, case, override_mesh, parallel_separ)

    print("Results:", results)


# Example IEEE B2

# inputs
filepath = "Fig_B2__mm.dxf"
fileunits="mm"
conductor_type = "Copper, anealed soft-drawn"
short_circuit_conductor = 6.814 # kA
short_circuit = 3.18  # kA
fault_duration = 0.5  # seconds
person_weight = 70  # kg
cable_depth = 0.5  # meters
depth_crushed_rock = 0.102  # meters
ro = 400  # Ohm-m
ros = 2500  # Ohm-m
ambient_temperature = 40  # Celsius
split_factor = 0.6  # Unitless
rod_length = 7.5 # meters
rod_diameter = 0.02  # meters
override_mesh=False
parallel_separ=8
case="Sverak"



results = ground_grid(filepath, fileunits, conductor_type, short_circuit_conductor,short_circuit, fault_duration, person_weight, cable_depth,
                        depth_crushed_rock, ro, ros, ambient_temperature, split_factor, rod_length, rod_diameter, case, override_mesh, parallel_separ)

print("Results:", results)


# Example IEEE B3

# inputs
filepath = "Fig_B3__m.dxf"
fileunits="m"
conductor_type = "Copper, anealed soft-drawn"
short_circuit_conductor = 6.814 # kA
short_circuit = 3.18  # kA
fault_duration = 0.5  # seconds
person_weight = 70  # kg
cable_depth = 0.5  # meters
depth_crushed_rock = 0.102  # meters
ro = 400  # Ohm-m
ros = 2500  # Ohm-m
ambient_temperature = 40  # Celsius
split_factor = 0.6  # Unitless
rod_length = 10 # meters
rod_diameter = 0.02  # meters
case="Sverak"



results = ground_grid(filepath, fileunits, conductor_type, short_circuit_conductor,short_circuit, fault_duration, person_weight, cable_depth,
                        depth_crushed_rock, ro, ros, ambient_temperature, split_factor, rod_length, rod_diameter, case, override_mesh, parallel_separ)

print("Results:", results)


# Example IEEE B4

# inputs
filepath = "Fig_B4__mm.dxf"
fileunits="mm"
conductor_type = "Copper, anealed soft-drawn"
short_circuit_conductor = 6.814 # kA
short_circuit = 3.18  # kA
fault_duration = 0.5  # seconds
person_weight = 70  # kg
cable_depth = 0.5  # meters
depth_crushed_rock = 0.102  # meters
ro = 400  # Ohm-m
ros = 2500  # Ohm-m
ambient_temperature = 40  # Celsius
split_factor = 0.6  # Unitless
rod_length = 7.5 # meters
rod_diameter = 0.02  # meters
case="Sverak"



results = ground_grid(filepath, fileunits, conductor_type, short_circuit_conductor,short_circuit, fault_duration, person_weight, cable_depth,
                        depth_crushed_rock, ro, ros, ambient_temperature, split_factor, rod_length, rod_diameter, case, override_mesh, parallel_separ)

print("Results:", results)


