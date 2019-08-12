# import the necessary packages
import imutils
import cv2
import numpy as np
from pypylon import pylon
import os


def nothing(x):
    pass


factory = pylon.TlFactory.GetInstance()
serial_number = "22887293"
device = [dev for dev in factory.EnumerateDevices() if dev.GetSerialNumber() == serial_number]
pfs_file_path = "../top1/data/pfs"
cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)
white_clr = (255, 255, 255)
black_clr = (0, 0, 0)

# Create Trackbars

cv2.createTrackbar("thresh1", "Trackbars", 0, 255, nothing)

# Set Initial position of Trackbars

cv2.setTrackbarPos("thresh1", "Trackbars", 77)


def defect_iter_1(obj_crop1):
    """
    finds defects on first circular surface.
    :param obj_crop1: detected object
    :return: ok or faulty
    """

    thresh1 = cv2.getTrackbarPos("thresh1", "Trackbars")

    res1 = None
    obj_gray = cv2.cvtColor(obj_crop1, cv2.COLOR_BGR2GRAY)
    _, obj_thresh1 = cv2.threshold(obj_gray, thresh1, 200, cv2.THRESH_BINARY_INV)
    cv2.circle(obj_thresh1, (365, 365), 345, black_clr, cv2.FILLED)
    cv2.circle(obj_thresh1, (365, 367), 414, black_clr, 115)

    defect_cnt = cv2.countNonZero(obj_thresh1)
    print("defect_cnt1", defect_cnt)
    obj_cnt, _ = cv2.findContours(obj_thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # print(obj_cnt)
    for c in obj_cnt:
        if defect_cnt > 50:
            a = cv2.contourArea(c)
            res1 = True
            if a:
                cv2.drawContours(obj_crop1, c, -1, (0, 0, 255), 2)

        else:
            res1 = False
    # obj_thresh1 = cv2.cvtColor(obj_thresh1, cv2.COLOR_BGR2RGB)
    # cv2.namedWindow("obj_thresh1", cv2.WINDOW_NORMAL)
    # cv2.imshow("obj_thresh1", np.hstack((obj_thresh1, obj_crop1)))
    return res1


def defect_iter_3(obj_crop3):
    """
       finds defects on third circular surface.
       :param obj_crop3: detected object
       :return: ok or faulty
    """
    res3 = None
    obj_gray3 = cv2.cvtColor(obj_crop3, cv2.COLOR_BGR2GRAY)
    obj_thresh3 = cv2.adaptiveThreshold(obj_gray3, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 121, 7)

    cv2.circle(obj_thresh3, (360, 364), 428, black_clr, 172)
    cv2.circle(obj_thresh3, (363, 374), 180, black_clr, cv2.FILLED)
    cv2.circle(obj_thresh3, (358, 367), 314, black_clr, 191)
    defect_cnt3 = cv2.countNonZero(obj_thresh3)
    print("defect_cnt3", defect_cnt3)
    obj_cnt, _ = cv2.findContours(obj_thresh3, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in obj_cnt:
        if defect_cnt3 > 3300:
            a = cv2.contourArea(c)
            if a:
                cv2.drawContours(obj_crop3, c, -1, (0, 0, 255), 2)
                res3 = True
        else:
            res3 = False
    # obj_thresh3 = cv2.cvtColor(obj_thresh3, cv2.COLOR_BGR2RGB)
    # cv2.namedWindow("obj_thresh3", cv2.WINDOW_NORMAL)
    # cv2.imshow("obj_thresh3", np.hstack((obj_thresh3, obj_crop3)))
    return res3


def reset_device(camera):
    """
    Loads pfs file into the camera.
    :param camera: camera instance.
    :return: None
    """
    camera.StopGrabbing()
    pfs_file = pfs_file_path + "/" + [x for x in os.listdir(pfs_file_path) if serial_number in x][0]
    print("loading parameter {}".format(pfs_file))
    camera.Open()
    pylon.FeaturePersistence.Load(pfs_file, camera.GetNodeMap(), True)
    camera.Close()


def improcess():
    """
    main image processing Function grabs camera and shows result
    :return: Nothing.
    """

    if any(device):
        camera = pylon.InstantCamera(factory.GetInstance().CreateDevice(device[0]))
        reset_device(camera)
        converter = pylon.ImageFormatConverter()
        converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        while camera.IsGrabbing():
            grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grabResult.GrabSucceeded():

                # Access the image data
                image_org = converter.Convert(grabResult)
                img = image_org.GetArray()
                image = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                img_orig = image.copy()

                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 121, 7)
                cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


                for cnt in cnts:
                    approxCurve = cv2.approxPolyDP(cnt, 5, True)
                    rectX, rectY, rectW, rectH = cv2.boundingRect(approxCurve)
                    if 712 < rectW < 780 and 718 < rectH < 795:
                        approxCurve = cv2.approxPolyDP(cnt, 3, True)
                        rectX, rectY, rectW, rectH = cv2.boundingRect(approxCurve)
                        obj_crop = image[rectY:rectY + rectH, rectX:rectX + rectW]
                        defect_iter_1(obj_crop)
                        f_iter = defect_iter_1(obj_crop)
                        f_iter3 = defect_iter_3(obj_crop)
                        if f_iter or f_iter3:
                            cv2.rectangle(image, (rectX - 3, rectY - 60), (rectX + 220, rectY), (0, 0, 255), -1)
                            cv2.rectangle(image, (rectX, rectY), (rectX + rectW, rectY + rectH,), (0, 0, 255), 6)
                            cv2.putText(image, "FAULTY", (rectX + 40, rectY - 20), cv2.FONT_HERSHEY_COMPLEX, 1.2, (0, 0, 0),
                                        4)

                        else:
                            cv2.rectangle(image, (rectX - 3, rectY - 80), (rectX + 180, rectY), (0, 255, 0), -1)
                            cv2.rectangle(image, (rectX, rectY), (rectX + rectW, rectY + rectH,), (0, 255, 0), 6)
                            cv2.putText(image, "OK", (rectX + 50, rectY - 20), cv2.FONT_HERSHEY_COMPLEX, 1.6, (0, 0, 0), 4)

                # image display
                cv2.rectangle(image, (400, 0), (600, 70), (0, 0, 0), -1)
                cv2.rectangle(img_orig, (400, 0), (520, 70), (0, 0, 255), -1)
                cv2.putText(image, "RESULT", (415, 50), cv2.FONT_HERSHEY_COMPLEX, 1.3, (255, 255, 255), 4)
                cv2.putText(img_orig, "LIVE", (415, 50), cv2.FONT_HERSHEY_COMPLEX, 1.3, (255, 255, 255), 4)

                cv2.imshow("Live", imutils.resize((np.hstack((img_orig, image))), width=1080, height=720))

                # Exit on Esc Key
                k = cv2.waitKey(2) & 0xFF
                if k == 27:
                    cv2.destroyAllWindows()
                    camera.StopGrabbing()
                    break


if __name__ == '__main__':
    improcess()
