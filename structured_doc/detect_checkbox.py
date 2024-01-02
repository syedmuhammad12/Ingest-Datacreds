import json
import csv
import math
import os
import urllib

import numpy as np
import pandas as pd
import cv2
import pytesseract
# from pytesseract import pytesseract as pt
from pytesseract import Output
from PIL import Image
from collections import Counter
from django.core.files.storage import default_storage
from file_management.models import File
from tempfile import NamedTemporaryFile
import difflib
from PIL import Image, ImageFilter
# import matplotlib.pyplot as plt

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

keys_path = os.path.dirname(__file__) + '/check_box/cioms_checkbox.xlsx'
keys_cors_path = os.path.dirname(__file__) + '/check_box/ciom_checkbox_cors.xlsx'

# Medwatch Key file path's
# med_keys_path = os.path.dirname(__file__) + '/check_box/excel-1-Keys.xlsx'
# med_keys_cors_path = os.path.dirname(__file__) + '/check_box/excel-2-CBox.xlsx'
med_keys_path = os.path.dirname(__file__) + '/check_box/med_checkbox.xlsx'
med_keys_cors_path = os.path.dirname(__file__) + '/check_box/med_checkbox_cors.xlsx'


# file = 'check_box\ciom_p1.png'


# file = 'input_images\med.png'
# file = 'input_images\image_1.png'
# file = 'input_images\image_bax.png'


class keyword_detect:
    def __init__(self, key_word_file_path, image_file):

        self.key_word_file_path = key_word_file_path
        req = urllib.request.urlopen(image_file)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        self.img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        # self.img = cv2.imread(image_file)
        self.key_collection = {}

    def get_detected_keywords(self):
        img = self.img
        # thresh, img_bin = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
        # img_bin = 255 - img_bin

        # extraction with border
        d = pytesseract.image_to_data(img, output_type=Output.DICT)
        n_boxes = len(d['text'])
        for i in range(n_boxes):
            final_data = d['text'][i].strip()

            if len(final_data) > 0:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                self.key_search(final_data, x, y, w, h)

        print(self.key_collection)
        final_str = ""
        detected_keys = []
        for value in self.key_collection:
            # print("#######################################")
            # print(value,len(key_collection[value]))
            if len(self.key_collection[value]) > 0:
                key_collection_next = self.key_collection[value]
                final_list = []
                str_value = ""
                for value_next in key_collection_next:
                    for value_final in value_next:
                        final_str = final_str + "__" + value_final
                        final_list.extend(value_next[value_final])

                key_list = list(set(final_list))
                for key_list_value in key_list:
                    detected_keys.append(key_list_value)

        print(final_str)
        detected_keys_li = list(set(detected_keys))
        detected_keys_li.sort()
        print("sort", detected_keys_li)
        print("\n\n")
        final_dict = {}

        for detected_keys_values in detected_keys_li:
            detected_keys_values_list = detected_keys_values.split(" ")
            final_list_keys = []
            for detected_keys_values_list_vl in detected_keys_values_list:
                temp_dict = {}
                # ocurr = [m.start() for m in re.finditer("_"+detected_keys_values_list_vl+"_", final_str)]
                ocurr = list(self.find_all(final_str, "_" + detected_keys_values_list_vl + "_"))
                # print(ocurr,detected_keys_values_list_vl)
                ocurr_cordinates = []
                if len(ocurr) > 0:
                    for ocurr_values in ocurr:
                        final_str_cut = final_str[int(ocurr_values) + len("_" + detected_keys_values_list_vl + "_"):]

                        # print(final_str_cut[:final_str_cut.find('__')])
                        ocurr_cordinates.append(final_str_cut[:final_str_cut.find('__')])
                    temp_dict = {detected_keys_values_list_vl: ocurr_cordinates}
                    final_list_keys.append(temp_dict)
                else:
                    break
            if len(final_list_keys) > 0:
                final_dict[detected_keys_values] = final_list_keys
            # break

        print(final_dict)
        print("***************")
        final_dict_final = {}
        for final_dict_vl in final_dict:
            li_of_key = final_dict_vl.split(" ")
            if len(li_of_key) < 2:
                if len(final_dict[final_dict_vl]) > 0:
                    final_dict_final[final_dict_vl] = final_dict[final_dict_vl][0][final_dict_vl]
            else:
                current_dict_key = final_dict[final_dict_vl]
                key_and_cordinates_final = []
                for index, value in enumerate(li_of_key):
                    next_index = index + 1
                    try:
                        print(li_of_key[index], li_of_key[next_index])
                        key_and_cordinates = {}
                        key_and_cordinates_dist = []
                        for cdk_val in current_dict_key[index][li_of_key[index]]:
                            for cdk_n_val in current_dict_key[next_index][li_of_key[next_index]]:
                                # print(li_of_key[index], cdk_val, li_of_key[next_index], cdk_n_val)
                                key_finalize_result = self.key_finalize(cdk_val, cdk_n_val)

                                if key_finalize_result > 0:
                                    # print(li_of_key[index], li_of_key[next_index], key_finalize_result,cdk_val + "__" + cdk_n_val)
                                    key_and_cordinates[key_finalize_result] = cdk_val + "__" + cdk_n_val
                                    key_and_cordinates_dist.append(key_finalize_result)
                        print("cors", key_and_cordinates, key_and_cordinates_dist, min(key_and_cordinates))
                        if min(key_and_cordinates_dist) < 110:
                            key_and_cordinates_final.append(key_and_cordinates[min(key_and_cordinates_dist)])
                    except Exception as e:
                        print(e, "end")
                if len(key_and_cordinates_final) > 0:
                    final_dict_final[final_dict_vl] = key_and_cordinates_final

        print(final_dict_final)
        return final_dict_final

    def key_search(self, key, x, y, w, h):
        try:
            df = pd.read_excel(self.key_word_file_path)
            df.dropna(inplace=True)

            df["Indexes"] = df["keywords"].str.find(key)
            code = df.loc[df['Indexes'] > -1]
            if len(list(code['keywords'])) > 0:
                temp_dict = {}
                temp_dict[key + "_" + str(x) + "_" + str(y) + "_" + str(w) + "_" + str(h)] = list(
                    code['keywords'])
                if y in self.key_collection:
                    temp_list = self.key_collection[y]
                    temp_list.append(temp_dict)
                    self.key_collection[y] = temp_list
                else:
                    self.key_collection[y] = [temp_dict]
        except Exception as e:
            print(e)

    def key_finalize(self, current, next):
        current_arr = current.split('_')
        next = next.split('_')
        x = int(current_arr[0])
        y = int(current_arr[1])
        x1 = int(next[0])
        y1 = int(next[1])
        if y < y1:
            diff = (x1 - x)
            z = pow(diff, 2)
            diff1 = (y1 - y)
            z1 = pow(diff1, 2)
            total = z + z1
            return math.sqrt(total)
        elif y == y1:
            return 1
        else:
            return -1

    def find_all(self, a_str, sub):
        start = 0
        while True:
            start = a_str.find(sub, start)
            if start == -1: return
            yield start
            start += len(sub)  # use start += 1 to find overlapping matches


