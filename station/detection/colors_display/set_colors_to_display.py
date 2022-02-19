import os
import pickle

display = {}
display['blue'] = (255, 128, 0)
display['purple'] = (255, 1, 146)
display['red'] = (0, 0, 255)
display['green'] = (0, 117, 39)
display['lime'] = (0, 255, 85)
display['yellow'] = (0,255,239)

directory = os.path.dirname(__file__)
path = os.path.join(directory, 'colors_display.pickle')
with open(path, 'wb') as handle:
    pickle.dump(display, handle, protocol=pickle.HIGHEST_PROTOCOL)
