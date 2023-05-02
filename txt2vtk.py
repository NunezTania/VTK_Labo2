#!/usr/bin/env python
#
# Labo 2 from VTK.
#
# Goal: Achieve to reproduce a topographic map from a part of switzerland
#
# Authors: Forestier Quentin & Herzig Melvyn
#
# Date: 03.05.2022

import vtk
import math
import numpy as np
from skimage import measure, morphology

# --------- constants ---------

FILENAME = "data/altitudes.txt"

EARTH_RADIUS = 6_371_009

CAMERA_DISTANCE = 500_000

# North latitude
LAT_MIN = 45
LAT_MAX = 47.5

# East longitude
LON_MIN = 5
LON_MAX = 7.5

# Sea level
SEA_LEVEL = 0


# Spherical to cartesian
def to_cartesian(radius: float, latitude: float, longitude: float):
    """
    Translate spherical coordinate to cartesian coordinate
    inclination and azimuth must be in radian
    https://en.wikipedia.org/wiki/Spherical_coordinate_system
    """
    x = radius * math.sin(latitude) * math.sin(longitude)
    y = radius * math.cos(latitude)
    z = radius * math.sin(latitude) * math.cos(longitude)
    return x, y, z


# StructuredGrid use vtkPoints to be placed in the scene.
points = vtk.vtkPoints()

# Will store the attributes of the above points to define which color to use.
altitudes = vtk.vtkIntArray()

# First line contain size of grid
# Then it contains a grid of elevations.
with open(FILENAME) as file:
    rows, cols = map(int, file.readline().strip().split(" "))

    interval_azimuth = (LAT_MAX - LAT_MIN) / (rows - 1)
    interval_inclination = (LON_MAX - LON_MIN) / (cols - 1)

    elevations = np.array([[int(x) for x in line.strip().split(" ")] for line in file])

# For each point, we transform the spherical coordinate into cartesian coordinates in order to place them in the world
for i, elevs in enumerate(elevations):
    for j, elev in enumerate(elevs):
        (x, y, z) = to_cartesian(elev + EARTH_RADIUS,
                                 math.radians(LAT_MIN + i * interval_azimuth),
                                 math.radians(LON_MIN + j * interval_inclination))

        points.InsertNextPoint(x, y, z)

# Here we detect water surfaces.
labels = measure.label(elevations, connectivity=1)  # connectivity=1 -> to compare only adjacent cells.
# Then, we remove regions where area is too small.
lakes = morphology.remove_small_objects(labels, 512) > 0
# Use an arbitrary value to represent water
elevations[lakes] = 0

# For each point, we set his attribute (altitude) that will define his color. The altitude attribute is not necessary of
# the real world altitude. To color water we have defined that the altitude attribute should be 0. For example, for the
# points of the lakes, their attributes are set to 0 but their real altitude is not 0.
#
# Note: Here we make a second pass on each point. Another way to achieve this in one pass would have required to use
# a copy of the altitudes array. Without the copy or without the second pass, the lake points on the scene would have
# use the 0 altitude to determine their cartesian coordinates.
for i in range(0, rows):
    for j in range(0, cols):
        if elevations[i, j] < SEA_LEVEL:
            altitudes.InsertNextValue(0)
        else:
            altitudes.InsertNextValue(elevations[i, j])

# Create grid
# We had the choice between multiple data structures:
# - Image data (Not adapted because our point are not fully aligned)
# - Rectilinear grid (Not adapted for altitude)
# - Structured grid (Perfect for storing array of coordinates)
grid = vtk.vtkStructuredGrid()
grid.SetDimensions(rows, cols, 1)
grid.SetPoints(points)
grid.GetPointData().SetScalars(altitudes)

# Write the transformed grid to a vtkStructuredGrid file
writer = vtk.vtkStructuredGridWriter()
writer.SetFileName("structuredGrid.vtk")
writer.SetInputData(grid)
writer.Write()