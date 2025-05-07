import matplotlib.pyplot as plt
from parser.parser import process_dxf, convert_units


def plot_grid_with_lines_and_rods(filepath, fileunits, polygon=None, complete=True, title="Grounding Grid"):
    """
    Plot the grounding grid polygon along with the lines_list and rods_list.
    
    Args:
        polygon: The Shapely polygon object representing the grounding grid.
        lines_list: A list of line segments (each line is a list of two points).
        rods_list: A list of rod positions (each rod is a tuple of x, y coordinates).
        title: The title of the plot.
    
    """
    # Parse the DXF file to get the lines and rods
    lines_list_raw, rods_list_raw = process_dxf(filepath)

    # Scale the lines and rods
    lines_list, rods_list =convert_units(lines_list_raw, rods_list_raw, fileunits)

     # Create a figure and axes
    fig, ax = plt.subplots(figsize=(8, 8))

    if polygon is not None:
        # Plot the polygon
        x, y = polygon.exterior.xy
        ax.plot(x, y, 'b-', label="Polygon Boundary")  # Polygon boundary in blue


    if complete:
         # Plot the lines_list
        for line in lines_list:
            x, y = zip(*line)
            ax.plot(x, y, 'b-', label="Lines" if 'Lines' not in ax.get_legend_handles_labels()[1] else "")  # Lines in blue

        # Plot the rods_list
        for rod in rods_list:
            x, y = rod
            ax.plot(x, y, 'ro', label="Rods" if 'Rods' not in ax.get_legend_handles_labels()[1] else "")  # Rods as red dots

    # Add labels and legend
    ax.set_title(title)
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.grid(True)
    ax.legend()
    ax.set_aspect('equal', adjustable='datalim', anchor='C')

    # Set x-axis limits based on the data
    all_x = [point[0] for line in lines_list for point in line] + [rod[0] for rod in rods_list]
    x_min, x_max = min(all_x), max(all_x)
    ax.set_xlim(x_min - 10, x_max + 10)  # Add some padding to the x-axis limits
    plt.close(fig)

    # Return the figure
    return fig
