import image_elements
import scipy as sp


def pente_moy(pixel, contour, precision=1):
    """pixel un objet de la classe Pixel
    contour un objet de la classe Contour
    sens orientation de la tangente
     precision nombre de pixel pris en compte
     renvoie la pente de la tangente au contour au point pixel """
    index = contour.xys.index(pixel)
    n = len(contour.xys)
    pente = 0
    for i in range(-precision,precision+1):
        if index + i < 0:
            other_x = contour.xys[index + i].x
            other_y = contour.xys[index + i].y
        else:
            other_x = contour.xys[(index + i) % n].x
            other_y = contour.xys[(index + i) % n].y
        try:
            pente += (pixel.y-other_y)/(pixel.x-other_x)
        except:
            pass
    return pente/(precision)


def clockwise(p1,p2,p3):
    """test le sens des 3 points p1, p2, p3"""
    p1p2 = (p2.x - p1.x, p2.y - p1.y)
    p1p3 = (p3.x - p1.x, p3.y - p1.y)
    return  p1p2[0] * p1p3[1] - p1p2[1] * p1p3[0] < 0


def find_inflexion(contour,start):
    start_index = contour.xys.index(start)
    if start_index  > len(contour.xys):
        return contour.xys[start_index + 1]
    if start_index + 1 > len(contour.xys):
        return contour.xys[start_index + 2]
    sens=clockwise(start,contour.xys[start_index+1],contour.xys[start_index+2])
    while clockwise(start,contour.xys[start_index+1],contour.xys[start_index+2])==sens:
        if start_index + 2 > len(contour.xys):
            return contour.xys[start_index + 2]
        start_index +=1
    return contour.xys[start_index + 1]


def control(contour, start):
    pente_s = pente_moy(start, contour)
    end = find_inflexion(contour, start)
    pente_e = pente_moy(end, contour)
    middle_x = (end.x - start.x) / (pente_s - pente_e)
    middle_y = start.y + pente_s * middle_x
    return image_elements.BezierCurve((sp.array((start.x, start.y)),
                                       sp.array((middle_x, middle_y)),
                                       sp.array((end.x, end.y))))


def list_curves(Contours):
    for contour in Contours:
        pass
