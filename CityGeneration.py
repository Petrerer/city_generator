import random
import math
import tkinter as tk
from building import *
import os

class City:
    def __init__(self, n):
        self.city_size = n
        self.max_height = 40
        self.min_height = 10
        self.map = self.generate_city()

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
        bloom_factor = 1
        stopping_factor = 0.0
        blind_factor = 0.8
        spacing = 6
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
                if random.uniform(0, 1) < city_density and city_map[i][j]!='s':
                    city_map[i][j] = 'c'
        return city_map
    
    
    

    def visualise_city(self):
        root = tk.Tk()
        root.title("City Grid Visualization")
        
        cell_size = 600/self.city_size
        canvas_width = self.city_size * cell_size
        canvas_height = self.city_size * cell_size
        
        canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
        canvas.pack(padx=10, pady=10)
        
        for i in range(self.city_size):
            for j in range(self.city_size):
                
                x1, y1 = j * cell_size, i * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                
                if self.map[i][j] == 'c':
                    color = "orange"
                elif self.map[i][j] == 's':
                    color = "gray"
                else:
                    color = "green"
                
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
        
        root.mainloop()

    def generate_stl(self,name):
        #Setup
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, name + '.stl')
        
        #Generate buildings
        buildings = list()
        prev = 0
        for i in range(self.city_size):
            for j in range(self.city_size):
                if (i*self.city_size+j)/(self.city_size*self.city_size)-0.01>prev:
                    print(round(prev,2))
                    prev+=0.01
                if self.map[i][j]=='c':
                    b = create_building(i*10,j*10,i*10+10,j*10+10,self.calculate_building_height(i,j))
                    buildings.append(b)

        # Combine plane and building into one scene
        combined = create_plane(self.city_size*10,self.city_size*10)
        for building in buildings:
            combined = trimesh.util.concatenate([combined, building])

        combined.export(output_path)
        print(f"Wygenerowano plik: {output_path}")

