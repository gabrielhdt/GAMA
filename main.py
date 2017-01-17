#!/usr/bin/python3
"""Main part, takes an image as argument and vectorises it"""
# -*- coding: utf-8 -*-
import sys
import argparse
import scipy.misc
import image_processing
import writesvg
import control_points


def main(imagefile):
    seuil = 0.3
    matrgb = scipy.misc.imread(imagefile)
    dim = matrgb.shape
    print("Contours")
    contset = image_processing.contours_image(matrgb, seuil=seuil)
    print("Séparation")
    contset = list(contset)
    navailablecont = len(contset)
    i = 0
    while i < navailablecont:
        try:
            contset[i].optimseparate()
            i += 1
        except KeyError:
            print("Failed to determine contour")
            contset.pop(i)
            navailablecont -= 1
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
    parser.parse_args()
    main(sys.argv[1])
