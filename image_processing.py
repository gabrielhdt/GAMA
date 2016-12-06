#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Matrice de niveaux de gris, "moyenne" pour chaque triplet RGB.
Classement par seuils de niveaux de gris,detection des contours pour
chaque zone.
Notations:
Matriceniveauxdegris: niveau de gris entre 0 et 1, avec coefficients
(0.2126,0.7152,0.0722) pour (R,G,B)/ Wikipedia
"""
import scipy.misc as smp
import numpy as np
import matplotlib.pyplot as plt
import random
import image_elements


def Matriceniveauxdegris(matriceRGB):
    (a,b,c)=matriceRGB.shape #ici matriceRGB est la matrice RGB de l'image choisie
    Matrice_gray=np.zeros(shape=(a,b)) #Matrice_gray pour Matriceniveauxdegris
    for i in range (a):
        for j in range (b):
            Matrice_gray[i][j]+=((matriceRGB[i][j][0]/255)*0.2126+(matriceRGB[i][j][1]/255)*0.7152+(matriceRGB[i][j][2]/255)*0.0722)
    return Matrice_gray

def ajout_bord(matriceNG):
    # retourne la matrice de départ avec un contour formé de 2
    (lig, col) = matriceNG.shape
    # matrice NG designe la matrice en niveau de gris de taille (lignes, colonnes)
    mat_ajoutbord = 2*np.ones((lig+2, col+2), dtype=float)
    #initialise une matrice de taille (lig+1, col+1) avec des un
    for i in range(1, lig):
        for j in range(1, col):
            mat_ajoutbord[i][j] = matriceNG[i][j]
    return mat_ajoutbord

def AdrienContour(matriceNG):   #NotEgocentric
    # retourne la matrice de départ avec un tres fameux contour d Adrien
    (lig, col) = matriceNG.shape
    # matrice NG designe la matrice en niveau de gris de taille (lignes, colonnes)
    mat_ajoutcontour = 7 * np.ones((lig+2, col+2), dtype=int)
    #initialise une matrice de taille (lig+2, col+2) avec des septs (pourquoi pas?)
    mat_ajoutcontour[1: lig+1, 1: col+1] = matriceNG
    return mat_ajoutcontour


def detection_contour(matriceNG, pixel, seuil, pretendants, contour_inter,
                      matread):
    """
    matriceNG -- grey level matrix
    pixel -- inspected pixel
    seuil -- minimum difference value between levels of grey to
        differentiate colours
    pretendants -- old neighbours that weren't in contour
    contour_int -- contour built
    matread -- boolean matrix
    """
    matread[pixel.x, pixel.y] = True
    colorpixel = matriceNG[pixel.x, pixel.y]
    voisins = pixel.adjs(matread) + pretendants
    voisins_contourless = voisins[:]  # Slicing pour copie...
    if colorpixel <= 1:  # Si pas dans le bord ajouté artificiellement
        for vois in voisins:
            matread[vois.x, vois.y] = True
            colorvois = matriceNG[vois.x][vois.y]
            if abs(colorpixel - colorvois) > seuil:
                contour_inter.xys.append(vois)
                voisins_contourless.remove(vois)
    else:
        pass
    if len(voisins_contourless) > 0:
        pretendant = voisins_contourless[1:]
        return detection_contour(matriceNG, voisins_contourless[0],
                                 seuil, pretendant, contour_inter, matread)
    else:
        return contour_inter

def contour_image(matriceNG, seuil):
    # prend en argument une matrice en niveau de gris à laquelle on a rajouté un contour de 1
    # et un seuil de couleurs pour classer les pixels
    # renvoie la liste des contours de l'image
    (line, column) = matriceNG.shape
    liste_contours = []
    matread = sp.ones_like(matriceNG, dtype=bool)
    matread[1:-1, 1:-1] = sp.zeros_like(matng[1:-1, 1:-1], dtype=bool)
    pretendants = []
    contour_inter = image_elements.Contour([])
    for i in range(line):
        for j in range(column):
            liste_contours.append(detection_contour(matriceNG, image_elements.Pixel(i,j), seuil, pretendants, contour_inter, matread))
    return liste_contours

def visualisation_contour(matriceNG,liste_contours):
    (lin, col) = matriceNG.shape
    visu = np.zeros((lin, col))
    for contour in liste_contours :
        pixels = contour.xys
        for pixel in pixels :
            i = pixel.x
            j = pixel.y
            visu[i][j] = 1
    return visu


#M = np.arrange(0,1).reshape((100,100))
#Mo = ajout_bord(M)
#pixel = image_element.Pixel(50, 50)
#seuil = 0.1
#pretendants = []
#contour_inter = image_element.Contour([])
#print(detection_contour(Mo, pixel, seuil, pretendants, contour_inter))
#print(M)
#M = np.zeros((4,7))
#print(ajout_bord(M))


def separate_contour(contour_raw):
    """Sépare les contours présents dans contour_raw, qui
    est susceptible d'en contenir 2. Au nouveau contour on ajoute les pixels
    adjacents à celui étudié, qui sont dans le contour, et pas déjà dans le
    lacet.
    contour_raw -- contour pouvant en contenir en réalité 2;
        image_elements.Contour() object
    """
    loop = image_elements.Contour([])
    refpix = contour_raw.xys[0]
    inspix = (set(contour_raw.xys) & set(refpix.adjs())).pop()
    while inspix != refpix:
        loop.xys.append(inspix)
        inspix = (set(inspix.adjs()) & set(contour_raw.xys) -\
                  set(loop.xys)).pop()
    return loop


if __name__ == "__main__":
    MatriceRGB = smp.imread("essai.png")
    matrix = Matriceniveauxdegris(MatriceRGB)
    plt.imshow(matrix, cmap=plt.cm.gray)
    plt.show()
    pixel = matrix[150][150]
    contour_inter = image_elements.Contour([])

#Liste de liste pour les zones (liste de contours avec une couleur et les coordonees de chaque points du contour)
#Class Pixel
#Class Contour
