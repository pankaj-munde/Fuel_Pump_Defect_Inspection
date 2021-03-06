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
pfs_file_path = "./data/pfs"
cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)
white_clr = (255, 255, 255)
black_clr = (0, 0, 0)

# Create Trackbars
# cv2.createTrackbar("X", "Trackbars", 0, 255, nothing)
# cv2.createTrackbar("area", "Trackbars", 0, 5000, nothing)
# cv2.createTrackbar("obj_w_min", "Trackbars", 0, 1200, nothing)
# cv2.createTrackbar("obj_w_max", "Trackbars", 0, 1200, nothing)
# cv2.createTrackbar("obj_h_min", "Trackbars", 0, 1200, nothing)
# cv2.createTrackbar("obj_h_max", "Trackbars", 0, 1200, nothing)
# cv2.createTrackbar("c_x", "Trackbars", 0, 1200, nothing)
# cv2.createTrackbar("c_x1", "Trackbars", 0, 1200, nothing)
# cv2.createTrackbar("c_y", "Trackbars", 0, 1200, nothing)
# cv2.createTrackbar("c_y1", "Trackbars", 0, 1200, nothing)
# cv2.createTrackbar("c_r", "Trackbars", 0, 1200, nothing)
# cv2.createTrackbar("c_r1", "Trackbars", 0, 1200, nothing)
# cv2.createTrackbar("c_s", "Trackbars", 0, 1200, nothing)
# cv2.createTrackbar("obj_area", "Trackbars", 0, 5000, nothing)
cv2.createTrackbar("thresh1", "Trackbars", 0, 255, nothing)
# cv2.createTrackbar("thresh2", "Trackbars", 0, 255, nothing)
# cv2.createTrackbar("thresh3", "Trackbars", 0, 255, nothing)

# Set Initial position of Trackbars
# cv2.setTrackbarPos("obj_w_min", "Trackbars", 703)
# cv2.setTrackbarPos("obj_w_max", "Trackbars", 779)
# cv2.setTrackbarPos("obj_h_min", "Trackbars", 603)
# cv2.setTrackbarPos("obj_h_max", "Trackbars", 650)
# cv2.setTrackbarPos("c_x", "Trackbars", 310)
# cv2.setTrackbarPos("c_x1", "Trackbars", 308)
# cv2.setTrackbarPos("c_y", "Trackbars", 306)
# cv2.setTrackbarPos("c_y1", "Trackbars", 307)
# cv2.setTrackbarPos("c_r", "Trackbars", 282)
# cv2.setTrackbarPos("c_r1", "Trackbars", 469)
# cv2.setTrackbarPos("c_s", "Trackbars", 344)
# cv2.setTrackbarPos("X", "Trackbars", 94)
# cv2.setTrackbarPos("area", "Trackbars", 500)
# cv2.setTrackbarPos("obj_area", "Trackbars", 20)
cv2.setTrackbarPos("thresh1", "Trackbars", 94)


# cv2.setTrackbarPos("thresh2", "Trackbars", 69)
# cv2.setTrackbarPos("thresh3", "Trackbars", 128)


