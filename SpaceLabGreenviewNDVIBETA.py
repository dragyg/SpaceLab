#Import libraries
import time
import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import picamera
import picamera.array
from datetime import datetime, timedelta
from orbit import ISS
import reverse_geocoder as rg
import math
from pathlib import Path

#Set the time
instantdebut = datetime.now()
instantactuel = datetime.now()
#This variable will be used to compute the distance between the camera point and the nearest city
distanceok = 1
#Data folder
base_folder = Path(__file__).parent.resolve()

def contrast_stretch(im):
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)

    out_min = 0.0
    out_max = 255.0

    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min

    return out

def run():
    with picamera.PiCamera() as camera:
        ##Sets the camera's resolution to 2592x1944
        camera.resolution = (2592, 1944)
        time.sleep(10)

    with picamera.array.PiRGBArray(camera) as stream:
        ##Sets a 175 minutes loop
        while (instantactuel < instantdebut + timedelta(minutes=175)):
            ##Search for the coordinates of the nearest city
            coordoneesISS = ISS.coordinates()
            coordoneesVILLE = (coordoneesISS.latitude.degrees, coordoneesISS.longitude.degrees)
            ville = rg.search(coordoneesVILLE)
            ##Computes the distance between the nearest city and the camera point (source: https://www.wikiwand.com/fr/Trigonom%C3%A9trie_sph%C3%A9rique)
            distanceok = 6,371*np.arccos(np.sin(coordoneesISS.latitude.radians) * np.sin((2*math.pi*ville.lat)/180) + np.cos(coordoneesISS.latitude.radians) * np.cos((2*math.pi*ville.lat)/180) * np.cos((2*math.pi*ville.lon)/180 - coordoneesISS.longitude.radians))
            ##Checks if the distance between the nearest city and the camera point is inferior to 10 kilometers
            if distanceok < 10:
                camera.capture(stream, format ='bgr', use_video_port=True)
                ##Sets an 'imageanalysee' variable to store the datas collected by the camera as an array
                imageanalysee = stream.array
                ##b = blue value
                ##g = green value
                ##r = red value
                ##Stores individual components of the 'imageanalysee' array in 3 lists.
                b, g, r = cv2.split(imageanalysee)
                ##Computes the NDVI (source: https://eos.com/make-an-analysis/ndvi/)
                ##Computes first the bottom half of the fraction
                dessousfraction = (r.astype(float) + b.astype(float))
                ##Check for values equal to 0 and set them to 0.01 to prevent divide by 0 error.
                dessousfraction[dessousfraction == 0] = 0.01
                ##Computes the whole NDVI fraction
                ndvi = (r.astype(float) - b) / dessousfraction
                ##Makes an NDVI image
                ndvi = contrast_stretch(ndvi)
                ndvi = ndvi.astype(np.uint8)
                ##Makes the non-NDVI image
                imageanalysee = contrast_stretch(imageanalysee)
                imageanalysee = imageanalysee.astype(np.uint8)
                ##Sets a nowtime variable for labelization
                nowtime = datetime.now()
                ##Makes the NDVI image file to store in the data folder as nowtimeNDVI.png
                plt.imshow(ndvi)
                plt.title("NDVI" + coordoneesISS)
                plt.savefig(base_folder/nowtime + 'NDVI.png')
                plt.close()
                ##Makes the non NDVI image file to store in the date folder as nowtime.png
                plt.imshow(imageanalysee)
                plt.title(coordoneesISS)
                plt.savefig(base_folder/nowtime + '.png')
            #Upgrades the program's clock to now time
            instantactuel = datetime.now()

##launch the run function
if __name__ == '__main__':
    run()
