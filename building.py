import numpy as np
import trimesh
import random


def create_box(x1, y1, z1, x2, y2, z2):
    x_min, x_max = sorted([x1, x2])
    y_min, y_max = sorted([y1, y2]) 
    z_min, z_max = sorted([z1, z2]) 

    vertices = np.array([
        [x_min, y_min, z_min], [x_max, y_min, z_min],
        [x_max, y_max, z_min], [x_min, y_max, z_min],
        [x_min, y_min, z_max], [x_max, y_min, z_max],
        [x_max, y_max, z_max], [x_min, y_max, z_max],
    ])

    faces = np.array([
        [0, 1, 2], [0, 2, 3],
        [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4],
        [1, 2, 6], [1, 6, 5],
        [2, 3, 7], [2, 7, 6],
        [3, 0, 4], [3, 4, 7],
    ])

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)

    if not mesh.is_volume:
        mesh = mesh.convex_hull

    return mesh

def create_building(x1, y1, x2, y2, height):
    main_box = create_box(x1, y1, 0, x2, y2, height)

    detail_w = 1
    detail_h = 1
    depth = 0.15
    spacing = 3
    min_margin = 1

    x_min, x_max = sorted([x1, x2])
    y_min, y_max = sorted([y1, y2])

    details = []

    def symmetric_positions_with_min_margin(start, end, obj_size, spacing, min_margin):
        available = end - start
        usable = available - 2 * min_margin
        if usable < obj_size:
            return []
        max_count = int((usable + spacing) // spacing)
        while max_count > 0:
            total_span = (max_count - 1) * spacing + obj_size
            margin = (available - total_span) / 2
            if margin >= min_margin:
                break
            max_count -= 1
        if max_count <= 0:
            return []
        positions = [start + margin + i * spacing for i in range(max_count)]
        return positions

    x_positions = symmetric_positions_with_min_margin(x_min, x_max, detail_w, spacing, min_margin)
    y_positions = symmetric_positions_with_min_margin(y_min, y_max, detail_w, spacing, min_margin)
    z_positions = symmetric_positions_with_min_margin(0, height, detail_h, spacing, min_margin)

    for x in x_positions:
        for z in z_positions:
            if z < 3:
                continue
            details.append(create_box(x, y_min - depth, z, x + detail_w, y_min, z + detail_h))
            details.append(create_box(x, y_max, z, x + detail_w, y_max + depth, z + detail_h))

    for y in y_positions:
        for z in z_positions:
            if z < 3:
                continue
            details.append(create_box(x_min - depth, y, z, x_min, y + detail_w, z + detail_h))
            details.append(create_box(x_max, y, z, x_max + depth, y + detail_w, z + detail_h))

    door_width = 2
    door_height = 3
    door_x = (x_min + x_max - door_width) / 2
    door_y = (y_min + y_max - door_width) / 2

    details.extend([
        create_box(door_x, y_min - depth, 0, door_x + door_width, y_min, door_height),
        create_box(door_x, y_max, 0, door_x + door_width, y_max + depth, door_height),
        create_box(x_min - depth, door_y, 0, x_min, door_y + door_width, door_height),
        create_box(x_max, door_y, 0, x_max + depth, door_y + door_width, door_height),
    ])

    roof_faces = np.array([])
    roof_vertic = np.array([])
    fancy_metric = min(height/50, 1)
    
    roof_variant = np.random.choice([0, 1, 2], p=[fancy_metric, (1 - fancy_metric)/2, (1 - fancy_metric)/2])
    roof_height = 0
    
    #flat roof
    if roof_variant==0:
        height = 0
        roof_vertices = np.array([
        [x_min, y_min, height], 
        [x_max, y_min, height],
        [x_max, y_max, height],
        [x_min, y_max, height],
        [(x_min + x_max) / 2, (y_min + y_max) / 2, 0],

        ])

        roof_faces = np.array([
            [0, 1, 4],
            [1, 2, 4],
            [2, 3, 4],
            [3, 0, 4],
        ])
        
    
    #piramid roof
    if roof_variant==1:
        random.seed()
        roof_height = random.uniform(4, height / 4)

        roof_vertices = np.array([
            [x_min, y_min, height],
            [x_max, y_min, height],
            [x_max, y_max, height],
            [x_min, y_max, height],
            [(x_min + x_max) / 2, (y_min + y_max) / 2, height + roof_height],

        ])

        roof_faces = np.array([
            [0, 1, 4],
            [1, 2, 4], 
            [2, 3, 4],
            [3, 0, 4],
        ])
    
    
    if roof_variant==2:
        random.seed()
        roof_height = random.uniform(3, 7)

        roof_vertices = np.array([
            [x_min, y_min, height],
            [x_max, y_min, height],
            [x_max, y_max, height],
            [x_min, y_max, height],
            [(x_min + x_max) / 2, y_min, height + roof_height],
            [(x_min + x_max) / 2, y_max, height + roof_height],
        ])

        roof_faces = np.array([
            [0, 1, 4], [1, 2, 4],
            [2, 3, 5], [3, 0, 5],
            [0, 4, 5], [0, 5, 3],
            [1, 2, 5], [1, 5, 4],
        ])

    details.append(trimesh.Trimesh(vertices=roof_vertices, faces=roof_faces, process=True))

    gutter_size = 0.4
    offset = 0.05
    total_height = height

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

    details.extend(gutters)

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

    details.extend(horizontal_gutters)

    # Add vertical pole (mast) at the center of the roof
    mast_width = 0.3
    mast_height = 2

    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    z_base = height + roof_height - 1

    mast = create_box(
        x_center - mast_width / 2, y_center - mast_width / 2, z_base,
        x_center + mast_width / 2, y_center + mast_width / 2, z_base + mast_height
    )

    details.append(mast)


    return trimesh.util.concatenate([main_box] + details)


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
    return trimesh.Trimesh(vertices=vertices, faces=faces)