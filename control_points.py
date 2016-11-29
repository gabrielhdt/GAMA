import image_elements
import scipy as sp

def pente_moy(pixel, contour, sens=1, precision=5):
    """pixel un objet de la classe Pixel
    contour un objet de la classe Contour
    sens orientation de la tangente
     precision nombre de pixel pris en compte
     renvoie la pente de la tangente au contour au point pixel """
    index = contour.xys.index(pixel)
    pente = 0
    for i in range(1,precision+1):
        other_x = contour.xys[index+i*sens].x
        other_y = contour.xys[index+i*sens].y
        pente += (pixel.y-other_y)/(pixel.x-other_x)
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
    middle = (end - start) / (pente_s - pente_e)
    return sp.array((start.x, start.y), (middle.x, middle.y), (end.x, end.y))













