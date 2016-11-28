#Author: Maelys

#    Matrice de niveaux de gris, "moyenne" pour chaque triplet RGB.
#    Classement par seuils de niveaux de gris,detection des contours pour chaque zone

#    Notations:
#    Matriceniveauxdegris: niveau de gris entre 0 et 1, avec coefficients (0.2126,0.7152,0.0722) pour (R,G,B)/ Wikipedia

import scipy.misc as smp
import numpy as np
import matplotlib.pyplot as plt
import image_elements


def Matriceniveauxdegris(matriceRGB):
    (a,b,c)=matriceRGB.shape #ici matriceRGB est la matrice RGB de l'image choisie
    MNG=np.zeros(shape=(a,b)) #MNG pour Matriceniveauxdegris
    for i in range (a):
        for j in range (b):
            MNG[i][j]+=((matriceRGB[i][j][0]/255)*0.2126+(matriceRGB[i][j][1]/255)*0.7152+(matriceRGB[i][j][2]/255)*0.0722)
    return MNG


def ajout_contour(matriceNG):
    # retourne la matrice de départ avec un contour formé de 2
    (lig,col) = matriceNG.shape
    # matrice NG designe la matrice en niveau de gris de taille (lignes, colonnes)
    mat_ajoutcontour = np.ones((lig+1,col+1), dtype=int)
    #initialise une matrice de taille (lig+1, col+1) avec des un
    for i in range(1,lig):
        for j in range(1, col):
            mat_ajoutcontour[i][j] = matriceNG[i][j]
    return mat_ajoutcontour

def contours(matriceNG, s):
    # prend en argument une matrice en niveau de gris à laquelle on a rajouté un contour de 1
    # et un seuil de couleurs pour classer les pixels
    #renvoie la liste des contours de l'image
    voisins = []
    contours = []
    (lig,col) = matriceNG.shape
    contour = []
    for i in range(lig):
        for j in range(col):
            pixel = image_elements.Pixel(i,j)
            voisins = []
            

if __name__ == "__main__":
    MatriceRGB = smp.imread("imagesimple.jpg")
    matrix=Matriceniveauxdegris(MatriceRGB)
    #plt.imshow(matrix, cmap=plt.cm.gray)
    #plt.show()

