import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import CityGeneration as cg

class CityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("City STL Generator")
        self.stl_filename = "city.stl"

        tk.Label(root, text="Size of the city:").pack()
        self.size = tk.Scale(root, from_=5, to=50, orient='horizontal')
        self.size.set(20)
        self.size.pack()

        tk.Label(root, text="Maximum building height:").pack()
        self.max = tk.Scale(root, from_=5, to=80, orient='horizontal')
        self.max.set(52)
        self.max.pack()

        tk.Label(root, text="Minimum building height:").pack()
        self.min = tk.Scale(root, from_=5, to=80, orient='horizontal')
        self.min.set(8)
        self.min.pack()

        tk.Label(root, text="Building Density:").pack()
        self.bloom = tk.Scale(root, from_=0, to=1, resolution=0.01, orient='horizontal')
        self.bloom.set(0.5)
        self.bloom.pack()

        self.generate_button = tk.Button(root, text="Generate city", command=self.generate_all)
        self.generate_button.pack(pady=10)

    def generate_all(self):
        size = self.size.get()
        max_h = self.max.get()
        min_h = self.min.get()
        bloom = self.bloom.get()

        messagebox.showinfo("Start", f"Click OK to generate city of size {size}x{size}")

        city = cg.City(size, max_h, min_h, bloom)
        city.generate_stl("city")

        messagebox.showinfo("Success", f"File generated: {self.stl_filename}\n Click OK to open in MeshLab...")
        subprocess.Popen([r"C:\Program Files\VCG\MeshLab\meshlab.exe", self.stl_filename])

if __name__ == "__main__":
    root = tk.Tk()
    app = CityApp(root)
    root.mainloop()
