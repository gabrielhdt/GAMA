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
    upper = 300
    matread_loc = np.zeros_like(matng, dtype=bool)
    # Adding begpix to be sure to launche function (if begpix is alone)
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
    DEPRECATED
    """
    loop = image_elements.Contour([])  # Ordonné, donc ici liste
    inspix = set(contour_raw.xys).pop()
    neighbourhood = set(inspix.neighbours()) & set(contour_raw.xys)
    while len(neighbourhood) >= 1:
        if len(neighbourhood) > 1:
            inspix = (neighbourhood & set(inspix.closest_neighbours())).pop()
        else:
            inspix = neighbourhood.pop()
        loop.xys.append(inspix)
        contour_raw.xys.remove(inspix)
        neighbourhood = set(inspix.neighbours()) & set(contour_raw.xys)
    raw_minusloop = image_elements.Contour(contour_raw.xys.copy())
    return loop, raw_minusloop


def separate_all_contours(contour_raw):
    """DEPRECATED, use method"""

    def separate(contour_raw):
        if len(contour_raw.xys) < 1:
            return []
        else:
            loop, raw_minusloop = separate_contour(contour_raw)
            return [loop] + separate(raw_minusloop)
    return separate(contour_raw)


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


def directremove(contlist):
    """Removes smaller contours from bigger ones
    contlist -- list of Contour()
    """
    i = 0  # Counter
    imax = len(contlist)
    while i < imax:
        for j, cont in enumerate(contlist.copy()):
            if i >= j:  # Don't try to remove bigger from smaller...
                pass
            else:
                if contlist[i].hasequivin(cont):
                    contlist[j].disinclude(contlist[i])
        i += 1


def buildisinlist(contlist):
    """Returns a list indicated in which contour is included contlist[i], i.e.
    isinlist[k] = {j|contlist[k] has equivalent in j}
    contlist -- list of Contour()
    """
    isinlist = [None for _ in contlist]
    for i1, cont1 in enumerate(contlist):
        for i2, cont2 in enumerate(contlist[i1:]):  # Mind the shift
            if i1 == i2:
                pass
            elif cont1.hasequivin(cont2):
                isinlist[i1] = i2 + i1  # Shift
    return isinlist


def buildhasinlist(contlist):
    """Returns a list indicating which contour is included in contlist[k], i.e.
    hasinlist[k] = {j|contlist[j] has equivalent in k}
    cntlist -- list of Contour()
    """
    inclusionlist = [set() for _ in contlist]
    for i1, cont1 in enumerate(contlist):  # No need of last contour
        for i2, cont2 in enumerate(contlist[:i1]):  # As cont2 smaller
            if i1 == i2:
                pass
            elif cont2.hasequivin(cont1):  # If cont2 in cont1
                inclusionlist[i1].add(i2)
    return inclusionlist
