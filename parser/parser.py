import ezdxf
import numpy as np


def line_length(line):
    (x1,y1), (x2,y2) = line
    return np.hypot(x2-x1, y2-y1)

def is_overlapping(line1, line2, tolerance=1e-6):
    (x1,y1), (x2,y2) = line1
    (x3,y3), (x4,y4) = line2

    # Function to check if a point is on the line
    def is_point_on_line(x,y, x1,y1, x2,y2):
        cross_product=(x-x1)*(y2-y1)-(y-y1)*(x2-x1)
        if abs(cross_product) > tolerance: #Is it collinear?
            return False
        dot_product=(x-x1)*(x2-x1)+(y-y1)*(y2-y1)
        if dot_product < 0: #Is it beyond the start of the line?
            return False
        squared_length_line=(x2-x1)**2+(y2-y1)**2
        if dot_product > squared_length_line: #Is it beyond the end of the line?
            return False
        return True
    
    #check if any endpoint of line2 is on line1
    if (is_point_on_line(x3,y3, x1,y1, x2,y2) or
        is_point_on_line(x4,y4, x1,y1, x2,y2) or
        is_point_on_line(x1,y1, x3,y3, x4,y4) or
        is_point_on_line(x2,y2, x3,y3, x4,y4)):
        return True 
    
    return False

# Function to process the dxf file
def  process_dxf(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    lines_list = [] #Stores cables coordinates
    rods_list = []  #stores rods

    # Get cables and rods
    for entity in msp.query('LINE CIRCLE LWPOLYLINE POLYLINE'):
        if entity.dxf.layer.lower()== 'grounding' or entity.dxf.layer.lower() == 'Grounding' or entity.dxf.layer.lower() == 'Grounding':
            # get cables saveds as lines
            if entity.dxftype() == 'LINE':
                lines_list.append([(entity.dxf.start.x,entity.dxf.start.y),(entity.dxf.end.x,entity.dxf.end.y)])

            # get cables saved as polylines
            elif entity.dxftype() in ('LWPOLYLINE', 'POLYLINE'):
                points = list(entity.get_points())

                # print("points", points)
                # print("len(points)", len(points))

                for i in range(len(points) - 1):
                    lines_list.append([(float(points[i][0]), float(points[i][1])),
                                       (float(points[i + 1][0]), float(points[i + 1][1]))])

                # If the polyline is closed, add an additional line
                if entity.is_closed:
                    lines_list.append([(float(points[-1][0]), float(points[-1][1])),
                                       (float(points[0][0]), float(points[0][1]))])
            
            elif entity.dxftype() == 'CIRCLE':
                rods_list.append((float(entity.dxf.center.x),float(entity.dxf.center.y)))

    filtered_lines=lines_list.copy()

    # Remove overlapping lines
    for line in lines_list:
        for line2 in lines_list:
            if line != line2 and is_overlapping(line, line2):
                if line_length(line) < line_length(line2):
                    if line in filtered_lines:
                        filtered_lines.remove(line)
                        break
                              
    return lines_list, rods_list

def convert_units(lines_list, rods_list, unit):
    
    # Define scale factors for each unit
    scale_factors = {
        'mm': 1 / 1000,  # Convert millimeters to meters
        'm': 1,          # Meters remain the same
        'in': 0.0254,    # Convert inches to meters
        'ft': 0.3048     # Convert feet to meters
    }

    # Check if the unit is valid
    if unit not in scale_factors:
        raise ValueError(f"Unsupported unit: {unit}. Supported units are 'mm', 'm', 'in', 'ft'.")

    # Get the scale factor for the given unit
    scale_factor = scale_factors[unit]

    # Convert lines_list to meters
    converted_lines_list = [
        [(x1 * scale_factor, y1 * scale_factor), (x2 * scale_factor, y2 * scale_factor)]
        for (x1, y1), (x2, y2) in lines_list
    ]

    # Convert rods_list to meters
    converted_rods_list = [
        (x * scale_factor, y * scale_factor) for (x, y) in rods_list
    ]

    return converted_lines_list, converted_rods_list



if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    # Assuming lines_list and rods_list are obtained from the process_dxf function
    lines_list, rods_list= process_dxf("Grounding_Test.dxf")
    print("Lines:", lines_list)
    print("Rods:", rods_list)

    lines_list_mm, rods_list_mm= process_dxf("Fig_B2__mm.dxf")
    print("Lines:", lines_list_mm)
    print("Rods:", rods_list_mm)

    lines_list_m = [[(x1 / 1000, y1 / 1000), (x2 / 1000, y2 / 1000)] for (x1, y1), (x2, y2) in lines_list_mm]
    rods_list_m = [(x / 1000, y / 1000) for (x, y) in rods_list_mm]
    print("Lines:", lines_list_m)
    print("Rods:", rods_list_m)

   
