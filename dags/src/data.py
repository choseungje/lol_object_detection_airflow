import numpy as np
import cv2
import json
from copy import deepcopy
import os
from tqdm import tqdm


np.random.seed(0)


# yolo = x, y, width, height
def _image_compositing(
    background, target, label_num, save_path: str, save_txt_path: str
):
    row = col = 0
    while 1:
        row = np.random.randint(background.shape[0])
        col = np.random.randint(background.shape[1])

        mask_end_row = row + target.shape[0]
        mask_end_col = col + target.shape[1]

        if mask_end_row < background.shape[0] and mask_end_col < background.shape[1]:
            break

    background[row:mask_end_row, col:mask_end_col, :] = 0
    background[row:mask_end_row, col:mask_end_col, :] = target

    cv2.imwrite(save_path, background)

    center_x = round(((row + mask_end_row) // 2) / background.shape[0], 6)
    center_y = round(((col + mask_end_col) // 2) / background.shape[1], 6)

    width = round(target.shape[1] / background.shape[1], 6)
    height = round(target.shape[0] / background.shape[0], 6)
    # print(center_x, center_y, width, height)

    with open(save_txt_path, "w") as f:
        f.write(f"{label_num} {center_y} {center_x} {width} {height}")


def create_dataset(background_path, labels_path, create_num, labels, save_folder: str):
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)
    images_folder = save_folder + "/images"
    if not os.path.exists(images_folder):
        os.mkdir(images_folder)
    labels_folder = save_folder + "/labels"
    if not os.path.exists(labels_folder):
        os.mkdir(labels_folder)

    background = cv2.imread(background_path)

    for label in labels:
        path = labels_path + label + ".png"
        target = cv2.imread(path)
        for i in tqdm(range(create_num // len(labels))):
            background_img = deepcopy(background)
            save_path = save_folder + "/images/" + label + f"_{i}.jpg"
            save_txt_path = save_folder + "/labels/" + label + f"_{i}.txt"
            _image_compositing(
                background_img, target, labels[label], save_path, save_txt_path
            )