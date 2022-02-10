#J'importe les librairies
##import = importer
##as = l'abréviation utilisée (Ecrire np.qqch revient à écrire numpy.qqch)
##from = dans une librairie, on importe uniquement une seule chose (une classe)
###Quentin 04/02/22
import time
import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as img
import matplotlib.cm as cm
import picamera
import picamera.array
from datetime import datetime, timedelta

#Je crée l'horloge du programme et initialise la variable numéro qui nous permettra de voir combien d'images sont prises et traitées dans un laps de temps donné
#(nombre d'images / temps donné en seconde)x10800 = nombre d'image prises et analysées en 3h à fréquence constante.
###Quentin 10/02/22
instantdébut = datetime.now()
instantactuel = datetime.now()
numéro = 1
#Je définis une fonction qui aura pour but de retourner l'objet combined
##def = définir 
##return = ce que la fonction sort en résultat lorsqu'elle est appelée
##Je crée la fonction disp_multiple() qui servira à créer l'objet combined qui sera divisé en 4 parties (im1, im2, im3, im4)
##Je passe des paramètres aux 4 parties de combined que je dimensionne entre les []
###Quentin 04/02/22
def disp_multiple(im1=None):
    height, width = im1.shape

    combined = np.zeros((2 * height, 2 * width, 3), dtype=np.uint8)

    combined[0:height, 0:width, :] = cv2.cvtColor(im1, cv2.COLOR_GRAY2RGB)
    return combined

#Je crée des "labels" aux parties de combined
##Pas d'explication particulière ici
###Quentin 04/02/22
def label(image, text):
    return cv2.putText(image, text, (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

#Je mets un contraste aux parties de combined
##On pourrait s'étendre sur des explications poussées mais ce n'est pas vraiment nécessaire.
##Vous pouvez recopier ce morceau tel quel
###Quentin 04/02/22
def contrast_stretch(im):
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)

    out_min = 0.0
    out_max = 255.0

    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min

    return out

#C'est ici que se trouve le plus gros du script.
#Je vais donc faire les explications à l'intérieur de la fonction
###Quentin 04/02/22
def run():
    ###########################################################################
    with picamera.PiCamera() as camera:
        ##Ici, je fais les paramétrages de la résolution en lui donnant une résolution de 2592 sur 1944 pixels
        ###Quentin 10/02/22
        camera.resolution = (2592, 1944)
        time.sleep(1)
    ###########################################################################

    with picamera.array.PiRGBAarray(camera) as stream:
        ##Ici, je paramètre le programme de façon à ce qu'il tourne en boucle pendant une durée définie
        ##Et je donne à la variable image analysée, la valeur de l'image captée par la caméra
        ###Quentin 10/02/22
        while (instantactuel < instantdébut + timedelta(seconds=20)):
            camera.capture(stream, format ='bgr', use_video_port=True)
            ##Ici, j'initialise une variable "image analysée" à laquelle je donne la valeur de l'image captée par la caméra
            imageanalysée = stream.array
            ##b = quantité de bleu
            ##v = quantité de vert
            ##r = quantité de rouge
            b, v, r = cv2.split(imageanalysée)
            ##Ici je commence le calcul de la NDVI en calculant d'abord le dessous de la fraction (vous référez à https://eos.com/make-an-analysis/ndvi/ pour la formule.)
            dessousfraction = (r.astype(float) + b.astype(float))
            ##Ici je m'assure que le dénominateur ne sera pas égal à 0 et si il est égal à 0 je lui donne arbitrairement la valeur de 0,01 afin de quand même pouvoir calculer
            ##mais avec une petite marge d'erreur. Vous pouvez réduire la valeur autant que vous voulez du moment qu'elle reste > 0
            dessousfraction[dessousfraction == 0] = 0.01
            ##Ici je termine le calcul de la NDVI en faisant la division complète
            ndvi = (r.astype(float) - b) / dessousfraction
            ##Ici je donne la valeur de la ndvi au contraste de chaque pixel de l'image
            ndvi = contrast_stretch(ndvi)
            ndvi = ndvi.astype(np.uint8)
            ##Ici je donne un titre à chaque élément de l'objet combined
            label(b, 'Bleu')
            label(v, 'Vert')
            label(r, "NIR")
            label(ndvi, 'NDVI')

            ##Ici je rassemble toutes les parties de l'objet combined selon l'ordre donnée lors de la définition de la fonction disp_multiple() (Juste après l'importation des librairies)
            combined = disp_multiple(ndvi)
    
            ##Ici je crée l'image à afficher et la sauvegarde sous le nom "sauvegarde.jpg" + la valeur de la variable numéro
            ##Attention, on devra utiliser un autre système pour nommer les images sinon on perdra la précédente à chaque sauvegarde d'une nouvelle image
            plt.imshow(ndvi)
            cv2.imwrite("image sauvegardée " + str(numéro) + ".png", combined)
            plt.show()
            plt.savefig('sauvegarde.png')
            numéro +=1

##Ici j'exécute tout le script
###Quentin 04/02/22
if __name__ == '__main__':
    run()
