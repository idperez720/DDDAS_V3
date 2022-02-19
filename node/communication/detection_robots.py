##
import numpy as np
import skimage.io as io
from skimage.color import *
import os
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu
import cv2

def calc_hist(img):
    size = len(img) * len(img[0])

    hist_r = np.histogram(np.array(img[:, :, 0].flatten('C')), bins=255, range=(0, 255))
    hist_g = np.histogram(np.array(img[:, :, 1].flatten('C')), bins=255, range=(0, 255))
    hist_b = np.histogram(np.array(img[:, :, 2].flatten('C')), bins=255, range=(0, 255))

    new_hist = np.append(hist_r[0] / size, hist_g[0] / size)
    new_hist = np.append(new_hist, hist_b[0] / size)

    new_base = np.append(hist_r[1][:-1], hist_g[1][:-1] + 255)
    new_base = np.append(new_base, hist_b[1][:-1] + 255 * 2)
    return new_hist, new_base

def import_ref_img(list):
    res = {}
    for each_img in list:
        img = io.imread(os.path.join(os.getcwd(),"Robot_"+each_img+".JPG"))
        new_hist, new_base = calc_hist(img)
        res[each_img] = new_hist, new_base
    return  res

def intersect_hist(hist_1, hist_2):
    sim = 0
    for i in range(len(hist_1)):
        sim += min(hist_1[i], hist_2[i])
    sim /= 3
    return sim

def looking_for_robots(img, robots_list, robots_hist, size_kernel=111//2):

    best_fit_value = {}
    best_fit_coor = {}

    shape = np.shape(img)
    new_img = np.zeros((shape[0]+2*size_kernel, shape[1]+2*size_kernel,3))
    new_img[size_kernel:len(new_img)-size_kernel,size_kernel:len(new_img[0])-size_kernel] = img

    for i in range(0,len(img),2):
        for j in range(0,len(img[0]),2):
            i_img = i+size_kernel
            j_img = j+size_kernel
            sub_img = new_img[i_img-size_kernel:i_img+size_kernel+1,j_img-size_kernel:j_img+size_kernel+1]

            hist = calc_hist(sub_img)

            for each_robot in robots_list:
                fit = intersect_hist(hist[0], robots_hist[each_robot][0])
                if each_robot not in best_fit_value:
                    best_fit_value[each_robot] = fit
                    best_fit_coor[each_robot] = (i,j)
                else:
                    if best_fit_value[each_robot] < fit:
                        best_fit_value[each_robot] = fit
                        best_fit_coor[each_robot] = (i, j)
                        print(best_fit_coor)

    return best_fit_coor

def plot_ref_hist(robots, colors, ref_hist):
    plt.figure()
    for i in range(len(robots)):
        plt.subplot(3, 2, i + 1)
        info = ref_hist[robots[i]]
        plt.bar(info[1], info[0], color=colors[i])
        plt.axis("off")
        plt.title(robots[i])

def locate_boxes(img, coor, robots_lits, color_list, size=111):
    for i in range(len(robots_lits)):
        coor_xy = coor[robots_lits[i]]
        sub_image = img[coor_xy[0]-size//2:coor_xy[0]+size//2,coor_xy[1]-size//2:coor_xy[1]+size//2]

        l = len(sub_image)
        sub_image[:,0,:] = np.ones(np.shape(sub_image[:,0,:]))*color_list[i]
        sub_image[:, l-1, :] = np.ones(np.shape(sub_image[:, l-1, :]))*color_list[i]

        sub_image[0,:,:] = np.ones(np.shape(sub_image[0,:,:]))*color_list[i]
        sub_image[l-1, :, :] = np.ones(np.shape(sub_image[l-1, :, :]))*color_list[i]

        img[coor_xy[0] - size // 2:coor_xy[0] + size // 2, coor_xy[1] - size // 2:coor_xy[1] + size // 2] = sub_image

    return  img


def main():
    input_camara = io.imread(os.path.join(os.getcwd(),"imagen_final.jpg")) #Se guarda la imagen en una variable

    robots = ["verde", "rojo", "verdec", "azul", "amarillo", "morado"]
    colors = ["green", "red", "greenyellow", "blue", "yellow", "purple"]
    colors_rgb = [[3,255,62], [255,0,0], [158, 255, 68], [0, 26, 255], [255, 255, 0], [180,0,255]]

    ref_hist = import_ref_img(robots)
    #plot_ref_hist(robots, colors, ref_hist)

    plt.figure()
    plt.subplot(2,1,1)
    plt.imshow(input_camara)
    plt.axis("off")

    coor = looking_for_robots(input_camara, robots, ref_hist)
    new_image = locate_boxes(input_camara, coor, robots, colors_rgb)

    plt.subplot(2,1,2)
    plt.imshow(new_image)
    plt.axis("off")

main()


