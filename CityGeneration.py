import random
import tkinter as tk
import building

class City:
    def __init__(self, n):
        self.n = n
        self.map = self.generate_city()

    def generate_city(self):
        city_density = 0.9
        city_map = [['n' for _ in range(self.n)] for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                if random.uniform(0, 1) < city_density:
                    city_map[i][j] = 'c'
        return city_map

    def visualise_city(self):
        root = tk.Tk()
        root.title("City Grid Visualization")
        
        cell_size = 30
        canvas_width = self.n * cell_size
        canvas_height = self.n * cell_size
        
        canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
        canvas.pack(padx=10, pady=10)
        
        for i in range(self.n):
            for j in range(self.n):
                x1, y1 = j * cell_size, i * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                
                if self.map[i][j] == 'c':
                    color = "green"
                else:
                    color = "gray"
                
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
        
        root.mainloop()

    def generate_stl():
        for i in range(self.n):
            for j in range(self.n):
                building(i-0.5,j-0.5,i+0.5,j+0.5,random.uniform(3,10))
