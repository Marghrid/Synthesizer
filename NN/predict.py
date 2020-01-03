import os
os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"
from collections import defaultdict

import efficientnet.keras as efn
import numpy as np
import pandas as pd
from keras import Model, losses
from keras import backend as K
from keras.layers import GlobalAveragePooling2D, Dense, RepeatVector, LSTM
import argparse
import cv2


#from tensorflow import set_random_seed


from generator import image_generator
from keras_lookahead import Lookahead

BATCH_SIZE = 15
N_TOTAL_BARS = 15
INPUT_SIZE = 240

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_PATH = CURRENT_PATH + "/weights/weights.hdf5"



def get_model():
    base_model = efn.EfficientNetB1(weights='imagenet', include_top=False)
    x = base_model.output
    x = GlobalAveragePooling2D()(x)

    output_values = [Dense(N_TOTAL_BARS, activation='softmax')(x)]
    for _ in range(N_TOTAL_BARS):
        output_values.append(Dense(1, activation=lambda z: K.clip(z, 0, 1))(x))

    model = Model(inputs=base_model.input, outputs=output_values)
    return model


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-image_path', metavar='i', type=str, help='image path')
    parser.add_argument('-max', metavar='m', type=int, help='max value y')
    args = parser.parse_args()

    model = get_model()
    model.load_weights(WEIGHTS_PATH)

    img = cv2.imread(args.image_path, cv2.IMREAD_UNCHANGED)
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    img = cv2.resize(img, (INPUT_SIZE, INPUT_SIZE), interpolation=cv2.INTER_AREA)
    img = img / 255
    #print(img)

    y = model.predict(np.array([img]))
    n_bars = np.argmax(y[0]) + 1
    values = y[1:]

    print('({}, {})'.format(n_bars, [el[0][0]*args.max for el in values]))


