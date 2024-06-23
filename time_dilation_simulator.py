import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QLCDNumber, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import Axes3D

# Constants for physics calculations
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
c = 299792458  # Speed of light (m/s)
mass_jupiter = 1.898e27  # Mass of Jupiter in kg
mass_sun = 1.989e30  # Mass of the Sun in kg

class TimeMachineSimulation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Machine Simulation")
        self.setGeometry(100, 100, 1200, 800)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Create and set up the control panel (left side)
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        layout.addWidget(control_panel)

        # Create and set up the visualization panel (right side)
        viz_panel = QWidget()
        viz_layout = QVBoxLayout(viz_panel)
        layout.addWidget(viz_panel)

        # Set up the matplotlib figure for 3D visualization
        self.figure = plt.figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        viz_layout.addWidget(self.toolbar)
        viz_layout.addWidget(self.canvas)

        # Set up the clock panel for displaying time
        clock_panel = QWidget()
        clock_layout = QHBoxLayout(clock_panel)
        viz_layout.addWidget(clock_panel)

        # Create and set up the outside clock display
        outside_clock_layout = QVBoxLayout()
        outside_label = QLabel("Outside Time")
        outside_label.setAlignment(Qt.AlignCenter)
        outside_label.setFont(QFont('Arial', 12, QFont.Bold))
        outside_clock_layout.addWidget(outside_label)
        self.outside_clock = QLCDNumber()
        self.outside_clock.setDigitCount(6)
        self.outside_clock.setSegmentStyle(QLCDNumber.Filled)
        self.outside_clock.setStyleSheet("background-color: black; color: green;")
        outside_clock_layout.addWidget(self.outside_clock)
        clock_layout.addLayout(outside_clock_layout)

        # Create and set up the inside clock display
        inside_clock_layout = QVBoxLayout()
        inside_label = QLabel("Inside Time")
        inside_label.setAlignment(Qt.AlignCenter)
        inside_label.setFont(QFont('Arial', 12, QFont.Bold))
        inside_clock_layout.addWidget(inside_label)
        self.inside_clock = QLCDNumber()
        self.inside_clock.setDigitCount(6)
        self.inside_clock.setSegmentStyle(QLCDNumber.Filled)
        self.inside_clock.setStyleSheet("background-color: black; color: red;")
        inside_clock_layout.addWidget(self.inside_clock)
        clock_layout.addLayout(inside_clock_layout)

        control_layout.addWidget(QLabel("Simulation Controls"))

        # Create sliders for adjusting simulation parameters
        self.num_points_slider = self.create_slider("Number of Points", 20, 2000, 100)
        control_layout.addWidget(self.num_points_slider)

        self.mass_slider = self.create_slider("Mass of Each Point (kg)", 20, 50, 30, log=True)
        control_layout.addWidget(self.mass_slider)

        # Label for displaying mass equivalent of each point
        self.point_mass_equivalent_label = QLabel("Each Point Mass Equivalent: ")
        control_layout.addWidget(self.point_mass_equivalent_label)

        self.radius_slider = self.create_slider("Radius (meters)", -2, 12, 7, log=True)
        control_layout.addWidget(self.radius_slider)

        # Labels for displaying simulation results
        self.time_dilation_label = QLabel("Time Dilation: ")
        self.safe_radius_label = QLabel("Safe Radius: ")
        self.total_mass_equivalent_label = QLabel("Total Mass Equivalent: ")
        control_layout.addWidget(self.time_dilation_label)
        control_layout.addWidget(self.safe_radius_label)
        control_layout.addWidget(self.total_mass_equivalent_label)

        # Create zoom buttons for the visualization
        zoom_layout = QHBoxLayout()
        zoom_in_button = QPushButton("Zoom In")
        zoom_out_button = QPushButton("Zoom Out")
        zoom_layout.addWidget(zoom_in_button)
        zoom_layout.addWidget(zoom_out_button)
        control_layout.addLayout(zoom_layout)

        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_out_button.clicked.connect(self.zoom_out)

        # Create reset button for the clocks
        reset_clock_button = QPushButton("Reset Clocks")
        reset_clock_button.clicked.connect(self.reset_clocks)
        control_layout.addWidget(reset_clock_button)

        control_layout.addStretch()

        # Initialize time and timer for clock updates
        self.time = 0
        self.zoom_level = 1.0  # Initialize zoom level
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second (each second represents a day)

        self.update_visualization()

    def create_slider(self, name, min_val, max_val, default_val, log=False):
        """
        Create a slider widget with label and value display.
        
        :param name: Name of the slider
        :param min_val: Minimum value of the slider
        :param max_val: Maximum value of the slider
        :param default_val: Default value of the slider
        :param log: If True, use logarithmic scale for the slider
        :return: Widget containing the slider and labels
        """
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval((max_val - min_val) // 10)
        slider.valueChanged.connect(self.update_visualization)

        label = QLabel(name)
        value_label = QLabel(str(default_val))

        def update_label(value):
            if log:
                value_label.setText(f"{10**value:.2e}")
            else:
                value_label.setText(str(value))

        slider.valueChanged.connect(update_label)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(slider)
        layout.addWidget(value_label)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def get_slider_value(self, slider, log=False):
        """
        Get the current value of a slider.
        
        :param slider: The slider widget
        :param log: If True, return 10^value for logarithmic scale
        :return: Current value of the slider
        """
        value = slider.findChild(QSlider).value()
        return 10 ** value if log else value

    def fibonacci_sphere(self, samples, scale):
        """
        Generate points on a sphere using the Fibonacci spiral method.
        
        :param samples: Number of points to generate
        :param scale: Radius of the sphere
        :return: Array of 3D coordinates of points on the sphere
        """
        points = []
        phi = np.pi * (3. - np.sqrt(5.))  # Golden angle in radians
        for i in range(samples):
            y = 1 - (i / float(samples - 1)) * 2
            radius = np.sqrt(1 - y * y)
            theta = phi * i
            x = np.cos(theta) * radius
            z = np.sin(theta) * radius
            points.append((x * scale, y * scale, z * scale))
        return np.array(points)

    def update_visualization(self):
        """
        Update the 3D visualization based on current slider values.
        This method calculates and displays the time dilation, safe radius,
        and mass equivalents based on the current configuration.
        """
        # Get current values from sliders
        num_points = self.get_slider_value(self.num_points_slider)
        mass_per_point = self.get_slider_value(self.mass_slider, log=True)
        radius = self.get_slider_value(self.radius_slider, log=True)

        # Generate points on the sphere
        points = self.fibonacci_sphere(samples=num_points, scale=radius)

        # Calculate total mass and gravitational potential
        total_mass = mass_per_point * num_points
        center_potential = -G * total_mass / radius
        
        # Calculate time dilation factor
        self.time_dilation = 1 / np.sqrt(1 + (2 * abs(center_potential) / c**2))
        
        # Calculate safe radius (Lagrange bubble)
        safe_radius = radius * np.cbrt(c**2 / (2 * G * total_mass * radius))
        safe_radius = min(safe_radius, radius * 0.99)

        # Clear the previous plot and create a new 3D subplot
        self.figure.clear()
        self.ax = self.figure.add_subplot(111, projection='3d')

        # Plot the mass points
        self.ax.scatter(points[:, 0], points[:, 1], points[:, 2], c='blue', s=10)

        # Plot the safe radius as a wireframe sphere
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = safe_radius * np.cos(u) * np.sin(v)
        y = safe_radius * np.sin(u) * np.sin(v)
        z = safe_radius * np.cos(v)
        self.ax.plot_wireframe(x, y, z, color="green", alpha=0.5, linewidth=1)

        # Add centered person representation for scale
        person_height = 1.8  # Constant height of the person in meters
        person_bottom = -person_height / 2
        person_top = person_height / 2
        self.ax.plot([0, 0], [0, 0], [person_bottom, person_top], color='red', linewidth=2)
        self.ax.text(0, 0, person_top, "Person", color='red', fontsize=8, ha='center', va='bottom')

        # Set axis limits and labels
        self.max_range = max(radius, safe_radius) * 1.1 / self.zoom_level
        self.ax.set_xlim(-self.max_range, self.max_range)
        self.ax.set_ylim(-self.max_range, self.max_range)
        self.ax.set_zlim(-self.max_range, self.max_range)
        self.ax.set_xlabel('X (meters)')
        self.ax.set_ylabel('Y (meters)')
        self.ax.set_zlabel('Z (meters)')
        self.ax.set_title('Time Machine Simulation')

        # Add a scale indicator
        scale_length = self.max_range / 5
        self.ax.plot([self.max_range*0.8, self.max_range*0.8 + scale_length], 
                     [self.max_range*0.8, self.max_range*0.8], 
                     [-self.max_range, -self.max_range], 'k-', lw=2)
        self.ax.text(self.max_range*0.8 + scale_length/2, self.max_range*0.8, -self.max_range, 
                     f'{scale_length:.2e} m', ha='center', va='bottom')

        self.canvas.draw()

        # Update info labels
        self.time_dilation_label.setText(f"Time Dilation: {self.time_dilation:.6f}")
        self.safe_radius_label.setText(f"Safe Radius: {safe_radius:.2e} m")
        
        # Update mass equivalent labels
        def format_mass_equivalent(mass):
            """Format mass in terms of Jupiters and Suns"""
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

        total_mass_equiv = format_mass_equivalent(total_mass)
        point_mass_equiv = format_mass_equivalent(mass_per_point)

        self.total_mass_equivalent_label.setText(f"Total Mass Equivalent: {total_mass_equiv}")
        self.point_mass_equivalent_label.setText(f"Each Point Mass Equivalent: {point_mass_equiv}")

    def zoom_in(self):
        """Increase the zoom level and update the visualization"""
        self.zoom_level *= 1.2
        self.update_visualization()

    def zoom_out(self):
        """Decrease the zoom level and update the visualization"""
        self.zoom_level /= 1.2
        self.update_visualization()

    def reset_clocks(self):
        """Reset both clocks to zero"""
        self.time = 0
        self.update_time()

    def update_time(self):
        """
        Update the clock displays.
        Outside time increments normally, while inside time is affected by time dilation.
        """
        outside_time = self.time
        inside_time = self.time * self.time_dilation

        self.outside_clock.display(f"{outside_time:06.1f}")
        self.inside_clock.display(f"{inside_time:06.1f}")

        self.time += 1  # Increment by 1 day

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = TimeMachineSimulation()
    main_window.show()
    sys.exit(app.exec_())
