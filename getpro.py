import os, time, sys
try:
    import numpy as np
    import cv2
except:
    os.system("pip install cv2")
    os.system("pip install numpy")
    os.system("pip install opencv-python")
import numpy as np
import cv2

class ADB:
    def __init__(self,handle):
        self.handle = handle
    def screen_capture(self,name):
        os.system(f"adb -s {self.handle} exec-out screencap -p > {name}.png ")
    def click(self,x,y):
        os.system(f"adb -s {self.handle} shell input tap {x} {y}")
    #def sendtext(self,text):
        #os.system(f"adb -s {self.handle} shell input text '{text}'")
    def swipe(self,x1,y1,x2,y2):
        os.system(f"adb -s {self.handle} shell input swipe {x1} {y1} {x2} {y2} 400")
    def find(self,img='',template_pic_name=False,threshold=0.99):
        if template_pic_name == False:
            self.screen_capture(self.handle)
            template_pic_name = self.handle+'.png'
        else:
            self.screen_capture(template_pic_name)
        img = cv2.imread(img)
        img2 = cv2.imread(template_pic_name)
        result = cv2.matchTemplate(img,img2,cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= threshold)
        test_data = list(zip(*loc[::-1]))
        return test_data

d = ADB('emulator-5554')
d.click(284,214)