def defect_iter_1(obj_crop1):
    # x = cv2.getTrackbarPos("X", "Trackbars")
    # c_x = cv2.getTrackbarPos("c_x", "Trackbars")
    # c_y = cv2.getTrackbarPos("c_y", "Trackbars")
    # c_r = cv2.getTrackbarPos("c_r", "Trackbars")
    # c_s = cv2.getTrackbarPos("c_s", "Trackbars")
    # c_x1 = cv2.getTrackbarPos("c_x1", "Trackbars")
    # c_y1 = cv2.getTrackbarPos("c_y1", "Trackbars")
    # c_r1 = cv2.getTrackbarPos("c_r1", "Trackbars")
    thresh1 = cv2.getTrackbarPos("thresh1", "Trackbars")

    res1 = None
    obj_gray = cv2.cvtColor(obj_crop1, cv2.COLOR_BGR2GRAY)
    _, obj_thresh1 = cv2.threshold(obj_gray, thresh1, 200, cv2.THRESH_BINARY_INV)

    # common circles
    cv2.circle(obj_thresh1, (310, 307), 389, black_clr, 344)  # outer BG circle
    cv2.circle(obj_thresh1, (310, 306), 206, black_clr, -1)  # inner circle (r =192)

    defect_cnt = cv2.countNonZero(obj_thresh1)
    print("defect_cnt1", defect_cnt)
    obj_cnt, _ = cv2.findContours(obj_thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # print(obj_cnt)
    for c in obj_cnt:
        if defect_cnt > 100:
            a = cv2.contourArea(c)
            res1 = True
            if a:
                cv2.drawContours(obj_crop1, c, -1, (0, 0, 255), 2)

        else:
            res1 = False
    # obj_thresh1 = cv2.cvtColor(obj_thresh1, cv2.COLOR_BGR2RGB)
    # cv2.namedWindow("obj_thresh1", cv2.WINDOW_NORMAL)
    # cv2.imshow("obj_thresh1", np.hstack((obj_thresh1, obj_crop)))
    return res1


def reset_device(camera):
    camera.StopGrabbing()
    pfs_file = pfs_file_path + "/" + [x for x in os.listdir(pfs_file_path) if serial_number in x][0]
    print("loading parameter {}".format(pfs_file))
    camera.Open()
    pylon.FeaturePersistence.Load(pfs_file, camera.GetNodeMap(), True)
    camera.Close()


def improcess():
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
                thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 191, 7)
                cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # get values from Trackbars
                # obj_w_min = cv2.getTrackbarPos("obj_w_min", "Trackbars")
                # obj_w_max = cv2.getTrackbarPos("obj_w_max", "Trackbars")
                # obj_h_min = cv2.getTrackbarPos("obj_h_min", "Trackbars")
                # obj_h_max = cv2.getTrackbarPos("obj_h_max", "Trackbars")

                for cnt in cnts:
                    approxCurve = cv2.approxPolyDP(cnt, 5, True)
                    rectX, rectY, rectW, rectH = cv2.boundingRect(approxCurve)
                    if 703 < rectW < 779 and 603 < rectH < 650:
                        approxCurve = cv2.approxPolyDP(cnt, 3, True)
                        rectX, rectY, rectW, rectH = cv2.boundingRect(approxCurve)
                        obj_crop = image[rectY:rectY + rectH, rectX:rectX + rectW]

                        f_iter = defect_iter_1(obj_crop)

                        if f_iter:
                            cv2.rectangle(image, (rectX - 3 - 20, rectY - 60 - 20), (rectX + 220, rectY - 20),
                                          (0, 0, 255), -1)
                            cv2.rectangle(image, (rectX - 20, rectY - 20), (rectX + rectW, rectY + rectH + 20,),
                                          (0, 0, 255), 6)
                            cv2.putText(image, "FAULTY", (rectX + 40, rectY - 20 - 20), cv2.FONT_HERSHEY_COMPLEX, 1.2,
                                        (0, 0, 0), 4)

                        else:
                            cv2.rectangle(image, (rectX - 3 - 20, rectY - 80 - 20), (rectX + 180, rectY - 20),
                                          (0, 255, 0), -1)
                            cv2.rectangle(image, (rectX - 20, rectY - 20), (rectX + rectW, rectY + rectH + 20,),
                                          (0, 255, 0), 6)
                            cv2.putText(image, "OK", (rectX + 50, rectY - 20 - 20), cv2.FONT_HERSHEY_COMPLEX, 1.6,
                                        (0, 0, 0), 4)

                cv2.rectangle(image, (400, 0), (600, 70), (0, 0, 0), -1)
                cv2.rectangle(img_orig, (400, 0), (520, 70), (0, 0, 255), -1)
                cv2.putText(image, "RESULT", (415, 50), cv2.FONT_HERSHEY_COMPLEX, 1.3, (255, 255, 255), 4)
                cv2.putText(img_orig, "LIVE", (415, 50), cv2.FONT_HERSHEY_COMPLEX, 1.3, (255, 255, 255), 4)

                cv2.imshow("Live", imutils.resize((np.hstack((img_orig, image))), width=1080, height=720))
                # cv2.namedWindow("Thresh", cv2.WINDOW_NORMAL)
                # cv2.imshow("Thresh", thresh)

                # Exit on Esc Key
                k = cv2.waitKey(2) & 0xFF
                if k == 27:
                    cv2.destroyAllWindows()
                    camera.StopGrabbing()
                    break


if __name__ == '__main__':
    improcess()
