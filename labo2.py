#!/usr/bin/env python
#
# Labo 2 - Partie 2
# Le but de ce fichier est d'utiliser le fichier altitudes.vtk pour le visualiser.
#
# Auteurs: Mélissa Gehring et Tania Nunez


import vtk
import math

# Nom du fichier contenant le vtkStructuredGrid
INPUT_FILE = "data/altitudes.vtk"

# Rayon de la terre
EARTH_RADIUS = 6371009

# Niveau de l'eau
WATER_LEVEL = 0

# Latitudes et longitudes de la zone à afficher
LAT_MIN = 45
LAT_MAX = 47.5
LON_MIN = 5
LON_MAX = 7.5

# Distance de la caméra par rapport au centre de la zone
CAMERA_DISTANCE = 500000


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

# Lecture du fichier .vtk contenant le vtkStructuredGrid
reader = vtk.vtkStructuredGridReader()
reader.SetFileName(INPUT_FILE)
reader.Update()

# Obtention du vtkStructuredGrid
grid = reader.GetOutput()

ctf = vtk.vtkColorTransferFunction()
ctf.AddRGBPoint(0, 0.513, 0.49, 1)  # Water, Blue (0x827CFF) for water
ctf.AddRGBPoint(1, 0.157, 0.325, 0.141)  # Grass, Dark green (0x285223) for low altitude
ctf.AddRGBPoint(500, 0.219, 0.717, 0.164)  # Grass, Light green (0x37B629) for middle (low) altitude
ctf.AddRGBPoint(900, 0.886, 0.721, 0.364)  # Rock, Sort of yellow/brown (0xE1B75C)) for middle (high) altitude
ctf.AddRGBPoint(1600, 1, 1, 1)  # Snow, White (0xFFFFFF) for high altitude (for cliffs)

# --------- Mapper - Actor ---------
mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(grid)
mapper.SetLookupTable(ctf)

gridActor = vtk.vtkActor()
gridActor.SetMapper(mapper)

# --------- Render ---------
renderer = vtk.vtkRenderer()
renderer.AddActor(gridActor)

# Setting focal point to center of the displayed area.
fx, fy, fz = to_cartesian(EARTH_RADIUS, math.radians((LAT_MIN + LAT_MAX) / 2), math.radians((LON_MIN + LON_MAX) / 2))
renderer.GetActiveCamera().SetFocalPoint([fx, fy, fz])

# Setting camera position to center of the zone, elevated by CAMERA_DISTANCE (500km currently)
cx, cy, cz = to_cartesian(EARTH_RADIUS + CAMERA_DISTANCE, math.radians((LAT_MIN + LAT_MAX) / 2),
                          math.radians((LON_MIN + LON_MAX) / 2))
renderer.GetActiveCamera().SetPosition([cx, cy, cz])
renderer.GetActiveCamera().SetClippingRange(0.1, 1_000_000)

renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(renderer)
renWin.SetSize(800, 800)

# --------- Interactor ---------
intWin= vtk.vtkRenderWindowInteractor()
intWin.SetRenderWindow(renWin)

style = vtk.vtkInteractorStyleTrackballCamera()
intWin.SetInteractorStyle(style)

# --------- Print image ---------
renWin.Render()
w2if = vtk.vtkWindowToImageFilter()
w2if.SetInput(renWin)
w2if.Update()
filename = "Map_Screenshot_Sea_Level_" + str(WATER_LEVEL) + ".png"
writer = vtk.vtkPNGWriter()
writer.SetFileName(filename)
writer.SetInputData(w2if.GetOutput())
writer.Write()

intWin.Initialize()
intWin.Start()
