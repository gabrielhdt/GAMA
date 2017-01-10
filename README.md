# GAMA
Vectorisation d'images

## Vectorisation d'une image
1. Lecture de l'image avec `matrgb = scipy.misc.imread(imagefile)`
2. passage en niveaux de gris avec `matgl = image_processing.Matriceniveauxdegris(matrgb)`;
3. ajout des bordures `matgl = image_processing.add_border(matgl)`;
4. filtrage: regroupement des couleurs (évite les dégradés) `matgl = image_processing.regroupement_couleur(matgl, seuil)`
5. premier ensemble de contours `contset = image_processing.contours_image(matgl, seuil)`
6. séparation des contours
  ```python
  separated_cont = []
    for cont in contset:
        separated_cont += image_processing.separate_all_contours(cont)
    contset = set(separated_cont)
  ```
7. suppression des doublons `image_processing.remove_double(contset)`
8. affinage des contours
  ```python
  for cont in contset:
        cont.skinnier()
  ```
9. points d'inflexion et de contrôle pour un contour: `curves = control_points.list_curves([cont])` suivi de `curvemat = control_points.curves2curvemat(curves)`;
10. création d'un fichier svg `svgfile = writeSvg.SvgFile(svgname, dim)`
11. écriture du contour `svgfile.draw_contour(curvemat)`
12. fermeture du fichier `svgfile.close_svg()`

Pour l'écriture d'un contour en pixels: `svgfile.draw_contour_pix(cont)` avec `cont` un contour.
