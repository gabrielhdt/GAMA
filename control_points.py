# -*- coding: utf-8 -*-
"""
Processing of control points, called waypoints and tangents. From contours to
Bezier curves
"""
import numpy as np
from numpy.linalg import norm
import image_elements


def clockwise(p1, p2, p3):
    """Renvoie True si la rotation pour aller du vecteur p2p1 p3p1 se fait en
    sens horaire (par calcul du déterminant)"""
    p1p2 = (p2.x - p1.x, p2.y - p1.y)
    p1p3 = (p3.x - p1.x, p3.y - p1.y)
    return p1p2[0] * p1p3[1] - p1p2[1] * p1p3[0] < 0


def vertan(points):
    """ Teste si la projection sur l'axe x des vecteurs {p2-p1, p3-p1, p4-p1}
    présente un maximum, i.e. si la tangente à la courbe passe à la verticale.
    points -- list of four image_elements.Pixel() objects
    returns -- True s'il y a un extremum
    """
    assert len(points) == 4
    projx = [None for _ in range(3)]
    for i in range(3):
        projx[i] = abs(points[i + 1].x - points[0].x)
    return projx[1] > projx[0] and projx[1] > projx[2]
    # Stricte ou large? Stricte: passage ponctuel, large direction constante
    # sur un intervalle.


def contloop(cont, start, stop):
    """Returns a slice of the contour cont. If stop > len(cont), the slice
    goes back to the beginning."""
    length = len(cont.xys)
    if stop <= length:
        return cont.xys[start:stop]
    else:
        return cont.xys[start:stop] + cont.xys[0:stop - length]


def nextop(contour, start, linedges=set()):
    """Renvoie le pixel correspondant au point de controle d arrivee
    de la portion de contour partant du pixel start:
    soit le premier point d'inflexion rencontre, soit le dernier point
    du contour.
    NB (+2, +1 dernière ligne): le pixel à renvoyer est celui sur lequel a
        été fait le dernier test, d'où les ajouts. +2 pour la tangente car
        test sur 4 pixels, on prend celui du milieu.
    contour -- image_elements.Contour() object
    start -- pixel de début, image_elements.Pixel() object
    """
    factor = len(contour.xys)//150
    cxys = contour.xys  # Shortcut
    start_index = cxys.index(start)
    n = len(cxys) - 1  # dernier indice disponible
    # Si dépassement, on renvoie le dernier pixel
    if start_index + 1 > n or start_index + 2 > n:
        return contour.xys[-1]
    # Initialisation
    found = (False, "")
    sens = clockwise(start, contour.xys[start_index + 1],
                     contour.xys[start_index + 2])
    new_sens = sens
    is_vert = vertan(contloop(contour, start_index, start_index + 4))
    if is_vert:  # Si tangente directement verticale
        return cxys[start_index + 2]
    # 0 for linedges, 1 for trespassing, 2 for clockwise, 3 for vertan
    while not found[0]:
        if cxys[start_index] in linedges:
            found = (True, 0)
        elif start_index + 3 > n:  # dernier point de contour atteint...
            found = (True, 1)  # ...sans inflexion
        start_index += 1  # Préparation de la prochaine boucle
        is_vert = vertan([start] + \
            contloop(contour, start_index + 1, start_index + 4))
        new_sens = clockwise(contour.xys[start_index],
                             contour.xys[(start_index + 1*factor)%n],
                             contour.xys[(start_index + 2*factor)%n])
        # and not found[0] avoids changing reason of leaving
        if new_sens != sens and not found[0]:
            found = (True, 2)
        elif is_vert and not found[0]:
            found = (True, 3)
    if found[1] == 0:
        return cxys[start_index - 1]  # Previous point
    elif found[1] == 1:
        return cxys[-1]
    elif found[1] == 3:  # Vérifie s'il y a une fin de ligne avant
        contemp = set(cxys[start_index - 1:start_index + 2]) & linedges
        if len(contemp) > 0:  # i.e. there is a linedge
            return contemp.pop()
        else:
            return cxys[start_index + 2] if is_vert else cxys[start_index + 1]
    elif found[1] == 2:
        if start_index + factor >= n:
            return cxys[-1]
        else:
            return cxys[start_index + factor]


