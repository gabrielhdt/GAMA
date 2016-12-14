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
        pixel_voisins = set()
        for k in range(x-1,x+2):
            for j in range (y-1,y+2):
                if not(k == x and j == y) and not matread[k, j] and \
                        k >= 0 and j >= 0:
                    pixel_voisins.add(Pixel(k,j))
        return pixel_voisins

    def neighbours(self):
        """
        A supprimer: quick fix car j'ai besoin des adjacents sans la matread
        """
        x = self.x
        y = self.y
        pixel_voisins = set()
        for k in range(x-1, x+2):
            for j in range(y-1, y+2):
                if not(k == x and j == y) and \
                        k >= 0 and j >= 0:
                    pixel_voisins.add(Pixel(k, j))
        return pixel_voisins

    def closest_neighbours(self):
        """
        Neighbours directly contiguous, i.e. with only one different
        coordinate
        """
        x = self.x
        y = self.y
        pixel_voisins = set()
        for k in range(x-1, x+2):
            for j in range(y-1, y+2):
                if (k == x) ^ (j == y) and k >= 0 and j >= 0:
                    pixel_voisins.add(Pixel(k, j))
        return pixel_voisins

    def neighbourscont(self, cont):
        """Returns neighbours that are in contour cont
        cont -- Contour() object
        """
        return self.neighbours() & set(cont.xys)


class Contour(object):
    def __init__(self, xys):
        """
        xys -- list of pixels
        """
        self.xys = xys
        self.colour = None

    def __eq__(self, other):
        return self.xys == other.xys

    def __hash__(self):
        if len(self.xys) == 0:
            return 0
        else:
            return self.xys[0].x + 100*self.xys[len(self.xys)//2].x

    def thinner(self):
        """Removes redundant pixel in contour, i.e. when it has too much
        closest neighbours. The method may not be the best, if two pixels
        side to side have each 3 closest_neighbours, only one will be removed
        as the other will lose the latter. It avoids bugs (holes in contour).
        """
        overcrowding = []  # Pixels which have more than 2 close neighbours
        for pix in self.xys:
            if len(pix.closest_neighbours() & set(self.xys)) >= 3:
                overcrowding.append(pix)
        will_die = [True for _ in overcrowding]  # Each pixel can die
        for i, choked in enumerate(overcrowding):
            crowd = choked.closest_neighbours() & set(self.xys)
            safe = crowd - set(overcrowding)  # Not overcrowded crowd
            assert len(safe) >= 2
            if len(safe) >= 2:
                choker1, choker2 = safe.pop(), safe.pop()
                if choker1 not in choker2.neighbours():  # Is there a hole?
                    will_die[i] = False
        exterminate = [doomed for (i, doomed) in enumerate(overcrowding) if
                       will_die[i]]
        for doomed in exterminate:
            self.xys.remove(doomed)

    def skinnier(self):
        """Thins more the contour, a pixel must have only 2 neighbours. To
        process a pixel, the neighbours of the neighbours are inspected. If
        first neighbour has only two neighbours, the pixel shouldn't be
        removed"""
        # First filter: remove if more than 3 closest_neighbours (easy)
        for pix in self.xys[:]:
            if len(pix.closest_neighbours() & set(self.xys)) >= 3:
                    self.xys.remove(pix)
        # Second filter: removes angles
        """
        overcrowding = set()
        for pix in self.xys:
            if len(pix.neighbours() & set(self.xys)) >= 3:
                overcrowding.add(pix)
        for choked in overcrowding:
            doomed = True
            crowd = choked.neighbours() & set(self.xys)
            for choker in crowd:
                crowdofchoker = choker.neighbourscont(self)
                if len(crowdofchoker) == 2:
                    doomed = False
            if doomed:
                self.xys.remove(choked)
        """
        overcrowding = set()
        """
        for pix in self.xys[:]:
            choker = 0
            for neighbour in pix.neighbourscont(self):
                if len(neighbour.neighbourscont(self)) >= 3:
                    choker += 1
            if choker >= 2:
                self.xys.remove(pix)
        """
        for pix in self.xys:
            if len(pix.neighbours() & set(self.xys)) >= 3:
                overcrowding.append(pix)
        will_die = [True for _ in overcrowding]
        for i, choked in enumerate(overcrowding):
            for choker in choked.neighbours() & set(self.xys):
                if len(choker.neighbours() & set(self.xys) - set([choked])) <= 2:
                    will_die[i] = False
                if will_die[i]:
                    self.xys.remove(choker)
        """
        extermination = [doomed for (i, doomed) in enumerate(overcrowding) if
                         will_die[i]]
        for doomed in extermination:
            self.xys.remove(doomed)
        """
