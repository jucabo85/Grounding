import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely.ops import unary_union,polygonize

# line length counter
def line_length(line):
    (x1, y1), (x2, y2) = line
    return np.hypot(x2 - x1, y2 - y1)

def lines_overall_length(lines_list):
    Lines_lengths = [float(line_length(line)) for line in lines_list]
    return sum(Lines_lengths)

def polyg_one(lines_list):
    """
    Create a polygon from the given lines_list. Ensure all lines are considered.
    """
    # Convert lines_list to LineString objects
    line_strings = [LineString(line) for line in lines_list]
    
    # Combine all LineStrings into a MultiLineString
    multi_line = MultiLineString(line_strings)
    
    # Check if the MultiLineString forms a closed polygon
    if not multi_line.is_closed:
        raise ValueError("The lines do not form a closed polygon. Ensure the lines_list is complete and forms a closed loop.")
    
    # Use polygonize to create polygons
    polygons = list(polygonize(multi_line))
    
    if polygons:
        return polygons[0]  # Return the first polygon
    else:
        raise ValueError("The lines do not form a valid polygon.")

# Create a polygon from the lines
def create_polygon_OLD(lines_list):
    line_strings = [LineString(line) for line in lines_list]
    multi_line = unary_union(line_strings)
    polygons = list(polygonize(multi_line))
    if polygons:
        return polygons[0]  # Return the first polygon
    else:
        raise ValueError("The lines do not form a closed polygon")

# Check if three points are collinear
def are_collinear(p1, p2, p3):
    # Calculate the area of the triangle formed by the three points
    # If the area is zero, the points are collinear
    return abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])) < 1e-6

# Simplify the polygon by removing collinear points
def simplify_polygon(polygon):
    coords = list(polygon.exterior.coords)
    simplified_coords = []
    num_vertices = len(coords) - 1  # Exclude the repeated last point

    for i in range(num_vertices):
        p1 = coords[i]
        p2 = coords[(i + 1) % num_vertices]
        p3 = coords[(i + 2) % num_vertices]

        if not are_collinear(p1, p2, p3):
            simplified_coords.append(p1)

    # Add the last point to close the polygon
    simplified_coords.append(simplified_coords[0])
    return Polygon(simplified_coords)

# Calculate the area of the polygon
def total_area_covered(polygon):
    return polygon.area

# Calculate the perimeter of the polygon
def perimeter_covered(polygon):
    return polygon.length

# Calculate the maximum lengths in x and y directions
def max_lengths(polygon):
    bounds = polygon.bounds
    max_length_x = bounds[2] - bounds[0]
    max_length_y = bounds[3] - bounds[1]
    return max_length_x, max_length_y

# Calculate the maximum distance between any two points in the polygon
def max_distance(polygon):
    coords = list(polygon.exterior.coords)
    max_dist = 0
    for i in range(len(coords)):
        for j in range(i + 1, len(coords)):
            dist = np.hypot(coords[j][0] - coords[i][0], coords[j][1] - coords[i][1])
            if dist > max_dist:
                max_dist = dist
    return max_dist

def is_rectangle_or_l_shape(polygon):
    # Simplify the polygon to merge collinear points
    simplified_polygon = polygon.simplify(tolerance=0.01, preserve_topology=True)
    coords = list(simplified_polygon.exterior.coords)
    num_vertices = len(coords) - 1  # Last point is the same as the first point
    
    print("num_vertices", num_vertices)

    print("coords", coords)
            
    # Check for L-shape by analyzing the angles between consecutive edges
    angles = []
    vert_length = []
    for i in range(num_vertices):
        p1 = np.array(coords[i])
        p2 = np.array(coords[(i + 1) % num_vertices])
        p3 = np.array(coords[(i + 2) % num_vertices])
        
        v1 = p2 - p1
        v2 = p3 - p2
        
        vert_length.append(float(np.hypot(v1[0], v1[1])))
        # print("p1", p1)
        # print("p2", p2)
        # print("vert_length", vert_length)

        angle = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
        angle = np.degrees(angle)
        if angle < 0:
            angle += 360
        angles.append(angle)
    
    right_angles = [angle for angle in angles if 80 <= angle <= 100 or 260 <= angle <= 280]

    if len(right_angles) >= 2 and num_vertices != 4:
       # Identify sides for L-shape
        side_lengths = [float(line_length((coords[i], coords[(i + 1) % num_vertices]))) for i in range(num_vertices)]
        
        print("side_lengths",side_lengths)

        # Divide the L-shape into two rectangles
        # Rectangle 1 (Horizontal)
        rect1_sides = [side_lengths[0], side_lengths[2]]

        print("rectangle1_sides",rect1_sides)

        side1 = min(rect1_sides)
        side2 = max(rect1_sides)
        
        # Rectangle 2 (Vertical)
        rect2_sides = [side_lengths[1]-side_lengths[-1], side_lengths[3]]

        print("rectangle2_sides",rect2_sides)

        side3 = min(rect2_sides)
        side4 = max(rect2_sides)

        return "L-shape", side1, side2, side3, side4
    
    # Check for equal opposite sides
    side_lengths = [line_length((coords[i], coords[(i + 1) % num_vertices])) for i in range(num_vertices)]
    if len(right_angles) == 4 and np.isclose(side_lengths[0], side_lengths[2]) and np.isclose(side_lengths[1], side_lengths[3]):
        side_lengths.sort(reverse=True)
        longer_sides = side_lengths[:2]
        shorter_sides = side_lengths[2:]
        side1 = min(longer_sides)
        side2 = min(shorter_sides)
        
        return "Rectangle", side1, side2, None, None

    return "imported", None, None, None, None


