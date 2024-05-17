import cv2
import omr_utils

path = '44.jpg'
img = cv2.imread(path)
widthImg = 1300
heightImg = 700

questions = 5
choices = 5

imgContours = img.copy()
imgBiggestContours = img.copy()

imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
imgBlur = cv2.GaussianBlur(imgGray, (5,5), 1)
imgCanny = cv2.Canny(imgBlur, 100, 250)

countours, hierarchy = cv2.findContours(imgCanny,  cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(imgContours, countours, -1, (0, 255, 0), 10)


rectCon = utils.rectContour(countours)
biggestContour = utils.getCornorpoints(rectCon)
# print(biggestContour)

cv2.drawContours(imgBiggestContours, biggestContour, -1, (0, 255, 0), 40)
biggestContour = utils.recorder(biggestContour)

# cv2.imshow('bb',biggestContour)

import numpy as np
pt1 = np.float32(biggestContour)
pt2 = np.float32([[0,0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
matrix = cv2.getPerspectiveTransform(pt1, pt2)
imgWrapColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

imgWrapGray = cv2.cvtColor(imgWrapColored, cv2.COLOR_BGR2GRAY)
imgThresh = cv2.threshold(imgWrapGray, 200, 255, cv2.THRESH_BINARY_INV)[1]



# cv2.imshow('test', imgThresh)


boxes = utils.splitboxes(imgThresh)
cv2.imshow("test", boxes[249])

myPixelVal = np.zeros((questions, choices))


countC = 0
countR = 0

ans ={}
sl = 0
allpixels = []

for image in boxes:
    totalPixels = cv2.countNonZero(image)
    allpixels.append(totalPixels) 

s = 0
e = 4
print(allpixels)

while sl < 50:
    sl += 1
    numgr = allpixels[s +1 : e +1]
    ans.update({sl : numgr})

    s += 5
    e += 5

print(ans)
    # print(myPixelVal)
sl= 1
newAns = {}



# exit(0)
for j in ans:
    a = max(ans[j])
    # print(ans[sl], sl)

    # break
    b = ans[sl].index(a)
    c = b
    if a > 1000:
        if b == 1:
            c = 'A'
        elif b == 2:
            c = 'B'
        elif b == 3:
            c = 'C'
        elif b == 4:
            c = 'D'
        else:
            c = 'N/A'
        newAns.update({sl : c})
    else:
        newAns.update({sl : "N/A"})

    sl +=1 

print(newAns)   

    
with open("ans.txt") as ee:
    aa = ee.read()
    bb = aa.split('\n')

print(bb)
correct = 0
wrong = 0
for b in bb:
    if b.split('-')[1] == newAns[bb.index(b) + 1]:
        correct += 1
    else:
        wrong += 1


una = len(newAns) - (correct + wrong)
print("Total questions :", len(newAns))
print("correct: ",correct)
print("incorrect: ",wrong)
print("Unatended: ", una)



# cv2.imshow('Original', imgThresh)
# utils.splitboxes(imgThresh)
# cv2.imshow('test', imgContours)

cv2.waitKey(0)



