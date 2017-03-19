# -*- coding: utf-8 -*-
"""Defines graphical elements which will be used in the program"""
from numpy import array
from numpy.linalg import norm
from numpy import argmin


class Waypoint(object):
    """Points over which the Bezier curve will pass"""
    def __init__(self, pix):
        self.x = pix.x
        self.y = pix.y
        self.arr = array((pix.x, pix.y))
        self.slope = None
        self.paratan = None

    def __repr__(self):
        return "<Waypoint at {}, {}>".format(self.x, self.y)

    def computan(self, contour, precision):
        """Computes tangent to contour for waypoint"""

        def paratan2slope(delta_xy):
            """Pente associée à la tangente paramétrée par delta_x, delta_y
            delta_xy -- itérable à deux éléments, delta_x en 0 et delta_y
            en 1"""
            assert len(delta_xy) == 2
            if abs(delta_xy[0]) <= 1e-15:
                return "inf"
            elif abs(delta_xy[1]) <= 1e-15:
                return 0
            else:
                return delta_xy[1]/delta_xy[0]

        def weight(dist):
            """Gives weight to pixel while processing tangent.
            Weight depends on the distance between the hook and the point
            dist -- integer, distance between hook and pixel"""
            return 2**(-abs(dist))

        index = contour.xys.index(self)
        n = len(contour.xys)
        delta_x_mean = 0
        delta_y_mean = 0
        beforeweight = [weight(i) for i in range(1, precision + 1)]
        afterweight = [weight(i) for i in range(1, precision + 1)]
        totweight = sum(beforeweight) + sum(afterweight)
        for i in range(-precision, 0):
            other_x = contour.xys[(index + i) % n].x
            other_y = contour.xys[(index + i) % n].y
            delta_x_mean += ((self.x - other_x) *
                             beforeweight[abs(i) - 1]/totweight)
            delta_y_mean += ((self.y - other_y) *
                             beforeweight[abs(i) - 1]/totweight)
        for i in range(1, precision + 1):
            other_x = contour.xys[(index + i) % n].x
            other_y = contour.xys[(index + i) % n].y
            delta_x_mean += (other_x - self.x)*afterweight[i - 1]/totweight
            delta_y_mean += (other_y - self.y)*afterweight[i - 1]/totweight
        self.paratan = array((delta_x_mean, delta_y_mean))
        self.normalise()
        self.slope = paratan2slope((delta_x_mean, delta_y_mean))

    def normalise(self):
        """Normalises tangent coefficient (norm of vector self (dx, dy))"""
        paranorm = norm(self.paratan)
        self.paratan = (1/paranorm)*self.paratan


class Pixel(object):
    """A Pixel of the picture"""
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
        return 1000000000*int(self.x) + int(self.y)  # Should be int anyway

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

    def iscorner(self, cont):
        """Returns whether self is a corner of contour cont
        cont -- Contour()
        """
        clneighbourhood = self.closest_neighbours(cont=cont)
        if len(clneighbourhood) < 2:
            return False
        else:  # At least two closest neighbours
            neighbour1 = clneighbourhood.pop()
            neighbour2 = clneighbourhood.pop()
            cond1 = neighbour1.x == self.x and neighbour2.y == self.y
            cond2 = neighbour1.y == self.y and neighbour2.x == self.x
            return cond1 or cond2

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

    def is_neighbour_quick(self, other):
        """Quick way to test whether other is in neighbourhood of self"""
        return abs(self.x - other.x) <= 1 and abs(self.x - other.y) <= 1


