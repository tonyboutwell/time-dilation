# Copyright (C) 2024  Tony Boutwell - tonyboutwell@gmail.com
# This program is free software: you can redistribute it and/or modify it under the terms of the 
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.

import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QSlider, QLabel, QLCDNumber, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# Constants for physics calculations
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
c = 299792458    # Speed of light (m/s)
mass_jupiter = 1.898e27  # Mass of Jupiter in kg
mass_sun = 1.989e30       # Mass of the Sun in kg

class TimeMachineSimulation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Machine Simulation")
        self.setGeometry(100, 100, 1200, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Control panel
        control_panel = QWidget()
        main_layout.addWidget(control_panel)
        control_layout = QVBoxLayout(control_panel)

        # Visualization panel
        viz_panel = QWidget()
        main_layout.addWidget(viz_panel)
        viz_layout = QVBoxLayout(viz_panel)

        # Matplotlib figure
        self.figure = plt.figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        viz_layout.addWidget(self.toolbar)
        viz_layout.addWidget(self.canvas)

        # Clocks panel
        clock_panel = QWidget()
        clock_layout = QHBoxLayout(clock_panel)
        viz_layout.addWidget(clock_panel)

        # Outside clock
        outside_clock_layout = QVBoxLayout()
        outside_label = QLabel("Outside Time (days)")
        outside_label.setAlignment(Qt.AlignCenter)
        outside_label.setFont(QFont('Arial', 12, QFont.Bold))
        outside_clock_layout.addWidget(outside_label)
        self.outside_clock = QLCDNumber()
        self.setup_lcd(self.outside_clock, "green")
        outside_clock_layout.addWidget(self.outside_clock)
        clock_layout.addLayout(outside_clock_layout)

        # Inside clock
        inside_clock_layout = QVBoxLayout()
        inside_label = QLabel("Inside Time (days)")
        inside_label.setAlignment(Qt.AlignCenter)
        inside_label.setFont(QFont('Arial', 12, QFont.Bold))
        inside_clock_layout.addWidget(inside_label)
        self.inside_clock = QLCDNumber()
        self.setup_lcd(self.inside_clock, "red")
        inside_clock_layout.addWidget(self.inside_clock)
        clock_layout.addLayout(inside_clock_layout)

        # Simulation Controls title
        control_layout.addWidget(QLabel("Simulation Controls"))

        # Sliders
        self.num_points_slider, self.num_points_value = self.create_slider("Number of Points", 20, 2000, 100, log=False)
        control_layout.addWidget(self.num_points_slider)

        self.mass_slider, self.mass_value = self.create_slider("Mass of Each Point (kg, 10^x)", 20, 50, 30, log=True)
        control_layout.addWidget(self.mass_slider)

        self.point_mass_equivalent_label = QLabel("Each Point Mass Equivalent: ")
        control_layout.addWidget(self.point_mass_equivalent_label)

        self.radius_slider, self.radius_value = self.create_slider("Radius (meters, 10^x)", -2, 12, 7, log=True)
        control_layout.addWidget(self.radius_slider)

        # Info labels
        self.time_dilation_label = QLabel("Time Dilation: ")
        self.safe_radius_label = QLabel("Safe Radius: ")
        self.total_mass_equivalent_label = QLabel("Total Mass Equivalent: ")
        control_layout.addWidget(self.time_dilation_label)
        control_layout.addWidget(self.safe_radius_label)
        control_layout.addWidget(self.total_mass_equivalent_label)

        # Zoom buttons
        zoom_layout = QHBoxLayout()
        zoom_in_button = QPushButton("Zoom In")
        zoom_out_button = QPushButton("Zoom Out")
        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_out_button.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(zoom_in_button)
        zoom_layout.addWidget(zoom_out_button)
        control_layout.addLayout(zoom_layout)

        # Reset clocks
        reset_clock_button = QPushButton("Reset Clocks")
        reset_clock_button.clicked.connect(self.reset_clocks)
        control_layout.addWidget(reset_clock_button)
        control_layout.addStretch()

        # Initialize time and zoom
        self.time = 0
        self.zoom_level = 1.0
        self.time_dilation = 1.0  # Default until computed

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Each second in real-time represents one "day" in the simulation

        # Initial update
        self.update_visualization()

    def setup_lcd(self, lcd, color):
        lcd.setDigitCount(6)
        lcd.setSegmentStyle(QLCDNumber.Filled)
        lcd.setStyleSheet(f"background-color: black; color: {color};")

    def create_slider(self, label_text, min_val, max_val, default_val, log=False):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel(label_text)
        layout.addWidget(label)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval((max_val - min_val) // 10)
        layout.addWidget(slider)

        value_label = QLabel()
        layout.addWidget(value_label)

        def update_label(val):
            display_val = 10**val if log else val
            value_label.setText(f"{display_val:.2e}")

        slider.valueChanged.connect(lambda val: update_label(val))
        slider.valueChanged.connect(self.update_visualization)
        
        # Initialize label
        update_label(default_val)

        return widget, value_label

    def get_slider_value(self, slider_widget, log=False):
        slider = slider_widget.findChild(QSlider)
        val = slider.value()
        return 10**val if log else val

    def fibonacci_sphere(self, samples, scale):
        points = []
        phi = np.pi * (3. - np.sqrt(5.))  # Golden angle
        for i in range(samples):
            y = 1 - (i / float(samples - 1)) * 2
            radius = np.sqrt(1 - y * y)
            theta = phi * i
            x = np.cos(theta) * radius
            z = np.sin(theta) * radius
            points.append((x * scale, y * scale, z * scale))
        return np.array(points)

    def format_mass_equivalent(self, mass):
        mass_in_jupiters = mass / mass_jupiter
        mass_in_suns = mass / mass_sun

        if mass_in_jupiters < 1:
            jupiter_text = f"{mass_in_jupiters:.3f} Jupiters"
        else:
            jupiter_text = f"{mass_in_jupiters:.0f} Jupiters"

        if mass_in_suns < 1:
            sun_text = f"{mass_in_suns:.6f} Suns"
        else:
            sun_text = f"{mass_in_suns:.3f} Suns"

        return f"{mass:.2e} kg ({jupiter_text}, {sun_text})"

    def compute_parameters(self):
        num_points = self.get_slider_value(self.num_points_slider, log=False)
        mass_per_point = self.get_slider_value(self.mass_slider, log=True)
        radius = self.get_slider_value(self.radius_slider, log=True)

        # Generate sphere points
        points = self.fibonacci_sphere(samples=num_points, scale=radius)

        total_mass = mass_per_point * num_points
        center_potential = -G * total_mass / radius
        time_dilation = 1 / np.sqrt(1 + (2 * abs(center_potential) / c**2))
        
        # Safe radius calculation
        safe_radius = radius * np.cbrt(c**2 / (2 * G * total_mass * radius))
        safe_radius = min(safe_radius, radius * 0.99)

        return points, total_mass, mass_per_point, radius, safe_radius, time_dilation

    def update_visualization(self):
        points, total_mass, mass_per_point, radius, safe_radius, self.time_dilation = self.compute_parameters()

        # Update labels
        self.time_dilation_label.setText(f"Time Dilation: {self.time_dilation:.6f}")
        self.safe_radius_label.setText(f"Safe Radius: {safe_radius:.2e} m")
        self.total_mass_equivalent_label.setText("Total Mass Equivalent: " + self.format_mass_equivalent(total_mass))
        self.point_mass_equivalent_label.setText("Each Point Mass Equivalent: " + self.format_mass_equivalent(mass_per_point))

        # Redraw the plot
        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')
        ax.scatter(points[:, 0], points[:, 1], points[:, 2], c='blue', s=10)

        # Wireframe sphere
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = safe_radius * np.cos(u) * np.sin(v)
        y = safe_radius * np.sin(u) * np.sin(v)
        z = safe_radius * np.cos(v)
        ax.plot_wireframe(x, y, z, color="green", alpha=0.5, linewidth=1)

        # Person marker
        person_height = 1.8
        ax.plot([0, 0], [0, 0], [-person_height/2, person_height/2], color='red', linewidth=2)
        ax.text(0, 0, person_height/2, "Person", color='red', fontsize=8, ha='center', va='bottom')

        self.max_range = max(radius, safe_radius) * 1.1 / self.zoom_level
        ax.set_xlim(-self.max_range, self.max_range)
        ax.set_ylim(-self.max_range, self.max_range)
        ax.set_zlim(-self.max_range, self.max_range)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('Time Machine Simulation')

        # Scale indicator
        scale_length = self.max_range / 5
        ax.plot([self.max_range*0.8, self.max_range*0.8 + scale_length],
                [self.max_range*0.8, self.max_range*0.8],
                [-self.max_range, -self.max_range], 'k-', lw=2)
        ax.text(self.max_range*0.8 + scale_length/2, self.max_range*0.8, -self.max_range,
                f'{scale_length:.2e} m', ha='center', va='bottom')

        self.canvas.draw()

    def zoom_in(self):
        self.zoom_level *= 1.2
        self.update_visualization()

    def zoom_out(self):
        self.zoom_level /= 1.2
        self.update_visualization()

    def reset_clocks(self):
        self.time = 0
        self.update_time()

    def update_time(self):
        outside_time = self.time
        inside_time = self.time * self.time_dilation

        # Display times as floating point with one decimal place
        self.outside_clock.display(f"{outside_time:06.1f}")
        self.inside_clock.display(f"{inside_time:06.1f}")

        self.time += 1  # Each increment represents one day in the simulation

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = TimeMachineSimulation()
    main_window.show()
    sys.exit(app.exec_())
