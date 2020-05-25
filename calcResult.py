import sys
from cv2 import cv2
import numpy as np
import skimage.feature
from PIL import Image
from skfuzzy import control as ctrl
import skfuzzy as fuzz
import os

def contrastEachRiceKernel(roi, c):
    cv2.imwrite("img"+str(c+1)+".jpg", roi)
    greyroi = Image.open("img"+str(c+1)+".jpg").convert('L')

    greyroi_arr = np.array(greyroi)
    gCoMat = skimage.feature.greycomatrix(
        greyroi_arr, [2], [0], 256, symmetric=True, normed=True)
    contrast = skimage.feature.greycoprops(gCoMat, prop='contrast')
    dissimilarity = skimage.feature.greycoprops(gCoMat, prop='dissimilarity')
    homo = skimage.feature.greycoprops(gCoMat, prop='homogeneity')
    energy = skimage.feature.greycoprops(gCoMat, prop='energy')
    correlation = skimage.feature.greycoprops(gCoMat, prop='correlation')
    return contrast[0][0]

def calculatePBKandContrast(image):
    contrast = []
    total = 0
    c = 0
    roi = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_filtered = cv2.GaussianBlur(gray, (11, 11), 0)
    ret3, th31 = cv2.threshold(gray_filtered, 140, 255, cv2.THRESH_OTSU)
    # edges_high_thresh = cv2.Canny(th31, 80, 100)
    contours, hierarchy = cv2.findContours(th31, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    for i in contours:
        if cv2.contourArea(i) > 40:
            ellipse = cv2.fitEllipse(i)
            axes = ellipse[1]
            minor, major = axes
            if major > 190:
                x, y, w, h = cv2.boundingRect(i)
                roi = image[y:y+h, x: x+w]
                contrast.append(contrastEachRiceKernel(roi, total-c))
                cv2.drawContours(image, [i], 0, (0, 255, 0), 10, 5)
                total += 1
            if (major > 50) and (major <190):
                cv2.drawContours(image, [i], 0, (0, 0, 255), 10, 5)
                c += 1
                total += 1
    return round(c/total * 100, 2), np.average(contrast)
def calculateFuzzy(pbkInput,contrastInput):

    # New Antecedent/Consequent objects hold universe variables and membership
    # functions
    pbk = ctrl.Antecedent(np.arange(0, 30), 'pbk')
    dom = ctrl.Antecedent(np.arange(40, 150), 'dom')
    qual = ctrl.Consequent(np.arange(0, 11), 'quality')

    # Auto-membership function population is possible with .automf(3, 5, or 7)
    pbk.automf(3)
    dom.automf(3)

    # Custom membership functions can be built interactively with a familiar,
    # Pythonic API
    qual['low'] = fuzz.trimf(qual.universe, [0, 2, 4])
    qual['medium'] = fuzz.trimf(qual.universe, [3, 5, 7])
    qual['high'] = fuzz.trimf(qual.universe, [6, 8, 10])

    # pbk.view()
    # dom.view()
    # qual.view()


    #poor means low
    #average->medium
    #good is high
    rule1 = ctrl.Rule(pbk['poor'] & dom['poor'], qual['medium'])
    rule2 = ctrl.Rule(pbk['poor'] & dom['average'], qual['high'])
    rule3 = ctrl.Rule(pbk['poor'] & dom['good'], qual['high'])
    rule4 = ctrl.Rule(pbk['average'] & dom['poor'], qual['low'])
    rule5 = ctrl.Rule(pbk['average'] & dom['average'], qual['medium'])
    rule6 = ctrl.Rule(pbk['average'] & dom['good'], qual['medium'])
    rule7 = ctrl.Rule(pbk['good'] & dom['poor'], qual['low'])
    rule8 = ctrl.Rule(pbk['good'] & dom['average'], qual['low'])
    rule9 = ctrl.Rule(pbk['good'] & dom['good'], qual['medium'])

    # rule1.view()

    qual_ctrl = ctrl.ControlSystem([rule1, rule2, rule3,rule4,rule5,rule6,rule7,rule8,rule9])
    quality = ctrl.ControlSystemSimulation(qual_ctrl)

    quality.input['pbk'] = float(pbkInput)
    quality.input['dom'] = float(contrastInput)

    quality.compute()

    # qual.view(sim=quality)
    
    return quality.output['quality']


fileName = sys.argv[1]
image = cv2.imread("D:/UploadImagesProject/"+fileName)
pbk, contrast = calculatePBKandContrast(image)
fuzzOutput = calculateFuzzy(pbk, contrast)
print('{"pbk": '+str(pbk)+', "quality": '+str(fuzzOutput)+"}")
sys.stdout.flush()
cv2.imwrite(os.path.join("D:/UploadImagesProject","processed_"+fileName), image)
cv2.imwrite(os.path.join("D:/ricequalityanalysisgui/src/assets/","processed_"+fileName), image)