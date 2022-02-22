import numpy as np
import cv2, pickle, os

class Detector():
    def __init__(self, robots = ['blue', 'purple', 'red', 'green', 'lime', 'yellow']):
        self._nd = len(robots)
        self._num_links = (self._nd**2 - self._nd)//2

        # Data arrays (as placeholders for the multiprocessing implementation)
        self._positions_array = [0]*(self._nd*3) # x-y-phi
        self._targets_array = [0]*(self._nd*3) # x-y-phi targets
        self._active_links_array = [0]*self._num_links
        self._keep_running = [1]

        # Useful pre-computations (to draw graph)
        self._draw_graph_flag = [1]
        self._poses = np.zeros((3, self._nd))
        self._detected_flag = [1]*self._nd
        self._links = np.zeros((2, self._num_links))
        idxs = np.arange(1, self._nd)[::-1]
        first = 0
        for i in range(self._nd-1):
            self._links[0, first:first + idxs[i]] = i
            self._links[1, first:first + idxs[i]] = np.arange(i+1, self._nd)
            first += idxs[i]

        self._links = self._links.astype(int)

        # Load filters
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'color_filters/filters.pickle')
        with open(path, 'rb') as handle:
            filters = pickle.load(handle)

        # Load display colors
        path = os.path.join(directory, 'colors_display/colors_display.pickle')
        with open(path, 'rb') as handle:
            self._display_dict = pickle.load(handle)

        # Set filters
        self._filters = {}
        for id, key in enumerate(robots):
            self._filters[key] = [id, filters[key]]

        self._keys_detector = self._filters.keys() # Useful pre-computation

        # Pixels to cm conversion
        self._pix_2_cm = 8.0/40.0 # 8cm are 40 pixels
        self._cm_2_pix = 40.0/8.0 # 40 pixes are 8cm

    def run_camera(self, show=True, record_video=False):
        self._cap = cv2.VideoCapture(0)
        self.setup_video_writer(record = record_video)
        while self._keep_running[0] == 1:
            _, frame = self._cap.read()
            frame_to_show = frame.copy()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            for k in self._keys_detector:
                mask = cv2.inRange(frame, self._filters[k][1][0], self._filters[k][1][1])
                mask = cv2.erode(mask, None, iterations=2)
                mask = cv2.dilate(mask, None, iterations=2)
                cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                id = self._filters[k][0]
                #self._detected_flag[id] = 0
                if(len(cnts) == 2):
                    #self._detected_flag[id] = 1
                    ((x1, y1), r1) = cv2.minEnclosingCircle(cnts[0])
                    ((x2, y2), r2) = cv2.minEnclosingCircle(cnts[1])
                    x, y = (x1 + x2)/2.0, (y1 + y2)/2.0
                    angle = np.arctan2(y2 - y1, x2 - x1) + np.pi*np.maximum(np.sign(r2 - r1), 0)
                    x_out, y_out, angle_out = self.export_coordinates(x, y, angle)
                    self._poses[:, id] = [x, y, angle]
                    self._positions_array[id] = x_out
                    self._positions_array[id + self._nd] = y_out
                    self._positions_array[id + 2*self._nd] = angle_out

                if(show):
                    x, y, angle = self._poses[:, id]
                    x2 = int(x + 20*np.cos(angle))
                    y2 = int(y + 20*np.sin(angle))
                    cv2.line(frame_to_show, (int(x), int(y)), (x2, y2), (0, 255, 0), 2)
                    xt = self._targets_array[id]
                    yt = self._targets_array[id + self._nd]
                    xt, yt = self.import_coordinates(xt, yt)
                    cv2.circle(frame_to_show, (xt, yt), 5, self._display_dict[k], 2)

            if(show):
                if(self._draw_graph_flag[0] == 1): # draw graph
                    for i in range(self._num_links):
                        if(self._active_links_array[i] == 1):
                            j, k = self._links[0, i], self._links[1, i]
                            #if(self._detected_flag[j] == 1 and self._detected_flag[k] == 1):
                            x1, y1, x2, y2 = int(self._poses[0, j]), int(self._poses[1, j]), int(self._poses[0, k]), int(self._poses[1, k])
                            cv2.line(frame_to_show, (x1, y1), (x2, y2), (0, 0, 0), 2)

                if(self._recording_video):
                    self._writer.write(frame_to_show)
                cv2.imshow('Camera', frame_to_show)
                if(cv2.waitKey(1) & 0xFF == ord('q')):
                    break

        self._cap.release()
        self._writer.release()
        cv2.destroyAllWindows()
        self._keep_running[0] = 0

    def convert_pixels_to_cm(self, pix_value):
        return self._pix_2_cm*pix_value

    def convert_cm_to_pixels(self, cm_value):
        return int(self._cm_2_pix*cm_value)

    def export_coordinates(self, x, y, angle):
        new_x = self.convert_pixels_to_cm(x)
        new_y = 90 - self.convert_pixels_to_cm(y) # 90 is the maximum height of the platform
        new_angle = -angle
        return new_x, new_y, new_angle

    def import_coordinates(self, x, y):
        new_x = self.convert_cm_to_pixels(x)
        new_y = self.convert_cm_to_pixels(90 - y) # 90 is the maximum height of the platform
        return new_x, new_y

    def setup_video_writer(self, record = True, video_name='output'):
        self._recording_video = record
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'videos/' + video_name + '.avi')
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')                           # Working on my system
        self._writer = cv2.VideoWriter(path, fourcc, 25.0, (640, 480))     # Working on my system

    def close_detector(self):
        print('\nDetector is closed!')

if __name__ == "__main__":
    det = Detector(robots = ['blue', 'purple', 'green', 'lime', 'red', 'yellow'])
    det.setup_video_writer()
    det.run_camera(show=True)
    det.close_detector()
