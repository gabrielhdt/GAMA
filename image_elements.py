# -*- coding: utf-8 -*-
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
        return 100*int(self.x) + int(self.y)  # Should be int anyway

    def adjs(self, matread):
        """ Returns neighbours that have not been read (according to matread)
        returns a set() as we can't order the pixels. Matrix is considered as
        a torus, i.e. adjs of a pixel on a border are pixels on the other
        border (done automatically on border with index 0). (x, y) or (y, x)?
        """
        dim = matread.shape
        x = self.x
        y = self.y
        pixel_voisins = set()
        if x == dim[0] - 1:  # If on right border
            rangex = (x - 1, x, 0)  # Loop on the other side of matrix
        else:
            rangex = (x - 1, x, x + 1)
        if y == dim[1] - 1:  # If on lower border
            rangey = (y - 1, y, 0)
        else:
            rangey = (y - 1, y, y + 1)
        for k in rangex:
            for j in rangey:
                if not(k == x and j == y) and not matread[k, j] and \
                        k >= 0 and j >= 0:
                    pixel_voisins.add(Pixel(k, j))
        return pixel_voisins

    def closest_adjs(self, matread):
        """Returns closest neighbours which haven't been read according to
        matread"""
        return self.adjs(matread) & self.closest_neighbours()

    def aligned(self, other):
        """Returns a boolena indicating whether self is aligned with other
        pixel"""
        return self.x == other.x or self.y == other.y

    def neighbours(self, cont=None):
        """
        A supprimer: quick fix car j'ai besoin des adjacents sans la matread
        Si cont est spécifié, renvoit les voisins dans le contour cont.
        """
        x = self.x
        y = self.y
        pixel_voisins = set()
        for k in range(x-1, x+2):
            for j in range(y-1, y+2):
                if not(k == x and j == y) and \
                        k >= 0 and j >= 0:
                    pixel_voisins.add(Pixel(k, j))
        if cont is None:
            return pixel_voisins
        else:
            return pixel_voisins & set(cont.xys)

    def closest_neighbours(self, cont=None):
        """
        Neighbours directly contiguous, i.e. with only one different
        coordinate. If cont is specified, returns closest_neighbours which are
        in cont.
        """
        x = self.x
        y = self.y
        pixel_voisins = set()
        for k in range(x-1, x+2):
            for j in range(y-1, y+2):
                if (k == x) ^ (j == y) and k >= 0 and j >= 0:
                    pixel_voisins.add(Pixel(k, j))
        if cont is None:
            return pixel_voisins
        else:
            return pixel_voisins & set(cont.xys)

    def neighbourscont(self, cont):
        """Returns neighbours that are in contour cont
        cont -- Contour() object
        DEPRECATED
        """
        return self.neighbours() & set(cont.xys)


