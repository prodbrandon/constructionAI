import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from tkinter import Tk, Label, Entry, Button, StringVar, DoubleVar
import pandas as pd
from rtree import index
#from rpw import RevitPythonShell
#from Autodesk.Revit.DB import *

# Define the AABB class
class AABB:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

# Define the Beam class
class Beam:
    def __init__(self, aabb, material_properties, loads):
        self.aabb = aabb
        self.material_properties = material_properties
        self.loads = loads

    def calculate(self):
        # Assume a simply supported beam with a uniform distributed load
        span_length = self.aabb.x_max - self.aabb.x_min
        max_deflection = span_length / 360  # Deflection limit (L/360)
        applied_load = self.loads['uniform_distributed_load']

        # Calculate the required moment of inertia
        modulus_of_elasticity = self.material_properties['modulus_of_elasticity']
        required_moment_of_inertia = (applied_load * span_length ** 4) / (8 * modulus_of_elasticity * max_deflection)

        # Calculate the required section modulus
        allowable_bending_stress = self.material_properties['allowable_bending_stress']
        required_section_modulus = (applied_load * span_length ** 2) / (8 * allowable_bending_stress)

        # Assume a rectangular cross-section
        depth = math.sqrt((12 * required_moment_of_inertia) / self.aabb.y_max)
        width = required_section_modulus / (depth / 6)

        return depth, width

    def visualize(self, depth, width):
        fig, ax = plt.subplots()
        ax.add_patch(Rectangle((self.aabb.x_min, self.aabb.y_min), self.aabb.x_max - self.aabb.x_min, self.aabb.y_max - self.aabb.y_min, edgecolor='black', facecolor='none', linewidth=1))
        ax.plot([self.aabb.x_min, self.aabb.x_max], [self.aabb.y_max + depth / 2, self.aabb.y_max + depth / 2], 'k-', linewidth=2)
        ax.plot([self.aabb.x_min, self.aabb.x_max], [self.aabb.y_max - depth / 2, self.aabb.y_max - depth / 2], 'k-', linewidth=2)
        ax.plot([self.aabb.x_min, self.aabb.x_min], [self.aabb.y_max + depth / 2, self.aabb.y_max - depth / 2], 'k-', linewidth=2)
        ax.plot([self.aabb.x_max, self.aabb.x_max], [self.aabb.y_max + depth / 2, self.aabb.y_max - depth / 2], 'k-', linewidth=2)
        ax.set_aspect('equal')
        plt.show()

# Define the material properties and loads
material_properties = {
    'modulus_of_elasticity': 200000,  # MPa
    'allowable_bending_stress': 160   # MPa
}

# Define the GUI
root = Tk()
root.title("Beam Design")

x_min_var = DoubleVar()
y_min_var = DoubleVar()
x_max_var = DoubleVar()
y_max_var = DoubleVar()
load_var = DoubleVar()

Label(root, text="Enter x_min:").grid(row=0, column=0)
x_min_entry = Entry(root, textvariable=x_min_var)
x_min_entry.grid(row=0, column=1)

Label(root, text="Enter y_min:").grid(row=1, column=0)
y_min_entry = Entry(root, textvariable=y_min_var)
y_min_entry.grid(row=1, column=1)

Label(root, text="Enter x_max:").grid(row=2, column=0)
x_max_entry = Entry(root, textvariable=x_max_var)
x_max_entry.grid(row=2, column=1)

Label(root, text="Enter y_max:").grid(row=3, column=0)
y_max_entry = Entry(root, textvariable=y_max_var)
y_max_entry.grid(row=3, column=1)

Label(root, text="Enter uniform distributed load (kN/m):").grid(row=4, column=0)
load_entry = Entry(root, textvariable=load_var)
load_entry.grid(row=4, column=1)

result_label = StringVar()
Label(root, textvariable=result_label).grid(row=5, column=0, columnspan=2)

# Create a pandas DataFrame to store beam data
beam_data = pd.DataFrame(columns=['x_min', 'y_min', 'x_max', 'y_max', 'load', 'depth', 'width'])

# Create an OBBTree for spatial indexing
beam_tree = index.Index()

def calculate_beam():
    x_min = x_min_var.get()
    y_min = y_min_var.get()
    x_max = x_max_var.get()
    y_max = y_max_var.get()
    uniform_distributed_load = load_var.get()

    aabb = AABB(x_min, y_min, x_max, y_max)
    loads = {'uniform_distributed_load': uniform_distributed_load}
    beam = Beam(aabb, material_properties, loads)

    depth, width = beam.calculate()
    result_label.set(f"Required beam dimensions: Depth = {depth:.2f} m, Width = {width:.2f} m")

    # Add beam data to the DataFrame
    beam_data.loc[len(beam_data)] = [x_min, y_min, x_max, y_max, uniform_distributed_load, depth, width]

    # Add beam to the OBBTree
    beam_tree.insert(len(beam_data) - 1, (x_min, y_min, x_max, y_max), obj=beam)

    beam.visualize(depth, width)

    # Integrate with Revit using RevitPythonShell
    revit_shell = RevitPythonShell()
    revit_shell.open()
    active_doc = revit_shell.doc

    # Create a new beam element in Revit
    line = Line.CreateBound(XYZ(x_min, y_min, 0), XYZ(x_max, y_max, 0))
    beam_curve = active_doc.Create.NewFamilyInstanceCurve(line, Symbol.GetFamily(active_doc, FamilySymbolUtils.GetDefaultFamilySymbolByName(active_doc, "Structural Framing")))
    active_doc.Regenerate()

Button(root, text="Calculate Beam", command=calculate_beam).grid(row=6, column=0, columnspan=2)

root.mainloop()