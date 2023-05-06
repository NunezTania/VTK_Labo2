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

# Nom de l'image à sauvegarder
OUTPUT_FILE = "data/rendu.png"

# Rayon de la terre
EARTH_RADIUS = 6371009

# Niveau pour les couleurs
WATER_LEVEL = 0
DARK_GRASS_LEVEL = 1
LIGHT_GRASS_LEVEL = 550
ROCK_LEVEL = 900
SNOW_LEVEL = 1600

# Latitudes et longitudes de la zone à afficher
LAT_MIN = 45
LAT_MAX = 47.5
LON_MIN = 5
LON_MAX = 7.5

# Hauteur de la caméra
CAMERA_ALT = 400000

# Fonction qui convertit les coordonnées sphériques en coordonnées cartésiennes
def spherical_to_cartesian(radius: float, latitude: float, longitude: float):
    x = radius * math.sin(latitude) * math.sin(longitude)
    y = radius * math.cos(latitude)
    z = radius * math.sin(latitude) * math.cos(longitude)
    return x, y, z

# Création de la lookuptable des couleurs pour les altitudes
ctf = vtk.vtkColorTransferFunction()
# Surface d'eau : #508ecc
ctf.AddRGBPoint(WATER_LEVEL, 0.314, 0.553, 0.8)
# Herbe foncée : #54a339
ctf.AddRGBPoint(DARK_GRASS_LEVEL, 0.329, 0.639, 0.224)
# Herbe claire : #d2f09c
ctf.AddRGBPoint(LIGHT_GRASS_LEVEL, 0.824, 0.941, 0.612)
# Roche : #d4ba90
ctf.AddRGBPoint(ROCK_LEVEL, 0.831, 0.729, 0.565)
# Neige : #ffffff
ctf.AddRGBPoint(SNOW_LEVEL, 1, 1, 1)

# Lecture du fichier .vtk contenant le vtkStructuredGrid
reader = vtk.vtkStructuredGridReader()
reader.SetFileName(INPUT_FILE)
reader.Update()

# Obtention du vtkStructuredGrid
structuredGrid = reader.GetOutput()

# Mapper
gridMapper = vtk.vtkDataSetMapper()
gridMapper.SetInputData(structuredGrid)
gridMapper.SetLookupTable(ctf)

# Actor
gridActor = vtk.vtkActor()
gridActor.SetMapper(gridMapper)

# Render 
ren = vtk.vtkRenderer()
ren.AddActor(gridActor)

# Paramètres de la caméra du rendu
# On calcule la position de la caméra en coordonnées cartésiennes
camX, camY, camZ = spherical_to_cartesian(EARTH_RADIUS + CAMERA_ALT, math.radians((LAT_MIN + LAT_MAX) / 2),
                          math.radians((LON_MIN + LON_MAX) / 2))
ren.GetActiveCamera().SetPosition([camX, camY, camZ])
# Clipping range de la caméra (pour éviter que la caméra ne coupe la terre)
ren.GetActiveCamera().SetClippingRange(0.1, 1000000)

# Paramètres du focal point de la caméra
# On calcule le focal point en coordonnées cartésiennes
fpX, fpY, fpZ = spherical_to_cartesian(EARTH_RADIUS, math.radians((LAT_MIN + LAT_MAX) / 2), math.radians((LON_MIN + LON_MAX) / 2))
ren.GetActiveCamera().SetFocalPoint([fpX, fpY, fpZ])

# Render window
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(900, 900)

# Sauvegarder l'image
renWin.Render()
w2if = vtk.vtkWindowToImageFilter()
w2if.SetInput(renWin)
w2if.Update()
writer = vtk.vtkPNGWriter()
writer.SetFileName(OUTPUT_FILE)
writer.SetInputData(w2if.GetOutput())
writer.Write()

# Interactor
intWin= vtk.vtkRenderWindowInteractor()
intWin.SetRenderWindow(renWin)
style = vtk.vtkInteractorStyleTrackballCamera()
intWin.SetInteractorStyle(style)

# Initialisation et démarrage de l'interactor
intWin.Initialize()
intWin.Start()
