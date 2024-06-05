import cv2
import numpy as np
from PIL import Image as pi_image
import datetime
import numpy


# Function to calculate the length of sides
def calculate_side_lengths(contour):
    side_lengths = []
    for i in range(len(contour)):
        p1 = contour[i][0]
        p2 = contour[(i + 1) % len(contour)][0]
        length = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        side_lengths.append(length)
    return side_lengths

# Function to check if the sides are almost similar
def are_sides_similar(side_lengths, threshold):
    max_diff = max(side_lengths) - min(side_lengths)
    return max_diff <= threshold

def rectContour(contours, image, min_area, max_area):
    # Filter contours to get only squares with area close to 1000 and similar sides
    squares = []
    all_cods = []  # List to store all coordinates, width, and height
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area and area < max_area:

            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
            x, y, w, h = cv2.boundingRect(approx)
            # print(area, x, y, w, h)
            if len(approx) == 4:
                side_lengths = calculate_side_lengths(approx)
                if are_sides_similar(side_lengths, 15):  # Adjust the threshold as needed
                    squares.append(approx)
                    # Get bounding box coordinates
                    x, y, w, h = cv2.boundingRect(approx)
                    print("Area of contours", area, [x, y])
                    all_cods.append([[x, y], [w, h]])

    # Draw contours around squares
    for square in squares:
        # cv2.drawContours(image, [square], -1, (0, 255, 0), 2)
        cv2.drawContours(image, [square], -1, (255,255,0), -1)
        
    print(all_cods)    
    cv2.imshow("kk", image)
    cv2.waitKey(0)


img_file_name = "img.png"
img = cv2.imread(img_file_name)
img_new_name = "img_720.png"
# cv2.imwrite(img_new_name, img)

file_width = img.shape[1]
file_height = img.shape[0]

print(file_width, file_height)
new_width = 960 #1920 # 960    height 2560
if file_width < file_height:
    img2 = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    img = img2

print(img.shape[0])
if img.shape[1] != new_width:
    file_height = img.shape[0]
    file_width = img.shape[1]
    a_ratio = file_height / file_width
    new_height = int(new_width * a_ratio)
    resized_img = cv2.resize(img, (new_width, new_height))
    img = resized_img

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

max_area = 14000  #1500
min_area = 1000  #800

cv2.imshow("kk", binary)
cv2.waitKey(0)
rectContour(contours, img, min_area, max_area)      


