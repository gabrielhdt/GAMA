#Author: Maelys

#Matrice de niveaux de gris, moyenne pour chaque triplet RGB. Classement par seuils de niveaux de gris,detection des contours
#chaque zone

#Notations:
#Matriceniveauxdegris: moyenne de couleur pour chaque triplet RGB

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
            MNG[i][j]+=((matriceRGB[i][j][0]/255)*0.2126+(matriceRGB[i][j][1]/255)*0.7152+(matriceRGB[i][j][2]/255)*0.0722)#Coeffs definis par l'UIT (Wikipedia)
    return MNG

matrix=Matriceniveauxdegris(MatriceRGB)
plt.imshow(matrix)
plt.show()

