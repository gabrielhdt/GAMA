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
    svgfile.write("</svg>")