class Contour(object):
    def __init__(self, xys):
        """
        xys -- list or set of pixels
        """
        self.xys = xys
        self.colour = None
        self.surface = 0
        self.zone = None

    def __eq__(self, other):
        return self.xys == other.xys

    def __lt__(self, other):
        return len(self.xys) < len(other.xys)

    def lowersurface(self, other):
        """Will be used mainly to separate contours"""
        return self.surface < other.surface

    def __hash__(self):
        if len(self.xys) == 0:
            return 0
        else:
            if type(self.xys) is list:
                return (int(self.xys[0].x) +
                        int(1000*self.xys[len(self.xys)//2].x))
            elif type(self.xys) is set:
                return (int(self.xys.copy().pop().x) +
                        int(1000*self.xys.copy().pop().x))

    def pixincommon(self, other):
        """Returns whether self has a pixel in common with other contour
        other -- Contour"""
        return not len(self.xys | other.xys) == len(self.xys) + len(other.xys)

    def disinclude(self, smaller):
        """Removes in place the smaller contour from self. smaller must have
        an equivalent in self, which is included in self
        smaller -- Contour()"""
        intercont = set()
        for pix in smaller.xys:
            # Getting equivalent pixels
            for neighbour in pix.closest_neighbours(self):
                intercont.add(neighbour)
        self.xys -= intercont

    def hasequivin(self, other):
        """Returns whether self has an equivalent in the other contour.
        We say equivalent as they won't be exactly the same, but one longer,
        circling the smaller (due to detection_contour). If each pixel of
        smaller has a closest_neighbour in bigger, the former has an
        equivalent in bigger.
        other -- Contour()
        """
        smallen = len(self.xys)
        samecount = 0
        for pix in self.xys:
            if len(pix.closest_neighbours(cont=other)):
                samecount += 1
        return samecount == smallen

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
        # Second filter: removes angles inside contour (staircase like)
        for pix in self.xys[:]:
            cl_neighbourhood = pix.closest_neighbours() & set(self.xys)
            neighbourhood = pix.neighbourscont(self)
            if len(cl_neighbourhood) == 2 and len(neighbourhood) == 4:
                rdneighbour = cl_neighbourhood.pop()  # Random neighbour
                # If other neighbour in neighbourhood of random neighbour
                if cl_neighbourhood.pop() in rdneighbour.neighbourscont(self):
                    self.xys.remove(pix)
        """
        # Fourth filter: removes angles with two neighbours (right angle)
        # identifies angles thanks to number of neighbours
        for pix in self.xys[:]:
            neighbourhood = pix.neighbours(cont=self)
            if len(neighbourhood) == 2:
                neighbour1 = neighbourhood.pop()
                neighbour2 = neighbourhood.pop()
                if (len(neighbour1.neighbours(cont=self)) ==
                    len(neighbour2.neighbours(cont=self)) == 3):
                    self.xys.remove(pix)
                    print("Fourth filter", pix)
        """
        # Fourth and a half filter...
        # identifies angle thanks to neighbours coords
        for pix in self.xys.copy():
            neighbourhood = pix.closest_neighbours(cont=self)
            if len(neighbourhood) == 2:
                neighbour1 = neighbourhood.pop()
                neighbour2 = neighbourhood.pop()
                if not neighbour1.aligned(neighbour2):
                    self.xys.remove(pix)
        # Third filter: for lumps in diagonal
        for pix in self.xys[:]:
            cl_neighbourhood = pix.closest_neighbours() & set(self.xys)
            if len(cl_neighbourhood) == 2:
                doomed = True  # Will be removed, unless...
                for neigh in cl_neighbourhood:
                    if len(neigh.neighbourscont(self)) <= 2:
                        doomed = False  # ... neighbourhood is sparse
                if doomed:
                    self.xys.remove(pix)

    def isloop(self):
        """Returns whether the contour is a loop"""
        copy = Contour(self.xys.copy())  # To avoid modifying self
        return len(copy.separate_contour()[1].xys) == 0

    def separate_contour(self):
        """Sépare les contours présents dans self, qui
        est susceptible d'en contenir 2. Au nouveau contour on ajoute les
        pixels adjacents à celui étudié, qui sont dans le contour, et pas
        déjà dans le lacet.
        self -- contour pouvant en contenir en réalité 2;
            image_elements.Contour() object
        returns -- loop, containing one loop, i.e. a contour object of
            contiguous pixels, and raw_minusloop, the self without loop, i.e.
            the other contour.
        """
        is_empty = False
        loop = Contour([])  # Ordonné donc liste
        assert type(self.xys) is set
        inspix = self.xys.pop()
        inspix_beg = inspix  # For the sake of not going back
        neighbourhood = inspix.neighbours(cont=self)
        # Initial step
        if len(inspix.closest_neighbours(cont=self)) >= 1:
            inspix = inspix.closest_neighbours(cont=self).pop()
            loop.xys.append(inspix)
            self.xys.remove(inspix)
        elif len(neighbourhood) >= 1:
            inspix = neighbourhood.pop()
            loop.xys.append(inspix)
            self.xys.remove(inspix)
            # - set([inspix_beg]) to avoid going back
        neighbourhood = (inspix.neighbours(cont=self) - set([inspix_beg]))
        while not is_empty:
            clneighbourhood = inspix.closest_neighbours(cont=self)
            neighbourhood = inspix.neighbours(cont=self)
            if len(clneighbourhood) >= 1:
                inspix = clneighbourhood.pop()
            elif len(neighbourhood) >= 1:  # Could be else
                inspix = neighbourhood.pop()
            loop.xys.append(inspix)
            if inspix in self.xys:  # For first loop only...
                self.xys.remove(inspix)
            neighbourhood = inspix.neighbours(cont=self)
            is_empty = len(neighbourhood) == 0
        if inspix_beg not in loop.xys:  # To prevent holes
            loop.xys.append(inspix_beg)
        raw_minusloop = Contour(self.xys.copy())
        return loop, raw_minusloop

    def separate_all_contour(self):
        """Separates every contour present in self"""

        def separate(contour_raw):
            if len(contour_raw.xys) < 1:
                return set()
            else:
                loop, raw_minusloop = self.separate_contour()
                return set([loop]) | separate(raw_minusloop)
        return separate(self)

    def scanlines(self):
        """Looks for straight lines with length greater than 3 pixels.
        Fortunately for choordinate, right angles don't exist in our
        world"""
        cxys = self.xys[1:]  # Shortcut
        linedges = set()  # Don't care about order
        aligned = 0
        for i, pix in enumerate(cxys):
            # choordinate stands for change of coordinate (we mean both)...
            choordinate = not(pix.x == self.xys[i].x or pix.y == self.xys[i].y)
            if not choordinate:
                aligned += 1
                # If last pixel of contour in a line
                if pix == cxys[-1] and aligned >= 3:
                    for inlinepix in cxys[i - aligned + 1:i]:
                        linedges.remove(inlinepix)
                elif pix == cxys[-1] and aligned == 2:  # Particular case
                    linedges.add(pix)
                elif aligned == 2:  # If 3 points are aligned
                    for k in range(3):
                        linedges.add(cxys[i - k])
                elif aligned >= 3:
                    linedges.add(pix)
            elif aligned >= 2 and choordinate:  # Coordinate change after
                for inlinepix in cxys[i - aligned:i - 1]:  # aligned sequence
                    linedges.remove(inlinepix)  # Removes line content
                aligned = 0
            else:  # Coordinate change without any alignement
                aligned = 0
        return linedges
