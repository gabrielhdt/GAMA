"""Defines graphical elements which will be used in the program"""
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
        ctrl_pts -- tuple of vectors containing at least three
            points: start point, control point and end point
        """
        self.deg = len(ctrl_pts)
        self.ctrl_pts = ctrl_pts

        def coef_bezier(k):
            ctrl_pts_col = []  # Column vectors for polynomial
            for i, vec in enumerate(ctrl_pts):
                ctrl_pts_col.append(sp.array([[vec[0]], [vec[1]]]))
            return ctrl_pts_col[k]*BernsteinBasisPoly(k, self.deg)
        pol_coeffs = sum((coef_bezier(i) for i in range(self.deg)))
        self.polytuple = (sp.poly1d(pol_coeffs[0]), sp.poly1d(pol_coeffs[1]))
        self.fct = lambda t: sp.array([[self.polytuple[0](t)],
                                       [self.polytuple[1](t)]])


class Pixel(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "<Pixel at {}, {}>".format(self.x, self.y)

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __ne__(self, other):
        return (self.x, self.y) != (other.x, other.y)

    def __hash__(self):
        return 100*self.x + self.y

    def adjs(self, matread):
        x = self.x
        y = self.y
        pixel_voisins = []
        for k in range(x-1,x+2):
            for j in range (y-1,y+2):
                if not(k == x and j == y) and not matread[k, j] and \
                        k >= 0 and j >= 0:
                    pixel_voisins.append(Pixel(k,j))
        return pixel_voisins

    def neighbours(self):
        """
        A supprimer: quick fix car j'ai besoin des adjacents sans la matread
        """
        x = self.x
        y = self.y
        pixel_voisins = []
        for k in range(x-1, x+2):
            for j in range(y-1, y+2):
                if not(k == x and j == y) and \
                        k >= 0 and j >= 0:
                    pixel_voisins.append(Pixel(k, j))
        return pixel_voisins

    def closest_neighbours(self):
        """
        Closest neighbours
        """
        x = self.x
        y = self.y
        pixel_voisins = []
        for k in range(x-1, x+2):
            for j in range(y-1, y+2):
                if k == x or j == y and k >= 0 and j >= 0:
                    pixel_voisins.append(Pixel(k, j))
        return pixel_voisins


class Contour(object):
    def __init__(self, xys):
        """
        xys -- list of pixels
        """
        self.xys = xys
        self.color = None
