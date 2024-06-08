import sys
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.patches import Rectangle
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
import pandas as pd
from rtree import index
#from rpw import RevitPythonShell
#from Autodesk.Revit.DB import *
class AABB:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

class Beam:
    def __init__(self, aabb, material_properties, loads):
        self.aabb = aabb
        self.material_properties = material_properties
        self.loads = loads

    def calculate(self):
        span_length = self.aabb.x_max - self.aabb.x_min
        max_deflection = span_length / 360
        applied_load = self.loads['uniform_distributed_load']

        modulus_of_elasticity = self.material_properties['modulus_of_elasticity']
        required_moment_of_inertia = (applied_load * span_length ** 4) / (8 * modulus_of_elasticity * max_deflection)

        allowable_bending_stress = self.material_properties['allowable_bending_stress']
        required_section_modulus = (applied_load * span_length ** 2) / (8 * allowable_bending_stress)

        depth = math.sqrt((12 * required_moment_of_inertia) / self.aabb.y_max)
        width = required_section_modulus / (depth / 6)

        shear_force = applied_load * span_length / 2
        shear_stress = shear_force / (width * depth / 2)

        moment_of_inertia = (width * depth ** 3) / 12
        max_beam_deflection = (applied_load * span_length ** 4) / (384 * modulus_of_elasticity * moment_of_inertia)

        return depth, width, shear_stress, max_beam_deflection

material_properties = {
    'modulus_of_elasticity': 200000,
    'allowable_bending_stress': 160
}

class BeamCalculatorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('BeamCalc')

        layout = QVBoxLayout()

        self.x_min_label = QLabel('x_min:')
        self.x_min_input = QLineEdit(self)
        layout.addWidget(self.x_min_label)
        layout.addWidget(self.x_min_input)

        self.y_min_label = QLabel('y_min:')
        self.y_min_input = QLineEdit(self)
        layout.addWidget(self.y_min_label)
        layout.addWidget(self.y_min_input)

        self.x_max_label = QLabel('x_max:')
        self.x_max_input = QLineEdit(self)
        layout.addWidget(self.x_max_label)
        layout.addWidget(self.x_max_input)

        self.y_max_label = QLabel('y_max:')
        self.y_max_input = QLineEdit(self)
        layout.addWidget(self.y_max_label)
        layout.addWidget(self.y_max_input)

        self.uniform_load_label = QLabel('Uniform Distributed Load (kN/m):')
        self.uniform_load_input = QLineEdit(self)
        layout.addWidget(self.uniform_load_label)
        layout.addWidget(self.uniform_load_input)

        self.calculate_button = QPushButton('Calculate', self)
        self.calculate_button.clicked.connect(self.calculate)
        layout.addWidget(self.calculate_button)

        self.results_text = QTextEdit(self)
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

        self.setLayout(layout)

    def calculate(self):
        try:
            x_min = float(self.x_min_input.text())
            y_min = float(self.y_min_input.text())
            x_max = float(self.x_max_input.text())
            y_max = float(self.y_max_input.text())
            uniform_distributed_load = float(self.uniform_load_input.text())

            aabb = AABB(x_min, y_min, x_max, y_max)
            loads = {'uniform_distributed_load': uniform_distributed_load}
            beam = Beam(aabb, material_properties, loads)

            depth, width, shear_stress, max_beam_deflection = beam.calculate()

            results = (
                f"Required beam dimensions:\n"
                f"Depth: {depth:.2f} m\n"
                f"Width: {width:.2f} m\n"
                f"Shear Stress: {shear_stress:.2f} MPa\n"
                f"Maximum Beam Deflection: {max_beam_deflection:.2f} m\n"
            )
            self.results_text.setText(results)

            self.ax.clear()
            self.ax.add_patch(Rectangle((aabb.x_min, aabb.y_min), aabb.x_max - aabb.x_min, aabb.y_max - aabb.y_min, edgecolor='black', facecolor='none', linewidth=1))
            self.ax.plot([aabb.x_min, aabb.x_max], [aabb.y_max + depth / 2, aabb.y_max + depth / 2], 'k-', linewidth=2)
            self.ax.plot([aabb.x_min, aabb.x_max], [aabb.y_max - depth / 2, aabb.y_max - depth / 2], 'k-', linewidth=2)
            self.ax.plot([aabb.x_min, aabb.x_min], [aabb.y_max + depth / 2, aabb.y_max - depth / 2], 'k-', linewidth=2)
            self.ax.plot([aabb.x_max, aabb.x_max], [aabb.y_max + depth / 2, aabb.y_max - depth / 2], 'k-', linewidth=2)
            self.ax.set_aspect('equal')
            self.canvas.draw()

        except ValueError:
            QMessageBox.critical(self, "Invalid input", "Please enter valid numbers")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = BeamCalculatorApp()
    ex.show()
    sys.exit(app.exec_())
