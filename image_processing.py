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
    """
    regroupe sous formes d'intervalles les couleurs de la matrice
    en noir et blanc. Traitement spécial pour le 0 à cause de la condition
    mat_condidion1
    A appliquer AVANT l'ajout de bordure
    """
    matfilt = np.ones_like(matricenb)
    couleur = np.arange(0, 1 + seuil, seuil)
    # Special treatment for 0s...
    cond = np.where(matricenb == 0, True, False)
    matfilt[cond] = (couleur[0] + couleur[1])/2*np.ones_like(matricenb[cond])
    for i in range(len(couleur[:-1])):
        mat_condition1 = np.where(matricenb > couleur[i], True, False)
        mat_condition2 = np.where(matricenb <= couleur[i + 1], True, False)
        mat = np.logical_and(mat_condition1, mat_condition2)
        matfilt[mat] = min((2*i+1)*seuil/2, 1) * np.ones_like(matricenb[mat])
    return matfilt


def add_border(matng):
    """Adds a border of 7s (not a greyscale) to the matrix matng. Apply
    AFTER regroupement_couleur.
    matng -- greyscale matrix sp.array of floats between 0 and 1
    returns -- a new matrix with borders on each side (lines and rows of 7s)
    """
    (row, col) = matng.shape
    matng_border = 7*np.ones((row+2, col+2), dtype=float)
    matng_border[1:row+1, 1:col+1] = matng.copy()
    return matng_border


def detection_contour(matng, begpix, seuil=0.01):
    """Detects a contour circling a zone of a colour, contour is outside the
    zone of same colour (avoids issues of contours sharing pixels)
    matng -- greylevel matrix
    begpix -- pixel on which the recursion is to begin
    seuil -- could be removed, because of regroupement_couleur
    """
    upper = 300
    matread_loc = np.zeros_like(matng, dtype=bool)
    # Adding begpix to be sure to launch function (if begpix is alone)
    notreadneighbours = begpix.closest_neighbours() | set((begpix, ))
    begcolour = matng[begpix.x, begpix.y]
    # Removing pixels from another zone from notreadneighbours
    for neighbour in notreadneighbours.copy():
        neighcolour = matng[neighbour.x, neighbour.y]
        if abs(neighcolour - begcolour) > seuil:
            notreadneighbours.remove(neighbour)
    contour = image_elements.Contour(set())

    def contourec(inspix, notreadneighbours, k=0):
        """
        notreadneighbours -- list of pixels which haven't been inspix yet, i.e.
            a pixel in notreadneighbours may have been compared with an inspix
            while its neighbours haven't been
        inspix -- Pixel() inspected, each neighbour's colour is compared with
            the former's to determine whether inspix is the last pixel of the
            colour. If so, it will be added to contpart, and then to contour.
            It is removed from the notreadneighbours when acquired via pop()
        k -- counter, to avoid MaxRecursionDepth
        """
        matread_loc[inspix.x, inspix.y] = True
        neighbourhood = inspix.closest_adjs(matread_loc)
        notreadneighbours |= neighbourhood
        contour_found = False
        inscolour = matng[inspix.x, inspix.y]
        contour_part = set()
        for neighbour in neighbourhood:
            neighcolour = matng[neighbour.x, neighbour.y]
            if abs(neighcolour - inscolour) > seuil:
                contour_found = True
                notreadneighbours.remove(neighbour)
                contour_part.add(neighbour)
            # If not other colour, don't read it again. However, its
            # neighbours will be inspected, as it has been added to
            # notreadneighbours
            else:
                matread_loc[neighbour.x, neighbour.y] = True
        if contour_found:
            return contour_part
        elif k == upper or len(notreadneighbours) == 0:
            return set((None, ))
        else:
            nextinspix = notreadneighbours.pop()
            return contourec(nextinspix, notreadneighbours, k + 1)

    while len(notreadneighbours) > 0:
        begpix = notreadneighbours.pop()
        contour.xys |= contourec(begpix, notreadneighbours)
    contour.xys.discard(None)
    # Contour attributes
    return contour, matread_loc


def contours_image(matngb, seuil=0.01):
    """
    Donne l'ensemble des contours de la matrice en niveaux de gris avec
    bordure matngb.
    matngb -- np.array, greyscale matrix, with added border
    seuil -- float, min difference of colour between two pixels to create
        a contour
    """
    contset = set()
    matread = np.zeros_like(matngb, dtype=bool)
    while False in matread:
        # Finds false in matread without border
        notread = np.where(matread == False)
        notread = notread[0][0], notread[1][0]
        # + 1's compensate border, avoid falling in the border
        begpix = image_elements.Pixel(notread[0], notread[1])
        cont, upmatread = detection_contour(matngb, begpix, seuil)
        matread += upmatread
        contset.add(cont)
    contset = contset - set((image_elements.Contour([]), ))  # Removes empty
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


def compare_cont(cont1, cont2):
    """Compares contours returning a float between 0 and 1, corresponding
    to the resemblance of the two contours (1: a contour is a subset of the
    other, 0 they are disjoint).
    """
    if len(cont1.xys) > len(cont2.xys):  # Asserts cont1 is smaller than cont2
        cont1, cont2 = cont2, cont1
    return len(set(cont1.xys) & set(cont2.xys))/len(cont1.xys)


def remove_double(contset):
    """Removes contours that are twice in contset. Modifies contset in place"""
    for cont1 in contset.copy():
        for cont2 in contset.copy() - set((cont1, )):
            resemblance = compare_cont(cont1, cont2)
            bcont = max(cont1, cont2)  # Bigger contour
            if resemblance >= 0.75 and bcont in contset:
                contset.remove(bcont)