def list_waypoints(contour):
    """Creates list of fly over waypoints. Waypoints are given by nextop,
    and one waypoint is added between the two (middle)
    contour -- Contour()
    """
    start = contour.xys[0]
    waypoints = [image_elements.Waypoint(start)]
    linedges = contour.scanlines()
    while start != contour.xys[-1]:
        currentindex = contour.xys.index(start)
        start = nextop(contour, start, linedges=linedges)
        linedges.discard(start)  # Avoids looping infinitely
        newindex = contour.xys.index(start)
        interwaypt = image_elements.Waypoint(contour.xys[(currentindex +
                                                          newindex)//2])
        waypoints.append(interwaypt)
        waypoints.append(image_elements.Waypoint(start))
    waypoints[-1] = image_elements.Waypoint(contour.xys[0])
    return waypoints


def usecub(start, end):
    """Sets fly by waypoint between start and end"""
    startarr = np.array((start.x, start.y))
    endarr = np.array((end.x, end.y))
    bagheera = 4e-1*norm(endarr - startarr)  # Brings cub to ctrlpoint
    startctls = (startarr + bagheera*start.paratan,
                 startarr - bagheera*start.paratan)
    endctls = endarr + bagheera*end.paratan, endarr - bagheera*end.paratan
    startctl = min(startctls, key=lambda x: norm(x - endarr))
    endctl = min(endctls, key=lambda x: norm(x - startarr))
    return startctl, endctl


def curves(contour):
    """Creates Bezier curves for contour
    contour -- Contour()
    """
    curves = []
    waypoints = list_waypoints(contour)
    n = len(waypoints)
    for i in range(n):  # Waypoint by waypoint
        before, after = waypoints[i - 1], waypoints[(i + 1)%n]
        distanceb = max(dist(contour, before, waypoints[i]), 3)
        distancea = max(dist(contour, waypoints[i], after), 3)
        precision = min(distancea, distanceb)
        waypoints[i].computan(contour, precision)
    for i in range(n - 1):
        start, end = waypoints[i], waypoints[i + 1]
        middle_s, middle_e = usecub(start, end)
        curves.append(np.array([[start.x, start.y],
                                [middle_s[0], middle_s[1]],
                                [middle_e[0], middle_e[1]],
                                [end.x, end.y]]))
    return curves


def validate_flyby(ctrlpt, wayptb, waypta):
    """Asserts whether ctrlpt is in the square delimited by wayptb and
    waypta
    ctrlpt -- tuple, coordinates of ctrlpt
    wayptb, waypta -- three Waypoint()
    """
    minx, maxx = min(waypta.x, wayptb.x), max(waypta.x, wayptb.x)
    miny, maxy = min(waypta.y, wayptb.y), max(waypta.y, wayptb.y)
    return minx <= ctrlpt[0] <= maxx and miny <= ctrlpt[1] <= maxy


def dist(cont, pix1, pix2):
    """Returns the number of pixels between pix1 and pix2 in contour cont
    cont -- image_elements.Contour(), with cont.xys a list, therefore ordered
    pix{1,2} -- image_elements.Pixel()
    """
    assert isinstance(cont.xys, list)
    lind = min(cont.xys.index(pix1), cont.xys.index(pix2))
    gind = max(cont.xys.index(pix1), cont.xys.index(pix2))
    length = len(cont.xys)
    return min(gind - lind, length - gind + lind)


def curves2curvemat(curves):
    """Converts a list of curves to a single array of control points. In
    addition it removes redondant points, which are the first point of each
    element of curves, except for curves[0].
    curves -- list of curves, i.e. list of arrays
    """
    curvemat = np.zeros((3 + 2*(len(curves) - 1), 2))
    curvemat[:3, ] = curves[0].copy()
    for i, curve in enumerate(curves[1:]):
        curvemat[2*i + 3:2*i + 5, ] = curve[1:, ].copy()  # Not 1st point
    return curvemat


def curves2curvematc(curvel):
    """Same as above for cubic curves
    curvel -- list of curves (i.e. of arrays)"""
    curvemat = np.zeros((4 + 3 * (len(curvel)-1), 2))
    curvemat[:4, ] = curvel[0].copy()
    for i, curve in enumerate(curvel[1:]):
        curvemat[3*i + 4:3*i + 7, ] = curve[1:, ].copy()  # Not 1st point
    return curvemat
