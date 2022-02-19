##
import numpy as np
import skimage.io as io
import os
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu

def fijar_bordes(img):
    l = len(img)
    a = len(img[0])
    new = np.zeros((l, a))
    new[0,:a-1] = np.ones((1,a-1))
    new[l-1,:a - 1] = np.ones((1,a-1))
    new[:l-1, 0] = np.ones((l-1,1))
    new[:l - 1, a-1] = np.ones((l - 1, 1))
    img_final = (img+new)>=1
    return  img_final



plt.figure()
img_raw = io.imread(os.path.join(os.getcwd(),"imagen_final.jpg")) #Se guarda la imagen en una variable

xlen = 1000 #Arbitrarios
ylen = 1500
img_raw = img_raw[100:xlen, 300:ylen,:]

plt.imshow(img_raw)

otsu_umbral = threshold_otsu(img_raw) #Aplicación de la función de otsu
img_otsu = img_raw < otsu_umbral #Binarización de la imagen


plt.subplot(2,2,1)
plt.imshow(img_raw, cmap="gray")
plt.title("Imagen raw")

plt.subplot(2,2,2)
plt.imshow(img_otsu[:,:,0], cmap="gray")
plt.title("Canal R")

plt.subplot(2,2,3)
plt.imshow(img_otsu[:,:,1], cmap="gray")
plt.title("Canal G")

plt.subplot(2,2,4)
plt.imshow(img_otsu[:,:,2], cmap="gray")
plt.title("Canal B")

img_final = (img_otsu[:,:,2]+img_otsu[:,:,1]+img_otsu[:,:,0])>=1

plt.figure()
plt.imshow(img_final, cmap="gray")
plt.title("Imagen binarizada")

img_final_bordes = fijar_bordes(img_final)

plt.figure()
plt.imshow(img_final_bordes, cmap="gray")
plt.title("Imagen binarizada con bordes")

