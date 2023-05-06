#!/usr/bin/env python
#
# Labo 2 - Partie 1
# Le but de ce fichier est de convertir le fichier altitudes.txt en un fichier vtkStructuredGrid.
#
# Auteurs: Mélissa Gehring et Tania Nunez

import vtk
from skimage import measure, morphology
import math
import numpy as np

# Nom des fichiers contenant les altitudes
INPUT_FILE = "data/altitudes.txt"
OUTPUT_FILE = "data/altitudes.vtk"

# Rayon de la terre
EARTH_RADIUS = 6371009

# Niveau de l'eau
WATER_LEVEL = 0

# Latitudes et longitudes de la zone à afficher
LAT_MIN = 45
LAT_MAX = 47.5
LON_MIN = 5
LON_MAX = 7.5

# Nous avons choisi de représenter les données sous forme de vtkStructuredGrid, 
# qui utilise des vtkPoints pour être placé
points = vtk.vtkPoints()

# Chaque point a un attribut altitude qui va ensuite déterminer sa couleur sur la carte
# Nous avons choisi un vtkIntArray car dans le fichier altitudes.txt, les altitudes sont des entiers
altitudes_color = vtk.vtkIntArray()

# Fonction qui convertit les coordonnées sphériques en coordonnées cartésiennes
def spherical_to_cartesian(radius: float, latitude: float, longitude: float):
    x = radius * math.sin(latitude) * math.sin(longitude)
    y = radius * math.cos(latitude)
    z = radius * math.sin(latitude) * math.cos(longitude)
    return x, y, z

# Pour chaque ligne du fichier altitudes.txt
with open(INPUT_FILE) as file:
    # On récupère le nombre de lignes et de colonnes
    rows, cols = [int(x) for x in next(file).strip().split(" ")]

    # On calcule l'intervalle à utiliser entre chaque point
    diff_lat = (LAT_MAX - LAT_MIN) / (rows - 1)
    diff_lon = (LON_MAX - LON_MIN) / (cols - 1)

    # On récupère les altitudes dans un tableau numpy
    altitudes_raw = np.array([[int(x) for x in line.strip().split(" ")] for line in file])


# Pour chaque altitute dans le tableau numpy, on convertit les coordonnées sphériques en coordonnées cartésiennes
for i in range(0, rows):
    for j in range(0, cols):
        # On récupère l'altitude
        altitude = altitudes_raw[i, j]

        # On calcule la latitude et la longitude
        latitude = math.radians(LAT_MIN + i * diff_lat)
        longitude = math.radians(LON_MIN + j * diff_lon)

        # On convertit les coordonnées sphériques en coordonnées cartésiennes
        x, y, z = spherical_to_cartesian(EARTH_RADIUS + altitude, latitude, longitude)

        # On ajoute le point aux vtkPoints ^
        points.InsertNextPoint(x, y, z)

# Après avoir ajouté les points, on peut détecter les lacs grâce à la librairie skimage
# On détecte les surfaces d'eau
water_surfaces = measure.label(altitudes_raw, connectivity=1)
# On enlève les régions trop petites
water_surfaces = morphology.remove_small_objects(water_surfaces, 512) > 0
# On applique les surfaces trouvées sur le tableau d'altitudes, en mettant les valeurs à 0
altitudes_raw[water_surfaces] = 0
altitudes_raw[altitudes_raw < WATER_LEVEL] = 0

# On ajoute les altitudes au vtkIntArray qui va déterminer la couleur des points
for i in range(0, rows):
    for j in range(0, cols):
            altitudes_color.InsertNextValue(altitudes_raw[i, j])

# Comme mentionné plus haut, nous avons choisi de représenter les données sous forme de vtkStructuredGrid
# Car c'est la structure qui est la plus adaptée pour stocker des tableaux de coordonnées et d'altitudes
structuredGrid = vtk.vtkStructuredGrid()
structuredGrid.SetDimensions(rows, cols, 1)
structuredGrid.SetPoints(points) # points contient les coordonnées
structuredGrid.GetPointData().SetScalars(altitudes_color) # altitudes_color contient les altitudes

# On écrit le vtkStructuredGrid dans un fichier vtk
writer = vtk.vtkStructuredGridWriter()
writer.SetFileName(OUTPUT_FILE)
writer.SetInputData(structuredGrid)
writer.Write()