class Contour(object):
    """A set or list of pixel circling an area of a same colour"""
    def __init__(self, xys):
        """
        xys -- list or set of pixels
        """
        self.xys = xys
        self.colour = None

    def __eq__(self, other):
        return self.xys == other.xys

    def __lt__(self, other):
        return len(self.xys) < len(other.xys)

    def __hash__(self):
        if len(self.xys) == 0:
            return 0
        else:
            if isinstance(self.xys, list):
                return int(self.xys[0].x)
            elif isinstance(self.xys, set):
                return int(self.xys.copy().pop().x)

    def separate_contour(self, begpix):
        """Extracts and replaces self.xys by the greater contour in self,
        ordering and filtering pixels. Filter is made by favouring
        Xneighbours over close neighbours. loopcount is used to manage inital
        steps, which is the hardest part of the program.
        begpix -- Pixel() on which the inspection will start
        """
        assert isinstance(self.xys, set)

        loop = []  # Ordered, therefore list
        inspix = begpix
        self.xys.remove(inspix)
        loop.append(inspix)
        neighbourhood = inspix.neighbours(cont=self)
        clneighbourhood = neighbourhood & inspix.closest_neighbours()
        xneighbourhood = neighbourhood - clneighbourhood
        sparepix = list(neighbourhood)  # Used if KeyError
        while len(sparepix) > 0:
            try:
                if len(xneighbourhood) > 0:
                    inspix = xneighbourhood.pop()
                else:
                    inspix = clneighbourhood.pop()
                sparepix.remove(inspix)
            except KeyError:
                inspix = sparepix.pop()
            finally:
                self.xys.remove(inspix)
                loop.append(inspix)
                neighbourhood = inspix.neighbours(cont=self)
                clneighbourhood = neighbourhood & inspix.closest_neighbours()
                xneighbourhood = neighbourhood - clneighbourhood
                for px in neighbourhood:
                    if px not in sparepix:
                        sparepix.append(px)
        return loop

    def optimseparate(self):
        """ If several contours are in self (not declared), returns the closest
        from border"""
        pix = min(self.xys, key=lambda p: abs(p.x))
        self.xys = self.separate_contour(pix)

    def sort_cont(self):
        """Sorts pixels in self.xys. First tests whether next pixel is in
        the neighbourhood. If not, searches for nearer pixel. Needs time..."""
        def distpx(v1, v2):
            return norm((v1.x - v2.x, v1.y - v2.y))

        def search_nearer(px, cont):
            """Searches nearer pixel of px in cont"""
            dists = map(lambda x: distpx(px, x), cont)
            return argmin(dists)

        cont = self.xys  # Shortcut
        leave = False
        pos = 0  # Position in cont
        sortcont = [cont.pop(0)]
        while not leave:
            if sortcont[-1].is_neighbour_quick(cont[pos]):
                sortcont.append(cont.pop(pos))
            else:
                pos = search_nearer(sortcont[-1], cont)
                leave = (distpx(sortcont[-1], cont[pos]) <=
                         distpx(sortcont[-1], sortcont[0]))
                if not leave:
                    sortcont.append(cont.pop(pos))
            leave = leave or len(cont) == 0
        return sortcont

    def scanlines(self):
        """Looks for straight lines with length greater than 3 pixels.
        Fortunately for choordinate, right angles don't exist in our
        world"""
        cxys = self.xys[1:]  # Shortcut
        linedges = set()  # Don't care about order
        aligned = 0
        threshold = max(int(len(self.xys)*0.03), 3)  # Chosen after tests
        for i, pix in enumerate(cxys):
            # choordinate stands for change of coordinate (we mean both)...
            choordinate = not(pix.x == self.xys[i].x or pix.y == self.xys[i].y)
            if not choordinate:
                aligned += 1
                # If last pixel of contour in a line
                if pix == cxys[-1] and aligned >= threshold:
                    for inlinepix in cxys[i - aligned + 1:i]:
                        linedges.remove(inlinepix)
                # Particular case
                elif pix == cxys[-1] and aligned == threshold - 1:
                    linedges.add(pix)
                elif aligned == threshold - 1:  # If 3 points are aligned
                    for k in range(threshold):
                        linedges.add(cxys[i - k])
                elif aligned >= threshold:
                    linedges.add(pix)
            # Coordinate change after aligned sequence
            elif aligned >= threshold - 1 and choordinate:
                for inlinepix in cxys[i - aligned:i - 1]:
                    linedges.remove(inlinepix)  # Removes line content
                aligned = 0
            else:  # Coordinate change without any alignement
                aligned = 0
        return linedges