class check_box_detect:
    def __init__(self, image_file, template_name, file_id, page_no,tenant):
        print("image_file", image_file)
        req = urllib.request.urlopen(image_file)
        print("executed read")
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    
        self.img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        self.tenant=tenant
        if template_name == "CIOMS":
            self.final_dict_final = keyword_detect(keys_path, image_file).get_detected_keywords()
            self.keys_path = keys_path
            self.keys_cors_path = keys_cors_path
        elif template_name == "MedWatch":
            self.med_keys_path = med_keys_path
            self.med_keys_cors_path = med_keys_cors_path
            self.med_image_file_path = image_file
            self.file_id = file_id
            self.page_no = page_no

    def detect_checked(self, x, y, w, h):
        img = self.img
        checked = 0
        x = x + 6
        y = y + 6
        h = h - 6
        w = w - 6
        crop_img = img[y:h, x:w]
        # cv2.imwrite(str(y)+'detecttable_ciom.jpg', crop_img)
        hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)

        # White color detect
        lower_range = np.array([0, 0, 0])
        upper_range = np.array([0, 0, 0])

        mask = cv2.inRange(hsv, lower_range, upper_range)
        mid_row = mask[int(len(mask) / 2)]
        white = max(mid_row)
        # print(mid_row, len(mask), white)
        if white == 255:
            checked = 1

        return checked

    def isNan(self, key):
        try:
            if math.isnan(key):
                return 0
            else:
                return 1
        except Exception as e:
            return 1

    def nearest_dist(self, x1, y1, key, current_key_multi):
        df = pd.read_excel(self.keys_cors_path)
        sqrt_li = []
        sqrt_li_dict = {}
        if current_key_multi == 0:
            for index, row in df.iterrows():
                if self.isNan(row[key]) == 1:
                    data = row[key].split(':')
                    x = int(data[0])
                    y = int(data[1])
                    diff = (x1 - x)
                    z = pow(diff, 2)
                    diff1 = (y1 - y)
                    z1 = pow(diff1, 2)
                    total = z + z1
                    sqrt_li.append(math.sqrt(total))
                    sqrt_li_dict[math.sqrt(total)] = row[key]

        elif current_key_multi == 1:
            for index, row in df.iterrows():
                print("shot_v", row[key], self.isNan(row[key]))
                if self.isNan(row[key]) == 1:
                    full_arr = row[key].split('_')
                    sqrt_li_in = []

                    for full_arr_val in full_arr:
                        data = full_arr_val.split(':')
                        x = int(data[0])
                        y = int(data[1])
                        diff = (x1 - x)
                        z = pow(diff, 2)
                        diff1 = (y1 - y)
                        z1 = pow(diff1, 2)
                        total = z + z1
                        sqrt_li_in.append(math.sqrt(total))
                    avg = sum(sqrt_li_in) / len(sqrt_li_in)
                    sqrt_li.append(avg)
                    sqrt_li_dict[avg] = row[key]
        return sqrt_li_dict[min(sqrt_li)]

    def get_cor_key(self, key):
        status = 0
        df = pd.read_excel(self.keys_path)
        df.dropna(inplace=True)
        df["Indexes"] = df["keywords"].str.find(key)
        code = df.loc[df['Indexes'] > -1]
        try:
            code_list = list(code['cor'])
            code_list_m = list(code['multiple'])
            if code_list[0]:
                status = {'cor': code_list[0], 'multiple': code_list_m[0]}
        except Exception as e:
            print("cor", e)
            status = 0
        return status

    def find_nearest_checkbox_and_detect(self):

        final_json_data = []
        final_dict_final = self.final_dict_final
        for final_dict_final_vl in final_dict_final:
            print("**********************")
            try:
                status = self.get_cor_key(final_dict_final_vl)
                # print("status", status)
                if status != 0:
                    current_key = status['cor']
                    current_key_multi = status['multiple']
                    first_cor = final_dict_final[final_dict_final_vl]
                    print(final_dict_final_vl, first_cor)
                    # for first_cor_vl in first_cor:
                    #     first_cor_vl=first_cor_vl.spli("__")
                    first_cor_vl_inside = first_cor[0].split("__")
                    print(first_cor_vl_inside)
                    start = first_cor_vl_inside[0].split("_")
                    cor_ner_result = self.nearest_dist(int(start[0]), int(start[1]), current_key, current_key_multi)
                    # print("mul", cor_ner_result)
                    if current_key_multi == 0:
                        cor_ner_result_aar = cor_ner_result.split(":")
                        if_checked = [self.detect_checked(int(cor_ner_result_aar[0]), int(cor_ner_result_aar[1]),
                                                          int(cor_ner_result_aar[2]), int(cor_ner_result_aar[3]))]
                    elif current_key_multi == 1:

                        cor_ner_result_full_arr = cor_ner_result.split("_")

                        multi_checks = []
                        for cor_ner_result_val in cor_ner_result_full_arr:
                            cor_ner_result_aar = cor_ner_result_val.split(":")

                            if_checked_multi = self.detect_checked(int(cor_ner_result_aar[0]),
                                                                   int(cor_ner_result_aar[1]),
                                                                   int(cor_ner_result_aar[2]),
                                                                   int(cor_ner_result_aar[3]))
                            multi_checks.append(if_checked_multi)
                        if_checked = multi_checks
                    # print(final_dict_final_vl, if_checked, cor_ner_result_aar)
                    key_cors_list = []
                    for first_cor_val in first_cor:
                        temp_arr = first_cor_val.split("__")
                        for tav in temp_arr:
                            key_cors_list.append(tav.replace("_", ":"))
                    cor_ner_result_arr = cor_ner_result.split("_")
                    current_data = {"key": final_dict_final_vl, "key_name": current_key, "key_cors": key_cors_list,
                                    "values": if_checked, "values_cors": cor_ner_result_arr}
                    final_json_data.append(current_data)

            except Exception as e:
                print(final_dict_final_vl, e, "endd")
        return final_json_data
        # print("checked", self.detect_checked(1275, 393, 1297, 417))
        # print("checked", self.detect_checked(1272, 447, 1298, 473))
        # cv2.imshow('img', img)
        # cv2.imwrite('detecttable_ciom_01-02-23.jpg', img)
        # cv2.waitKey(0)

    def preprocess_image(self, filename):
        try:
            # print(filename)
            with default_storage.open(str(filename), mode='rb') as img_buffer:

                img_array = np.asarray(bytearray(img_buffer.read()), dtype=np.uint8)
                imgs = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
              
                # Convert the image to grayscale
                gray = cv2.cvtColor(imgs, cv2.COLOR_BGR2GRAY) 

                # Apply thresholding
                _, binary_image = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) 

                return binary_image 
        except Exception as e:
            print(f"Error in preprocessing: {e}")
            return None

    def ocr_core(self, image, custom_config=r'--oem 3 --psm 6'):
        # try:
        #     # print("ocr")
        #     # print(image)            
        #     pil_img = Image.fromarray(image)
        #     # return
        #     data = pytesseract.image_to_data(pil_img, config=custom_config, output_type=Output.DICT)
        #     valid_data = [i for i, conf in enumerate(data['conf']) if int(conf) > 0 and data['text'][i].strip() != '']
        #     words_and_boxes = [(data['text'][i], (data['left'][i], data['top'][i], data['width'][i], data['height'][i]))
        #                     for i in valid_data]
        #     return words_and_boxes
        # except Exception as e:
        #     print(f"Error in OCR processing: {e}")
        #     return None

        """
        This function will handle the OCR processing of preprocessed images.
        """
        try:
            # Convert OpenCV image (NumPy array) to PIL Image
            pil_img = Image.fromarray(image) 

            # Image preprocessing
            pil_img = pil_img.convert('L')  # Convert to grayscale
            pil_img = pil_img.point(lambda x: 0 if x < 128 else 255)  # Binarization
            pil_img = pil_img.filter(ImageFilter.MedianFilter(size=3))  # Median filter for noise reduction

            # Use Tesseract to get OCR data from the image
            data = pytesseract.image_to_data(pil_img, config=custom_config, output_type=pytesseract.Output.DICT) 

            # Extract recognized words from the data
            # recognized_words = [word for word, conf in zip(data['text'], data['conf']) if int(conf) > 0 and word.strip() != ''] 

            # return ' '.join(recognized_words) 

            return data

        except Exception as e:
            print(f"Error in OCR processing: {e}")
            return None
        
    def find_text_boxes(self, words_and_boxes, text_list):
        coordinates_dict = {}
        for word, (x, y, w, h) in words_and_boxes:
            for text_to_find in text_list:
                if word.lower().strip() == text_to_find.lower():
                    formatted_coordinates = f"{x}:{y}:{x+w}:{y+h}"
                    coordinates_dict[text_to_find] = formatted_coordinates
                    break  
        return coordinates_dict

    def match_coordinates_with_excel(self, excel_path, extracted_coordinates):
        df = pd.read_excel(excel_path)
        closest_match = None
        closest_distance = float('inf')

        for index, row in df.iterrows():
            for col in df.columns[2:]:  
                excel_coords = row[col].split(':')
                if len(excel_coords) != 4:
                    continue  
                excel_coords = list(map(int, excel_coords))
                distance = (extracted_coordinates[0] - (excel_coords[0]*2))**2 + (extracted_coordinates[1] - (excel_coords[1]*2))**2
                
                if distance < closest_distance:
                    closest_distance = distance
                    closest_match = row['NAMES']

        return closest_match


    def check_black_markings(self, image, coordinates_str, key_cord):
        img = self.img
        # print("in blank")
        coords = coordinates_str.split(':')
        # x3, y3, w3, h3 = key_cord
        if len(coords) != 4:
            print(f"Error: Invalid coordinates format for {coordinates_str}.")
            return False

        x1, y1, x2, y2 = map(int, coords)

        x = (x1 * 2)
        y = (y1 * 2)
        w = (x2 * 2) - (x1 * 2)
        h = (y2 * 2) - (y1 * 2)

        midpoint_x = x + w // 2
        midpoint_y = y + h // 2

        pixel_color = img[midpoint_y, midpoint_x]
        # print(pixel_color)
        # img = cv2.rectangle(img, (x3, y3), ( x3+w3,  y3+h3), (0, 255, 0), 2)
        # img = cv2.rectangle(img, (x, y), ( x+w,  y+h), (68, 79, 179), 2)
        # cv2.imwrite(r'2013253408_3.png',img)

        threshold = 50 
        return all(val < threshold for val in pixel_color)

    def check_all_from_excel(self, image_path, excel_path, row_number):
        # print("in function")
        # print(image_path)
        # image = cv2.imread(image_path)
        # image = Image.fromarray(image)
        # print(image)
        # if image is None:
        #     return "Error: Image not found."

        df = pd.read_excel(excel_path)
        # print(df)

        results = {}

        for col in df.columns[1:]: 
            header = col
            coordinates_str = df.at[row_number - 1, header]  # Adjust for zero-based index
            if pd.isnull(coordinates_str) or not isinstance(coordinates_str, str):
                results[header] = False  
                continue  
            results[header] = self.check_black_markings(image_path, coordinates_str)
        # print(results)
        return results

    def np_encoder(self, object):
        if isinstance(object, np.generic):
            return object.item()

    def find_key_data(self, words_and_boxes, text_list, key_cord, preprocessed_image):
        coordinates_dict = {}
        print("inside")
        try:
            print(self.med_keys_cors_path)
            
            # df.dropna(inplace=True)

            img_height, img_width = preprocessed_image.shape[:2]
            print(f"{img_height}---<>{img_width}")
            
            # for word, (x, y, w, h) in words_and_boxes:
            # for text_to_find in text_list:
            for key, text_to_find in enumerate(text_list):
                print(key, "---", text_to_find)
                key_words = str(text_to_find).split()
                key_length = len(key_words)
                threshold=90
                closest_match_index = -1
                max_similarity = 0
                cor_name = key_cord[key]
                print("cor_name",cor_name)
                sqrt_li = []
                sqrt_li_dict = {}
                max_limit = 50
                min_limit = 7
                fdata = ""
                df = pd.read_excel(self.med_keys_cors_path, usecols=[cor_name])
                # print(df)
                

                # df["Indexes"] = df["keywords"].str.find(key)
                # code = df.loc[df['Indexes'] > -1]
                # if len(list(code['keywords'])) > 0:
                #     list(code['keywords'])

                for i in range(len(words_and_boxes) - key_length + 1):
                    if all(words_and_boxes[i + j][0] == key_words[j] for j in range(key_length)):
                        # return i
                        print(words_and_boxes[i])
                        # print(words_and_boxes[i][1])
                        cor = words_and_boxes[i][1]
                        kx, ky, kwidth, kheight = cor
                        print(f"x-->{kx}-->y-->{ky}-->w-->{kwidth}-->h-->{kheight}")

                        for index, row in df.iterrows():
                            square_found = False  # Flag to indicate if a square is found
                            # print("yes", index)
                            # print(row[cor_name])
                            # data = row['weight'].split(':')
                            if isinstance(row[cor_name], str):
                                coords = row[cor_name].split(':')
                                # print("dd")
                                # coords = coordinates_str.split(':')
                                if len(coords) != 4:
                                    print(f"Error: Invalid coordinates format for {row[cor_name]}.")
                                    return False

                                x1, y1, x2, y2 = map(int, coords)

                                cx = (x1 * 2)
                                cy = (y1 * 2)
                                cw = (x2 * 2) - (x1 * 2)
                                ch = (y2 * 2) - (y1 * 2)                                

                                # Validate coordinates
                                if x1 < 0 or y1 < 0 or x2 > img_width or y2 > img_height or x1 >= x2 or y1 >= y2:
                                    print("Error: Invalid coordinates out of image bounds.")
                                    continue
                                

                                 # Extract the area of interest
                                area_of_interest = preprocessed_image[cy:cy+ch, cx:cx+cw]

                                with NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                                    cv2.imwrite(temp_file.name, area_of_interest)

                                if cy <= ky:
                                    distance = math.sqrt(((kx-35) - cx) ** 2 + (ky - cy) ** 2)
                                    print("yes"+ str(distance))
                                    if distance < 50:
                                        if self.is_square(temp_file.name):
                                            print("The shape is a square!")
                                            print(f"cx-->{cx}-->cy-->{cy}-->cw-->{cw}-->ch-->{ch}")
                                            sqrt_li.append(distance)
                                            sqrt_li_dict[distance] = row[cor_name] 
                                            if int(min(sqrt_li)) < max_limit:
                                                # print(f"{coords}--------{distance}")
                                                fdata = sqrt_li_dict[min(sqrt_li)]                                          
                                                
                                           
                                        else:
                                            print("The shape is not a square!")
                        
                        if fdata:
                            print("fdata",fdata)
                            coords = fdata.split(':')
                            x1, y1, x2, y2 = map(int, coords)

                            cx = (x1 * 2)
                            cy = (y1 * 2)
                            cw = (x2 * 2) - (x1 * 2)
                            ch = (y2 * 2) - (y1 * 2)
                            img = cv2.rectangle(preprocessed_image, (cx, cy), (cx + cw, cy + ch), (255, 255, 0), 2)
                            cv2.imwrite(r'2013252233_plot_23_4.png',img)  
                            final_data = self.check_black_markings(self.med_image_file_path, fdata, cor)
                            print(final_data) 

                                # if area_of_interest.size == 0:
                                #     print("Warning: Extracted area is empty.")
                                #     continue


                                #  # Convert to grayscale and apply threshold
                                # # gray = cv2.cvtColor(area_of_interest, cv2.COLOR_BGR2GRAY)

                                # # Check if the area_of_interest is already grayscale
                                # if len(area_of_interest.shape) == 2:
                                #     # The image is already grayscale
                                #     gray = area_of_interest
                                # else:
                                #     # Convert to grayscale
                                #     gray = cv2.cvtColor(area_of_interest, cv2.COLOR_BGR2GRAY)

                                # _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
                        
                                # # Find contours
                                # contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                        
                                # for contour in contours:
                                #     # print("contour")
                                #     epsilon = 0.1 * cv2.arcLength(contour, True)
                                #     approx = cv2.approxPolyDP(contour, epsilon, True)
                                #     # print(approx)
                                #     if len(approx) == 4:
                                #         _, _, w, h = cv2.boundingRect(approx)
                                #         aspectRatio = float(w)/h
                                #         if 0.95 < aspectRatio < 1.05:  # Close to 1 indicates a square
                                #             square_found = True
                                #             # break  # Break after detecting a square
                                    

                                # Apply binary thresholding
                                # _, thresh = cv2.threshold(preprocessed_image, 127, 255, cv2.THRESH_BINARY_INV)
                            
                                # Find contours
                                # contours, _ = cv2.findContours(preprocessed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                                # # Assuming the largest contour is the shape of interest
                                # contour = max(contours, key=cv2.contourArea)
                                # # Get bounding rectangle
                                # x, y, w, h = cv2.boundingRect(contour)
                            
                                # # Check if it's a square by comparing width and height
                                # tolerance = 0.1  # 10% tolerance, adjust as needed
                                # if (1 - tolerance) <= w/h <= (1 + tolerance):
                                #     square_found = True
                                #     print("yes")
                                # else:
                                #     square_found = False
                        
                                # if square_found:
                                    
                                #     distance = math.sqrt(((kx-35) - cx) ** 2 + (ky - cy) ** 2)
                                #     print("yes"+ str(distance))
                                #     print(row[cor_name])
                                #     sqrt_li.append(distance)
                                #     sqrt_li_dict[distance] = row[cor_name]
                                #     # print(sqrt_li)
                                #     # print(sqrt_li_dict)
                                #     if int(min(sqrt_li)) > min_limit and int(min(sqrt_li)) < max_limit:
                                #     # if int(min(sqrt_li)) < max_limit:
                                #         # print(f"{coords}--------{distance}")
                                #         fdata = sqrt_li_dict[min(sqrt_li)]
                                #         img = cv2.rectangle(preprocessed_image, (cx, cy), (cx + cw, cy + ch), (0, 255, 0), 2)
                                #         cv2.imwrite(r'2013253379_plot_2_'+str(cx)+str(cy)+'.png',img)
                                            
                                    #     break  # Break the outer loop if a square is found
                        
                            # plt.figure(figsize=(20, 20))
                            # plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                            # plt.axis('off')
                            # plt.show()
                        
                        # if square_found:
                        #     print("SQUARE")
                        # else:
                        #     print("No Square")
                                

                                

                        # # print(sqrt_li_dict)
                        # print("fdata--->", fdata)
                        # if fdata:
                        #     final_data = self.check_black_markings(self.med_image_file_path, fdata, cor)
                        #     print(final_data)
                        # break
            return 1
        except Exception as e:
            print(e)

    def plot_and_check_square(self, image_path, coordinates_str):
        coordinate_sets = coordinates_str.split(';')
        square_found = False  # Flag to indicate if a square is found
    
        # image = cv2.imread(image_path)
        image = self.preprocess_image(image_path)
        if image is None:
            print("Error: Image not found.")
            return
    
        img_height, img_width = image.shape[:2]
    
        for coords in coordinate_sets:
            print(coords)
            coords = coords.split(':')
            if len(coords) != 4:
                print("Error: Invalid coordinates format in one of the sets.")
                continue
    
            x1, y1, x2, y2 = map(int, coords)
    
            # Validate coordinates
            if x1 < 0 or y1 < 0 or x2 > img_width or y2 > img_height or x1 >= x2 or y1 >= y2:
                print("Error: Invalid coordinates out of image bounds.")
                continue
    
            x = x1
            y = y1
            w = x2 - x1
            h = y2 - y1
    
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
            # Extract the area of interest
            area_of_interest = image[y:y+h, x:x+w]
    
            if area_of_interest.size == 0:
                print("Warning: Extracted area is empty.")
                continue
    
            # Convert to grayscale and apply threshold
            gray = cv2.cvtColor(area_of_interest, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
    
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
            for contour in contours:
                epsilon = 0.1 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
    
                if len(approx) == 4:
                    _, _, w, h = cv2.boundingRect(approx)
                    aspectRatio = float(w)/h
                    if 0.95 < aspectRatio < 1.05:  # Close to 1 indicates a square
                        square_found = True
                        break  # Break after detecting a square
    
            if square_found:
                break  # Break the outer loop if a square is found
    
        # plt.figure(figsize=(20, 20))
        # plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        # plt.axis('off')
        # plt.show()
    
        if square_found:
            print("SQUARE")
        else:
            print("No Square")

    def read_key_file(self, template_name):
        try: 
        # read by default 1st sheet of an excel file
            if template_name == "MedWatch":
                csv_file_path = self.med_keys_path                
            elif template_name == "CIOMS":
                csv_file_path = os.path.dirname(__file__) + "/key_files/cimos_key_file.xlsx"
            elif template_name == "IRMS":
                csv_file_path = os.path.dirname(__file__) + "/key_files/irms_key_file.xlsx"

            dataframe = pd.read_excel(csv_file_path)
            key_list = []
            key_cord = []
            for index, row in dataframe.iterrows():               
                key_name = row['keywords'] 
                cordints = row['cor']
                key_list.append((list(key_name.split(" "))))
                key_cord.append(cordints)

            # print(key_list)
            return { "key": key_list, "cord": key_cord}

        except Exception as e:
            print(e)
    
    def find_checkbox_result_medwatch(self):
        file_data = File.objects.using(self.tenant).filter(id_file=self.file_id)
        for file in file_data:

            if file.file_format == 'application/pdf':
                file_name = 'uploads/'+self.tenant+'/'+str(self.file_id)+'/page_'+str(self.page_no)+'.png'
            elif file.file_format == 'image/jpeg' or file.file_format == 'image/png':
                file_name = file.file_name

            with default_storage.open(str(file_name), mode='rb') as img:               
                
                image = self.preprocess_image(img)
                tesseract_output = ""
                if image is not None:
                    tesseract_output = self.ocr_core(image)                    
                else:
                    print("Error in image preprocessing.")

                new_dataframe = pd.DataFrame(tesseract_output)                
                
                
                keywords = self.read_key_file("MedWatch")
                # print(keywords)
                # return
                key_data = keywords['key']
                key_cord = keywords['cord']
                
            
                result_key = []
                gg = 0
                try:
                    for key_name in key_data:
                        # print(key_name)
                        map_val_data = []
                        cc = 0

                        for key in key_name:                            
                            cordinates_name = key_cord[gg]
                            # print(cordinates_name)
                            m = 0
                            map_data = []
                            
                            for text in new_dataframe['text']:

                                if text != '':
                                    
                                    temp = difflib.SequenceMatcher(None,text.lower() ,key.lower())
                                    ratio = (temp.ratio())*100
                                    data = []
                                    if (ratio > 80):                                        
                                        data = {
                                            'text': text,
                                            'left': new_dataframe['left'][m],
                                            'top': new_dataframe['top'][m],
                                            'width': new_dataframe['width'][m],
                                            'height': new_dataframe['height'][m],
                                            'ratio': ratio
                                        }

                                        map_data.append(data) 
                                            
                                m = m + 1  

                            val = {
                                'word'+str(cc): map_data
                            }
                            map_val_data.append(val)
                            cc = cc + 1
                        length = len(map_val_data) 
                        # print(length)
                        # print(map_val_data)
                        f_data = self.find_key_value(map_val_data, key_name, image, cordinates_name, "MedWatch")
                        # print(f"###*{2}")
                        # print(f_data)
                        gg = gg + 1
                        if f_data:                        
                            result_key.append(f_data) 
                        else:
                            print("No result Key")                  
                        
                    print(result_key) 

                    # print(filter_final_data)
                    task = {
                        'data': result_key
                    }
                    # print(task)
                    json_string = json.dumps(task, default=self.np_encoder)
                    # print("&&&&&&&&&")
                    # print(json_string)
                    return json_string
                       
                except Exception as e:
                    print(e)    

    def matched_array(self, word_array, top_val, left, width):
        match2 = 0
        level2_arr = []
        final_arr = []

        for w2 in word_array:
            w2_top = w2['top']

            level2_arr.append(w2_top)               
            diff = self.find_diff(top_val, w2_top)
            # print("dif"+str(diff))
            w2_left = w2['left']            
            if diff == 1: 
                next_pos = int(left) + int(width) + 100  
                # print(f"w2_left-->{w2_left}-->left-->{left}-->next_pos-->{next_pos}")               
                if w2_left < next_pos and w2_left > left: 
                    # print("yes")                                                     
                    x1 = w2['left']
                    y1 = w2['top']
                    w1 = w2['width']
                    h1 = w2['height']  
                    final_arr.append(w2)
                    match2 = 1
                    break             
                
            

        if match2 == 0:
            # if len(word_array) ==  1:
            for w2 in word_array:

                #Logic1
               
                # next_pos = int(left) + int(width) + 100
                # w2_left = w2['left']                
                # if w2_left < next_pos and w2_left > left:
                #     final_arr.append(w2)
                #     match2 = 1
                # break

                #Logic2

                x = left
                y = top_val

                x1 = w2['left']
                y1 = w2['top']

                diff = (x1 - x)
                z = pow(diff, 2)
                diff1 = (y1 - y)
                z1 = pow(diff1, 2)
                total = z + z1

                sq = math.sqrt(total)
                # print(sq)

                if int(sq) < 150 :
                    final_arr.append(w2)
                    match2 = 1
                    break           

        # print(final_arr)            
        return final_arr


    def find_key_value(self, result_data, key_name, image, cordinates_name, template_name):
         # print("key_name:"+str(key_name))        
        key_name = ' '.join(key_name)
        # print("result_string",key_name)
        # print("match position--",result_data)
        length = len(result_data)
        word_arr = {}
        for i in range(0, (length)):           
            wrd = 'word'+str(i)            
            word_arr[i] = result_data[i][wrd]        

        word_length = len(word_arr)

        final_json_data = []
        value_json_data = []
        final_array = []
        final_data = ""
        if word_length == 1:
            for w1 in word_arr[0]:               
                # print("w1--", w1) 
                sdata = self.find_nearest_checkbox(w1, key_name, cordinates_name, image)
                # print("****************")
                # print(sdata)                
                if sdata:
                    final_array.append(sdata)
            
            # print(final_array)
            
        elif word_length == 2:
            # print(word_length)
            for w1 in word_arr[0]:
                print(w1)
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']                 
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], y, x, w)
                    # print("xxx")
                    # print(data)                    
                    if len(data) > 0:
                        # print("yes")
                        sdata = self.find_nearest_checkbox(w1, key_name, cordinates_name, image)
                        # print("****************")
                        # print(sdata)  
                        if sdata:
                            final_array.append(sdata)              
        

        if final_array:
                # Remove None values
                filtered_data = [item for item in final_array if item is not None]

                # Find the index of the minimum value
                if filtered_data:
                    minvalue_index = min(range(len(filtered_data)), key=lambda i: filtered_data[i]['minvalue'])
                    print(f"The index of the minimum value is: {minvalue_index}")
                    print(type(filtered_data[minvalue_index]['fdata']))
                    fdata = str(filtered_data[minvalue_index]['fdata'])
                    keycor = str(filtered_data[minvalue_index]['keycor'])
                    # coords = fdata.split(':')
                    # x1, y1, x2, y2 = map(int, coords)

                    # cx = (x1 * 2)
                    # cy = (y1 * 2)
                    # cw = (x2 * 2) - (x1 * 2)
                    # ch = (y2 * 2) - (y1 * 2)
                    # img = cv2.rectangle(image, (cx, cy), (cx + cw, cy + ch), (0, 255, 0), 2)
                    # cv2.imwrite(r'2013252233_plot_23_2_'+str(key_name)+'.png',img)  
                    final_data = self.check_black_markings(self.med_image_file_path, fdata, keycor)
                    # print(final_data)
                    if final_data:
                        final_json_data = {
                            "key": key_name,
                            "value" : "1",
                            "co_ord" : cordinates_name
                        }
                    else:
                        final_json_data = {
                            "key": key_name,
                            "value" : "0",
                            "co_ord" : cordinates_name
                        } 
                else:
                    print("No valid data in the list.")

        
        return final_json_data

 

    def find_nearest_checkbox(self,word_arr, key_name, cordinates_name, image):
        # print("x")
        sqrt_li = []
        sqrt_li_dict = {}
        max_limit = 50
        min_limit = 10
        fdata = ""
        minvalue = ""
        kx = word_arr['left']
        ky = word_arr['top']
        kw = word_arr['width']
        kh = word_arr['height'] 
        cor = (kx, ky, kw, kh)
        img_height, img_width = image.shape[:2]
        # print(f"{img_height}---<>{img_width}")
        df = pd.read_excel(self.med_keys_cors_path, usecols=[cordinates_name])
        for index, row in df.iterrows():
            square_found = False  # Flag to indicate if a square is found
            # print("yes", index)
            # print(row[cor_name])
            # data = row['weight'].split(':')
            if isinstance(row[cordinates_name], str):
                coords = row[cordinates_name].split(':')
                # print("dd")
                # coords = coordinates_str.split(':')
                if len(coords) != 4:
                    print(f"Error: Invalid coordinates format for {row[cordinates_name]}.")
                    return False

                x1, y1, x2, y2 = map(int, coords)

                cx = (x1 * 2)
                cy = (y1 * 2)
                cw = (x2 * 2) - (x1 * 2)
                ch = (y2 * 2) - (y1 * 2)                                

                # Validate coordinates
                if x1 < 0 or y1 < 0 or x2 > img_width or y2 > img_height or x1 >= x2 or y1 >= y2:
                    print("Error: Invalid coordinates out of image bounds.")
                    continue
                

                    # Extract the area of interest
                area_of_interest = image[cy:cy+ch, cx:cx+cw]

                with NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    cv2.imwrite(temp_file.name, area_of_interest)

                diff = ky - cy
                # print("Difff--->", diff)
                # print(f"cx-->{cx}-->cy-->{cy}-->kx-->{kx}-->ky-->{ky}--->Difff--->{diff}")

                if diff <= 10 or diff >= -10:
                    distance = math.sqrt(((kx-35) - cx) ** 2 + (ky - cy) ** 2)
                    # print("yes"+ str(distance))
                    # if distance > min_limit and distance < max_limit:
                    if distance < 50:
                        if self.is_square(temp_file.name):
                            # print("The shape is a square!")
                            # print(f"cx-->{cx}-->cy-->{cy}-->cw-->{cw}-->ch-->{ch}-->distance--->{distance}")
                            sqrt_li.append(distance)
                            sqrt_li_dict[distance] = row[cordinates_name] 
                            if int(min(sqrt_li)) < max_limit:
                                # print(f"{coords}--------{distance}")
                                fdata = sqrt_li_dict[min(sqrt_li)]                                          
                                minvalue = min(sqrt_li)
                            
                        # else:
                        #     print("The shape is not a square!")
        
        # print(sqrt_li_dict)
        if fdata:
            # print("fdata",fdata)           

            data = {
                'fdata' : fdata,
                'minvalue' : minvalue,
                'key_name' : key_name,
                'keycor' : cor

            }

            return data


    def is_square(self, image_path):
        # Load image
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
        # Check if the image is loaded successfully
        if image is None:
            print("Error: Image not found.")
            return False
    
        # Apply binary thresholding
        _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check if any contours were found
        if not contours:
            # print("No shapes found in the image.")
            return False
    
        # Assuming the largest contour is the shape of interest
        contour = max(contours, key=cv2.contourArea)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
    
        # Check if it's a square by comparing width and height
        tolerance = 0.1  # 10% tolerance, adjust as needed
        if (1 - tolerance) <= w/h <= (1 + tolerance):
            return True
        else:
            return False

    def detect_medwatch_nearest_checkbox_new(self):

        file_data = File.objects.using(self.tenant).filter(id_file=self.file_id)
        for file in file_data:

            if file.file_format == 'application/pdf':
                file_name = 'uploads/'+self.tenant+'/'+str(self.file_id)+'/page_'+str(self.page_no)+'.png'
            elif file.file_format == 'image/jpeg' or file.file_format == 'image/png':
                file_name = file.file_name

        preprocessed_image = self.preprocess_image(file_name)
       
        # return

        try:
            print(self.med_keys_path)
            df = pd.read_excel(self.med_keys_path)
            # df.dropna(inplace=True)
            key_list = []
            key_cord = []
            # df["Indexes"] = df["keywords"].str.find("Female")
            for index, row in df.iterrows():
                # print(row['keywords'])               
                key_name = row['keywords'] 
                cordints = row['cor']
                key_list.append(key_name)
                key_cord.append(cordints)   
            print(key_list)
        except Exception as e:
            print(e)
            print("exception")
        # return
        filter_final_data = []
        if preprocessed_image is not None:
            words_and_boxes = self.ocr_core(preprocessed_image)
            # print(words_and_boxes)
            if words_and_boxes:
                print("yes")
                key_data = self.find_key_data(words_and_boxes, key_list, key_cord, preprocessed_image)
                print(key_data)

    def find_diff(self, value1, value2):
        diff = (value1 - value2)
        # print(diff)
        # if diff == 1 or diff == -1 or diff == 0 or diff == 2 or diff == -2:
        if diff >= -6 and diff <= 5:
            return 1
        else:
            return 0

    def detect_medwatch_nearest_checkbox(self):
        # print("inside Medwatch function")
        # print(self.med_image_file_path)
        # print(self.med_keys_path)
        # print(self.med_keys_cors_path)

        file_data = File.objects.using(self.tenant).filter(id_file=self.file_id)

        for file in file_data:

            if file.file_format == 'application/pdf':
                file_name = 'uploads/'+self.tenant+'/'+str(self.file_id)+'/page_'+str(self.page_no)+'.png'
            elif file.file_format == 'image/jpeg' or file.file_format == 'image/png':
                file_name = file.file_name

        preprocessed_image = self.preprocess_image(file_name)
        # return
        filter_final_data = []
        if preprocessed_image is not None:
            words_and_boxes = self.ocr_core(preprocessed_image)
            # print(words_and_boxes)
            if words_and_boxes:
                text_list = ["Life-threatening", "Disability", "Death", "Hospitalization"]
                coordinates = self.find_text_boxes(words_and_boxes, text_list)
                # print(coordinates)
                row_matches = []
                for text, coords in coordinates.items():
                    # print("forloop")
                    extracted_coords = coords.split(':')[:2] 
                    extracted_coords = list(map(int, extracted_coords))
                    match = self.match_coordinates_with_excel(self.med_keys_path, extracted_coords)
                    if match is not None:
                        row_matches.append(match)
                # print(row_matches)
                # print("************")
                if row_matches:
                    most_common_row = Counter(row_matches).most_common(1)[0][0]
                    # print(most_common_row)
                    # return
                    results = self.check_all_from_excel(self.med_image_file_path, self.med_keys_cors_path, most_common_row)
                    # print(results)
                    for header, has_black_marking in results.items():
                        check_value = 0
                        if has_black_marking:
                            check_value = 1
                        else:
                            check_value = 0
                        value = {
                            'key': header,
                            'value': check_value, 
                            'co_ord': header                           
                        }
                        # print(value)
                        filter_final_data.append(value)
                        # print(f"{header}: {has_black_marking}")

                    # print(filter_final_data)
                    task = {
                        'data': filter_final_data
                    }
                    # print(task)
                    json_string = json.dumps(task, default=self.np_encoder)
                    # print("&&&&&&&&&")
                    # print(json_string)
                    return json_string

                else:
                    print("No matching row found.")
            else:
                print("No text extracted or error occurred.")
        else:
            print("Error in image preprocessing.")



# final_result = check_box_detect(keys_path, file, keys_cors_path).find_nearest_checkbox_and_detect()
# print(final_result)
