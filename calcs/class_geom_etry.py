import numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, Point

import matplotlib.pyplot as plt

class Geom_etry():
    def __init__(self,lines_list, rods_list):
        self.lines_list = lines_list
        self.rods_list = rods_list
        self.side1=None
        self.side2=None
        self.side3=None
        self.side4=None
        self.hull = None
        self.area=None
        self.line_lengths=None
        self.horizontal_lines = []
        self.vertical_lines = []
        self.largest_horizontal = ()
        self.largest_vertical = ()
        self.lines_overall_length()
        self.sort_lines()
        self.polyg_one()
        self.convex_hull_to_polygon()
        self.largest_two_lines()
        self.is_rectangle_or_l_shape()
        self.calculate_polygon_area()
        self.perimeter_covered()
        self.max_lengths()
        self.max_distance()
        self.largest_parallel_separation()
        self.check_rods_location()

    # Calculate the overall length of all lines
    def lines_overall_length(self):
        Lines_lengths = [float(line_length(line)) for line in self.lines_list]
        self.line_lengths=sum(Lines_lengths)

    # Defining the outer polygon covered by the lines 
    def polyg_one(self):
        # Extract all points from the lines
        points = np.array([point for line in self.lines_list for point in line])
        
        # Compute the convex hull
        self.hull = ConvexHull(points)

    def convex_hull_to_polygon(self):
        """
        Convert a ConvexHull object to a Shapely Polygon.
        """
        hull_points = np.roll(self.hull.points[self.hull.vertices], -1, axis=0)
        # print("hull_points",hull_points)
        self.polyg_on= Polygon(hull_points)

    def sort_lines(self):
        # Sort horizontal and vertical lines from left to right and bottom to top
        self.horizontal_lines = []
        self.vertical_lines = []

        for line in self.lines_list:
            (x1, y1), (x2, y2) = line
            if np.isclose(y1, y2):  # Horizontal line
                self.horizontal_lines.append((min(x1, x2), y1, max(x1, x2)))
            elif np.isclose(x1, x2):  # Vertical line
                self.vertical_lines.append((x1, min(y1, y2), max(y1, y2)))

        # Sort lines by their x-y coordinate if they are horizontal or vertical
        self.horizontal_lines.sort(key=lambda line: line[1])
        self.vertical_lines.sort(key=lambda line: line[0])


    def largest_two_lines(self):
    
        # Calculate lengths of horizontal lines
        self.horizontal_lengths = [line[2] - line[0] for line in self.horizontal_lines]

        # Calculate lengths of vertical lines
        self.vertical_lengths = [line[2] - line[1] for line in self.vertical_lines]

        # Sort lengths in descending order
        self.horizontal_lengths.sort(reverse=True)
        self.vertical_lengths.sort(reverse=True)

        # Find the two largest horizontal lengths
        self.largest_horizontal = [self.horizontal_lengths[0]] if self.horizontal_lengths else []
        for length in self.horizontal_lengths[1:]:
            if abs(length - self.largest_horizontal[0]) > 0.1 * self.largest_horizontal[0]:
                self.largest_horizontal.append(length)
                break
        self.largest_horizontal = tuple(self.largest_horizontal[:2])

        # Find the two largest vertical lengths
        self.largest_vertical = [self.vertical_lengths[0]] if self.vertical_lengths else []
        for length in self.vertical_lengths[1:]:
            if abs(length - self.largest_vertical[0]) > 0.1 * self.largest_vertical[0]:
                self.largest_vertical.append(length)
                break
        self.largest_vertical = tuple(self.largest_vertical[:2])

    def create_l_polygon(self):

        # First vertex: Start point of the first horizontal line
        v1 = (self.horizontal_lines[0][0], self.horizontal_lines[0][1])

        # Second vertex: End point of the first horizontal line
        v2 = (self.horizontal_lines[0][2], self.horizontal_lines[0][1])

        # Third vertex: Same x as v2, y = y of v2 + second value in largest_vertical
        v3 = (v2[0], v2[1] + self.largest_vertical[1])

        # Fourth vertex: Same y as v3, x = x of v3 - difference between largest_horizontal values
        v4 = (v3[0] - abs(self.largest_horizontal[0] - self.largest_horizontal[1]), v3[1])

        # Fifth and sixth vertices: Points of the final vertical line
        v5 = (self.vertical_lines[-1][2], self.vertical_lines[-1][0]+self.largest_vertical[1])
        v6 = (self.vertical_lines[-1][1], self.vertical_lines[-1][0]+self.largest_vertical[1])
        vertices=[v1,v2,v3,v4,v5,v6]

        # Print the vertices for debugging
        # print(f"Polygon Vertices: {vertices}")
        
        # Create the polygon using Shapely
        self.l_polygon = Polygon(vertices)
        self.polyg_on = self.l_polygon

        # Calculate the sides
        self.side1=self.largest_horizontal[0]
        self.side2=self.largest_vertical[1]
        self.side3=self.largest_horizontal[1]
        self.side4=self.largest_vertical[0]-self.largest_vertical[1]

    def is_rectangle_or_l_shape(self):
        hull_points = self.hull.points[self.hull.vertices]
        num_vertices = len(hull_points)
        
        # print("hull_points",hull_points)
                
        # Check for L-shape by analyzing the angles between consecutive edges
        angles = []
        vert_length=[]
        for i in range(num_vertices):
            p1 = hull_points[i]
            p2 = hull_points[(i + 1) % num_vertices]
            p3 = hull_points[(i + 2) % num_vertices]
            
            v1 = p2 - p1
            v2 = p3 - p2
            
            vert_length.append(float(np.hypot(v1[0], v1[1])))
            # print("p1",p1)
            # print("p2",p2)
            # print("vert_length",vert_length)

            # print("p1",p1)
            # print("p2",p2)
            # print("p3",p3)

            angle = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
            angle = np.degrees(angle)
            if angle < 0:
                angle += 360
            angles.append(angle)
        
        right_angles = [angle for angle in angles if 80 <= angle <= 100 or 260 <= angle <= 280]

        if len(right_angles) >= 2 and num_vertices != 4:
            # Identify sides for L-shape
            side_lengths = [line_length((hull_points[i], hull_points[(i + 1) % num_vertices])) for i in range(num_vertices)]
            side_lengths.sort(reverse=True)
            self.side1, self.side2, self.side3, self.side4 = side_lengths[:4]
            self.shape= "L"
            self.create_l_polygon()


              
        # Check for equal opposite sides, rectangular shape
        side_lengths = [line_length((hull_points[i], hull_points[(i + 1) % num_vertices])) for i in range(num_vertices)]
        if len(right_angles) == 4 and np.isclose(side_lengths[0], side_lengths[2]) and np.isclose(side_lengths[1], side_lengths[3]):
            side_lengths.sort(reverse=True)
            self.side1, self.side2 = side_lengths[1],side_lengths[3]
            self.shape = "rectangle"

        return "imported", None, None, None, None

    def calculate_polygon_area(self):
        if self.polyg_on:

            # Shapely area
            shapely_area = self.polyg_on.area

            self.area = shapely_area
        else:
            raise ValueError("Polygon (polyg_on) has not been created yet.")
        
    def perimeter_covered(self):
        if self.polyg_on:
            # Shapely perimeter
            shapely_perimeter = self.polyg_on.length
            self.perimeter = shapely_perimeter

        else:
            raise ValueError("Polygon (polyg_on) has not been created yet.")
    
    # Calculate the maximum lengths in the x and y directions for a Shapely Polygon.
    def max_lengths(self):
        
        # Extract the exterior coordinates of the polygon
        x_coords, y_coords = zip(*self.polyg_on.exterior.coords)

        # Calculate the maximum lengths in x and y directions
        self.max_length_x = max(x_coords) - min(x_coords)
        self.max_length_y = max(y_coords) - min(y_coords)

    # Calculate the maximum distance between any two points in a Shapely Polygon.
    def max_distance(self):
    
        # Extract the exterior coordinates of the polygon
        points = list(self.polyg_on.exterior.coords)

        # Calculate the maximum distance between any two points
        max_dist = 0
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                dist = np.hypot(points[j][0] - points[i][0], points[j][1] - points[i][1])
                if dist > max_dist:
                    max_dist = dist
        self.max_dist= max_dist

    # Calculate the largest separation between parallel lines that are next to each other in the lines_list
    def largest_parallel_separation(self):

        # Helper function to calculate the separation between two parallel lines
        def separation_between_lines(line1, line2, is_horizontal):
            if is_horizontal:
                return abs(line1[1] - line2[1])  # Difference in y-coordinates
            else:
                return abs(line1[0] - line2[0])  # Difference in x-coordinates

        
        # Find the largest separation between sorted horizontal lines
        max_horizontal_separation = 0
        for i in range(len(self.horizontal_lines) - 1):
            separation = separation_between_lines(self.horizontal_lines[i], self.horizontal_lines[i + 1], is_horizontal=True)
            self.max_horizontal_separation = max(max_horizontal_separation, separation)

        # Find the largest separation between sorted vertical lines
        max_vertical_separation = 0
        for i in range(len(self.vertical_lines) - 1):
            separation = separation_between_lines(self.vertical_lines[i], self.vertical_lines[i + 1], is_horizontal=False)
            self.max_vertical_separation = max(max_vertical_separation, separation)

        # Return the largest separation among parallel lines that are next to each other
        self.max_separation=max(self.max_horizontal_separation, self.max_vertical_separation)

    # Check if the points in the rods_list are located in or near the perimeter of the polygon.
    def check_rods_location(self):
        
        if not self.rods_list:
            self.location_rods = "no"
            return self.location_rods

        if not self.polyg_on:
            raise ValueError("Polygon (polyg_on) has not been created yet.")

        # Define a buffer around the polygon's perimeter with a tolerance of 3 meters
        perimeter_buffer = self.polyg_on.buffer(3)

        # Check each rod's location
        rods_near_perimeter = 0
        for rod in self.rods_list:
            rod_point = Point(rod)
            if perimeter_buffer.contains(rod_point):
                rods_near_perimeter += 1

        # Determine the location of the rods
        if rods_near_perimeter > 0:
            self.location_rods = "perimeter"
        else:
            self.location_rods = "non_perimeter"



