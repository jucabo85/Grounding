# Description: This function calculates the cable size based on the short circuit current and the time of fault.

import numpy as np

#Table 1 from IEEE 80 dictionary
table_data = [
["Copper, anealed soft-drawn", "100", "0.00393", "234", "1083", "1.72", "3.4"],
["Copper, anealed hard-drawn", "97", "0.00381", "242", "1084", "1.78", "3.4"],
["Copper-clad steel wire-40", "40", "0.00378", "245", "1084", "4.4", "3.8"],
["Copper-clad steel wire-30", "30", "0.00378", "245", "1084", "5.86", "3.846"],
["Copper-clad steel rod", "17", "0.00378", "245", "1084", "10.1", "3.8"],
["Aluminim-clad steel wire", "20.3", "0.00378", "258", "657", "8.48", "3.561"],
["Steel, 1020", "10.8", "0.0036", "245", "1510", "15.9", "3.8"],
["Stainless-clad steel rod", "9.6", "0.00377", "245", "1400", "17.5", "4.4"],
["Zin-coated steel road", "8.6", "0.0032", "293", "419", "20.10", "3.9"],
["Stainless Steel", "2.4", "0.0013", "749", "1400", "72", "4"],
]
# Create dictionary from table data
table_dict = {row[0]: [float(value) for value in row[1:]] for row in table_data}

# Conductor types and their nominal areas in kcmil and mm2 Dictionary
conductor_areas = {
    "1/0 AWG": {"kcmil": 105.6, "mm²": 53.5, "diameter": 8.25},
    "2/0 AWG": {"kcmil": 133.1, "mm²": 67.4, "diameter": 9.27},
    "3/0 AWG": {"kcmil": 167.8, "mm²": 85.0, "diameter": 10.4},
    "4/0 AWG": {"kcmil": 211.6, "mm²": 107.2, "diameter": 11.7},
    "250 kcmil": {"kcmil": 250, "mm²": 127, "diameter": 14.6},
    "300 kcmil": {"kcmil": 300, "mm²": 152, "diameter": 16.0},
    "350 kcmil": {"kcmil": 350, "mm²": 177, "diameter": 17.3},
    "400 kcmil": {"kcmil": 400, "mm²": 203, "diameter": 18.5},
    "500 kcmil": {"kcmil": 500, "mm²": 253, "diameter": 20.7},
    "600 kcmil": {"kcmil": 600, "mm²": 304, "diameter": 22.7},
    "700 kcmil": {"kcmil": 700, "mm²": 355, "diameter": 23.7},
    "750 kcmil": {"kcmil": 750, "mm²": 380, "diameter": 25.4},
    "1000 kcmil": {"kcmil": 1000, "mm²": 507, "diameter": 29.3}
}

def cable_sizing(cable,short_circuit,time_fault, Temp_amb=40):

    #Calculation of equation
    TCAP_Factor=table_dict[cable][5]*1e-4/(time_fault*table_dict[cable][1]*table_dict[cable][4])
    Ln_fact=np.log((table_dict[cable][2]+table_dict[cable][3])/(table_dict[cable][2]+Temp_amb))

    # print for debbuging
    # print("TCAP_Factor",TCAP_Factor)
    # print("Ln_fact",Ln_fact)
    # print("TCAP_Factor*Ln_fact",TCAP_Factor*Ln_fact/1e-4)

    Area=short_circuit/np.sqrt(TCAP_Factor*Ln_fact) #short_circuit in kA, Area in mm2

    # Convert area to kcmil
    Area_kcmil=Area*197.4/100

    # Finde the closest conductor size
    selected_cable=min(
        (cable_type for cable_type, areas in conductor_areas.items() if areas["kcmil"]>=Area_kcmil),
        key=lambda cable_type: conductor_areas[cable_type]["kcmil"],
        default=None         
    )

    selected_diameter=conductor_areas[selected_cable]["diameter"] if selected_cable else None

    # print("selected_cable",selected_cable)
    # print("selected_diameter",selected_diameter)
    # print("Area",Area)

    return Area, selected_cable, selected_diameter

if __name__ == '__main__':
    funct_restults=cable_sizing("Copper-clad steel wire-30",15,1)
    # cables=funct_restults[0]
    Area=funct_restults[0]
    selected_cable=funct_restults[1]
    selected_diameter=funct_restults[2]

    
    # print(cables)
    # print(cables['Copper-clad steel wire-30'])
    # print(cables['Copper-clad steel wire-30'][1])
    print("Area (mm2)",Area)
    print("Area (kcmil)",Area*197.4/100)
    print(f"Selected Cable: {selected_cable}" )
    print(f"Selected Diameter: {selected_diameter} mm" )