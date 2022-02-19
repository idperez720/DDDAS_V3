##
import numpy as np
import matplotlib.pyplot as plt
import os
from skimage.morphology import *
from scipy.ndimage.morphology import *

def read_file(dir):
    # Open file txt with location info
    with open(dir) as f:
        raw_info = f.readline()
    return  raw_info

def process_txt(raw_info, scale_factor):
    list_raw = raw_info.split(";")
    x_coor = np.array([])
    y_coor = np.array([])
    for each_coor in list_raw:
        print(each_coor)
        coor = each_coor.split(",")
        x_coor = np.append(x_coor, float(coor[0])*scale_factor)
        y_coor = np.append(y_coor, float(coor[1])*scale_factor)
    return x_coor, y_coor

def conv2D(img, kernel):
    shape = np.shape(img)
    size_kernel = len(kernel)//2
    new_img = np.zeros((shape[0]+2*size_kernel, shape[1]+2*size_kernel))
    new_img[size_kernel:len(new_img)-size_kernel,size_kernel:len(new_img[0])-size_kernel] = img

    for i in range(len(img)):
        for j in range(len(img[0])):
            i_img = i+size_kernel
            j_img = j+size_kernel
            sub_img = new_img[i_img-size_kernel:i_img+size_kernel+1,j_img-size_kernel:j_img+size_kernel+1]
            value = np.sum(np.multiply(sub_img, kernel))
            if not (255 in sub_img):
                img[i, j] = value
    return img


def generate_board(dim, x_coor, y_coor):
    new_board =255*np.ones((dim[0],dim[1])).astype(np.uint8)
    for i in range(len(x_coor)):
        if int(x_coor[i]) >= 0 and int(y_coor[i]) >= 0:
         new_board[int(x_coor[i]),int(y_coor[i])] = 0
    return new_board

def process_board(kernel_dim, board):
    kernel = np.ones(kernel_dim)
    new_board = conv2D(board, kernel)
    return new_board

def main():
    print("Welcome! This is the first functional prototype of DWhiteBoard,\n  once system is conected and running please press any key...")

    empty = input("")
    scale_factor = 10
    x_coor_prev = -1
    y_coor_prev = -1
    t=0

    print("Firstly, lets check all docs are on the appropiate folder. \n The .txt file must be on the following dir: \n", os.getcwd())
    dir = input("Enter the name of the file (including .txt extension): ")

    graph = True
    while graph:
        raw_file = read_file(dir)
        x_coor_t, y_coor_t = process_txt(raw_file, scale_factor)

        for i in range(len(x_coor_t)):
            x_coor = np.append(x_coor_t[i], x_coor_prev)
            y_coor = np.append(y_coor_t[i], y_coor_prev)

            board_raw = generate_board((500, 500), x_coor, y_coor)

            # Taking a matrix of size 5 as the kernel
            board_proc = binary_erosion(board_raw, np.ones((5, 5), np.uint8), iterations=3)

            plt.ion()
            plt.show()
            plt.imshow(board_proc, cmap="gray")
            plt.title("t = {}".format(t))
            plt.draw()
            plt.pause(0.001)
            plt.clf()

            x_coor_prev = np.append(x_coor_prev, x_coor_t[i])
            y_coor_prev = np.append(y_coor_prev, y_coor_t[i])
            t += 1

        if t==50:
            break

main()
