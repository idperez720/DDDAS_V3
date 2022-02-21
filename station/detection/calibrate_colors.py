import numpy as np
import cv2
import pickle
import os


def click_values(event, x, y, flags, param):
    global counter

    if event == cv2.EVENT_RBUTTONDOWN:
        counter = np.clip(counter + 1, 0, 5)
        key = colors[counter]
        print('Left click on the ', key, ' robot. Press the right click for next robot or q to quit.')

    if event == cv2.EVENT_LBUTTONDOWN:
        pixels = frame[y, x, :]
        key = colors[counter]
        values[key].append(pixels)
        print('Values registered for the ', key, ' robot ---> ', pixels)

def run_calibration_camera(filters, robot_to_filter = -1):
    global frame, counter, values
    counter = 0

    cv2.namedWindow('Camera')
    cv2.setMouseCallback('Camera', click_values, param=counter)
    cap = cv2.VideoCapture(0)

    while(True):
        _, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if(robot_to_filter in values.keys()):
            k = robot_to_filter
            frame = cv2.inRange(frame, filters[k][0], filters[k][1])
            frame = cv2.erode(frame, None, iterations=2)
            frame = cv2.dilate(frame, None, iterations=2)

        cv2.imshow('Camera', frame)
        if(cv2.waitKey(1) & 0xFF == ord('q')):
            break
    cap.release()
    cv2.destroyAllWindows()

def run_test_camera(colors_to_test = ['blue', 'purple', 'red', 'green', 'lime', 'yellow']):
    global filters

    cap = cv2.VideoCapture(0)

    while(True):
        _, frame = cap.read()
        frame_to_show = frame.copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        for k in colors_to_test:
            mask = cv2.inRange(frame, filters[k][0], filters[k][1])
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            _, cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(cnts) > 0:
                for c in cnts:
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    if radius > 0:
                        cv2.circle(frame_to_show, (int(x), int(y)), int(radius), (0, 255, 0), 2)

        cv2.imshow('Camera', frame_to_show)
        if(cv2.waitKey(1) & 0xFF == ord('q')):
            break
    cap.release()
    cv2.destroyAllWindows()


def main_calibrate_colors(mode, colors, n):
    global values

    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 'color_filters/filters.pickle')

    if (mode == 'calibrate'):
        TRAIN = True
        TEST = True
    else:
        TRAIN = False
        TEST = True
        with open(path, 'rb') as handle:
            filters = pickle.load(handle)

    if(TRAIN):
        values = {}
        filters = {}
        counter = 0
        slack = 30
        for i in range(n):
            values[colors[i]] = []

        print('_____________________________')
        print('Left click on the ', colors[counter], ' robot. Press the right click for next robot or q to quit.')
        run_calibration_camera( filters,-1)

        print('_____________________________')
        keys = values.keys()
        print('Finished. Registered ', len(keys), 'robots. Computing filters...')

        for k in keys:
            if(len(values[k]) > 0):
                records = np.array(values[k])
                mean = np.mean(records, 0)
                std = np.std(records, 0)
                min_v = np.maximum(mean - std, np.min(records, 0)) - slack
                max_v = np.minimum(mean + std, np.max(records, 0)) + slack
                min_v[2], max_v[2] = min_v[2] - slack, max_v[2] + slack
                filters[k] = [np.clip(min_v, 0, 255), np.clip(max_v, 0, 255)]
                run_calibration_camera(k)

        print('_____________________________')
        print('Testing detection...')

    if(TEST):
        for key in filters.keys(): # To test one robot at a time
            print('Testing '+ key + ' robot!')
            run_test_camera([key])

    if(TRAIN):
        print('_____________________________')
        print('Saving filters...')
        with open(path, 'wb') as handle:
            pickle.dump(filters, handle, protocol=pickle.HIGHEST_PROTOCOL)

        print('Filters saved!')

