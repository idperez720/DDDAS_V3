import cv2
import pickle
import os

# Load filters
directory = os.path.dirname(__file__)
path = os.path.join(directory, 'color_filters/filters.pickle')
with open(path, 'rb') as handle:
    filters = pickle.load(handle)


def run_camera(colors_to_test = ['blue', 'purple', 'red', 'green', 'lime', 'yellow'], radius=10):
    global filters

    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()
        frame_to_show = frame.copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        for k in colors_to_test:
            mask = cv2.inRange(frame, filters[k][0], filters[k][1])
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            _, cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if(len(cnts) == 2):
                ((x1, y1), r1) = cv2.minEnclosingCircle(cnts[0])
                ((x2, y2), r2) = cv2.minEnclosingCircle(cnts[1])
                x, y = (x1 + x2)/2.0, (y1 + y2)/2.0
                cv2.circle(frame_to_show, (int(x), int(y)), radius, (0, 255, 0), 2)
                print('x = ', int(x*8/40), 'y = ', int(y*8/40))

        cv2.imshow('Camera', frame_to_show)
        if(cv2.waitKey(1) & 0xFF == ord('q')):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    cond = 1
    while(cond):
        print('Input radius (in pixels) to test:')
        radius = int(input())
        print('Running camera with radius = ', radius, '. Press q to quit.')
        run_camera(colors_to_test=['red'], radius=radius)
        print('Try new radius? Type 1 (yes) or 0 (no).')
        cond = int(input())
        print('The calibrated radius is: ', radius)
