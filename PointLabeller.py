import os
import cv2
import random
import pandas as pd
import numpy as np

from pathlib import Path

def obtain_images(listOfFolders):

    imgLabelFilepaths = []

    for folder in listOfFolders:

        images = []

        try:
            images =[os.path.join(folder, i) for i in os.listdir(folder)]

            if len(images) == 0:
                print("No images found in directory: " + str(folder))
                continue

            # check against existing save files to see if labelling required or not
            # output_directory = os.listdir(os.path.join(os.getcwd(), "output", "labels_eye_centre"))

            # check_against_participant = folder.split("/")[-2]+"_0.csv"

            
            # if output_directory.count(check_against_participant):
            #     print("Participant data: " + check_against_participant + " already labelled, skipping...")
            #     continue



        except FileNotFoundError:
            print("Directory does not exist: " + str(folder))
            continue

        selected_images = random.choices(images, k=10)
        imgLabelFilepaths.append(selected_images)

    return imgLabelFilepaths

def label_data(imgFolder, labelPaths):

    for set_of_paths in labelPaths:

        print(str(set_of_paths[0]).split("eme2_square_imgs/")[-1].split("/")[0])

        tmp_label_storage = []
        participant = (set_of_paths[0].split("eme2_square_imgs/"))[-1].split("/")[0]
        trialNum = (set_of_paths[0].split("eme2_square_imgs/"))[-1].split("/")[1]
        count = 0

        for path in set_of_paths:

            print(str(count) + "/" + str(len(set_of_paths)))

            global im

            im = cv2.imread(path)

            cv2.namedWindow('image')
            cv2.setMouseCallback('image', draw_circle)

            tmp_storage =  []

            while(1):

                cv2.imshow('image', im)

                k = cv2.waitKey(20) & 0xFF

                if k == ord('n'):
                    # skip/go to next image
                    break

                elif k == ord('a'):
                    new_coords = (MOUSE_X, MOUSE_Y)
                    print(new_coords)
                    tmp_storage.append(new_coords)

            cv2.destroyAllWindows()

            if len(tmp_storage) == 4:

                l_outer_x = tmp_storage[0][0]
                l_outer_y = tmp_storage[0][1]
                l_inner_x = tmp_storage[1][0]
                l_inner_y = tmp_storage[1][1]
                
                r_outer_x = tmp_storage[2][0]
                r_outer_y = tmp_storage[2][1]
                r_inner_x = tmp_storage[3][0]
                r_inner_y = tmp_storage[3][1]
                

            else:
                print("Wrong number of coordinates... INDICATING")
                l_outer_x, l_outer_y, l_inner_x, l_inner_y, r_outer_x, r_outer_y, r_inner_x, r_inner_y = 1, 1, 1, 1, 1, 1, 1, 1

            image_information = [path.split("eme2_square_imgs/")[-1], l_outer_x, l_outer_y, l_inner_x, l_inner_y, r_outer_x, r_outer_y, r_inner_x, r_inner_y]
            tmp_label_storage.append(image_information)
            count += 1

        # save labels to csv file
        df = pd.DataFrame(tmp_label_storage, columns=["filename", "l_outer_x", "l_outer_y", "l_inner_x", "l_inner_y", "r_outer_x", "r_outer_y", "r_inner_x", "r_inner_y"])
        df.to_csv(os.path.join(os.getcwd(), "output", "labels_eye_corners", participant + "_" + trialNum + ".csv"))

def draw_circle(event,x,y,flags,param):

    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(im,(x,y), 4, (0,0,255), -1)


        global MOUSE_X
        MOUSE_X = x
        global MOUSE_Y
        MOUSE_Y = y

        print(MOUSE_X, MOUSE_Y)

if __name__ == '__main__':

    # initialise key filepaths
    root_folder = os.getcwd()

    img_source_folder = os.path.join(root_folder, "mnt", "eme2_square_imgs") # filepath to images
    participant_folders = [os.path.join(img_source_folder, i) for i in os.listdir(img_source_folder)]

    trial_folders = []
    for i in ["0", "1", "2", "3"]:
        for participant in participant_folders:
            trial_folders.append(os.path.join(participant, i))

    filepaths_to_label = obtain_images(trial_folders)
    # print(len(filepaths_to_label))

    # label chosen filepaths
    label_data(img_source_folder, filepaths_to_label)
