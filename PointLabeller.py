import os
import cv2
import random
import pandas as pd
import numpy as np

from pathlib import Path

NUM_POINTS = 2
COLS = ["filename", "x1", "y1", "x2", "y2"]

def obtain_image_filepaths(folder):

    try:
        img_filepaths =[os.path.join(folder, i) for i in os.listdir(folder)]

        if len(img_filepaths) == 0:
            print("No images found in directory: " + str(folder))

        # check against existing save files to see if labelling required or not
        # output_directory = os.listdir(os.path.join(os.getcwd(), "output", "labels_eye_centre"))

        # check_against_participant = folder.split("/")[-2]+"_0.csv"

        
        # if output_directory.count(check_against_participant):
        #     print("Participant data: " + check_against_participant + " already labelled, skipping...")
        #     continue

    except FileNotFoundError:
        print("Directory does not exist: " + str(folder))

    return img_filepaths
    
def random_selection(list_of_filepaths, n):
    
    if len(list_of_filepaths) < n:
        return list_of_filepaths
    else:
        selected_images = random.choices(list_of_filepaths, k=n)
        return selected_images

def load_image(filepath):

    # load image
    global im
    im = cv2.imread(filepath)
    cv2.namedWindow('image')

    # draw blink region box on image
    
    blink_region(width=50)
    cv2.setMouseCallback('image', draw_circle)

def blink_region(width):
    cv2.rectangle(im, (0, 0), (width, width), (255, 0, 0), 5)

def define_points(filepath):

    tmp_label_storage = []

    width=50
    
    while(1):

        cv2.imshow('image', im)
        k = cv2.waitKey(20) & 0xFF

        if k == ord('n'):
            # skip/go to next image
            break

        elif k == ord('a'):
            # check that the coordinate is not in the region box
            if MOUSE_X < width and MOUSE_Y < width: 
                new_coords = (0, 0)
            else:
                new_coords = (MOUSE_X, MOUSE_Y)
            
            # save coordinate
            # print(new_coords)
            tmp_label_storage.append(new_coords)

        elif k == ord('r'):
            print("Resetting labels...")
            reset_image(filepath)
            tmp_label_storage = []

        elif k ==ord('p'):
            print("Current coordinates: " + str(tmp_label_storage))

    return tmp_label_storage

def reset_image(filepath):
    cv2.destroyAllWindows()
    load_image(filepath)

def label_data(list_of_filepaths):

    all_labels = []

    for filepath in list_of_filepaths:
        
        load_image(filepath)
        labels = define_points(filepath)
        
        # clean up
        cv2.destroyAllWindows()

        if len(labels) == NUM_POINTS:
            out = [point for coords in labels for point in coords]
            # print(out)

        else:
            print("Wrong number of coordinates. Coordinates will not be saved to csv file.")
            continue

        all_labels.append([filepath] + out)

    return all_labels

def save_to_csv(full_labels, save_filepath):
    # save labels to csv file
    df = pd.DataFrame(full_labels, columns=COLS)
    df.to_csv(save_filepath)

def draw_circle(event,x,y,flags,param):

    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(im,(x,y), 4, (0,0,255), -1)


        global MOUSE_X
        MOUSE_X = x
        global MOUSE_Y
        MOUSE_Y = y

        # print(MOUSE_X, MOUSE_Y)

def label_list_of_filepaths(filepaths_to_label):

    # define method of choosing which filepaths to label (some directories contain >40,000 images)
    filepaths_to_label = random_selection(filepaths_to_label, 10) # e.g. randomly select 10 images

    # label chosen filepaths
    all_labels = label_data(filepaths_to_label)
    save_filepath = os.path.join("output", os.path.basename(trial_folders)+".csv")

    save_to_csv(all_labels, save_filepath)

if __name__ == '__main__':

    # initialise key filepaths
    root_folder = os.getcwd()

    ## CHANGE THESE FILEPATHS AS NECESSARY
    img_source_folder = os.path.join(root_folder, "mnt", "eme2_square_imgs") # filepath to images
    trial_folders = os.path.join(root_folder, "dummy_images")

    ####
    # logic to obtain filepaths to image folders for Eye Movement Experiment II (subdirectories in subdirectories) 
    # - do not use if different directory structure
    # participant_folders = [os.path.join(img_source_folder, i) for i in os.listdir(img_source_folder)]
    # trial_folders = []
    # for i in ["0", "1", "2", "3"]:
    #     for participant in participant_folders:
    #         trial_folders.append(os.path.join(participant, i))
    ####

    # get filepaths of every image in chosen directories 
    filepaths_to_label = obtain_image_filepaths(trial_folders)

    # if filepaths_to_label is list of lists run following function in for loop
    label_list_of_filepaths(filepaths_to_label)

