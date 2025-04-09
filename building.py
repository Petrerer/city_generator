import numpy as np  # Import NumPy for array handling
import trimesh  # Import trimesh for 3D geometry creation
import random  # Import random for generating random numbers

# Function to create a 3D box (cuboid) mesh from two corner coordinates
def create_box(x1, y1, z1, x2, y2, z2):
    x_min, x_max = sorted([x1, x2])  # Ensure correct x bounds
    y_min, y_max = sorted([y1, y2])  # Ensure correct y bounds
    z_min, z_max = sorted([z1, z2])  # Ensure correct z bounds

    # Define 8 vertices of the cuboid
    vertices = np.array([
        [x_min, y_min, z_min], [x_max, y_min, z_min],
        [x_max, y_max, z_min], [x_min, y_max, z_min],
        [x_min, y_min, z_max], [x_max, y_min, z_max],
        [x_max, y_max, z_max], [x_min, y_max, z_max],
    ])

    # Define 12 triangular faces for the 6 sides
    faces = np.array([
        [0, 1, 2], [0, 2, 3],  # bottom
        [4, 5, 6], [4, 6, 7],  # top
        [0, 1, 5], [0, 5, 4],  # front
        [1, 2, 6], [1, 6, 5],  # right
        [2, 3, 7], [2, 7, 6],  # back
        [3, 0, 4], [3, 4, 7],  # left
    ])

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)  # Create mesh and auto-process

    if not mesh.is_volume:
        mesh = mesh.convex_hull  # Fix mesh if it's not a closed volume

    return mesh  # Return the mesh

# Function to generate the building geometry
def create_building(x1, y1, x2, y2, height):
    main_box = create_box(x1, y1, 0, x2, y2, height)  # Create the main building block

    detail_w = 1  # Window width
    detail_h = 1  # Window height
    depth = 0.15  # Extrusion depth of details
    spacing = 3  # Spacing between windows
    min_margin = 1  # Minimum margin from edges

    x_min, x_max = sorted([x1, x2])  # Get sorted x range
    y_min, y_max = sorted([y1, y2])  # Get sorted y range

    details = []  # List to collect all geometry parts

    # Function to calculate symmetrically distributed positions for windows
    def symmetric_positions_with_min_margin(start, end, obj_size, spacing, min_margin):
        available = end - start  # Total available space
        usable = available - 2 * min_margin  # Space minus margins
        if usable < obj_size:
            return []

        max_count = int((usable + spacing) // spacing)  # Max number of elements that can fit
        while max_count > 0:
            total_span = (max_count - 1) * spacing + obj_size  # Total space used by windows
            margin = (available - total_span) / 2  # Calculated margin
            if margin >= min_margin:
                break
            max_count -= 1

        if max_count <= 0:
            return []

        positions = [start + margin + i * spacing for i in range(max_count)]  # Final positions
        return positions

    # Calculate window positions along X, Y, Z axes
    x_positions = symmetric_positions_with_min_margin(x_min, x_max, detail_w, spacing, min_margin)
    y_positions = symmetric_positions_with_min_margin(y_min, y_max, detail_w, spacing, min_margin)
    z_positions = symmetric_positions_with_min_margin(0, height, detail_h, spacing, min_margin)

    # Add windows on front and back walls
    for x in x_positions:
        for z in z_positions:
            if z < 3: continue  # Skip too-low windows
            details.append(create_box(x, y_min - depth, z, x + detail_w, y_min, z + detail_h))  # Front
            details.append(create_box(x, y_max, z, x + detail_w, y_max + depth, z + detail_h))  # Back

    # Add windows on left and right walls
    for y in y_positions:
        for z in z_positions:
            if z < 3: continue  # Skip too-low windows
            details.append(create_box(x_min - depth, y, z, x_min, y + detail_w, z + detail_h))  # Left
            details.append(create_box(x_max, y, z, x_max + depth, y + detail_w, z + detail_h))  # Right

    # Define door size and position
    door_width = 2
    door_height = 3
    door_x = (x_min + x_max - door_width) / 2
    door_y = (y_min + y_max - door_width) / 2

    # Add doors to each wall
    details.extend([
        create_box(door_x, y_min - depth, 0, door_x + door_width, y_min, door_height),  # Front
        create_box(door_x, y_max, 0, door_x + door_width, y_max + depth, door_height),  # Back
        create_box(x_min - depth, door_y, 0, x_min, door_y + door_width, door_height),  # Left
        create_box(x_max, door_y, 0, x_max + depth, door_y + door_width, door_height),  # Right
    ])

    # Generate roof with random height
    random.seed()
    roof_height = random.uniform(0,height/10)

    # Roof vertices (2 triangles forming sloped roof)
    roof_vertices = np.array([
        [x_min, y_min, height],
        [x_max, y_min, height],
        [x_max, y_max, height],
        [x_min, y_max, height],
        [(x_min + x_max) / 2, y_min, height + roof_height],
        [(x_min + x_max) / 2, y_max, height + roof_height],
    ])

    # Roof faces (triangles)
    roof_faces = np.array([
        [0, 1, 4], [1, 2, 4],
        [2, 3, 5], [3, 0, 5],
        [0, 4, 5], [0, 5, 3],
        [1, 2, 5], [1, 5, 4],
    ])

    details.append(trimesh.Trimesh(vertices=roof_vertices, faces=roof_faces, process=True))  # Add roof to details

    # Create vertical gutters at building corners
    gutter_size = 0.4
    offset = 0.05
    total_height = height  # Gutter ends at roof base

    gutters = [
        create_box(x_min - offset - gutter_size, y_min - offset - gutter_size, 0,
                   x_min - offset, y_min - offset, total_height),
        create_box(x_max + offset, y_min - offset - gutter_size, 0,
                   x_max + offset + gutter_size, y_min - offset, total_height),
        create_box(x_max + offset, y_max + offset, 0,
                   x_max + offset + gutter_size, y_max + offset + gutter_size, total_height),
        create_box(x_min - offset - gutter_size, y_max + offset, 0,
                   x_min - offset, y_max + offset + gutter_size, total_height),
    ]

    details.extend(gutters)  # Add vertical gutters

    # Create horizontal gutters on roof slopes (sides)
    gutter_height = 0.4
    gutter_depth = 0.4
    roof_x_offset = 0.05

    horizontal_gutters = [
        create_box(
            x_min - roof_x_offset - gutter_depth, y_min - roof_x_offset, height - gutter_height / 2,
            x_min - roof_x_offset, y_max + roof_x_offset, height + gutter_height / 2
        ),
        create_box(
            x_max + roof_x_offset, y_min - roof_x_offset, height - gutter_height / 2,
            x_max + roof_x_offset + gutter_depth, y_max + roof_x_offset, height + gutter_height / 2
        )
    ]

    details.extend(horizontal_gutters)  # Add horizontal gutters

    return trimesh.util.concatenate([main_box] + details)  # Combine all parts into one mesh

# Function to create a flat rectangular plane as ground
def create_plane(width=100, depth=100, thickness=1):
    vertices = np.array([
        [0, 0, 0], [width, 0, 0], [width, depth, 0], [0, depth, 0],
        [0, 0, -thickness], [width, 0, -thickness],
        [width, depth, -thickness], [0, depth, -thickness],
    ])
    faces = np.array([
        [0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5],
        [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7],
    ])
    return trimesh.Trimesh(vertices=vertices, faces=faces)  # Return ground plane

