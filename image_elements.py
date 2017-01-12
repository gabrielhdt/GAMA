# -*- coding: utf-8 -*-
"""Defines graphical elements which will be used in the program"""
import scipy.special
import scipy as sp
import control_points


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

    def __eq__(self, other):
        return self.xys == other.xys

    def __lt__(self, other):
        return len(self.xys) < len(other.xys)

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
        equivalent in bigger. Will work only if self is circled by other.
        other -- Contour()
        """
        smallen = len(self.xys)
        samecount = 0
        for pix in self.xys:
            if len(pix.closest_neighbours(cont=other)):
                samecount += 1
        return samecount == smallen

    def separate_contour(self, begpix):
        """Extracts and replaces self.xys by the greater contour in self,
        ordering and filtering pixels. Filter is made by favouring
        Xneighbours over close neighbours. loopcount is used to manage inital
        steps, which is the hardest part of the program.
        begpix -- Pixel() on which the inspection will start
        """
        loop = []  # Ordered, therefore list
        assert type(self.xys) is set
        # Remove if corner
        if begpix.iscorner(cont=self):
            self.xys.remove(begpix)
        begpix = self.xys.copy().pop()
        loop.append(begpix)
        # First step
        tramp = begpix.neighbours(cont=self)
        clneighbourhood = begpix.closest_neighbours(cont=self)
        xneighbourhood = tramp - clneighbourhood
        if len(xneighbourhood) >= 1:
            self.xys.remove(begpix)
            inspix = xneighbourhood.pop()
        else:
            self.xys.remove(begpix)
            inspix = clneighbourhood.pop()
        loop.append(inspix)
        # 2nd step
        neighbourhood = inspix.neighbours(cont=self)
        clneighbourhood = inspix.closest_neighbours(cont=self)
        xneighbourhood = neighbourhood - clneighbourhood
        if len(xneighbourhood) >= 1:
            self.xys.remove(inspix)
            inspix = xneighbourhood.pop()
        else:
            self.xys.remove(inspix)
            inspix = clneighbourhood.pop()
        neighbourhood = inspix.neighbours(cont=self)
        self.xys.remove(inspix)
        while inspix not in tramp:
            loop.append(inspix)
            clneighbourhood = neighbourhood & inspix.closest_neighbours()
            xneighbourhood = neighbourhood - clneighbourhood
            if len(xneighbourhood) >= 1:
                inspix = xneighbourhood.pop()
                self.xys.remove(inspix)
                if len(clneighbourhood) >= 1:
                    self.xys.remove(clneighbourhood.pop())
            else:
                inspix = neighbourhood.pop()
                self.xys.remove(inspix)
            neighbourhood = inspix.neighbours(cont=self)
        loop.append(inspix)
        return loop

    def optimseparate(self):
        """ If several contours are in self (not declared), returns the closest
        from border"""
        pix = min(self.xys, key=lambda p: abs(p.x))
        self.xys = self.separate_contour(pix)

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
