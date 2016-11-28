import image_elements

def pente_moy(pixel,contour,sens=1,precision=5):
    """pixel un objet de la classe Pixel
    contour un objet de la classe Contour
    sens orientation de la tangente
     precision nombre de pixel pris en compte
     renvoie la pente de la tangente au contour au point pixel """
    index = contour.xys.index((pixel.x,pixel.y))
    pente = 0
    for i in range(1,precision+1):
        other_x = contour.xys[index+i*sens].x
        other_y = contour.xys[index+i*sens].y
        pente += (pixel.y-other_y)/(pixel.x-other_x)
    return pente/(precision-1)


def clockwise(p1,p2,p3):
    """test le sens des 3 points p1, p2, p3"""
    p1p2 = (p2.x - p1.x, p2.y - p1.y)
    p1p3 = (p3.x - p1.x, p3.y - p1.y)
    return  p1p2.x * p1p3.y - p1p2.y * p1p3.y < 0

