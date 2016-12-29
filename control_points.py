# -*- coding: utf-8 -*-
import image_elements
import scipy as sp


def pente_moy(pixel, contour, sens=1, precision=5):
    """pixel un objet de la classe Pixel
    contour un objet de la classe Contour
    sens orientation de la tangente
     precision nombre de pixel pris en compte
     renvoie la pente de la tangente au contour au point pixel """
    index = contour.xys.index(pixel)
    n = len(contour.xys)
    pente = 0
    for i in range(1, precision+1):
        if index + i * sens < 0:
            other_x = contour.xys[index + i * sens].x
            other_y = contour.xys[index + i * sens].y
        else:
            other_x = contour.xys[(index + i * sens) % n].x
            other_y = contour.xys[(index + i * sens) % n].y
        if pixel.x == other_x:
            return "inf"
        else:
            pente += (pixel.y-other_y)/(pixel.x-other_x)
    return pente/precision


def pente_moy2(pixel, contour, precision=5):
    """pixel un objet de la classe Pixel
    contour un objet de la classe Contour
    sens orientation de la tangente
     precision nombre de pixel pris en compte
     renvoie la pente de la tangente au contour au point pixel """
    index = contour.xys.index(pixel)
    n = len(contour.xys)
    pente = 0
    for i in range(-precision, precision+1):
        if index + i < 0:
            other_x = contour.xys[index + i].x
            other_y = contour.xys[index + i].y
        else:
            other_x = contour.xys[(index + i) % n].x
            other_y = contour.xys[(index + i) % n].y
        if pixel.x == other_x:
            return "inf"
        else:
            pente += (pixel.y-other_y)/(pixel.x-other_x)
    return pente/precision


def tan_param(startpix, contour, precision=5, sens=1):
    """Donne les coefficients de l'équation paramétrique de la tangente:
    G(t) = (x(t), y(t)) = (a*t, b*t), i.e. a et b. S'inspire
    grandement de pente_moy. Sens détermine si les points à moyenner sont en
    amont (sens = -1) ou en aval (sens = 1) de startpix.
    startpix -- image_elements.Pixel() object
    contour -- image_elements.Contour() object
    precision -- int, nombre de pixels sur lesquels sont fait la moyenne
    sens -- dans {-1, 1}
    """
    index = contour.xys.index(startpix)
    n = len(contour.xys)
    delta_x_mean = 0
    delta_y_mean = 0
    for i in range(1, precision + 1):
        other_x = contour.xys[(index + i*sens) % n].x
        other_y = contour.xys[(index + i*sens) % n].y
        delta_x_mean += other_x - startpix.x
        delta_y_mean += other_y - startpix.y
    return delta_x_mean/precision, delta_y_mean/precision


def paratan2slope(delta_xy):
    """Pente associée à la tangente paramétrée par delta_x, delta_y
    delta_xy -- itérable à deux éléments, delta_x en 0 et delta_y en 1"""
    assert len(delta_xy) == 2
    return "inf" if delta_xy[0] == 0 else delta_xy[1]/delta_xy[0]


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
    projy = [None for _ in range(3)]
    for i in range(3):
        projx[i] = abs(points[i + 1].x - points[0].x)
        projy[i] = abs(points[i + 1].y - points[0].y)
    x = projx[1] > projx[0] and projx[1] >= projx[2]
    y = projy[1] > projy[0] and projy[1] >= projy[2]
    return x or y
    # Stricte ou large?


def contloop(cont, start, stop):
    """Returns a slice of the contour cont. If stop > len(cont), the slice
    goes back to the beginning."""
    length = len(cont.xys)
    if stop <= length:
        return cont.xys[start:stop]
    else:
        return cont.xys[start:stop] + cont.xys[0:stop - length]


def find_inflexion(contour, start):
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
    cxys = contour.xys  # Shortcut
    start_index = contour.xys.index(start)
    n = len(contour.xys) - 1    # dernier indice disponible
    if start_index + 1 > n or start_index + 2 > n:   # si dépassement on renvoie le dernier pixel
        return contour.xys[-1]
    # Initialisation
    sens = clockwise(start, contour.xys[start_index + 1],
                     contour.xys[start_index + 2])
    new_sens = sens
    is_vert = vertan(contloop(contour, start_index, start_index + 4))
    if is_vert:  # Si tangente directement verticale
        return cxys[start_index + 2]
    while new_sens == sens and not is_vert:
        if start_index + 3 > n:  # dernier point de contour atteint...
            return contour.xys[-1]  # ...sans inflexion
        start_index += 1  # Préparation de la prochaine boucle
        is_vert = vertan([start] + \
            contloop(contour, start_index + 1, start_index + 4))
        new_sens = clockwise(start, contour.xys[start_index + 1],
                             contour.xys[start_index + 2])
    return cxys[start_index + 2] if is_vert else cxys[start_index + 1]


def control(contour, start):
    """Renvoie le triple de points de controle pour tracer une courbe de
    Bezier quadratique sous forme d'un array scipy (concorde avec
    writesvg.add_polybezier)
    correspondant a la portion du contour qui commence au pixel start
    Est censée être lancée par list_curves.
    """
    end = find_inflexion(contour, start)
    distance = dist(contour, start, end)
    precision = min(distance, 5)  # S'il n'y a pas assez de pixels
    pente_s = paratan2slope(tan_param(start, contour, precision, sens=1))
    pente_e = paratan2slope(tan_param(end, contour, precision, sens=-1))
    if pente_s == pente_e:  # A préciser, utilisation d'une cubique?
        middle_x = (start.x + end.x)/2
        middle_y = (start.y + end.y)/2
    elif "inf" in (pente_e, pente_s):
        if pente_s == "inf":
            middle_x = start.x
            middle_y = end.y + pente_e * (end.x - start.x)
        elif pente_e == "inf":
            middle_x = end.x
            middle_y = start.y + pente_s * (start.x - end.x)
    elif 0 in (pente_e, pente_s):
        if pente_s == 0:
            middle_x = end.x + (start.y - end.y)/pente_e
            middle_y = start.y
        elif pente_e == 0:
            middle_x = start.x + (end.y - start.y)/pente_s
            middle_y = end.y
    else:   #pente_s != 0 and pente_e != 0:
        coef = 1/(pente_s - pente_e)
        middle_x = coef*(pente_s*start.x - pente_e*end.x + end.y - start.y)
        middle_y = pente_s*(middle_x - start.x) + start.y
    return sp.array([[start.x, start.y], [middle_x, middle_y], [end.x, end.y]])


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


def list_curves(contours):
    """Renvoie la liste de l ensemble des courbes a tracer,
    a partir de la liste de l ensemble des contours
    contours -- liste de image_elements.Contour()"""
    curves = []
    for contour in contours:
        start = contour.xys[0]
        c_end = contour.xys[-1]
        while start != c_end:
            curve = control(contour, start)
            start = image_elements.Pixel(curve[2][0], curve[2][1])
            curves.append(curve)
    return curves


def curves2curvemat(curves):
    """Converts a list of curves to a single array of control points. In
    addition it removes redondant points, which are the first point of each
    element of curves, except for curves[0].
    curves -- list of curves, i.e. list of arrays
    """
    curvemat = sp.zeros((3 + 2*(len(curves) - 1), 2))
    curvemat[:3, ] = curves[0].copy()
    for i, curve in enumerate(curves[1:]):
        curvemat[2*i + 3:2*i + 5, ] = curve[1:, ].copy()  # Not 1st point
    return curvemat
