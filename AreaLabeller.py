import os
import cv2
import random
import pandas as pd
import numpy as np

def draw_circle(event,x,y,flags,param):

    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(im,(x,y), 4, (0,0,255), -1)


        global MOUSE_X
        MOUSE_X = x
        global MOUSE_Y
        MOUSE_Y = y

        print(MOUSE_X, MOUSE_Y)

def label_data(imgFolder, labelPaths):

    # print("***************************")
    # print(imgFolder)
    # print(labelPaths)

    # df = pd.read_csv(labelPath)["filename"]

    # if dataframe is larger than 50 reduce to 50
    num_of_imgs = len(labelPaths)
    imgNumberThreshold = 50
    if num_of_imgs > imgNumberThreshold:
        labelPaths = labelPaths[:imgNumberThreshold]

    filenames = []
    all_eye_points = []
    count = 0

    for name in labelPaths:

        print(name)

        print(str(count) + " / " + str(len(labelPaths)))

        eye_points_frame = []

        # imgPath = os.path.join(imgFolder, str(df["filename"][name]))
        imgPath = os.path.join(imgFolder, str(name))
        print(imgPath)

        global im
        global cache



        try:
            im = cv2.imread(imgPath)
            # cache = copy.deepcopy(im)

            print("***" +str(im.shape))
            cv2.namedWindow('image')
            cv2.setMouseCallback('image', draw_circle)
            tmp_storage = []

            while(1):

                # print(MOUSE_X, MOUSE_Y)
                cv2.imshow('image', im)

                k = cv2.waitKey(20) & 0xFF

                if k == ord('n'):
                    # skip/go to next image
                    break

                elif k == ord('a'):
                    new_coords = (MOUSE_X, MOUSE_Y)
                    print(new_coords)
                    tmp_storage.append(new_coords)

                elif k == ord('r'):
                    cv2.rectangle(im, tmp_storage[-2], tmp_storage[-1], (255,0,0), 2) # bounding box in blue


            cv2.destroyAllWindows()

            print(tmp_storage)
            if len(tmp_storage) == 4:
                #left rectangle
                eye_points_frame.append(tmp_storage[0][0]) # (top x)
                eye_points_frame.append(tmp_storage[0][1]) # (top y)
                eye_points_frame.append(tmp_storage[1][0]) # (bottom x)
                eye_points_frame.append(tmp_storage[1][1]) # (bottom y)
                #right rectangle
                eye_points_frame.append(tmp_storage[2][0]) # (top x)
                eye_points_frame.append(tmp_storage[2][1]) # (top y)
                eye_points_frame.append(tmp_storage[3][0]) # (bottom x)
                eye_points_frame.append(tmp_storage[3][1]) # (bottom y)

            else:
                print("Wrong number of coordinates... INDICATING")
                for i in range(0, 8):
                    eye_points_frame.append(1) #

            all_eye_points.append(eye_points_frame)
            # filenames.append(df["filename"][name])
            print("Points verified")
            filenames.append(name)

        except:
            print("Image not found, or other exception...")

        count += 1

    df_points = pd.DataFrame(all_eye_points, columns=["lx_top", "ly_top", "lx_bottom", "ly_bottom", "rx_top", "ry_top", "rx_bottom", "ry_bottom"])
    # print(df_points)

    df_filenames = pd.DataFrame(filenames, columns=["filename"])

    df_labelled = pd.concat([df_filenames, df_points], axis=1)[["filename", "lx_top", "ly_top", "lx_bottom", "ly_bottom", "rx_top", "ry_top", "rx_bottom", "ry_bottom"]]
    print(df_labelled)

    # saveUnder = labelPath.replace("eye_centre_localisation", "eye_region_detector")
    # saveUnder = saveUnder.replace("labels", "bdbx_gth")

    saveUnderFilename = labelPaths[0].split("/")[0] + "_" + labelPaths[0].split("/")[1] + ".csv"
    saveUnder = os.path.join(os.getcwd().replace("data_labeller", "eye_region_detector"), "bdbx_gth", saveUnderFilename)

    df_labelled.to_csv(saveUnder)

    print("Completed!")

def create_csv_to_label(participantFolder):
    print("Create csv to label...")

    participantFolder = os.path.join(participantFolder, "0")

    all_filepaths = []
    try:
        all_filepaths = [os.path.join(participantFolder.split("eme2_square_imgs/")[-1], i) for i in os.listdir(participantFolder)]
        sample_images = random.choices(all_filepaths, k=50) # k = number of items to select
        return sample_images
    except FileNotFoundError:
        print("[ERROR] could not load filepaths in: " + str(participantFolder))
    except IndexError:
        print("[ERROR] could not select 50 samples from list of all filepaths in: " + str(participantFolder))

if __name__ == '__main__':

    home_folder = os.path.expanduser('~')
    rootFolder = os.path.join(home_folder, "Documents")

    # create lists of folders containing image information
    participantFolderRoot = os.path.join(rootFolder, "eye_centre_localisation", "mnt", "eme2_square_imgs")
    participantFolders = [os.path.join(participantFolderRoot, i) for i in os.listdir(participantFolderRoot)]
    # print(participantFolders)

    savedFilesRoot = os.path.join(rootFolder, "eye_region_detector", "bdbx_gth")
    savedFiles =  [os.path.join(savedFilesRoot, i) for i in os.listdir(savedFilesRoot)]

    # print(savedFiles)

    for participantFolder in participantFolders:
        # print(participantFolder)
        participantNumber = participantFolder.split("/")[-1]

        if any(participantNumber in s for s in savedFiles):
            print(str(participantNumber) + " already has at least one example...")
            continue
        elif participantNumber[0] == "2":
            print(str(participantNumber) + " is the second trial...")
            continue
        else:
            list_of_images = create_csv_to_label(participantFolder)
            print(type(list_of_images))

            if list_of_images is None:
                print("NoneType detected... pass.")
            else:
                label_data(participantFolderRoot, list_of_images)
