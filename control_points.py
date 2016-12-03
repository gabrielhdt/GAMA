import image_elements
import scipy as sp


def pente_moy(pixel, contour, precision=5):
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
            pente += 5  #donner du poids aux pente infini sans écraser l'influence des autres points
        else:
            pente += (pixel.y-other_y)/(pixel.x-other_x)
    return pente/precision


def clockwise(p1, p2, p3):
    """test le sens des 3 points p1, p2, p3"""
    p1p2 = (p2.x - p1.x, p2.y - p1.y)
    p1p3 = (p3.x - p1.x, p3.y - p1.y)
    return p1p2[0] * p1p3[1] - p1p2[1] * p1p3[0] < 0


def find_inflexion(contour, start):
    """Renvoie le pixel correspondant au point de controle d arrivee de la portion de contour partant du pixel start:
     soit le premier point d'inflexion rencontre, soit le dernier point du contour"""
    start_index = contour.xys.index(start)
    n = len(contour.xys) - 1    # dernier indice disponible
    if start_index + 1 > n:     # si dépassement on renvoie le dernier pixel
        return contour.xys[-1]
    sens = clockwise(start, contour.xys[start_index+1], contour.xys[start_index+2])
    while clockwise(start, contour.xys[start_index+1], contour.xys[start_index+2]) == sens:
        if start_index + 3 > n:   # le dernier point de contour est atteint sans inflexion
            return contour.xys[-1]
        start_index += 1
    return contour.xys[start_index + 2]
    # on sort de la boucle while, donc ce pixel correspond au premier point d inflexion rencontre


def control(contour, start):
    """Renvoie le triple de points de controle pour tracer une courbe de
    Bezier quadratique sous forme d'un array scipy (concorde avec
    writesvg.add_polybezier)
    correspondant a la portion du contour qui commence au pixel start"""
    pente_s = pente_moy(start, contour)
    end = find_inflexion(contour, start)
    pente_e = pente_moy(end, contour)
    middle_x = (end.x - start.x) / (pente_s - pente_e)
    middle_y = start.y + pente_s * middle_x
    return sp.array([[start.x, start.y], [middle_x, middle_y], [end.x, end.y]])


def list_curves(contours):
    """Renvoie la liste de l ensemble des courbes a tracer,
    a partir de la liste de l ensemble des contours
    contours -- liste de image_elements.Contour()"""
    curves = []
    for contour in contours:
        start = contour.xys[0]
        c_end = contour.xys[-1]
        curve = sp.array([(0, 0), (0, 0), (0, 0)])
        while start != c_end:
            curve = control(contour, start)
            start = curve[2]
        curves.append(curve)
    return curves
