import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

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

# Define the material properties and loads
material_properties = {
    'modulus_of_elasticity': 200000,  # MPa
    'allowable_bending_stress': 160   # MPa
}

# Prompt user for inputs
def getinput():
    x_min = float(input("Enter x_min: "))
    y_min = float(input("Enter y_min: "))
    x_max = float(input("Enter x_max: "))
    y_max = float(input("Enter y_max: "))
    uniform_distributed_load = float(input("Enter uniform distributed load (kN/m): "))
    return x_min, y_min, x_max, y_max, uniform_distributed_load

# Get user inputs
x_min, y_min, x_max, y_max, uniform_distributed_load = getinput()

# Define the AABB
aabb = AABB(x_min, y_min, x_max, y_max)

# Define the loads
loads = {
    'uniform_distributed_load': uniform_distributed_load  # kN/m
}

# Create the Beam object
beam = Beam(aabb, material_properties, loads)

# Calculate the required beam dimensions
depth, width = beam.calculate()
print(f"Required beam dimensions: Depth = {depth:.2f} m, Width = {width:.2f} m")

# Visualize the AABB and beam
fig, ax = plt.subplots()
ax.add_patch(Rectangle((aabb.x_min, aabb.y_min), aabb.x_max - aabb.x_min, aabb.y_max - aabb.y_min, edgecolor='black', facecolor='none', linewidth=1))
ax.plot([aabb.x_min, aabb.x_max], [aabb.y_max + depth / 2, aabb.y_max + depth / 2], 'k-', linewidth=2)
ax.plot([aabb.x_min, aabb.x_max], [aabb.y_max - depth / 2, aabb.y_max - depth / 2], 'k-', linewidth=2)
ax.plot([aabb.x_min, aabb.x_min], [aabb.y_max + depth / 2, aabb.y_max - depth / 2], 'k-', linewidth=2)
ax.plot([aabb.x_max, aabb.x_max], [aabb.y_max + depth / 2, aabb.y_max - depth / 2], 'k-', linewidth=2)
ax.set_aspect('equal')
plt.show()