# line length counter
def line_length(line):
    (x1,y1), (x2,y2) = line
    return np.hypot(x2-x1, y2-y1)


def plot_polygon(hull, title):
    hull_points = hull.points[hull.vertices]
    plt.figure()
    plt.plot(hull_points[:, 0], hull_points[:, 1], 'o')
    for simplex in hull.simplices:
        plt.plot(hull.points[simplex, 0], hull.points[simplex, 1], 'k-')
    plt.title(title)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    
    Lines_List_test2= [[(84.00000000000001, 0.0), (84.00000000000001, 63.0)], 
                      [(77.00000000000001, 4e-16), (77.00000000000001, 63.0)], 
                      [(70.00000000000001, 9e-16), (70.00000000000001, 63.0)], 
                      [(63.00000000000001, 1.3e-15), (63.00000000000001, 63.0)], 
                      [(56.00000000000001, 1.7e-15), (56.00000000000001, 63.0)], 
                      [(49.00000000000002, 2.1e-15), (49.00000000000002, 63.0)], 
                      [(42.00000000000001, 2.6e-15), (42.00000000000001, 63.0)], 
                      [(35.00000000000002, 3e-15), (35.00000000000002, 63.0)], 
                      [(28.00000000000002, 3.4e-15), (28.00000000000002, 63.0)], 
                      [(84.00000000000001, 0.0), (1.42e-14, 5.1e-15)], 
                      [(84.00000000000001, 7.0), (1.42e-14, 7.000000000000005)], 
                      [(84.00000000000001, 14.0), (1.42e-14, 14.0)], 
                      [(84.00000000000001, 21.0), (1.42e-14, 21.0)], 
                      [(84.00000000000001, 28.0), (1.42e-14, 28.00000000000001)], 
                      [(84.00000000000001, 35.0), (1.42e-14, 35.00000000000001)], 
                      [(84.00000000000001, 42.0), (1.42e-14, 42.00000000000001)], 
                      [(84.00000000000001, 49.0), (1.42e-14, 49.00000000000001)], 
                      [(84.00000000000001, 56.0), (1.42e-14, 56.00000000000001)], 
                      [(84.00000000000001, 63.0), (1.42e-14, 63.0)], 
                      [(1.42e-14, 63.0), (1.42e-14, 5.1e-15)], 
                      [(21.00000000000001, 3.9e-15), (21.00000000000002, 63.0)], 
                      [(14.00000000000001, 4.3e-15), (14.00000000000001, 63.0)], 
                      [(7.000000000000014, 4.7e-15), (7.000000000000014, 63.0)]]
    
    Class_geom=Geom_etry(Lines_List_test2)

    # print("Class_geom.horizontal_lines",Class_geom.horizontal_lines)
    # print("Class_geom.vertical_lines",Class_geom.vertical_lines)
    # print("Class_geom.largest_horizontal",Class_geom.largest_horizontal)
    # print("Class_geom.largest_vertical",Class_geom.largest_vertical)
    # print("Class_geom.side1",Class_geom.side1)
    # print("Class_geom.side2",Class_geom.side2)
    # print("Class_geom.side3",Class_geom.side3)
    # print("Class_geom.side4",Class_geom.side4)
    # print("Class_geom.shape",Class_geom.shape)
    # print("Class_geom.polyg_on",Class_geom.polyg_on)
    # print("Class_geom.area",Class_geom.area)
    # print("Class_geom.perimeter",Class_geom.perimeter)
    # print("Class_geom.max_length_x",Class_geom.max_length_x)
    # print("Class_geom.max_length_y",Class_geom.max_length_y)
    # print("Class_geom.max_dist",Class_geom.max_dist)
    # print("Class_geom.max_separation",Class_geom.max_separation)


    Lines_List_test= [[(0.0, 105.0), (0.0, 0.0)],
                    [(0.0, 0.0), (70.0, 0.0)],
                    [(70.0, 0.0), (70.0, 35.0)],
                    [(0.0, 7.0), (70.0, 7.0)],
                    [(63.0, 0.0), (63.0, 35.0)],
                    [(35.0, 63.0), (0.0, 63.0)],
                    [(7.0, 105.0), (7.0, 0.0)], 
                    [(35.0, 56.0), (0.0, 56.0)], 
                    [(35.0, 49.0), (0.0, 49.0)], 
                    [(35.0, 42.0), (0.0, 42.0)], 
                    [(70.0, 35.0), (0.0, 35.0)], 
                    [(70.0, 28.0), (0.0, 28.0)], 
                    [(70.0, 21.0), (0.0, 21.0)], 
                    [(70.0, 14.0), (0.0, 14.0)], 
                    [(14.0, 105.0), (14.0, 0.0)], 
                    [(21.0, 105.0), (21.0, 0.0)], 
                    [(28.0, 105.0), (28.0, 0.0)], 
                    [(35.0, 105.0), (35.0, 0.0)], 
                    [(42.0, 35.0), (42.0, 0.0)], 
                    [(49.0, 35.0), (49.0, 0.0)], 
                    [(56.0, 35.0), (56.0, 0.0)], 
                    [(35.0, 91.0), (0.0, 91.0)], 
                    [(35.0, 84.0), (0.0, 84.0)], 
                    [(35.0, 77.0), (0.0, 77.0)], 
                    [(35.0, 70.0), (0.0, 70.0)], 
                    [(35.0, 105.0), (0.0, 105.0)], 
                    [(35.0, 98.0), (0.0, 98.0)]]
    
    Class_geom1=Geom_etry(Lines_List_test)

    # print("Class_geom.horizontal_lines",Class_geom1.horizontal_lines)
    # print("Class_geom.vertical_lines",Class_geom1.vertical_lines)
    # print("Class_geom.largest_horizontal",Class_geom1.largest_horizontal)
    # print("Class_geom.largest_vertical",Class_geom1.largest_vertical)
    # print("Class_geom.side1",Class_geom1.side1)
    # print("Class_geom.side2",Class_geom1.side2)
    # print("Class_geom.side4",Class_geom1.side4)
    # print("Class_geom.shape",Class_geom1.shape)
    # print("Class_geom.polyg_on",Class_geom1.polyg_on)
    # print("Class_geom.area",Class_geom1.area)
    # print("Class_geom.perimeter",Class_geom1.perimeter)
    # print("Class_geom.max_length_x",Class_geom1.max_length_x)
    # print("Class_geom.max_length_y",Class_geom1.max_length_y)
    # print("Class_geom.max_dist",Class_geom1.max_dist)
    # print("Class_geom.max_separation",Class_geom1.max_separation)

    # lines_list_test = [
    #     [(0, 0), (4, 0)],
    #     [(4, 0), (4, 2)],
    #     [(4, 2), (2, 2)],
    #     [(2, 2), (2, 4)],
    #     [(2, 4), (0, 4)],
    #     [(0, 4), (0, 0)]
    # ]
    
    # pol = polyg_one(lines_list_test)
    # print("Area:", total_area_covered(pol))
    # print("Perimeter:", perimeter_covered(pol))

    # shape, side1, side2, side3, side4 = is_rectangle_or_l_shape(pol)
    # print("Shape:", shape)
    # print("Side1:", side1)
    # print("Side2:", side2)
    # print("Side3:", side3)
    # print("Side4:", side4)

    # plot_polygon(pol, "Polygon 1")

    # lines_list_test1 = [
    #     [(0, 0), (4, 0)],
    #     [(4, 0), (4, 4)],
    #     [(4, 4), (0, 4)],
    #     [(0, 4), (0, 0)],
    # ]
    
    # pol1 = polyg_one(lines_list_test1)
    # print("Area:", total_area_covered(pol1))
    # print("Perimeter:", perimeter_covered(pol1))

    # shape1, side1_1, side2_1, side3_1, side4_1 = is_rectangle_or_l_shape(pol1)
    # print("Shape:", shape1)
    # print("Side1:", side1_1)
    # print("Side2:", side2_1)
    # print("Side3:", side3_1)
    # print("Side4:", side4_1)

    # plot_polygon(pol1, "Polygon 2")

    # pass

    # lines_list_test2 = [
    #     [(0, 0), (0, 4)],
    #     [(4, 0), (4, 4)],
    #     [(7, 0), (7, 4)],
    #     [(6, 0), (6, 4)],
    #     [(0, 0), (5, 0)],
    #     [(0, 2), (5, 2)],
    #     [(0, 1), (5, 1)],
    #     [(0, 4.2), (5, 4.2)],
    #     [(0, 7.5), (5, 7.5)],
    #     [(0, 10), (2, 10)]
    # ]
    # De=largest_parallel_separation(lines_list_test2)
    # print(f"Largest Parallel Separation Between Parallel Lines Next to Each Other: {De:.2f} meters")


    # Plot the lines
    # plt.figure()
    # for line in lines_list_test2:
    #     (x1, y1), (x2, y2) = line
    #     plt.plot([x1, x2], [y1, y2], 'b-')
    # plt.title("Lines Plot")
    # plt.xlabel("X")
    # plt.ylabel("Y")
    # plt.grid(True)
    # plt.show()
