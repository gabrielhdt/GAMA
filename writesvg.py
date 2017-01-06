"""Defines a class for creating a svgfile"""


class SvgFile:
    def __init__(self, name, dim):
        """Links a file to object
        name -- name of the file (string)
        dim -- tuble of int, dimension of svg image. Be careful! An image
            of dimension (16, 16) can contain up to 17 pixel object per line or
            row (e.g. when using draw_pix), from 0 to 16, bounds included.
            Someone who wants to draw the pixels of an sp.array of dim 16, 16
            should have dim = (15, 15).
        """
        self.file = open(name, 'w')
        self.svgskel(dim)

    def write(self, string):
        """Shortcut for self.file.write(string)"""
        self.file.write(string)

    def svgskel(self, dim):
        """ Writes the skeleton of the svg file 'self'
        dim -- dimensions of image, tuple (width, height)
        """
        self.write("<?xml version=\"1.0\" standalone=\"yes\"?>\n")
        self.write("<svg xmlns=\"http://www.w3.org/2000/svg\"\n")
        self.write("\twidth=\"{}\" height=\"{}\">\n".format(dim[0], dim[1]))
        self.write("\t<desc>A short description</desc>\n")

    def open_path(self):
        """Opens a path"""
        self.write("\t<path d=\"")

    def begin_bezier(self, ctrl_pts):
        """Draws first Bezier of path
        ctrl_pts -- list of 3 points
        """
        self.write("M {} {}".format(ctrl_pts[0, 0], ctrl_pts[0, 1]))
        self.write(" Q {} {}".format(ctrl_pts[1, 0], ctrl_pts[1, 1]))
        self.write(", {} {}".format(ctrl_pts[2, 0], ctrl_pts[2, 1]))

    def close_path(self, colours):
        """Closes path and add parameters
        colours -- dictionnary containing colours: stroke and fill
        """
        self.write("\" stroke=\"{}\" fill=\"{}\"/>\n".format(colours["stroke"],
                                                             colours["fill"]))

    def add_polybezier(self, ctrl_pts):
        """Adds a quadratic Bezier curve in an opened path, i.e. a
        polybezier
        ctrl_pts -- list of two points, control point and stop point, beginning
            being defined by previous point
        """
        for i in range(2):
            self.write(", {} {}".format(ctrl_pts[i, 0], ctrl_pts[i, 1]))

    def close_svg(self):
        """Closes svg file"""
        self.write("</svg>")
        self.file.close()

    def draw_contour(self, ctrl_mat, colours=None):
        """Draws a contour with quadratic bezier curves whose control points are
        in ctrl_mat (a point is given by ctrl_mat[k,:]). To make a loop, first
        point must match last point.
        ctrl_mat -- (n, 2) int array
        colours -- dictionnary containing stroke colour and fill colour
        """
        if colours is None:
            colours = {"fill": "blue", "stroke": "blue"}
        assert ctrl_mat[3:, ].shape[0] % 2 == 0  # Pair of points except first
        n_bezier = ctrl_mat[3:, ].shape[0]//2  # Number of curves
        self.open_path()
        self.begin_bezier(ctrl_mat[:4, ])
        for i in range(3, 3 + 2*n_bezier, 2):
            self.add_polybezier(ctrl_mat[i:i + 2, ])
        self.close_path(colours)

    def draw_pix(self, pix):
        """Draws a pixel on svg, to see contour results
        pix -- image_elemnts.Pixel() element
        """
        self.write("\t<circle")
        self.write(" cx=\"{}\" cy=\"{}\" r=\"1\"/>\n".format(pix.x, pix.y))

    def draw_contour_pix(self, contour):
        """Draws pixels from contour
        contour -- Contour object
        """
        for pix in contour.xys:
            self.draw_pix(pix)
