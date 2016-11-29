#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Defines elements which will be used in svg file (e.g. Bezier curves)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
import scipy.special
import scipy as sp
import control_points


class BernsteinBasisPoly(sp.poly1d):
    def __init__(self, nu, n):
        """Defines nu-nth Bernstein basis polynomial
        nu -- int, number of the polynomial;
        n -- int, degree
        """
        assert nu <= n
        pol = sp.poly1d((1, 0))**nu  # P(X) = X^\nu
        pol *= sp.poly1d((-1, 1))**(n - nu)  # P(X) = (1 - X)^(n-\nu)
        pol *= scipy.special.binom(n, nu)
        super().__init__(pol)


class BezierCurve:
    def __init__(self, ctrl_pts):
        """Defines a Bezier curve from control points
        ctrl_pts -- tuple of vectors containing at least two
            points: start point and end point
        """
        self.start = ctrl_pts[0]
        self.stop = ctrl_pts[-1]
        self.ctrl = ctrl_pts[1:-1]
        self.deg = len(ctrl_pts)
        self.ctrl_pts = ctrl_pts

#        def coef_bezier(k):
#            return ctrl_pts[k]*BernsteinBasisPoly(k, self.deg)
#        pol_coeffs = sum((coef_bezier(i) for i in range(self.deg)))
#        self.polytuple = (sp.poly1d(pol_coeffs[0]), sp.poly1d(pol_coeffs[1]))
#        self.fct = lambda t: sp.array([[self.polytuple[0](t)],
#                                       [self.polytuple[1](t)]])

class Pixel(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.unread = True

    def __repr__(self):
        return "<Pixel at {}, {}>".format(self.x, self.y)

    def adjs(self):
        x=self.x
        y=self.y
        pixel_voisins=[]
        for k in range(x-1,x+2):
            for j in range (y-1,y+2):
                if (k!=x and j!=y) and Pixel(k,j).read:
                    pixel_voisins.append(Pixel(k,j))
        return pixel_voisins


class Contour(object):
    def __init__(self, xys):
        """
        xys -- list of pixels
        """
        self.xys = xys
        self.color = None

    def inflexion(self,start):
        start_index = self.xys.index(start)
        if start_index > len(self.xys):
            return self.xys[start_index + 1]
        if start_index + 1 > len(self.xys):
            return self.xys[start_index + 2]
        sens = self(start, self.xys[start_index + 1], self.xys[start_index + 2])
        while control_points.clockwise(start, self.xys[start_index + 1], self.xys[start_index + 2]) == sens:
            if start_index + 2 > len(self.xys):
                return self.xys[start_index + 2]
            start_index += 1
        return (self.xys[start_index + 1].x, self.xys[start_index + 1].y)
