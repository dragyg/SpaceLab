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
from orbit import ISS
import reverse_geocoder as rg
import math
from pathlib import Path

#Je crée l'horloge du programme
###Quentin 10/02/22
instantdébut = datetime.now()
instantactuel = datetime.now()
#Je crée la variable qui va me permettre de mesurer l'écart entre l'ISS et la ville
###Quentin 20/02/22
distanceok = 1
#Je crée le fichier d'enregistrement des données
###Quentin 20/02/22
base_folder = Path(__file__).parent.resolve()
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
        ###Quentin 10/02/22
        while (instantactuel < instantdébut + timedelta(seconds=20)):
            ##Ici, je prends la position de l'ISS et je cherche la ville la plus proche
            ###Quentin 20/02/22
            coordonéesISS = ISS.coordinates()
            coordonéesVILLE = (coordonéesISS.latitude.degrees, coordonnéesISS.longitude.degrees)
            ville = rg.search(coordonéesVILLE)
            ##Ici, je calcule la distance entre l'ISS et la ville la plus proche (vous référer à https://www.wikiwand.com/fr/Trigonom%C3%A9trie_sph%C3%A9rique pour la formule.)
            ##Si marche pas: remplacer toutes les occurences de ville.lat par float(ville.lat)
            ###Quentin 20/02/22
            distanceok = 6,371*np.arccos(np.sin(coordonéesISS.latitude.radians) * np.sin((2*math.pi*ville.lat)/180) + np.cos(coordonéesISS.latitude.radians) * np.cos((2*math.pi*ville.lat)/180) * np.cos((2*math.pi*ville.lon)/180 - coordonéesISS.longitude.radians))
            if distanceok < 0.5:
                camera.capture(stream, format ='bgr', use_video_port=True)
                ##Ici, j'initialise une variable "image analysée"#
                ##à laquelle j'attribue la valeur d'une image au format jpg. Je ne vais pas m'étendre sur le procédé car vous utiliserez la librairie picamera#
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
                combined = disp_multiple(imageanalysée, ndvi)
    
                ##Ici je crée l'image à afficher et la sauvegarde au format jpg en lui donnant pour nom l'heure d'exécution du script.
                plt.imshow(ndvi)
                plt.show()
                plt.savefig(base_folder/datetime.now() + '.png')

##Ici j'exécute tout le script
###Quentin 04/02/22
if __name__ == '__main__':
    run()
