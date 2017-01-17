#!/usr/bin/python3
"""Main part, takes an image as argument and vectorises it"""
# -*- coding: utf-8 -*-
import sys
import argparse
import scipy.misc
import image_processing
import writesvg
import control_points


def main(imagefile, ngreys):
    ngreys = int(ngreys)
    matrgb = scipy.misc.imread(imagefile)
    dim = matrgb.shape
    print("Contours")
    contset = image_processing.contours_image(matrgb, ngl=ngreys)
    print("Séparation")
    contset = list(contset)
    navailablecont = len(contset)
    failedcont = 0
    i = 0
    while i < navailablecont:
        try:
            contset[i].optimseparate()
            i += 1
        except KeyError:
            print("Failed to determine contour")
            failedcont += 1
            contset.pop(i)
            navailablecont -= 1
    print("{} contours failed".format(failedcont))
    image_processing.ordercontlist(contset)
    dim = matrgb.shape
    svgfile = writesvg.SvgFile("out.svg", dim)
    print("Écriture")
    curves = []
    for cont in contset:
        curves = control_points.curves(cont)
        curvemat = control_points.curves2curvematc(curves)
        colours = {"fill": cont.colour, "stroke": cont.colour}
        svgfile.draw_contourc(curvemat, colours)
    svgfile.close_svg()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("imagefile",
                        help="Filename of the picture to be processed",
                        nargs=1)
    parser.add_argument("ngls",
                        help="Number of greylevels to keep",
                        nargs=1)
    parser.parse_args()
    main(sys.argv[1], sys.argv[2])
