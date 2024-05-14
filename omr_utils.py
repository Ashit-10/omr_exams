import cv2
import numpy as np
from PIL import Image as pi_image
import datetime
import numpy

sep = "/"

async def rectContour(contours, img2, start_streo, streo):
    rectCon =[]
    all_cods = []
    
    for i in contours :        
        area= cv2.contourArea(i) 
        peri = cv2.arcLength(i, True)
        approx = cv2.approxPolyDP(i, 0.02 * peri, True)

        if len(approx) ==4 and area > start_streo and area < streo:
            cv2.fillPoly(img2, [i],(255, 52, 179))
            x,y,w,h = cv2.boundingRect(i)
            ratio = float(w)/h
            if ratio >= 0.8 and ratio <= 1.2:
                all_cods.append([[x, y], [w,h]])
            
                cv2.putText(img2, f"{x}, {y}", (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)
          
    return all_cods

async def read_img(img_file_name, output_file_name_given, ans_key_given, eval_folder, caption_file_name, cap_given, *args):
    if args:
        args = True
    else:
        args = False
    print(output_file_name_given)
    # Read image.
    img = cv2.imread(img_file_name)
    img_copy = img.copy()
    img_copy1 = img.copy()
    img2 = img.copy()
    img3 = img.copy()
    og_w = img.shape[0]
    og_h = img.shape[1]

    thresh_value_for_image = 120
    thresh_values = [130, 140, 150, 160, 170, 180, 190, 200, 210]
    #[125, 110, 85, 80, 75, 70, 210, 205, 195, 185, 170, 165, 160, 155, 145, 135]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    
    valls = None
    for thr in thresh_values:
        thresh1 = cv2.threshold(gray_blurred, thr, 255, cv2.THRESH_BINARY_INV)[1]

        # edged = cv2.Canny(gray, 10, 50)
        close = thresh1
       
        if img_file_name == "blank_sheet.jpg":
            streo = 25000
            start_streo = 12000
        else:
            streo = 4000
            start_streo = 1200
        contours, _ = cv2.findContours(close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        all_cods = await rectContour(contours, img2, start_streo, streo)
        print(all_cods, len(all_cods))

        if len(all_cods) == 4 and (not all_cods[0][0][0] == 0):
            thresh_value_for_image = thr
            valls=True
            
            break
        elif len(all_cods) == 5:
            for co in all_cods:
                if co[0][0] == 0:
                    all_cods.remove(co)
            thresh_value_for_image = thr
            valls=True
            break
        else:
            all_cods=[]

    if not valls:
            print("Could not find the end points !")
            return None

    print(all_cods, "hgh")


 

    all_cods_sort = sorted(all_cods, key=lambda k : [k[0][1], k[0][0]])

    Pall_cods_sort = [sorted(all_cods_sort[:2], key=lambda k : [k[0][1], k[0][0]]),
                    sorted(all_cods_sort[2:], key=lambda k : [k[0][0], k[0][1]])]




    a =[]
    for pt in all_cods_sort:
        a.append(pt[0][1])
    a.sort()

    a1 = a[:2]
    a2 = a[2:]

    b =[]
    for pt in all_cods_sort:
        b.append(pt[0][0])
    b.sort()
    b1 = b[:2]
    b2 = b[2:]


    c = []
    for b11 in b1:
        for q in all_cods_sort:
            if b11 == q[0][0]:        
                if q[0][1] in a1:
                    c.append(q)
                    b1.remove(b11)
    for q in all_cods_sort:
        if b1[0] == q[0][0]:        
                    c.append(q)

    for b22 in b2:
        for q in all_cods_sort:
            if b22 == q[0][0]:        
                if q[0][1] in a2:
                    c.append(q)
                    b2.remove(b22)
    for q in all_cods_sort:
        if b2[0] == q[0][0]:        
                    c.append(q)

    pp1 = c[0][0] 
    pp2 = c[3][0]
    pp3 = c[1][0]
    pp4 = c[2][0]


    p1 = [pp1[0], pp1[1]]
    p2 = [pp2[0] + c[3][1][0], pp2[1]]
    p3 = [pp3[0], pp3[1] + c[1][1][1]]
    p4 = [pp4[0]  + c[2][1][0], pp4[1] + c[2][1][1]]

    x_add = pp1[0]
    y_add = pp1[1]

    pic_points = [p1, p2, p3, p4]
    scale_percent=80
    w = 1200
    h = 400 


    pts1= np.float32([p1, p2, p3, p4])
    pts2= np.float32([[0,0], [w, 0], [0,h], [w,h]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    tframe = cv2.warpPerspective(img_copy1, matrix, (w,h))






    thresh2 = cv2.threshold(tframe, thresh_value_for_image, 255, cv2.THRESH_BINARY_INV)[1]



    # tframe = img_copy1
    tframe1 = tframe.copy()
    tframe2 = tframe.copy()
    gray2 = cv2.cvtColor(tframe, cv2.COLOR_BGR2GRAY)
    gray_blurred2 = cv2.GaussianBlur(gray2, (5, 5), 0)
    # Apply Hough transform on the blurred image.
    detected_circles = cv2.HoughCircles(gray2, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50,
                param2 = 30, minRadius = 8, maxRadius = 15)

    # Draw circles that are detected.
    import imutils
    print(detected_circles)

    # e parameters a, b and r to integers.
    try:
        detected_circles = np.uint16(np.around(detected_circles)) 
        print(len(detected_circles[0]))
    except Exception as e:
        print(e, "\n", "Problem with photos dimens.")
        return None

    import json


    with open("new_locations.txt", "r") as re:
        all_loc=json.load(re)



    all_circles=[]
    for ij in all_loc:
        r = 12
        a = all_loc.get(ij)[0]
        b = all_loc.get(ij)[1]
        x1=a - r
        y1 = b -r
        x2= a + r
        y2= b +r

        recImage = cv2.rectangle(thresh2, (x1,y1), (x2,y2), (0, 0, 255), 2)
        miniImage = recImage[y1:y2, x1:x2]
        cv2.circle(tframe1, (a,b), r, (0,255,0), 2)

        all_circles.append([[a, b], np.sum(miniImage == 255)])



    print(len(all_circles))

    k = 0
    num_s = []
    all_separate = []
    w = 0
    t = 1
    for i in all_circles:
        if k < 4:
            num_s.append(i)   
            k += 1
        if k > 3:
            k = 0
            column = t
            num_actual = column + (10 * w)
            all_separate.append([num_actual, num_s]) 
            num_s=[]
            w += 1
            if w > 4:
                w = 0
                t += 1


    all_separate.sort()


    print(all_separate)

    selected_options = {}
    for separate_nums in all_separate:    # looping all numbers till 50        
        options_list = []
        for separate_opts in separate_nums[1]:   # looping each options of each number
            if separate_opts[1] > 750:  # white pixel values
                abcd_option = tell_opt(separate_nums[1].index(separate_opts))
                options_list.append(str(abcd_option))

        selected_options.update({str(all_separate.index(separate_nums) + 1) : options_list})

    print(selected_options)
    correct_ans = []  # to green
    to_red = []
    wrong_num = 0

    
    ans_file = ans_key_given #{"1": ["A", "B", "C", "D"], "2": ["A"]}
    with open(ans_file, "r") as red:

        ans_key = json.load(red)

    for lets_match_ans in selected_options:
        the_red = None
        selected_opts_list = selected_options[lets_match_ans]
        if len(selected_opts_list) == 1:
            if ans_key.get(lets_match_ans):   # if answer for that question is in the answer 
                    # print(selected_opts_list, ans_key[lets_match_ans])
                    if selected_opts_list[0] in ans_key[lets_match_ans]:
                        opt_num = tell_num(selected_opts_list[0])
                        green_location = all_separate[int(lets_match_ans) - 1][1][opt_num]
                        correct_ans.append(green_location)
                        # print(green_location, 'green location')
                    else:
                        opt_num = tell_num(selected_opts_list[0])
                        the_red = True
                        red_location = all_separate[int(lets_match_ans) - 1][1][opt_num]
                        to_red.append(red_location)
                        # print(red_location, 'red location')

            else:
                break           
        elif len(selected_opts_list) > 0:
            the_red = True
            for wrong in selected_opts_list:
                opt_num = tell_num(wrong)
                red_location = all_separate[int(lets_match_ans) - 1][1][opt_num]
                to_red.append(red_location)
        if the_red:
            wrong_num += 1


    print(len(correct_ans), "correct")    
    print((to_red), "wrong")
    x_of_roll_1 = 1044
    roll_circles=[]
    roll_xy_1 = {"0": [x_of_roll_1, 66], "1": [x_of_roll_1, 98], "2": [x_of_roll_1, 132], "3": [x_of_roll_1, 168], 
                "4": [x_of_roll_1, 202], "5": [x_of_roll_1, 236], 
            "6": [x_of_roll_1, 270], "7": [x_of_roll_1, 306], "8": [x_of_roll_1, 344], "9": [x_of_roll_1, 384]}
    x_of_roll_1 += 31
    roll_xy_2 = {"0": [x_of_roll_1, 66], "1": [x_of_roll_1, 98], "2": [x_of_roll_1, 132], "3": [x_of_roll_1, 168], 
                "4": [x_of_roll_1, 202], "5": [x_of_roll_1, 236], 
            "6": [x_of_roll_1, 270], "7": [x_of_roll_1, 306], "8": [x_of_roll_1, 344], "9": [x_of_roll_1, 384]}
    roll_xy = [roll_xy_1, roll_xy_2]

    for new_roll_xyz in roll_xy:
        for new_roll in new_roll_xyz:
            r = 8
            a = new_roll_xyz[str(new_roll)][0]
            b = new_roll_xyz[str(new_roll)][1]
            x1=a - r
            y1 = b -r
            x2= a + r
            y2= b +r

            recImage = cv2.rectangle(thresh2, (x1,y1), (x2,y2), (0, 0, 255), 2)
            miniImage = recImage[y1:y2, x1:x2]
            roll_circles.append([[a, b], np.sum(miniImage == 255), new_roll])    

    roll_num_nums = ""
    for i in roll_circles:
        if i[1] > 450:
            a = i[0][0]
            b = i[0][1]
            roll_num_nums += i[2]

    print(roll_circles)
    
    if cap_given:
        roll_num_nums = caption_file_name
    print(roll_num_nums)

    for greens in correct_ans:
        a = greens[0][0]
        b = greens[0][1]
        cv2.circle(tframe, (a, b), 13, (0, 255, 0), 2, cv2.LINE_AA)  # green circle

    for reds in to_red:
        a = reds[0][0]
        b = reds[0][1]
        cv2.circle(tframe, (a, b), 13, (0, 0, 255), 2, cv2.LINE_AA)  # red circle
  



    scale_percent=80
    width = 1200 # int(img_copy.shape[1] * scale_percent / 100)
    height= 400 #int(img_copy.shape[0] * scale_percent / 100)
    dsize = (width , height)
    outout = cv2.resize(tframe, dsize)



    blank_image = np.zeros_like(tframe)
    og_w = img3.shape[0]
    og_h = img3.shape[1]

    pp1= [0, 0]
    pp2 = [width, 0]
    pp3 = [0, height]
    pp4 = [width, height]


    tt1 = pic_points[0]
    tt2= pic_points[1]
    tt3= pic_points[2]
    tt4= pic_points[3]



    correct_color = []

    for h in ans_key:
            att = ans_key[h]
            opt_index=None

            if len(att) > 0:
                for an in att:       
                    opt_index = tell_num(an)
                    if opt_index != None:
                        loc = all_separate[int(h) - 1][1][opt_index][0]
                        # print(loc)
                        # Add dot to correct answer
                        cv2.circle(tframe, (loc), 3, (238,48,167),3, cv2.LINE_AA)
                        correct_color.append(loc)

    for pink in correct_color:
        cv2.circle(blank_image, (pink[0], pink[1]), 3, (238,48,167), 3, cv2.LINE_AA)  # pink dot
        

    for gren in correct_ans:
        cv2.circle(blank_image, (gren[0][0], gren[0][1]), 13, (0, 255, 10), 2, cv2.LINE_AA)  # green circle
        

    for red in to_red:
        cv2.circle(blank_image, (red[0][0], red[0][1]), 13, (0, 10, 255), 2, cv2.LINE_AA)  # red circle
        

    

    #         cv2.circle(blank_image, (a,b), 9, (200, 150, 150), 2, cv2.LINE_AA)  # yyellow


    actual_roll = roll_num_nums
    correct_num = len(correct_ans)
    print(roll_num_nums, " num nums actual roll")

    if len(str(roll_num_nums)) > 2:
        actual_roll = None
    elif str(actual_roll).startswith("0"):
        actual_roll = actual_roll[1:]    
    if str(actual_roll) == "0":
        actual_roll = None
        
    
    if not actual_roll:
        actual_roll = output_file_name_given
    else:
        actual_roll = eval_folder + sep + actual_roll
    roll_num_nums = actual_roll[actual_roll.rfind("/") + 1 :]  


    if roll_num_nums:
        if len(roll_num_nums) == 1:
            x = "0"
            y = roll_num_nums
        else:
            x = roll_num_nums[0]
            y = roll_num_nums[1]
        first_num = roll_xy_1.get(x)
        second_num = roll_xy_2.get(y)
        # draing blacks 
        cv2.circle(tframe, (first_num), 8, (0, 0, 0), 9, cv2.LINE_AA)  # yellow
        cv2.circle(tframe, (second_num), 8, (0, 0, 0), 9, cv2.LINE_AA)  # yellow
        cv2.circle(blank_image, (first_num), 8, (0, 0, 0), 9, cv2.LINE_AA)  # yyellow
        cv2.circle(blank_image, (second_num), 8, (0, 0, 0), 9, cv2.LINE_AA)  # yyellow

        # drawing circles
        cv2.circle(tframe, (first_num), 10, (200, 200, 150), 2, cv2.LINE_AA)  # yellow
        cv2.circle(tframe, (second_num), 10, (200, 200, 150), 2, cv2.LINE_AA)  # yellow
        cv2.circle(blank_image, (first_num), 10, (200, 200, 150), 2, cv2.LINE_AA)  # yyellow
        cv2.circle(blank_image, (second_num), 10, (200, 200, 150), 2, cv2.LINE_AA)  # yyellow

        
    


    ans_position = 1110
    cir_size = 10
    text_size = 1
    text_thickness = 3
    text_u = 5
    text_d = int(1.8 * text_u)

    

    g_text = "N/A"
    by_text = "N/A"
    if len(str(len(correct_ans))) < 2:
        g_text = f" {len(correct_ans)}"
    else:
        g_text = str(len(correct_ans))

    if len(str(len(correct_ans))) < 2:
        by_text = f" {len(ans_key)}"
    else:
        by_text = str(len(ans_key))
    if roll_num_nums:
        cv2.putText(tframe, g_text, (18 + ans_position, 246 - text_u), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0,0,150), text_thickness, cv2.LINE_AA)
        cv2.putText(tframe, f"_____", (15 + ans_position , 249), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (139,0,0), 2, cv2.LINE_AA)
        cv2.putText(tframe, by_text, (18 + ans_position, 269 + text_d), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0,0,150), text_thickness, cv2.LINE_AA)
        cv2.circle(tframe, (40+ ans_position, 250), 28 + cir_size, (0, 10, 100), 2, cv2.LINE_AA)  # Answer circle
        c_date = datetime.datetime.now()
        exam_date = c_date.strftime("%d.%m.%Y")
        cv2.putText(tframe, exam_date, (1100, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 0, 0), 1, cv2.LINE_AA)


    # Adding sign with date
    cv2.imwrite("tframe.png", tframe)
    pi_filename = "sign.png"
    pi_filename1 = "tframe.png"
    frontimage = pi_image.open(pi_filename)
    background= pi_image.open(pi_filename1)

    frontimage = frontimage.resize((100, 47))

    frontimage = frontimage.convert("RGBA")
    background = background.convert("RGBA")
    background.paste(frontimage, (1095, 100), frontimage)
    background.save("new.png", format="png")
    
    # tframe = cv2.imread("new.png")


    cover_vals = 0
    newt1 = [tt1[0]- cover_vals, tt1[1] - cover_vals]
    newt2 = [tt2[0] + cover_vals, tt2[1] - cover_vals]
    newt3 = [tt3[0]- cover_vals, tt3[1] +cover_vals]
    newt4 = [tt4[0] + cover_vals, tt4[1] + cover_vals]

    img3 = pi_image.open(img_file_name)
    img3 = img3.convert("RGBA")
    source_coords = [(0, 0), (1200, 0), (1200, 400), (0, 400)]
    target_coords = [newt1, newt2, newt4, newt3]
    matrix = []
    for s, t in zip(source_coords, target_coords):
            matrix.append([t[0], t[1], 1, 0, 0, 0, -s[0]*t[0], -s[0]*t[1]])
            matrix.append([0, 0, 0, t[0], t[1], 1, -s[1]*t[0], -s[1]*t[1]])
    A = numpy.matrix(matrix, dtype=numpy.float32)
    B = numpy.array(source_coords).reshape(8)
    res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)

    img = pi_image.open("new.png")

    coeffs = numpy.array(res).reshape(8)

    new_image = img.transform((og_h, og_w), pi_image.PERSPECTIVE, coeffs,
                pi_image.BICUBIC)

    img3.paste(new_image, (0, 0), new_image)
    img3.save("img3.png", format="png")

    out_put = cv2.imread("img3.png")

    # ptss1= np.float32([newt1,newt2,newt3,newt4])
    # ptss2= np.float32([pp1,pp2,pp3,pp4])

    # homog, mask = cv2.findHomography(ptss2, ptss1, cv2.RANSAC, 5.0)
    # op = cv2.warpPerspective(tframe, homog, (og_h,og_w))

    # mask2 = np.zeros_like(img3)
    # roi_corner2 = np.int32([tt1, tt2, tt4, tt3])
    # channel_count2 = img3.shape[2]
    # ignore_mask_color2 = (255,)*channel_count2
    # cv2.fillConvexPoly(mask2, roi_corner2, ignore_mask_color2)

    # mask2 = cv2.bitwise_not(mask2)
    # masked_image2 = cv2.bitwise_and(img3, mask2)
    # finalOne  = cv2.bitwise_or(op, masked_image2)
    # out_put = finalOne

    already = True
    already_file = None # glob.glob(f"{actual_roll}*")
    if not already_file or img_file_name == "blank_sheet.jpg":
        if args or (roll_num_nums and (int(roll_num_nums) != 0)) or (img_file_name == "blank_sheet.jpg"):
            already = None

            # cv2.imwrite(f"{actual_roll}_{correct_num}.jpg", out_put)
            
    print(f"{actual_roll}")
    total_keys = len(ans_key)
    correct_num = len(correct_ans)
   
    selected_num = correct_num + wrong_num
    not_selected = total_keys - selected_num
    return out_put, selected_num, correct_num, wrong_num, total_keys, actual_roll, roll_num_nums, already  # actual caption rol should be given



def tell_opt(ind):
    if ind == 0:
        op = "A"
    elif ind == 1:
        op = "B"
    elif ind == 2:
        op = "C"
    elif ind == 3:
        op = "D"
    else:
        op = "N/A"
    return op


def tell_num(opts):
    if opts == "A":
        opt_num = 0
    elif opts == "B":
        opt_num = 1
    elif opts == "C":
        opt_num = 2
    elif opts == "D":
        opt_num = 3
    return opt_num 

