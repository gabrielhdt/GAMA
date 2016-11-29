#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    writesvg.py: creates SVG file from instructions
#    Copyright (C) 2016  Gabriel Hondet
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License


def svgskel(dim, svgfile):
    """ Writes the skeleton of the svg file 'svgfile'
    dim -- dimensions of image, tuple (width, height)
    svgfile -- file object, must be writable
    """
    svgfile.write("<?xml version=\"1.0\" standalone=\"yes\"?>\n")
    svgfile.write("<svg xmlns=\"http://www.w3.org/2000/svg\"\n")
    svgfile.write("\twidth=\"{}\" height=\"{}\">\n".format(dim[0], dim[1]))
    svgfile.write("\t<desc>A short description</desc>\n")


def write_bezier(ctrl_pts, svgfile):
    """Writes Bezier curves to file, see:
    http://commons.oreilly.com/wiki/index.php/SVG_Essentials/Paths
    ctrl_pts -- tuple of vectors which are control points
    svgfile -- writable file
    """
    bdeg = 'Q' if len(ctrl_pts) == 3 else 'C'  # Quadratic or cubic
    svgfile.write("\t<path d=\"")  # Beginning of line
    svgfile.write("M {} {}".format(ctrl_pts[0][0], ctrl_pts[0][1]))
    svgfile.write(" {} {} {}".format(bdeg, ctrl_pts[1][0], ctrl_pts[1][1]))
    svgfile.write(", {} {}".format(ctrl_pts[2][0], ctrl_pts[2][1]))
    if bdeg is 'C':
        svgfile.write(", {} {}\"".format(ctrl_pts[3][0], ctrl_pts[3][1]))
    else:
        svgfile.write("\"")
    svgfile.write(" style=\"stroke: black; fill: none;\"/>\n")


def close_svg(svgfile):
    """Closes svg file
    svgfile -- writable file object
    """
    svgfile.write("</svg>")
    svgfile.close()


def write_contour(curve_set, svgfile):
    """Write a set of Bezier
    curve_set -- list of BezierCurve objects
    """
    for curve in curve_set:
        write_bezier([curve.start, curve.ctrl, curve.stop], svgfile)
