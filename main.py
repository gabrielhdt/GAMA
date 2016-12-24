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
    seuil = 0.01
    matrgb = scipy.misc.imread(imagefile)
    matgl = image_processing.Matriceniveauxdegris(matrgb)
    matgl = image_processing.add_border(matgl)
    matgl = image_processing.regroupement_couleur(matgl, seuil)
    dim = matgl.shape
    contset = image_processing.contours_image(matgl, seuil)
    separated_cont = []
    for cont in contset:
        separated_cont += image_processing.separate_all_contours(cont)
    contset = separated_cont
    for cont in contset:
        cont.skinnier()
    svgnames = []
    for i, cont in enumerate(contset):
        svgnames.append("main{}.svg".format(i))
    svgfiles = []
    for i, name in enumerate(svgnames):
        svgfiles.append(writesvg.SvgFile(svgnames[i], dim))
    for i, cont in enumerate(contset):
        curves = control_points.list_curves([cont])
        curvemat = control_points.curves2curvemat(curves)
        svgfiles[i].draw_contour_pix(cont)
        svgfiles[i].draw_contour(curvemat)
        svgfiles[i].close_svg()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("imagefile",
                        help="Filename of the picture to be processed",
                        nargs=1)
    parser.parse_args()
    main(sys.argv[1])
