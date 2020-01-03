import cv2
import numpy as np
from keras.utils import to_categorical


def image_generator(x_original, y1_original, y2_original, batch_size=5, input_size=224, shuffle=True):
    x_copy, y1_copy, y2_copy = x_original[:], y1_original[:], y2_original[:]
    while True:

        if len(x_copy) < batch_size:
                x_copy, y1_copy, y2_copy = x_original[:], y1_original[:], y2_original[:]

        x, y_bins, y_stacks, y_values = list(), list(), list(), list()
        total_images = 0

        while total_images < batch_size:
            index = 0
            if shuffle: index = np.random.choice(range(len(x_copy)))
            img_id, y1_val, y2_val = x_copy.pop(index), y1_copy.pop(index), y2_copy.pop(index)

            img = cv2.imread(img_id, cv2.IMREAD_UNCHANGED)
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            img = cv2.resize(img, (input_size, input_size), interpolation=cv2.INTER_AREA)
            x.append(img / 255)
            y_bins.append(y1_val - 1)
            y_values.append(np.array(y2_val))
            total_images += 1


        yield np.array(x), [to_categorical(y_bins, num_classes=15),
                            np.array(y_values)[:, 0], np.array(y_values)[:, 1], np.array(y_values)[:, 2],
                            np.array(y_values)[:, 3], np.array(y_values)[:, 4], np.array(y_values)[:, 5],
                            np.array(y_values)[:, 6], np.array(y_values)[:, 7], np.array(y_values)[:, 8],
                            np.array(y_values)[:, 9], np.array(y_values)[:, 10], np.array(y_values)[:, 11],
                            np.array(y_values)[:, 12], np.array(y_values)[:, 13], np.array(y_values)[:, 14]]
