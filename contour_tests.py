# -*- coding: utf-8 -*-
import image_elements as ie


square = ie.Contour([])  # A square
square.xys += [ie.Pixel(10 + i, i) for i in range(10, 21)]
square.xys += [ie.Pixel(30 - i, 20 + i) for i in range(1, 11)]
square.xys += [ie.Pixel(20 - i, 30 - i) for i in range(1, 11)]
square.xys += [ie.Pixel(10 + i, 20 - i) for i in range(1, 10)]

cardioid = ie.Contour([])  # Like the square but upper half has inflexion
cardioid.xys += [ie.Pixel(10 + i, 20 - i) for i in range(10)]
cardioid.xys += [ie.Pixel(20 + i, 10 + i) for i in range(10)]
cardioid.xys += [ie.Pixel(30 + i, 20 - i) for i in range(10)]
cardioid.xys += [ie.Pixel(40 + i, 10 + i) for i in range(10)]
cardioid.xys += [ie.Pixel(50 - i, 20 + i) for i in range(20)]
cardioid.xys += [ie.Pixel(30 - i, 40 - i) for i in range(20)]
