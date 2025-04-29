import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import os
import CityGeneration as cg

class CityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("City STL Generator")
        self.stl_filename = "city.stl"

        # Główna ramka z podziałem na lewą i prawą kolumnę
        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10)

        # Lewa kolumna - GUI
        control_frame = tk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(control_frame, text="Size of the city:").pack()
        self.size = tk.Scale(control_frame, from_=5, to=30, orient='horizontal')
        self.size.set(17)
        self.size.pack()

        tk.Label(control_frame, text="Maximum building height:").pack()
        self.max = tk.Scale(control_frame, from_=5, to=80, orient='horizontal')
        self.max.set(42)
        self.max.pack()

        tk.Label(control_frame, text="Minimum building height:").pack()
        self.min = tk.Scale(control_frame, from_=5, to=80, orient='horizontal')
        self.min.set(42)
        self.min.pack()

        tk.Label(control_frame, text="Building density (bloom factor):").pack()
        self.bloom = tk.Scale(control_frame, from_=0, to=1, resolution=0.01, orient='horizontal')
        self.bloom.set(0.5)
        self.bloom.pack()

        self.generate_button = tk.Button(control_frame, text="Generate city", command=self.generate_all)
        self.generate_button.pack(pady=10)

        image_frame = tk.Frame(main_frame)
        image_frame.pack(side=tk.RIGHT)

        image_path = "3d.jpg" 
        try:
            image = Image.open(image_path)
            image = image.resize((300, 300))
            self.city_image = ImageTk.PhotoImage(image)
            self.image_label = tk.Label(image_frame, image=self.city_image)
            self.image_label.pack()
        except FileNotFoundError:
            tk.Label(image_frame, text="Image not found").pack()

    def generate_all(self):
        size = self.size.get()
        max_h = self.max.get()
        min_h = self.min.get()
        bloom = self.bloom.get()


        messagebox.showinfo("Start", f"Generating city {size}x{size}...")

        city = cg.City(size, max_h, min_h, bloom)
        city.generate_stl("city")

        messagebox.showinfo("Success", f"File generated: {self.stl_filename}\nOpening in MeshLab...")
        subprocess.Popen([r"C:\Program Files\VCG\MeshLab\meshlab.exe", self.stl_filename])

if __name__ == "__main__":
    root = tk.Tk()
    app = CityApp(root)
    root.mainloop()
