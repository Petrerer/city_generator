import random
import math
import tkinter as tk
from building import *
import os
import trimesh.transformations as tf
from streets import *

class City:
    def __init__(self, n, max_h, min_h, bloom):
        self.city_size = n
        self.max_height = max_h
        self.min_height = min_h
        self.blooming=bloom
        self.map = self.generate_city()
        self.roads=self.generate_roads()

    def calculate_building_height(self, x, y):
        cx, cy = self.city_size / 2, self.city_size / 2  # Center of the city
        d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)  # Euclidean distance
        sigma = self.city_size / 8  # Adjust for spread
        deviation = random.uniform(0,10)

        # Compute height using Gaussian function
        height = self.min_height + (self.max_height - self.min_height) * math.exp(- (d ** 2) / (2 * sigma ** 2)) + deviation
        
        return height
    
    def generate_city(self):
        city_map = [['n' for _ in range(self.city_size)] for _ in range(self.city_size)]
        bloom_factor = self.blooming
        stopping_factor = 0.0
        blind_factor = 0.8
        spacing = 4
        directions = [[1,0],[0,-1],[-1,0],[0,1]]
        streets = [[self.city_size//2,self.city_size//2,2],[self.city_size//2,self.city_size//2,0]]
        city_map[self.city_size//2][self.city_size//2] = 's'
        while(len(streets)>0):
            x,y,dir = streets[0]
            streets = streets[1:]
            print(x,y,dir)
            while(True):
                print(directions[dir])
                
                break_flag=False
                for i in range(spacing):
                    x +=directions[dir][0]
                    y +=directions[dir][1]  
                    if x<0 or x>=self.city_size or y<0 or y>=self.city_size or city_map[x][y]!='n':
                        break_flag = True
                        break
                    city_map[x][y] = 's'
                if break_flag:
                    break
                
                if random.uniform(0,1)<stopping_factor:
                    if random.uniform(0,1)<blind_factor:
                        break
                    else:
                        next_dir = random.choice([1, -1])
                        streets.append([x,y,(4+dir+next_dir)%4])
                        break
                if random.uniform(0,1)<bloom_factor:
                    streets.append([x,y,(4+dir-1)%4])
                if random.uniform(0,1)<bloom_factor:
                    streets.append([x,y,(4+dir+1)%4])
        
        city_density = 0.9
        for i in range(self.city_size):
            for j in range(self.city_size):
                # if random.uniform(0, 1) < city_density and city_map[i][j]!='s':
                #     city_map[i][j] = 'c'
                if city_map[i][j]!='s':
                    if (i>0 and city_map[i-1][j]=='s') or (i<self.city_size-1 and city_map[i+1][j]=='s') or (j > 0 and city_map[i][j - 1] == 's') or (j < self.city_size - 1 and city_map[i][j + 1] == 's'):
                        city_map[i][j]='c'
        return city_map
    
    def generate_roads(self):
        roads=[['n' for _ in range(self.city_size)] for _ in range(self.city_size)]
        for i in range(self.city_size):
            for j in range(self.city_size):
                if self.map[i][j] == 's':
                    is_up    = i > 0 and self.map[i - 1][j] == 's'
                    is_down  = i < self.city_size - 1 and self.map[i + 1][j] == 's'
                    is_left  = j > 0 and self.map[i][j - 1] == 's'
                    is_right = j < self.city_size - 1 and self.map[i][j + 1] == 's'

                    

                    if (is_down or is_up) and (not is_right and not is_left):
                        roads[i][j]='sv'
                    elif (is_right or is_left) and (not is_up and not is_down):
                        roads[i][j]='sh'
                    else:
                        roads[i][j] = 'sx'

        return roads
    
    
    

    # def visualise_city(self):
    #     root = tk.Tk()
    #     root.title("City Grid Visualization")
        
    #     cell_size = 600/self.city_size
    #     canvas_width = self.city_size * cell_size
    #     canvas_height = self.city_size * cell_size
        
    #     canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
    #     canvas.pack(padx=10, pady=10)
        
    #     for i in range(self.city_size):
    #         for j in range(self.city_size):
                
    #             x1, y1 = j * cell_size, i * cell_size
    #             x2, y2 = x1 + cell_size, y1 + cell_size
                
    #             if self.map[i][j] == 'c':
    #                 color = "orange"
    #             elif self.map[i][j]=='s':
    #                 if self.roads[i][j] == 'sx':
    #                     color = "gray"
    #                 elif self.roads[i][j] == 'sv':
    #                     color="purple"
    #                 elif self.roads[i][j] == 'sh':
    #                     color="yellow"
    #             else:
    #                 color = "green"
                
    #             canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
        
    #     root.mainloop()

    def generate_stl(self,name):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, name + '.stl')
        
        buildings = list()
        prev = 0
        tree_models = self.load_tree_models()
        for i in range(self.city_size):
            for j in range(self.city_size):
                if (i*self.city_size+j)/(self.city_size*self.city_size)-0.01>prev:
                    print(round(prev,2))
                    prev+=0.01
                if self.map[i][j]=='c':
                    b = create_building(i*10,j*10,i*10+10,j*10+10,self.calculate_building_height(i,j))
                    buildings.append(b)
                elif self.map[i][j]=='s':
                    if self.roads[i][j]=='sh':
                        r=create_street(i*10,j*10,i*10+10,j*10+10,"v")
                        buildings.append(r)
                    elif self.roads[i][j]=='sv':
                        r=create_street(i*10,j*10,i*10+10,j*10+10,"h")
                        buildings.append(r)
                    else:
                        r=create_street(i*10,j*10,i*10+10,j*10+10,"x")
                        buildings.append(r)
                elif self.map[i][j] == 'n':
                    if random.uniform(0, 1) < 2:
                        num_trees = random.randint(2, 5)
                        attempts = 0
                        placed = 0
                        while placed < num_trees and attempts < 15:
                            tree = random.choice(tree_models).copy()

                            scale_factor = random.uniform(0.6, 1.5)
                            tree.apply_scale(scale_factor)

                            angle = random.uniform(0, 2 * math.pi)
                            rotation_matrix = tf.rotation_matrix(angle, [0, 0, 1], tree.centroid)
                            tree.apply_transform(rotation_matrix)

                            bbox = tree.bounds
                            size_x = bbox[1][0] - bbox[0][0]
                            size_y = bbox[1][1] - bbox[0][1]

                            city_limit = self.city_size * 10

                            min_cx = max(0 + size_x / 2, i * 10)
                            max_cx = min(city_limit - size_x / 2, (i + 1) * 10)
                            min_cy = max(0 + size_y / 2, j * 10)
                            max_cy = min(city_limit - size_y / 2, (j + 1) * 10)

                            if min_cx >= max_cx or min_cy >= max_cy:
                                break

                            center_x = random.uniform(min_cx, max_cx)
                            center_y = random.uniform(min_cy, max_cy)

                            translation = [center_x - tree.centroid[0], center_y - tree.centroid[1], 0]
                            tree.apply_translation(translation)
                            tree_bbox = tree.bounds
                            tree_min_x = int(tree_bbox[0][0] // 10)
                            tree_max_x = int(tree_bbox[1][0] // 10)
                            tree_min_y = int(tree_bbox[0][1] // 10)
                            tree_max_y = int(tree_bbox[1][1] // 10)

                            conflict = False
                            for x in range(tree_min_x, tree_max_x + 1):
                                for y in range(tree_min_y, tree_max_y + 1):
                                    if 0 <= x < self.city_size and 0 <= y < self.city_size:
                                        if self.map[x][y] == 'c':  # drzewo wchodzi na budynek
                                            conflict = True
                                            break
                                if conflict:
                                    break

                            if conflict:
                                attempts += 1
                                continue

                            buildings.append(tree)
                            placed += 1
                            attempts += 1




        combined = create_plane(self.city_size*10,self.city_size*10)
        for building in buildings:
            combined = trimesh.util.concatenate([combined, building])

        combined.export(output_path)
        print(f"Wygenerowano plik: {output_path}")

    def load_tree_models(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        tree_paths = ["tree2.stl", "tree3.stl"]
        trees = []
        target_size = 9

        for filename in tree_paths:
            full_path = os.path.join(script_dir, filename)
            tree = trimesh.load(full_path)

            size = tree.extents
            max_dimension = max(size)
            
            if max_dimension > target_size:
                scale_factor = target_size / max_dimension
                tree.apply_scale(scale_factor)
            
            trees.append(tree)
        return trees



