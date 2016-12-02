# Author: Maelys

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
    Matrice_gray=np.zeros(shape=(a,b)) #Matrice_gray pour Matriceniveauxdegris
    for i in range (a):
        for j in range (b):
            Matrice_gray[i][j]+=((matriceRGB[i][j][0]/255)*0.2126+(matriceRGB[i][j][1]/255)*0.7152+(matriceRGB[i][j][2]/255)*0.0722)
    return Matrice_gray

def ajout_bord(matriceNG):
    # retourne la matrice de départ avec un contour formé de 2
    (lig, col) = matriceNG.shape
    # matrice NG designe la matrice en niveau de gris de taille (lignes, colonnes)
    mat_ajoutbord = np.ones((lig+1, col+1), dtype=int)
    #initialise une matrice de taille (lig+1, col+1) avec des un
    for i in range(1, lig):
        for j in range(1, col):
            mat_ajoutbord[i][j] = matriceNG[i][j]
             = mat_ajoutbord[i][j]
            
    return mat_ajoutbord

def detection_contour(matriceNG, pixel, seuil, pretendants, contour_inter):
    colorpixel = matriceNG[pixel.x][pixel.y]
    voisins = pixel.adjs.append(pretendants) #creer
    for (index, vois) in enumerate(voisins):
        if vois.exist: #teste si sont sur le bord ou pas
            vois.unread = False
            x1 = vois.x
            y1 = vois.y
            colorvois = matriceNG[x1][y1]
            if abs(colorpixel-colorvois) > seuil:
                contour_inter.xys.append(vois)
                voisins.pop(index)
    while len(voisins)>0:
        pretendant = voisins
        detection_contour(matriceNG, voisins[0], seuil, pretendant, contour_inter)
    return contour_inter

def contour_image(matriceNG, seuil):
    # prend en argument une matrice en niveau de gris à laquelle on a rajouté un contour de 1
    # et un seuil de couleurs pour classer les pixels
    # renvoie la liste des contours de l'image
    (line, column) = matriceNG.shape
    liste_contours = []
    contour_inter = image_elements.Contour([])
    pretendants = []
    for i in range(line):
        for j in range(column):
            liste_contours.append(detection_contour(matriceNG, matriceNG[i][j], seuil, pretendants, contour_inter))
    return liste_contours

def visualisation_contour(matriceNG,liste_contours):
    (lin, col) = matriceNG.shape
    visu = np.zeros(lin, col)
    for contour in liste_contours :
        pixels = contour.xys
        for pixel in pixels :
            i = pixel.x
            j = pixel.y
            visu[i][j] = 1
    return visu



if __name__ == "__main__":
    MatriceRGB = smp.imread("essai.png")
    matrix = Matriceniveauxdegris(MatriceRGB)
    plt.imshow(matrix, cmap=plt.cm.gray)
    plt.show()