def largest_parallel_separation(lines_list):
    """
    Calculate the largest separation between parallel lines in the lines_list.
    """
    # Separate lines into horizontal and vertical groups
    horizontal_lines = []
    vertical_lines = []

    for line in lines_list:
        (x1, y1), (x2, y2) = line
        if np.isclose(y1, y2):  # Horizontal line
            horizontal_lines.append((min(x1, x2), y1, max(x1, x2)))
        elif np.isclose(x1, x2):  # Vertical line
            vertical_lines.append((x1, min(y1, y2), max(y1, y2)))

    # Calculate the largest separation for horizontal lines
    horizontal_separations = []
    for i in range(len(horizontal_lines)):
        for j in range(i + 1, len(horizontal_lines)):
            if horizontal_lines[i][0] <= horizontal_lines[j][2] and horizontal_lines[j][0] <= horizontal_lines[i][2]:
                separation = abs(horizontal_lines[i][1] - horizontal_lines[j][1])
                horizontal_separations.append(separation)

    # Calculate the largest separation for vertical lines
    vertical_separations = []
    for i in range(len(vertical_lines)):
        for j in range(i + 1, len(vertical_lines)):
            if vertical_lines[i][1] <= vertical_lines[j][2] and vertical_lines[j][1] <= vertical_lines[i][2]:
                separation = abs(vertical_lines[i][0] - vertical_lines[j][0])
                vertical_separations.append(separation)

    # Find the largest separation
    max_horizontal_separation = max(horizontal_separations) if horizontal_separations else 0
    max_vertical_separation = max(vertical_separations) if vertical_separations else 0

    return max(max_horizontal_separation, max_vertical_separation)

def plot_polygon(polygon, title):
    x, y = polygon.exterior.xy
    plt.figure()
    plt.plot(x, y, 'o')
    plt.plot(x, y, 'k-')
    plt.title(title)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    
    lines_list_test = [
        [(0, 0), (6, 0)],
        [(6, 0), (6, 2)],
        [(6, 2), (2, 2)],
        [(1,2),(1,1)],
        [(1,1),(2,2)],
        [(1,3),(2,3)],
        [(2, 2), (2, 4)],
        [(2, 4), (0, 4)],
        [(0, 4), (0, 0)]
    ]
    
    pol = create_polygon(lines_list_test)
    print("Area:", total_area_covered(pol))
    print("Perimeter:", perimeter_covered(pol))

    shape, side1, side2, side3, side4 = is_rectangle_or_l_shape(pol)
    print("Shape:", shape)
    print("Side1:", side1)
    print("Side2:", side2)
    print("Side3:", side3)
    print("Side4:", side4)

    plot_polygon(pol, "Polygon 1")

    # lines_list_test1 = [
    #     [(0, 0), (6, 0)],
    #     [(6, 0), (6, 4)],
    #     [(6, 4), (0, 4)],
    #     [(0, 4), (0, 0)],
    # ]
    
    # pol1 = create_polygon(lines_list_test1)
    # print("Area:", total_area_covered(pol1))
    # print("Perimeter:", perimeter_covered(pol1))

    # shape1, side1_1, side2_1, side3_1, side4_1 = is_rectangle_or_l_shape(pol1)
    # print("Shape:", shape1)
    # print("Side1:", side1_1)
    # print("Side2:", side2_1)
    # print("Side3:", side3_1)
    # print("Side4:", side4_1)

    # plot_polygon(pol1, "Polygon 2")

    pass