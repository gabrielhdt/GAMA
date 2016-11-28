#Author: Maelys

#Matrice de niveaux de gris, "moyenne" pour chaque triplet RGB.
#  Classement par seuils de niveaux de gris,detection des contours pour chaque zone

#Notations:
#Matriceniveauxdegris: niveau de gris entre 0 et 1, avec coefficients (0.2126,0.7152,0.0722) pour (R,G,B)/ Wikipedia

import scipy.misc as smp
import numpy as np
import matplotlib.pyplot as plt

MatriceRGB=smp.imread("imagesimple.jpg")
#print(MatriceRGB)


def Matriceniveauxdegris(matriceRGB):
    (a,b,c)=matriceRGB.shape #ici matriceRGB est la matrice RGB de l'image choisie
    MNG=np.zeros(shape=(a,b)) #MNG pour Matriceniveauxdegris
    for i in range (a):
        for j in range (b):
            MNG[i][j]+=((matriceRGB[i][j][0]/255)*0.2126+(matriceRGB[i][j][1]/255)*0.7152+(matriceRGB[i][j][2]/255)*0.0722)
    return MNG

matrix=Matriceniveauxdegris(MatriceRGB)
plt.imshow(matrix, cmap=plt.cm.gray)
plt.show()

