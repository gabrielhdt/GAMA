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
import image_elements


def Matriceniveauxdegris(matriceRGB):
    (a,b,c)=matriceRGB.shape #ici matriceRGB est la matrice RGB de l'image choisie
    Matrice_gray=np.zeros(shape=(a,b)) #Matrice_gray pour Matriceniveauxdegris
    for i in range (a):
        for j in range (b):
            Matrice_gray[i][j]+=((matriceRGB[i][j][0]/255)*0.2126+(matriceRGB[i][j][1]/255)*0.7152+(matriceRGB[i][j][2]/255)*0.0722)
    return Matrice_gray

def regroupement_couleur(matricenb, seuil):
    # regroupe sous formes d'intervalles les couleurs de la matrice
    # en noir et blanc
    couleur = np.arange(0,1,seuil)
    n = len(couleur)
    for i in range(n) :
        mat_condition1 = np.where(i*seuil < matricenb, True, False)
        mat_condition2 = np.where(matricenb <=(i+1)*seuil, True, False)
        mat = np.logical_and(mat_condition1,mat_condition2)
        matricenb[mat] = (2*i+1)*seuil/2 * np.ones_like(matricenb[mat])
    return matricenb


def add_border(matng):
    """Adds a border of 7s (not a greyscale) to the matrix matng. Credits
    goes to Aurélie and Adrien, for their remarkable work in the world
    of borders.
    matng -- greyscale matrix sp.array of floats between 0 and 1
    returns -- a new matrix with borders on each side (lines and rows of 7s)
    """
    (row, col) = matng.shape
    matng_border = 7*np.ones((row+2, col+2), dtype=float)
    matng_border[1:row+1, 1:col+1] = matng.copy()
    return matng_border


def detection_contour(matng, pixel, seuil, pretendants, contour_inter,
                      matread):
    """
    matng -- grey level matrix
    pixel -- inspected pixel
    seuil -- minimum difference value between levels of grey to
        differentiate colours
    pretendants -- old neighbours that weren't in contour
    contour_int -- contour built
    matread -- boolean matrix
    """
    matread[pixel.x, pixel.y] = True
    colorpixel = matng[pixel.x, pixel.y]
    voisins = pixel.adjs(matread) + pretendants
    voisins_contourless = voisins[:]  # Slicing pour copie...
    if colorpixel <= 1:  # Si pas dans le bord ajouté artificiellement
        for vois in voisins:
            matread[vois.x, vois.y] = True
            colorvois = matng[vois.x][vois.y]
            if abs(colorpixel - colorvois) > seuil:
                contour_inter.xys.append(vois)
                voisins_contourless.remove(vois)
    else:
        pass
    if len(voisins_contourless) > 0:
        pretendant = voisins_contourless[1:]
        return detection_contour(matng, voisins_contourless[0],
                                 seuil, pretendant, contour_inter, matread)
    else:
        return contour_inter


def detection_contour_subfct(matng, pixel, seuil=0.01, matread=None):
    """
    Comme ci-dessus, mais en utilisant une sous fonction. Pourra aider pour
    la méthode dynamique.
    """
    if matread is None:
        matread = np.ones_like(matng, dtype=bool)
        matread[1:-1, 1:-1] = np.zeros_like(matng[1:-1, 1:-1], dtype=bool)
    contour_inter = image_elements.Contour([])

    def detecont_rec(inspix, neighbourhood):
        colour = matng[inspix.x, inspix.y]
        neighbourhood_contourless = neighbourhood[:]
        if colour <= 1:  # If not in added border
            for neighbour in neighbourhood:
                matread[neighbour.x, neighbour.y] = True
                neighbour_colour = matng[neighbour.x, neighbour.y]
                if abs(colour - neighbour_colour) > seuil:
                    contour_inter.xys.append(neighbour)
                    neighbourhood_contourless.remove(neighbour)
        if len(neighbourhood_contourless) > 0:
            nextinspix = neighbourhood_contourless.pop(0)
            nextneighbourhood = nextinspix.adjs(matread) + \
                neighbourhood_contourless
            return detecont_rec(nextinspix, nextneighbourhood)
        else:
            return contour_inter

    return detecont_rec(pixel, pixel.adjs(matread)), matread


def contours_image(matngb, seuil=0.01):
    """
    Donne l'ensemble des contours de la matrice en niveaux de gris avec
    bordure matngb.
    matngb -- np.array, greyscale matrix, with added border
    seuil -- float, min difference of colour between two pixels to create
        a contour
    """
    contset = set()
    matread = np.ones_like(matngb, dtype=bool)
    matread[1:-1, 1:-1] = np.zeros_like(matngb[1:-1, 1:-1], dtype=bool)
    while False in matread:
        notread = np.where(matread == False)
        notread = notread[0][0], notread[1][0]
        begpix = image_elements.Pixel(notread[0], notread[1])
        cont, matread = detection_contour_subfct(matngb, begpix,
                                                 seuil, matread)
        contset.add(cont)
    contset = contset - set((image_elements.Contour([]), ))
    return contset


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


def separate_contour(contour_raw):
    """Sépare les contours présents dans contour_raw, qui
    est susceptible d'en contenir 2. Au nouveau contour on ajoute les pixels
    adjacents à celui étudié, qui sont dans le contour, et pas déjà dans le
    lacet.
    contour_raw -- contour pouvant en contenir en réalité 2;
        image_elements.Contour() object
    returns -- loop, containing one loop, i.e. a contour object of contiguous
        pixels, and raw_minusloop, the contour_raw without loop, i.e. the other
        contour.
    """
    loop = image_elements.Contour([])
    refpix = contour_raw.xys[0]
    loop.xys.append(refpix)
    inspix = (set(contour_raw.xys) & set(refpix.neighbours())).pop()
    while inspix != refpix:
        loop.xys.append(inspix)
        contour_raw.xys.remove(inspix)
        neighbourhood = set(inspix.neighbours()) & set(contour_raw.xys)
        if len(neighbourhood) > 1:
            inspix = (neighbourhood & set(inspix.closest_neighbours())).pop()
        else:
            inspix = neighbourhood.pop()
    raw_minusloop = image_elements.Contour(contour_raw.xys[:])  # Copie
    raw_minusloop.xys.remove(refpix)
    return loop, raw_minusloop

def separate_all_contours(contour_raw):
    liste_contour = []
    def separate(contour_raw, liste_contour):
        if len(contour_raw)<1:
            return []
        else :
            loop, raw_minusloop = separate_contour(contour_raw)
            liste_contour.apend(loop)
            separate(raw_minusloop,liste_contour)
        return liste_contour
    return separate(contour_raw, liste_contour)


if __name__ == "__main__":
    MatriceRGB = smp.imread("essai.png")
    matrix = Matriceniveauxdegris(MatriceRGB)
    plt.imshow(matrix, cmap=plt.cm.gray)
    plt.show()
    pixel = matrix[150][150]
    contour_inter = image_elements.Contour([])
