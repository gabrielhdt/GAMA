import image_elements

def pente_moy(pixel,contour,sens=1,precision=5):
    index = contour.xys.index((pixel.x,pixel.y))
    pente = 0
    for i in range(1,precision+1):
        other_x = contour.xys[index+i*sens].x
        other_y = contour.xys[index+i*sens].y
        pente += (pixel.y-other_y)/(pixel.x-other_x)
    return pente/(precision-1)


