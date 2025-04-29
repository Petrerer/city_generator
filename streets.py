import numpy as np
import trimesh

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

def create_street(x1, y1, x2, y2, type):
    height=0.6
    components=[]
    if type=="h":
        components.append(create_box(x1,y1,0,x2,y1+2.5,height))
        components.append(create_box(x1,y2-2.5,0,x2,y2,height))
    if type=="v":
        components.append(create_box(x1,y1,0,x1+2.5,y2,height))
        components.append(create_box(x2-2.5,y1,0,x2,y2,height))
    if type=="x":
        components.append(create_box(x1,y1,0,x1+2.5,y1+2.5,height))
        components.append(create_box(x1,y2-2.5,0,x1+2.5,y2,height))
        components.append(create_box(x2-2.5,y1,0,x2,y1+2.5,height))
        components.append(create_box(x2-2.5,y2-2.5,0,x2,y2,height))
        
    return trimesh.util.concatenate(components)
