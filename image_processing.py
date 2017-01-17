# -*- coding: utf-8 -*-
"""
Operations performed on the image, from raw image to contours
"""
import numpy as np
import image_elements


def pic2greylvl(matrgb):
    """Coefficient found on wikipedia"""
    (a, b, c) = matrgb.shape
    matgl = np.zeros(shape=(a, b))  # matrix greylevels
    for i in range(a):
        for j in range(b):
            matgl[i][j] += ((matrgb[i][j][0]/255)*0.2126 +
                            (matrgb[i][j][1]/255)*0.7152 +
                            (matrgb[i][j][2]/255)*0.0722)
    return matgl


def colourgrouping(matgl, ngl):
    """Limits the number of greylevels in the image. Apply it BEFORE
    adding border.
    matgl -- greylevels matrix, coefficients in [0, 1]
    ngl -- int, number of grey levels to keep
    """
    matfilt = np.ones_like(matgl)
    greylevels = np.linspace(0, 1, ngl)
    cond = np.where(matgl == 0, True, False)
    matfilt[cond] = 0*np.ones_like(matgl[cond])
    for i in range(ngl - 1):
        mat_condition1 = np.where(matgl > greylevels[i], True, False)
        mat_condition2 = np.where(matgl <= greylevels[i + 1], True, False)
        mask = np.logical_and(mat_condition1, mat_condition2)
        matfilt[mask] = (((greylevels[i] + greylevels[i + 1])/2) *
                         np.ones_like(matgl[mask]))
    return matfilt


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


def detection_contour(matrgb, matng, begpix):
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
        if abs(neighcolour - begcolour) > 0:
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
            if abs(neighcolour - inscolour) > 0:
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
    # Setting colour
    truecoords = np.where(matread_loc)
    coord = truecoords[0][0], truecoords[1][0]
    colour = matrgb[coord[0] - 1, coord[1] - 1, :]
    contour.colour = vec2hex(colour)
    return contour, matread_loc


def clamp(x):
    return max(0, min(x, 255))


def vec2hex(colour_contour):
    """
    Converts RGB colour to a 6 digit code
    corresponding to the hexadecimal form
    """
    r = colour_contour[0]
    g = colour_contour[1]
    b = colour_contour[2]
    return "#{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))


def contours_image(matrgb, ngl=8):
    """
    Donne l'ensemble des contours de la matrice en niveaux de gris avec
    bordure matngb.
    matngb -- np.array, greyscale matrix, with added border
    ngl -- number of greylevels to keep in final image
    """
    matngb = pic2greylvl(matrgb)
    matngb = colourgrouping(matngb, ngl)
    matngb = add_border(matngb)
    contset = set()
    matread = np.zeros_like(matngb, dtype=bool)
    while False in matread[1:-1, 1:-1]:
        # Finds false in matread without border
        notread = np.where(matread[1:-1, 1:-1] == False)
        notread = notread[0][0] + 1, notread[1][0] + 1
        # + 1's compensate border, avoid falling in the border
        begpix = image_elements.Pixel(notread[0], notread[1])
        cont, upmatread = detection_contour(matrgb, matngb, begpix)
        matread += upmatread
        contset.add(cont)
    contset = contset - set((image_elements.Contour([]), ))  # Removes empty
    return contset


def ordercontlist(contlist):
    """Orders contour in contlist"""
    contlist.sort(key=lambda cont: min((pix.x for pix in cont.xys)))
