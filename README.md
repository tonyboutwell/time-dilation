# Time-Dilation Simulator
An interactive gravity-based time dilation simulator that explores the concept of Lagrange points in extreme gravitational fields.

## Overview
This simulator was inspired by NASA's use of Lagrange points for positioning space telescopes. It explores the theoretical concept of creating a "safe" zone within an immense gravitational field capable of inducing significant time dilation. The simulator allows users to configure a spherical array of mass points, forming a Lagrange bubble at the center where gravitational forces theoretically cancel out.

**Caution:** This is a theoretical model. Attempting to build such a structure in our solar system would likely disrupt planetary orbits and solar dynamics causing everyone to have a really bad day. 😉

## How It Works

### User Interface
- Built with PyQt5 for a responsive graphical user interface (GUI)
- Sliders control the number of points, mass per point, and sphere radius

### Visualization
- 3D rendering using Matplotlib
- Dynamic updates based on user input
- Displays mass points, safe radius (Lagrange bubble), and a human figure for scale

### Physics Simulation
- Utilizes the Fibonacci sphere algorithm for uniform mass point distribution
- Incorporates gravitational constant (G) and speed of light (c) for accurate calculations
- Computes total mass, gravitational potential, safe radius, and time dilation factor

### Key Features
- Real-time 3D visualization updates
- Detailed mass information (including Jupiter and Sun mass equivalents)
- Interactive controls for simulation parameters
- Time displays showing differential passage of time inside and outside the bubble
- Zoom functionality for detailed examination
- Clock reset option

### Installation
Ensure you have Python 3.7+ and install the required libraries:

```bash
pip install numpy PyQt5 matplotlib
