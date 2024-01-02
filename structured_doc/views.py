from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
import os, json, requests
from file_management.serializers import CreateFileSerializer, FileListSerializer
from file_management.models import File, DuplicateFilesTrack
from django.contrib.staticfiles.storage import staticfiles_storage
import boto3
from data_ingestion import settings
from configuration.aws import S3Bucket
import pandas as pd
import pytesseract
import numpy as np
import difflib
import cv2
import math
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
import mimetypes
from PIL import Image, ImageFilter
import re
from tempfile import NamedTemporaryFile

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Suma.k\AppData\Local\Tesseract-OCR\tesseract.exe"

# Create your views here.

class ExtractTrainData(S3Bucket):

    def post(self, request, *args, **kwargs):
        file_id = request.data['file_id']
        page_no = 1
        template_name = 'CIOMS'
        json_string = self.extract_cordinates(file_id, page_no, template_name)

        response_data = {
            'json_data': json_string,
            'message': "Success",
            'error': "0",
            'status_code': 200
        }

        return HttpResponse(json.dumps(response_data), status=status.HTTP_201_CREATED)

    def extract_cordinates(self, file_id, page_no, template_name,tenant):

        # try:

        # file_id = request.data['file_id']

        file_data = File.objects.using(tenant).filter(id_file=file_id)

        for file in file_data:

            if file.file_format == 'application/pdf':
                file_name = 'uploads/' + tenant + '/' + str(file_id) + '/page_' + str(page_no) + '.png'
            elif file.file_format == 'image/jpeg' or file.file_format == 'image/png':
                file_name = file.file_name

            with default_storage.open(str(file_name), mode='rb') as img:
                if template_name != "MedWatch":
                    # ------ Logic 1: To extract the text from Image ---------

                    image = cv2.imdecode(np.asarray(bytearray(img.read())), cv2.IMREAD_COLOR)
                    # image = cv2.imread(filePath)
                    # rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    custom_config = r'--oem 3 --psm 6'
                    # tesseract_output = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=custom_config)
                    tesseract_output = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                else:
                    # ------ Logic 2: To extract the text from Image using Binary Conversion---------

                    image = self.preprocess_image(img)
                    tesseract_output = ""
                    if image is not None:
                        tesseract_output = self.ocr_core(image)
                    else:
                        print("Error in image preprocessing.")

                new_dataframe = pd.DataFrame(tesseract_output)

                # print("tesseract---", tesseract_output)
                # return
                # csv_path = r"csv_data"

                # if not os.path.exists(csv_path):
                #     # if the demo_folder directory is not present
                #     # then create it.
                #     os.makedirs(csv_path)

                # csv_file = csv_path + '/image_csv1.csv'
                # new_dataframe.to_csv(csv_file)

                # Read the Keywords from xlsx file

                # keywords = self.read_key_file("MedWatch")
                # print("cioms_keys", template_name)
                # exit(1)
                keywords = self.read_key_file(template_name)

                key_data = keywords['key']
                key_cord = keywords['cord']

                result_key = []
                gg = 0

                for key_name in key_data:
                    print(key_name)
                    map_val_data = []
                    cc = 0

                    for key in key_name:
                        cordinates_name = key_cord[gg]
                        # print(cordinates_name)
                        m = 0
                        map_data = []

                        for text in new_dataframe['text']:

                            if text != '':

                                temp = difflib.SequenceMatcher(None, text.lower(), key.lower())
                                ratio = (temp.ratio()) * 100
                                data = []
                                if (ratio > 70):
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
                            'word' + str(cc): map_data
                        }
                        map_val_data.append(val)
                        cc = cc + 1

                    length = len(map_val_data)
                    if template_name == "MedWatch":
                        f_data = self.find_match_postioin_key_pair(map_val_data, key_name, image, cordinates_name,
                                                                   template_name)
                    else:
                        f_data = self.find_match_postioin(map_val_data, key_name, image, cordinates_name, template_name)

                    gg = gg + 1
                    # print(f_data)
                    # print("$$$$$$$$$$$$$$$$$$")
                    # # if f_data != '' or f_data != '[]':
                    if f_data:
                        result_key.append(f_data)
                    else:
                        print("x")

                task = {
                    'data': result_key
                }
                json_string = json.dumps(task, default=self.np_encoder)

                with open('key_ciom.json', mode='w') as f:
                    f.write(json_string)

                return json_string

        # except Exception as exc:
        #     print(exc)
        #     return Response(str(exc), status=status.HTTP_400_BAD_REQUEST)

    def preprocess_image(self, img_buffer, scale_percent=170):
        """
        This function will handle the preprocessing of images using OpenCV.
        """
        try:
            # Read the image using OpenCV
            # img = cv2.imread(filename)
            img_array = np.asarray(bytearray(img_buffer.read()), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            # Resize the image
            # width = int(img.shape[1] * scale_percent / 100)
            # height = int(img.shape[0] * scale_percent / 100)
            # dim = (width, height)
            # img = cv2.resize(img, dim, interpolation=cv2.INTER_LANCZOS4)

            # Convert the image to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Apply thresholding
            _, binary_image = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            return binary_image

        except Exception as e:
            print(f"Error in preprocessing: {e}")
            return None

    def ocr_core(self, image, custom_config=r'--oem 3 --psm 6'):
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

    def preprocess_image_with_scale(self, filename, scale_percent=145):  # Changed scale_percent to 145
        """
        This function will handle the preprocessing of images using OpenCV.
        The default scale_percent is set to 145, meaning the image will be enlarged by 45%.
        """
        print("preprocessing")
        try:
            # Read the image using OpenCV
            img = cv2.imread(str(filename))
            # Resize the image
            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            dim = (width, height)
            img = cv2.resize(img, dim, interpolation=cv2.INTER_LANCZOS4)
            # cv2.imwrite(r'C:\Qinecsa\Medwatch\new', img)
            # cv2.imwrite('cropped_bf_binary.png', img)
            # Convert the image to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Apply thresholding
            _, binary_image = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            # cv2.imwrite('cropped_after_binary.png', img)
            # Convert OpenCV image (NumPy array) to PIL Image
            pil_img = Image.fromarray(binary_image)
            custom_config = r'--oem 3 --psm 6'
            # Use Tesseract to get OCR data from the image

            data = pytesseract.image_to_data(pil_img, config=custom_config, output_type=pytesseract.Output.DICT)
            recognized_words = [word for word, conf in zip(data['text'], data['conf']) if
                                int(conf) > 0 and word.strip() != '']

            # print(recognized_words)
            result_string = ' '.join(recognized_words)
            return result_string
            # data = pytesseract.image_to_string(pil_img)
            # data = data.strip()
            # return data
        except Exception as e:
            print(f"Error in preprocessing: {e}")
            return None

    def np_encoder(self, object):
        if isinstance(object, np.generic):
            return object.item()

    def file_memory(self, file_obj, field_name, content_type):
        return InMemoryUploadedFile(
            file=file_obj,
            field_name=field_name,
            name=file_obj.name,
            content_type=content_type,
            size=file_obj.size,
            charset=None
        )

    def find_diff(self, value1, value2):
        diff = (value1 - value2)
        # print(diff)
        # if diff == 1 or diff == -1 or diff == 0 or diff == 2 or diff == -2:
        if diff >= -6 and diff <= 5:
            return 1
        else:
            return 0

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

                # Logic1

                # next_pos = int(left) + int(width) + 100
                # w2_left = w2['left']
                # if w2_left < next_pos and w2_left > left:
                #     final_arr.append(w2)
                #     match2 = 1
                # break

                # Logic2

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

                if int(sq) < 150:
                    final_arr.append(w2)
                    match2 = 1
                    break

                    # print(final_arr)
        return final_arr

    def nearest_dist(self, x1, y1, cordinates_name, template_name):
        x1 = x1 - 6
        y1 = y1 - 6

        print(f"x1 value: {x1}, y1 value: {y1}")

        if template_name == "CIOMS":
            csv_file_path = os.path.dirname(__file__) + "/key_files/cimos_cordinates.xlsx"
        elif template_name == "MedWatch":
            csv_file_path = os.path.dirname(__file__) + "/key_files/med_cordinates.xlsx"
        elif template_name == "IRMS":
            csv_file_path = os.path.dirname(__file__) + "/key_files/irms_cordinates.xlsx"

        df = pd.read_excel(csv_file_path)
        sqrt_li = []
        sqrt_li_dict = {}
        ndata = {}
        fdata = ""
        for index, row in df.iterrows():
            # data = row['weight'].split(':')
            if isinstance(row[cordinates_name], str):
                data = row[cordinates_name].split(':')
                x = int(data[0])
                y = int(data[1])
                closest_distance = float('inf')

                if template_name == 'IRMS':
                    limit = 175
                    diff = (x1 - x)
                    z = pow(diff, 2)
                    diff1 = (y1 - y)
                    z1 = pow(diff1, 2)
                    total = z + z1
                    sqrt_li.append(math.sqrt(total))
                    sqrt_li_dict[math.sqrt(total)] = row[cordinates_name]
                    print("-->>", int(min(sqrt_li)), "--->", limit)
                    if int(min(sqrt_li)) < limit:
                        fdata = sqrt_li_dict[min(sqrt_li)]
                elif template_name == 'CIOMS':
                    limit = 70
                    if y1 < y:
                        diff = (x1 - x)
                        z = pow(diff, 2)
                        diff1 = (y1 - y)
                        z1 = pow(diff1, 2)
                        total = z + z1
                        sqrt_li.append(math.sqrt(total))
                        sqrt_li_dict[math.sqrt(total)] = row[cordinates_name]
                        if int(min(sqrt_li)) < limit:
                            fdata = sqrt_li_dict[min(sqrt_li)]
                elif template_name == 'MedWatch':
                    limit = 100
                    x = x * 2
                    y = y * 2
                    if y1 < y:
                        # distance = (x1 - x)**2 + (y1 - y)**2
                        # print("**************Distance***********",distance,"------->",closest_distance)
                        # if distance < closest_distance:
                        #     print(distance)
                        diff = (x1 - x)
                        z = pow(diff, 2)
                        diff1 = (y1 - y)
                        z1 = pow(diff1, 2)
                        total = z + z1
                        sqrt_li.append(math.sqrt(total))
                        sqrt_li_dict[math.sqrt(total)] = row[cordinates_name]
                        if int(min(sqrt_li)) < limit:
                            fdata = sqrt_li_dict[min(sqrt_li)]
                            ndata[int(min(sqrt_li))] = fdata

        # if ndata:
        #     lowest_index = min(ndata.keys())
        #     fdata = ndata[lowest_index]
        print("fadata--------------------", fdata)
        return fdata

    def value_array(self, nearest, image, template_name):

        val_arr = {
            'label': "Value",
            'text': "",
            'x': "",
            'y': "",
            'w': "",
            'h': ""
        }
        if template_name == "MedWatch":
            if nearest != "":

                val_data = nearest.split(':')
                mx1 = int(val_data[0])
                my1 = int(val_data[1])
                mw1 = int(val_data[2])
                mh1 = int(val_data[3])
                mx1 = mx1 * 2
                my1 = my1 * 2
                mw1 = mw1 * 2
                mh1 = mh1 * 2
                if mw1 > mx1:
                    mw1 = mw1 - mx1
                if mh1 > my1:
                    mh1 = mh1 - my1

                cropped = image[my1:my1 + mh1, mx1:mx1 + mw1]

                # Save the cropped image as a temporary file
                with NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    cv2.imwrite(temp_file.name, cropped)

                crop_image_data = self.preprocess_image_with_scale(temp_file.name)

                print(crop_image_data)
                # Apply OCR on the cropped image
                # val_data = pytesseract.image_to_string(cropped)
                val_arr = {
                    'label': "Value",
                    'text': crop_image_data,
                    'x': mx1,
                    'y': my1,
                    'w': mw1,
                    'h': mh1
                }

        else:
            if nearest != "":

                val_data = nearest.split(':')
                mx1 = int(val_data[0])
                my1 = int(val_data[1])
                mw1 = int(val_data[2])
                mh1 = int(val_data[3])
                if mw1 > mx1:
                    mw1 = mw1 - mx1
                if mh1 > my1:
                    mh1 = mh1 - my1

                cropped = image[my1:my1 + mh1, mx1:mx1 + mw1]

                # Apply OCR on the cropped image
                val_data = pytesseract.image_to_string(cropped)
                val_arr = {
                    'label': "Value",
                    'text': val_data.strip(),
                    'x': mx1,
                    'y': my1,
                    'w': mw1,
                    'h': mh1
                }

        return val_arr

    def nearest_dist_key_pair(self, x1, y1, cordinates_name, template_name):
        # print("Nearest")
        x1 = x1 - 2
        y1 = y1 - 2
        max_limit = 100
        min_limit = 5
        if template_name == "CIOMS":
            csv_file_path = os.path.dirname(__file__) + "/key_files/cimos_cordinates.xlsx"
        elif template_name == "MedWatch":
            csv_file_path = os.path.dirname(__file__) + "/key_files/med_cordinates.xlsx"
        elif template_name == "IRMS":
            csv_file_path = os.path.dirname(__file__) + "/key_files/irms_cordinates.xlsx"
        # print(template_name)
        df = pd.read_excel(csv_file_path)
        sqrt_li = []
        sqrt_li_dict = {}
        fdata = ""
        ndata = {}
        m = 0
        result_string = ""
        # print(x1,"<------------>",y1)
        # print(cordinates_name)
        # print(df.iterrows())
        for index, row in df.iterrows():
            # print(row[cordinates_name])
            # data = row['weight'].split(':')
            if isinstance(row[cordinates_name], str):
                data_arr = row[cordinates_name].split('_')
                # print(data_arr)
                full_arr_val = data_arr[0]
                # for full_arr_val in data_arr[0]:
                # print(full_arr_val)
                # print("****************")
                data = full_arr_val.split(':')
                x = int(data[0])
                y = int(data[1])
                x = x * 2
                y = y * 2
                # if y <= (y1):
                diff = (x1 - x)
                z = pow(diff, 2)
                diff1 = (y1 - y)
                z1 = pow(diff1, 2)
                total = z + z1
                distance = math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
                # print("distance------>", distance)
                # print("math.sqrt(total)----->", math.sqrt(total))
                # if (diff >= -10 or diff <= 10) and (diff1 <= 10 or diff1 >= -10):
                # if diff >= -10 and diff1 >= -10:
                # if diff >= 0 and diff1 >= 0:
                # if diff >= -10 and diff <= 10:
                #     if diff1 >= -10 and diff1 <= 10:
                #         print("diff-X--->",diff,"diff1-Y--->",diff1,"distance------>", distance,"data_arr------>", data_arr)

                sqrt_li.append(math.sqrt(total))
                sqrt_li_dict[math.sqrt(total)] = row[cordinates_name]
                # print(sqrt_li)
                # print(sqrt_li_dict)
                # if int(min(sqrt_li)) > min_limit or int(min(sqrt_li)) < max_limit:
                if int(min(sqrt_li)) < max_limit:
                    fdata = sqrt_li_dict[min(sqrt_li)]
                    ndata[int(min(sqrt_li))] = fdata

        print("fdata--->", fdata)
        # print(ndata)
        # if ndata:
        #     lowest_index = min(ndata.keys())
        #     fdata = ndata[lowest_index]
        # print(fdata)
        if fdata:
            # Split the string by the underscore to get individual parts
            parts = fdata.split('_')

            # Initialize an empty list to store the modified parts
            doubled_parts = []

            # Process each part and multiply integer values by 2
            for part in parts:
                values = part.split(':')  # Split each part by ':'
                doubled_values = [str(int(value) * 2) for value in values]  # Multiply by 2 and convert back to a string
                doubled_parts.append(':'.join(doubled_values))  # Join the modified values with ':'

            # Join the modified parts with underscores to reconstruct the string
            result_string = '_'.join(doubled_parts)
        print(result_string)
        # exit(1)
        return result_string

    def value_array_key_pair(self, nearest, image, template_name):

        val_arr = {
            'label': "Value",
            'text': "",
            'x': "",
            'y': "",
            'w': "",
            'h': ""
        }

        if template_name == "MedWatch":
            if nearest != "":
                parts = nearest.split('_')
                val_data = parts[1].split(':')
                mx1 = int(val_data[0])
                my1 = int(val_data[1])
                mw1 = int(val_data[2])
                mh1 = int(val_data[3])
                # mx1 = mx1 * 2
                # my1 = my1 * 2
                # mw1 = mw1 * 2
                # mh1 = mh1 * 2
                if mw1 > mx1:
                    mw1 = mw1 - mx1
                if mh1 > my1:
                    mh1 = mh1 - my1

                cropped = image[my1:my1 + mh1, mx1:mx1 + mw1]

                # Save the cropped image as a temporary file
                with NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    cv2.imwrite(temp_file.name, cropped)

                crop_image_data = self.preprocess_image_with_scale(temp_file.name)

                print(crop_image_data)
                # Apply OCR on the cropped image
                # val_data = pytesseract.image_to_string(cropped)
                val_arr = {
                    'label': "Value",
                    'text': crop_image_data,
                    'x': mx1,
                    'y': my1,
                    'w': mw1,
                    'h': mh1
                }

        else:

            if nearest != "":
                parts = nearest.split('_')
                val_data = parts[1].split(':')
                mx1 = int(val_data[0])
                my1 = int(val_data[1])
                mw1 = int(val_data[2])
                mh1 = int(val_data[3])
                # mx1 = mx1 * 2
                # my1 = my1 * 2
                # mw1 = mw1 * 2
                # mh1 = mh1 * 2
                if mw1 > mx1:
                    mw1 = mw1 - mx1
                if mh1 > my1:
                    mh1 = mh1 - my1

                cropped = image[my1:my1 + mh1, mx1:mx1 + mw1]

                # Apply OCR on the cropped image
                val_data = pytesseract.image_to_string(cropped)
                val_arr = {
                    'label': "Value",
                    'text': val_data.strip(),
                    'x': mx1,
                    'y': my1,
                    'w': mw1,
                    'h': mh1
                }

        return val_arr

    def find_match_postioin(self, result_data, key_name, image, cordinates_name, template_name):
        # print("key_name:"+str(key_name))
        key_name = ' '.join(key_name)
        # print("result_string",key_name)
        # print("match position--",result_data)
        length = len(result_data)
        word_arr = {}
        for i in range(0, (length)):
            wrd = 'word' + str(i)
            word_arr[i] = result_data[i][wrd]

        word_length = len(word_arr)

        final_json_data = []
        value_json_data = []
        final_array = []

        # print("word_length--", word_length)
        # print("word_arr--", word_arr)

        if word_length == 1:
            for w1 in word_arr[0]:
                # print("w1--", w1)
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                nearest = self.nearest_dist(x, (y + h), cordinates_name, template_name)
                # nearest = self.nearest_dist_key_pair(x, (y + h), cordinates_name, template_name)

                # print(nearest)

                if (nearest):
                    info_arr = {
                        'label': "Keyword",
                        'text': w1['text'],
                        'x': x,
                        'y': y,
                        'w': w,
                        'h': h,
                        'key_name': str(key_name),
                        'cordinates_name': str(cordinates_name)
                    }
                    # print(info_arr)
                    final_json_data.append(info_arr)
                    val_arr = self.value_array(nearest, image, template_name)
                    # val_arr = self.value_array_key_pair(nearest, image, template_name)
                    # print(nearest)
                    value_json_data.append(val_arr)

                    final_array = {
                        'key': info_arr,
                        'value': val_arr
                    }

                    # print(final_array)
                    break

        elif word_length == 2:

            for w1 in word_arr[0]:

                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                if (len(word_arr[1]) > 0):

                    data = self.matched_array(word_arr[1], y, x, w)
                    # print(data)
                    if len(data) > 0:

                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']

                        xmin = x
                        ymin = y
                        wmin = w + w11 + 10
                        hmin = (min(h, h1))

                        info_arr = {
                            'label': "Keyword",
                            'text': str(w1['text']) + " " + str(data[0]['text']),
                            'x': xmin,
                            'y': ymin,
                            'w': wmin,
                            'h': hmin,
                            'key_name': str(key_name),
                            'cordinates_name': str(cordinates_name)
                        }

                        final_json_data.append(info_arr)

                        nearest = self.nearest_dist(x, (y + hmin), cordinates_name, template_name)
                        # nearest = self.nearest_dist_key_pair(x, (y + hmin), cordinates_name, template_name)
                        if (nearest):
                            val_arr = self.value_array(nearest, image, template_name)
                            # val_arr = self.value_array_key_pair(nearest, image, template_name)
                            # print(nearest)
                            value_json_data.append(val_arr)

                            final_array = {
                                'key': info_arr,
                                'value': val_arr
                            }
                            # match2 = 1
                            break
                            # return final_array

        elif word_length == 3:

            for w1 in word_arr[0]:

                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                xmin = x
                                ymin = y
                                wmin = w + w11 + w2 + 10
                                hmin = (min(h, h1, h2))

                                info_arr = {
                                    'label': "Keyword",
                                    'text': str(w1['text']) + " " + str(data[0]['text']) + " " + str(data2[0]['text']),
                                    'x': xmin,
                                    'y': ymin,
                                    'w': wmin,
                                    'h': hmin,
                                    'key_name': str(key_name),
                                    'cordinates_name': str(cordinates_name)
                                }
                                final_json_data.append(info_arr)

                                nearest = self.nearest_dist(x, (y + hmin), cordinates_name, template_name)
                                # nearest = self.nearest_dist_key_pair(x, (y + hmin), cordinates_name, template_name)

                                # print(nearest)
                                if (nearest):
                                    val_arr = self.value_array(nearest, image, template_name)
                                    # val_arr = self.value_array_key_pair(nearest, image, template_name)

                                    value_json_data.append(val_arr)

                                    final_array = {
                                        'key': info_arr,
                                        'value': val_arr
                                    }

        elif word_length == 4:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            # print(data2)
                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)
                                    # print("3333333333333")
                                    # print(data3)
                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        xmin = x
                                        ymin = y
                                        wmin = w + w11 + w2 + w3 + 10
                                        hmin = (min(h, h1, h2, h3))

                                        info_arr = {
                                            'label': "Keyword",
                                            'text': str(w1['text']) + " " + str(data[0]['text']) + " " + str(
                                                data2[0]['text']) + " " + str(data3[0]['text']),
                                            'x': xmin,
                                            'y': ymin,
                                            'w': wmin,
                                            'h': hmin,
                                            'key_name': str(key_name),
                                            'cordinates_name': str(cordinates_name)
                                        }
                                        final_json_data.append(info_arr)
                                        # print(w1)
                                        # print(data[0])
                                        # print(data2[0])
                                        # print(data3[0])

                                        nearest = self.nearest_dist(x, (y + hmin), cordinates_name, template_name)
                                        # print(nearest)
                                        if (nearest):
                                            # print("yes")
                                            val_arr = self.value_array(nearest, image, template_name)
                                            # print(val_arr)
                                            value_json_data.append(val_arr)

                                            final_array = {
                                                'key': info_arr,
                                                'value': val_arr
                                            }
                                            # print(final_array)
                                            # break

        elif word_length == 5:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)

                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        if (len(word_arr[4]) > 0):
                                            data4 = self.matched_array(word_arr[4], w1_top, x3, w3)

                                            if len(data4) > 0:
                                                x4 = data4[0]['left']
                                                y4 = data4[0]['top']
                                                w4 = data4[0]['width']
                                                h4 = data4[0]['height']

                                                xmin = x
                                                ymin = y
                                                wmin = w + w11 + w2 + w3 + w4 + 10
                                                hmin = (min(h, h1, h2, h3, h4))

                                                text_val = str(w1['text']) + " " + str(data[0]['text']) + " " + str(
                                                    data2[0]['text']) + " " + str(data3[0]['text']) + " " + str(
                                                    data4[0]['text'])

                                                info_arr = {
                                                    'label': "Keyword",
                                                    'text': text_val,
                                                    'x': xmin,
                                                    'y': ymin,
                                                    'w': wmin,
                                                    'h': hmin,
                                                    'key_name': str(key_name),
                                                    'cordinates_name': str(cordinates_name)
                                                }
                                                final_json_data.append(info_arr)
                                                # print(w1)
                                                # print(data[0])
                                                # print(data2[0])
                                                # print(data3[0])

                                                nearest = self.nearest_dist(x, (y + hmin), cordinates_name,
                                                                            template_name)

                                                val_arr = self.value_array(nearest, image, template_name)

                                                value_json_data.append(val_arr)

                                                final_array = {
                                                    'key': info_arr,
                                                    'value': val_arr
                                                }

        elif word_length == 6:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)

                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        if (len(word_arr[4]) > 0):
                                            data4 = self.matched_array(word_arr[4], w1_top, x3, w3)

                                            if len(data4) > 0:

                                                x4 = data4[0]['left']
                                                y4 = data4[0]['top']
                                                w4 = data4[0]['width']
                                                h4 = data4[0]['height']

                                                if (len(word_arr[5]) > 0):
                                                    data5 = self.matched_array(word_arr[5], w1_top, x4, w4)

                                                    if len(data5) > 0:
                                                        x5 = data5[0]['left']
                                                        y5 = data5[0]['top']
                                                        w5 = data5[0]['width']
                                                        h5 = data5[0]['height']

                                                        xmin = x
                                                        ymin = y
                                                        wmin = w + w11 + w2 + w3 + w4 + w5 + 10
                                                        hmin = (min(h, h1, h2, h3, h4, h5))

                                                        text_val = str(w1['text']) + " " + str(
                                                            data[0]['text']) + " " + str(data2[0]['text']) + " " + str(
                                                            data3[0]['text']) + " " + str(data4[0]['text']) + " " + str(
                                                            data5[0]['text'])

                                                        info_arr = {
                                                            'label': "Keyword",
                                                            'text': text_val,
                                                            'x': xmin,
                                                            'y': ymin,
                                                            'w': wmin,
                                                            'h': hmin,
                                                            'key_name': str(key_name),
                                                            'cordinates_name': str(cordinates_name)
                                                        }
                                                        final_json_data.append(info_arr)
                                                        # print(w1)
                                                        # print(data[0])
                                                        # print(data2[0])
                                                        # print(data3[0])

                                                        nearest = self.nearest_dist(x, (y + hmin), cordinates_name,
                                                                                    template_name)

                                                        val_arr = self.value_array(nearest, image, template_name)

                                                        value_json_data.append(val_arr)

                                                        final_array = {
                                                            'key': info_arr,
                                                            'value': val_arr
                                                        }

        elif word_length == 7:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)

                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        if (len(word_arr[4]) > 0):
                                            data4 = self.matched_array(word_arr[4], w1_top, x3, w3)

                                            if len(data4) > 0:

                                                x4 = data4[0]['left']
                                                y4 = data4[0]['top']
                                                w4 = data4[0]['width']
                                                h4 = data4[0]['height']

                                                if (len(word_arr[5]) > 0):
                                                    data5 = self.matched_array(word_arr[5], w1_top, x4, w4)

                                                    if len(data5) > 0:

                                                        x5 = data5[0]['left']
                                                        y5 = data5[0]['top']
                                                        w5 = data5[0]['width']
                                                        h5 = data5[0]['height']

                                                        if (len(word_arr[6]) > 0):
                                                            data6 = self.matched_array(word_arr[6], w1_top, x5, w5)

                                                            if len(data6) > 0:
                                                                x6 = data6[0]['left']
                                                                y6 = data6[0]['top']
                                                                w6 = data6[0]['width']
                                                                h6 = data6[0]['height']

                                                                xmin = x
                                                                ymin = y
                                                                wmin = w + w11 + w2 + w3 + w4 + w5 + w6 + 10
                                                                # make changes from min function to max function
                                                                hmin = (min(h, h1, h2, h3, h4, h5, h6))

                                                                text_val = str(w1['text']) + " " + str(
                                                                    data[0]['text']) + " " + str(
                                                                    data2[0]['text']) + " " + str(
                                                                    data3[0]['text']) + " " + str(
                                                                    data4[0]['text']) + " " + str(
                                                                    data5[0]['text'] + " " + str(data6[0]['text']))

                                                                info_arr = {
                                                                    'label': "Keyword",
                                                                    'text': text_val,
                                                                    'x': xmin,
                                                                    'y': ymin,
                                                                    'w': wmin,
                                                                    'h': hmin,
                                                                    'key_name': str(key_name),
                                                                    'cordinates_name': str(cordinates_name)
                                                                }
                                                                final_json_data.append(info_arr)
                                                                # print(w1)
                                                                # print(data[0])
                                                                # print(data2[0])
                                                                # print(data3[0])

                                                                nearest = self.nearest_dist(x, (y + hmin),
                                                                                            cordinates_name,
                                                                                            template_name)
                                                                # print(x,"<------------>",y,"=====",hmin,"<------------>",wmin)
                                                                val_arr = self.value_array(nearest, image,
                                                                                           template_name)

                                                                value_json_data.append(val_arr)

                                                                final_array = {
                                                                    'key': info_arr,
                                                                    'value': val_arr
                                                                }

        elif word_length == 8:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)

                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        if (len(word_arr[4]) > 0):
                                            data4 = self.matched_array(word_arr[4], w1_top, x3, w3)

                                            if len(data4) > 0:

                                                x4 = data4[0]['left']
                                                y4 = data4[0]['top']
                                                w4 = data4[0]['width']
                                                h4 = data4[0]['height']

                                                if (len(word_arr[5]) > 0):
                                                    data5 = self.matched_array(word_arr[5], w1_top, x4, w4)

                                                    if len(data5) > 0:

                                                        x5 = data5[0]['left']
                                                        y5 = data5[0]['top']
                                                        w5 = data5[0]['width']
                                                        h5 = data5[0]['height']

                                                        if (len(word_arr[6]) > 0):
                                                            data6 = self.matched_array(word_arr[6], w1_top, x5, w5)

                                                            if len(data6) > 0:

                                                                x6 = data6[0]['left']
                                                                y6 = data6[0]['top']
                                                                w6 = data6[0]['width']
                                                                h6 = data6[0]['height']

                                                                if (len(word_arr[7]) > 0):
                                                                    data7 = self.matched_array(word_arr[7], w1_top, x6,
                                                                                               w6)

                                                                    if len(data7) > 0:
                                                                        x7 = data7[0]['left']
                                                                        y7 = data7[0]['top']
                                                                        w7 = data7[0]['width']
                                                                        h7 = data7[0]['height']

                                                                        xmin = x
                                                                        ymin = y
                                                                        wmin = w + w11 + w2 + w3 + w4 + w5 + w6 + w7 + 10
                                                                        # make changes from min function to max function
                                                                        hmin = (min(h, h1, h2, h3, h4, h5, h6, h7))

                                                                        text_val = str(w1['text']) + " " + str(
                                                                            data[0]['text']) + " " + str(
                                                                            data2[0]['text']) + " " + str(
                                                                            data3[0]['text']) + " " + str(
                                                                            data4[0]['text']) + " " + str(
                                                                            data5[0]['text'] + " " + str(
                                                                                data6[0]['text']) + " " + str(
                                                                                data7[0]['text']))

                                                                        info_arr = {
                                                                            'label': "Keyword",
                                                                            'text': text_val,
                                                                            'x': xmin,
                                                                            'y': ymin,
                                                                            'w': wmin,
                                                                            'h': hmin,
                                                                            'key_name': str(key_name),
                                                                            'cordinates_name': str(cordinates_name)
                                                                        }
                                                                        final_json_data.append(info_arr)
                                                                        # print(w1)
                                                                        # print(data[0])
                                                                        # print(data2[0])
                                                                        # print(data3[0])

                                                                        nearest = self.nearest_dist(x, (y + hmin),
                                                                                                    cordinates_name,
                                                                                                    template_name)
                                                                        # print(x,"<------------>",y,"=====",hmin,"<------------>",wmin)
                                                                        val_arr = self.value_array(nearest, image,
                                                                                                   template_name)

                                                                        value_json_data.append(val_arr)

                                                                        final_array = {
                                                                            'key': info_arr,
                                                                            'value': val_arr
                                                                        }

        elif word_length == 9:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)

                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        if (len(word_arr[4]) > 0):
                                            data4 = self.matched_array(word_arr[4], w1_top, x3, w3)

                                            if len(data4) > 0:

                                                x4 = data4[0]['left']
                                                y4 = data4[0]['top']
                                                w4 = data4[0]['width']
                                                h4 = data4[0]['height']

                                                if (len(word_arr[5]) > 0):
                                                    data5 = self.matched_array(word_arr[5], w1_top, x4, w4)

                                                    if len(data5) > 0:

                                                        x5 = data5[0]['left']
                                                        y5 = data5[0]['top']
                                                        w5 = data5[0]['width']
                                                        h5 = data5[0]['height']

                                                        if (len(word_arr[6]) > 0):
                                                            data6 = self.matched_array(word_arr[6], w1_top, x5, w5)

                                                            if len(data6) > 0:

                                                                x6 = data6[0]['left']
                                                                y6 = data6[0]['top']
                                                                w6 = data6[0]['width']
                                                                h6 = data6[0]['height']

                                                                if (len(word_arr[7]) > 0):
                                                                    data7 = self.matched_array(word_arr[7], w1_top, x6,
                                                                                               w6)

                                                                    if len(data7) > 0:

                                                                        x7 = data7[0]['left']
                                                                        y7 = data7[0]['top']
                                                                        w7 = data7[0]['width']
                                                                        h7 = data7[0]['height']

                                                                        if (len(word_arr[8]) > 0):
                                                                            data8 = self.matched_array(word_arr[8],
                                                                                                       w1_top, x7, w7)

                                                                            if len(data8) > 0:
                                                                                x8 = data8[0]['left']
                                                                                y8 = data8[0]['top']
                                                                                w8 = data8[0]['width']
                                                                                h8 = data8[0]['height']

                                                                                xmin = x
                                                                                ymin = y
                                                                                wmin = w + w11 + w2 + w3 + w4 + w5 + w6 + w7 + w8 + 10
                                                                                # make changes from min function to max function
                                                                                hmin = (
                                                                                    min(h, h1, h2, h3, h4, h5, h6, h7,
                                                                                        h8))

                                                                                text_val = str(w1['text']) + " " + str(
                                                                                    data[0]['text']) + " " + str(
                                                                                    data2[0]['text']) + " " + str(
                                                                                    data3[0]['text']) + " " + str(
                                                                                    data4[0]['text']) + " " + str(
                                                                                    data5[0]['text'] + " " + str(
                                                                                        data6[0]['text']) + " " + str(
                                                                                        data7[0]['text']) + " " + str(
                                                                                        data8[0]['text']))

                                                                                info_arr = {
                                                                                    'label': "Keyword",
                                                                                    'text': text_val,
                                                                                    'x': xmin,
                                                                                    'y': ymin,
                                                                                    'w': wmin,
                                                                                    'h': hmin,
                                                                                    'key_name': str(key_name),
                                                                                    'cordinates_name': str(
                                                                                        cordinates_name)
                                                                                }
                                                                                final_json_data.append(info_arr)
                                                                                # print(w1)
                                                                                # print(data[0])
                                                                                # print(data2[0])
                                                                                # print(data3[0])

                                                                                nearest = self.nearest_dist(x,
                                                                                                            (y + hmin),
                                                                                                            cordinates_name,
                                                                                                            template_name)
                                                                                # print(x,"<------------>",y,"=====",hmin,"<------------>",wmin)
                                                                                val_arr = self.value_array(nearest,
                                                                                                           image,
                                                                                                           template_name)

                                                                                value_json_data.append(val_arr)

                                                                                final_array = {
                                                                                    'key': info_arr,
                                                                                    'value': val_arr
                                                                                }

        elif word_length == 10:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)

                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        if (len(word_arr[4]) > 0):
                                            data4 = self.matched_array(word_arr[4], w1_top, x3, w3)

                                            if len(data4) > 0:

                                                x4 = data4[0]['left']
                                                y4 = data4[0]['top']
                                                w4 = data4[0]['width']
                                                h4 = data4[0]['height']

                                                if (len(word_arr[5]) > 0):
                                                    data5 = self.matched_array(word_arr[5], w1_top, x4, w4)

                                                    if len(data5) > 0:

                                                        x5 = data5[0]['left']
                                                        y5 = data5[0]['top']
                                                        w5 = data5[0]['width']
                                                        h5 = data5[0]['height']

                                                        if (len(word_arr[6]) > 0):
                                                            data6 = self.matched_array(word_arr[6], w1_top, x5, w5)

                                                            if len(data6) > 0:

                                                                x6 = data6[0]['left']
                                                                y6 = data6[0]['top']
                                                                w6 = data6[0]['width']
                                                                h6 = data6[0]['height']

                                                                if (len(word_arr[7]) > 0):
                                                                    data7 = self.matched_array(word_arr[7], w1_top, x6,
                                                                                               w6)

                                                                    if len(data7) > 0:

                                                                        x7 = data7[0]['left']
                                                                        y7 = data7[0]['top']
                                                                        w7 = data7[0]['width']
                                                                        h7 = data7[0]['height']

                                                                        if (len(word_arr[8]) > 0):
                                                                            data8 = self.matched_array(word_arr[8],
                                                                                                       w1_top, x7, w7)

                                                                            if len(data8) > 0:

                                                                                x8 = data8[0]['left']
                                                                                y8 = data8[0]['top']
                                                                                w8 = data8[0]['width']
                                                                                h8 = data8[0]['height']

                                                                                if (len(word_arr[9]) > 0):
                                                                                    data9 = self.matched_array(
                                                                                        word_arr[9], w1_top, x8, w8)

                                                                                    if len(data9) > 0:
                                                                                        x9 = data9[0]['left']
                                                                                        y9 = data9[0]['top']
                                                                                        w9 = data9[0]['width']
                                                                                        h9 = data9[0]['height']

                                                                                        xmin = x
                                                                                        ymin = y
                                                                                        wmin = w + w11 + w2 + w3 + w4 + w5 + w6 + w7 + w8 + w9 + 10
                                                                                        # make changes from min function to max function
                                                                                        hmin = (
                                                                                            min(h, h1, h2, h3, h4, h5,
                                                                                                h6, h7, h8, h9))

                                                                                        text_val = str(
                                                                                            w1['text']) + " " + str(
                                                                                            data[0][
                                                                                                'text']) + " " + str(
                                                                                            data2[0][
                                                                                                'text']) + " " + str(
                                                                                            data3[0][
                                                                                                'text']) + " " + str(
                                                                                            data4[0][
                                                                                                'text']) + " " + str(
                                                                                            data5[0][
                                                                                                'text'] + " " + str(
                                                                                                data6[0][
                                                                                                    'text']) + " " + str(
                                                                                                data7[0][
                                                                                                    'text']) + " " + str(
                                                                                                data8[0][
                                                                                                    'text']) + " " + str(
                                                                                                data9[0]['text']))

                                                                                        info_arr = {
                                                                                            'label': "Keyword",
                                                                                            'text': text_val,
                                                                                            'x': xmin,
                                                                                            'y': ymin,
                                                                                            'w': wmin,
                                                                                            'h': hmin,
                                                                                            'key_name': str(key_name),
                                                                                            'cordinates_name': str(
                                                                                                cordinates_name)
                                                                                        }
                                                                                        final_json_data.append(info_arr)
                                                                                        # print(w1)
                                                                                        # print(data[0])
                                                                                        # print(data2[0])
                                                                                        # print(data3[0])

                                                                                        nearest = self.nearest_dist(x, (
                                                                                                    y + hmin),
                                                                                                                    cordinates_name,
                                                                                                                    template_name)
                                                                                        # print(x,"<------------>",y,"=====",hmin,"<------------>",wmin)
                                                                                        val_arr = self.value_array(
                                                                                            nearest, image,
                                                                                            template_name)

                                                                                        value_json_data.append(val_arr)

                                                                                        final_array = {
                                                                                            'key': info_arr,
                                                                                            'value': val_arr
                                                                                        }

        else:

            final_array = {
                'key': "Use Manual Approch",
                'value': "Use Manual Approch"
            }

        # temp_docx_path = os.path.dirname(__file__) + "/plot_images"

        # if not os.path.exists(temp_docx_path):
        #     os.makedirs(temp_docx_path)

        # temp_docx_path = temp_docx_path + "/7.png"

        # cv2.imwrite(temp_docx_path, image)

        return final_array

    def find_match_postioin_key_pair(self, result_data, key_name, image, cordinates_name, template_name):
        # print("key_name:"+str(key_name))
        key_name = ' '.join(key_name)
        # print("result_string",key_name)
        # print("match position--",result_data)
        length = len(result_data)
        word_arr = {}
        for i in range(0, (length)):
            wrd = 'word' + str(i)
            word_arr[i] = result_data[i][wrd]

        word_length = len(word_arr)

        final_json_data = []
        value_json_data = []
        final_array = []

        # print("word_length--", word_length)
        # print("word_arr--", word_arr)

        if word_length == 1:
            for w1 in word_arr[0]:
                # print("w1--", w1)
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # nearest = self.nearest_dist(x, (y + h), cordinates_name, template_name)
                nearest = self.nearest_dist_key_pair(x, y, cordinates_name, template_name)

                # print(nearest)

                if (nearest):
                    parts = nearest.split('_')
                    val_data = parts[0].split(':')

                    info_arr = {
                        'label': "Keyword",
                        'text': w1['text'],
                        'x': val_data[0],
                        'y': val_data[1],
                        'w': int(val_data[2]) - int(val_data[0]),
                        'h': int(val_data[3]) - int(val_data[1]),
                        'key_name': str(key_name),
                        'cordinates_name': str(cordinates_name)
                    }
                    # print(info_arr)
                    final_json_data.append(info_arr)
                    # val_arr = self.value_array(nearest, image, template_name)
                    val_arr = self.value_array_key_pair(nearest, image, template_name)
                    # print(nearest)
                    value_json_data.append(val_arr)

                    final_array = {
                        'key': info_arr,
                        'value': val_arr
                    }

                    # print(final_array)
                    break

        elif word_length == 2:

            for w1 in word_arr[0]:

                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                if (len(word_arr[1]) > 0):

                    data = self.matched_array(word_arr[1], y, x, w)
                    print(data)
                    if len(data) > 0:

                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']

                        xmin = x
                        ymin = y
                        wmin = w + w11 + 10
                        hmin = (min(h, h1))

                        nearest = self.nearest_dist_key_pair(x, y, cordinates_name, template_name)
                        # nearest = self.nearest_dist_key_pair(x, (y + hmin), cordinates_name, template_name)
                        if (nearest):
                            parts = nearest.split('_')
                            val_data = parts[0].split(':')

                            info_arr = {
                                'label': "Keyword",
                                'text': str(w1['text']) + " " + str(data[0]['text']),
                                'x': val_data[0],
                                'y': val_data[1],
                                'w': int(val_data[2]) - int(val_data[0]),
                                'h': int(val_data[3]) - int(val_data[1]),
                                'key_name': str(key_name),
                                'cordinates_name': str(cordinates_name)
                            }

                            final_json_data.append(info_arr)

                            val_arr = self.value_array_key_pair(nearest, image, template_name)
                            # val_arr = self.value_array_key_pair(nearest, image, template_name)
                            # print(nearest)
                            value_json_data.append(val_arr)

                            final_array = {
                                'key': info_arr,
                                'value': val_arr
                            }
                            # match2 = 1
                            break
                            # return final_array

        elif word_length == 3:

            for w1 in word_arr[0]:

                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)
                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)
                            # print(data2)
                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                xmin = x
                                ymin = y
                                wmin = w + w11 + w2 + 10
                                hmin = (min(h, h1, h2))

                                # nearest = self.nearest_dist(x, (y + hmin), cordinates_name, template_name)
                                nearest = self.nearest_dist_key_pair(x, y, cordinates_name, template_name)

                                # print(nearest)
                                if (nearest):
                                    print(f"x-->{x}---> y--->{y}--->h--->{h}-->w--->{w}")
                                    parts = nearest.split('_')
                                    val_data = parts[0].split(':')

                                    info_arr = {
                                        'label': "Keyword",
                                        'text': str(w1['text']) + " " + str(data[0]['text']) + " " + str(
                                            data2[0]['text']),
                                        'x': val_data[0],
                                        'y': val_data[1],
                                        'w': int(val_data[2]) - int(val_data[0]),
                                        'h': int(val_data[3]) - int(val_data[1]),
                                        'key_name': str(key_name),
                                        'cordinates_name': str(cordinates_name)
                                    }
                                    final_json_data.append(info_arr)

                                    # val_arr = self.value_array(nearest, image, template_name)
                                    val_arr = self.value_array_key_pair(nearest, image, template_name)

                                    value_json_data.append(val_arr)

                                    final_array = {
                                        'key': info_arr,
                                        'value': val_arr
                                    }

        elif word_length == 4:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            # print(data2)
                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)
                                    # print("3333333333333")
                                    # print(data3)
                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        xmin = x
                                        ymin = y
                                        wmin = w + w11 + w2 + w3 + 10
                                        hmin = (min(h, h1, h2, h3))

                                        # print(w1)
                                        # print(data[0])
                                        # print(data2[0])
                                        # print(data3[0])

                                        nearest = self.nearest_dist_key_pair(x, y, cordinates_name, template_name)
                                        # print(nearest)
                                        if (nearest):
                                            # print(f"x-->{x}---> y--->{y}--->h--->{h}-->w--->{w}")
                                            parts = nearest.split('_')
                                            val_data = parts[0].split(':')

                                            info_arr = {
                                                'label': "Keyword",
                                                'text': str(w1['text']) + " " + str(data[0]['text']) + " " + str(
                                                    data2[0]['text']) + " " + str(data3[0]['text']),
                                                'x': val_data[0],
                                                'y': val_data[1],
                                                'w': int(val_data[2]) - int(val_data[0]),
                                                'h': int(val_data[3]) - int(val_data[1]),
                                                'key_name': str(key_name),
                                                'cordinates_name': str(cordinates_name)
                                            }
                                            final_json_data.append(info_arr)
                                            # print("yes")
                                            val_arr = self.value_array_key_pair(nearest, image, template_name)
                                            # print(val_arr)
                                            value_json_data.append(val_arr)

                                            final_array = {
                                                'key': info_arr,
                                                'value': val_arr
                                            }
                                            print(final_array)
                                            # break

        elif word_length == 5:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)
                            # print(data2)
                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)
                                    # print(data3)
                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        if (len(word_arr[4]) > 0):
                                            data4 = self.matched_array(word_arr[4], w1_top, x3, w3)
                                            # print(data4)
                                            if len(data4) > 0:

                                                x4 = data4[0]['left']
                                                y4 = data4[0]['top']
                                                w4 = data4[0]['width']
                                                h4 = data4[0]['height']

                                                xmin = x
                                                ymin = y
                                                wmin = w + w11 + w2 + w3 + w4 + 10
                                                hmin = (min(h, h1, h2, h3, h4))

                                                text_val = str(w1['text']) + " " + str(data[0]['text']) + " " + str(
                                                    data2[0]['text']) + " " + str(data3[0]['text']) + " " + str(
                                                    data4[0]['text'])

                                                nearest = self.nearest_dist_key_pair(x, y, cordinates_name,
                                                                                     template_name)

                                                if (nearest):
                                                    parts = nearest.split('_')
                                                    val_data = parts[0].split(':')

                                                    info_arr = {
                                                        'label': "Keyword",
                                                        'text': text_val,
                                                        'x': val_data[0],
                                                        'y': val_data[1],
                                                        'w': int(val_data[2]) - int(val_data[0]),
                                                        'h': int(val_data[3]) - int(val_data[1]),
                                                        'key_name': str(key_name),
                                                        'cordinates_name': str(cordinates_name)
                                                    }
                                                    final_json_data.append(info_arr)
                                                    # print(w1)
                                                    # print(data[0])
                                                    # print(data2[0])
                                                    # print(data3[0])

                                                    val_arr = self.value_array_key_pair(nearest, image, template_name)

                                                    value_json_data.append(val_arr)

                                                    final_array = {
                                                        'key': info_arr,
                                                        'value': val_arr
                                                    }

        elif word_length == 6:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)

                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        if (len(word_arr[4]) > 0):
                                            data4 = self.matched_array(word_arr[4], w1_top, x3, w3)

                                            if len(data4) > 0:

                                                x4 = data4[0]['left']
                                                y4 = data4[0]['top']
                                                w4 = data4[0]['width']
                                                h4 = data4[0]['height']

                                                if (len(word_arr[5]) > 0):
                                                    data5 = self.matched_array(word_arr[5], w1_top, x4, w4)

                                                    if len(data5) > 0:

                                                        x5 = data5[0]['left']
                                                        y5 = data5[0]['top']
                                                        w5 = data5[0]['width']
                                                        h5 = data5[0]['height']

                                                        xmin = x
                                                        ymin = y
                                                        wmin = w + w11 + w2 + w3 + w4 + w5 + 10
                                                        hmin = (min(h, h1, h2, h3, h4, h5))

                                                        text_val = str(w1['text']) + " " + str(
                                                            data[0]['text']) + " " + str(data2[0]['text']) + " " + str(
                                                            data3[0]['text']) + " " + str(data4[0]['text']) + " " + str(
                                                            data5[0]['text'])
                                                        nearest = self.nearest_dist_key_pair(x, y, cordinates_name,
                                                                                             template_name)

                                                        if (nearest):
                                                            parts = nearest.split('_')
                                                            val_data = parts[0].split(':')
                                                            info_arr = {
                                                                'label': "Keyword",
                                                                'text': text_val,
                                                                'x': val_data[0],
                                                                'y': val_data[1],
                                                                'w': int(val_data[2]) - int(val_data[0]),
                                                                'h': int(val_data[3]) - int(val_data[1]),
                                                                'key_name': str(key_name),
                                                                'cordinates_name': str(cordinates_name)
                                                            }
                                                            final_json_data.append(info_arr)
                                                            # print(w1)
                                                            # print(data[0])
                                                            # print(data2[0])
                                                            # print(data3[0])

                                                            val_arr = self.value_array_key_pair(nearest, image,
                                                                                                template_name)

                                                            value_json_data.append(val_arr)

                                                            final_array = {
                                                                'key': info_arr,
                                                                'value': val_arr
                                                            }

        elif word_length == 7:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)

                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        if (len(word_arr[4]) > 0):
                                            data4 = self.matched_array(word_arr[4], w1_top, x3, w3)

                                            if len(data4) > 0:

                                                x4 = data4[0]['left']
                                                y4 = data4[0]['top']
                                                w4 = data4[0]['width']
                                                h4 = data4[0]['height']

                                                if (len(word_arr[5]) > 0):
                                                    data5 = self.matched_array(word_arr[5], w1_top, x4, w4)

                                                    if len(data5) > 0:

                                                        x5 = data5[0]['left']
                                                        y5 = data5[0]['top']
                                                        w5 = data5[0]['width']
                                                        h5 = data5[0]['height']

                                                        if (len(word_arr[6]) > 0):
                                                            data6 = self.matched_array(word_arr[6], w1_top, x5, w5)

                                                            if len(data6) > 0:

                                                                x6 = data6[0]['left']
                                                                y6 = data6[0]['top']
                                                                w6 = data6[0]['width']
                                                                h6 = data6[0]['height']

                                                                xmin = x
                                                                ymin = y
                                                                wmin = w + w11 + w2 + w3 + w4 + w5 + w6 + 10
                                                                # make changes from min function to max function
                                                                hmin = (min(h, h1, h2, h3, h4, h5, h6))

                                                                # print(f"y-->{y}-->y1-->{y1}-->y2-->{y2}-->y3-->{y3}-->y4-->{y4}-->y5-->{y5}-->y6-->{y6}")
                                                                nearest = self.nearest_dist_key_pair(x, y,
                                                                                                     cordinates_name,
                                                                                                     template_name)

                                                                if (nearest):
                                                                    text_val = str(w1['text']) + " " + str(
                                                                        data[0]['text']) + " " + str(
                                                                        data2[0]['text']) + " " + str(
                                                                        data3[0]['text']) + " " + str(
                                                                        data4[0]['text']) + " " + str(
                                                                        data5[0]['text'] + " " + str(data6[0]['text']))
                                                                    parts = nearest.split('_')
                                                                    val_data = parts[0].split(':')

                                                                    info_arr = {
                                                                        'label': "Keyword",
                                                                        'text': text_val,
                                                                        'x': val_data[0],
                                                                        'y': val_data[1],
                                                                        'w': int(val_data[2]) - int(val_data[0]),
                                                                        'h': int(val_data[3]) - int(val_data[1]),
                                                                        'key_name': str(key_name),
                                                                        'cordinates_name': str(cordinates_name)
                                                                    }
                                                                    final_json_data.append(info_arr)
                                                                    # print(w1)
                                                                    # print(data[0])
                                                                    # print(data2[0])
                                                                    # print(data3[0])

                                                                    # print(x,"<------------>",y,"=====",hmin,"<------------>",wmin)
                                                                    val_arr = self.value_array_key_pair(nearest, image,
                                                                                                        template_name)

                                                                    value_json_data.append(val_arr)

                                                                    final_array = {
                                                                        'key': info_arr,
                                                                        'value': val_arr
                                                                    }

        elif word_length == 8:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)

                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        if (len(word_arr[4]) > 0):
                                            data4 = self.matched_array(word_arr[4], w1_top, x3, w3)

                                            if len(data4) > 0:

                                                x4 = data4[0]['left']
                                                y4 = data4[0]['top']
                                                w4 = data4[0]['width']
                                                h4 = data4[0]['height']

                                                if (len(word_arr[5]) > 0):
                                                    data5 = self.matched_array(word_arr[5], w1_top, x4, w4)

                                                    if len(data5) > 0:

                                                        x5 = data5[0]['left']
                                                        y5 = data5[0]['top']
                                                        w5 = data5[0]['width']
                                                        h5 = data5[0]['height']

                                                        if (len(word_arr[6]) > 0):
                                                            data6 = self.matched_array(word_arr[6], w1_top, x5, w5)

                                                            if len(data6) > 0:

                                                                x6 = data6[0]['left']
                                                                y6 = data6[0]['top']
                                                                w6 = data6[0]['width']
                                                                h6 = data6[0]['height']

                                                                if (len(word_arr[7]) > 0):
                                                                    data7 = self.matched_array(word_arr[7], w1_top, x6,
                                                                                               w6)

                                                                    if len(data7) > 0:

                                                                        x7 = data7[0]['left']
                                                                        y7 = data7[0]['top']
                                                                        w7 = data7[0]['width']
                                                                        h7 = data7[0]['height']

                                                                        xmin = x
                                                                        ymin = y
                                                                        wmin = w + w11 + w2 + w3 + w4 + w5 + w6 + w7 + 10
                                                                        # make changes from min function to max function
                                                                        hmin = (min(h, h1, h2, h3, h4, h5, h6, h7))

                                                                        nearest = self.nearest_dist_key_pair(x, y,
                                                                                                             cordinates_name,
                                                                                                             template_name)

                                                                        if (nearest):
                                                                            parts = nearest.split('_')
                                                                            val_data = parts[0].split(':')
                                                                            text_val = str(w1['text']) + " " + str(
                                                                                data[0]['text']) + " " + str(
                                                                                data2[0]['text']) + " " + str(
                                                                                data3[0]['text']) + " " + str(
                                                                                data4[0]['text']) + " " + str(
                                                                                data5[0]['text'] + " " + str(
                                                                                    data6[0]['text']) + " " + str(
                                                                                    data7[0]['text']))

                                                                            info_arr = {
                                                                                'label': "Keyword",
                                                                                'text': text_val,
                                                                                'x': val_data[0],
                                                                                'y': val_data[1],
                                                                                'w': int(val_data[2]) - int(
                                                                                    val_data[0]),
                                                                                'h': int(val_data[3]) - int(
                                                                                    val_data[1]),
                                                                                'key_name': str(key_name),
                                                                                'cordinates_name': str(cordinates_name)
                                                                            }
                                                                            final_json_data.append(info_arr)
                                                                            # print(w1)
                                                                            # print(data[0])
                                                                            # print(data2[0])
                                                                            # print(data3[0])

                                                                            val_arr = self.value_array_key_pair(nearest,
                                                                                                                image,
                                                                                                                template_name)

                                                                            value_json_data.append(val_arr)

                                                                            final_array = {
                                                                                'key': info_arr,
                                                                                'value': val_arr
                                                                            }

        elif word_length == 9:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)

                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        if (len(word_arr[4]) > 0):
                                            data4 = self.matched_array(word_arr[4], w1_top, x3, w3)

                                            if len(data4) > 0:

                                                x4 = data4[0]['left']
                                                y4 = data4[0]['top']
                                                w4 = data4[0]['width']
                                                h4 = data4[0]['height']

                                                if (len(word_arr[5]) > 0):
                                                    data5 = self.matched_array(word_arr[5], w1_top, x4, w4)

                                                    if len(data5) > 0:

                                                        x5 = data5[0]['left']
                                                        y5 = data5[0]['top']
                                                        w5 = data5[0]['width']
                                                        h5 = data5[0]['height']

                                                        if (len(word_arr[6]) > 0):
                                                            data6 = self.matched_array(word_arr[6], w1_top, x5, w5)

                                                            if len(data6) > 0:

                                                                x6 = data6[0]['left']
                                                                y6 = data6[0]['top']
                                                                w6 = data6[0]['width']
                                                                h6 = data6[0]['height']

                                                                if (len(word_arr[7]) > 0):
                                                                    data7 = self.matched_array(word_arr[7], w1_top, x6,
                                                                                               w6)

                                                                    if len(data7) > 0:

                                                                        x7 = data7[0]['left']
                                                                        y7 = data7[0]['top']
                                                                        w7 = data7[0]['width']
                                                                        h7 = data7[0]['height']

                                                                        if (len(word_arr[8]) > 0):
                                                                            data8 = self.matched_array(word_arr[8],
                                                                                                       w1_top, x7, w7)

                                                                            if len(data8) > 0:

                                                                                x8 = data8[0]['left']
                                                                                y8 = data8[0]['top']
                                                                                w8 = data8[0]['width']
                                                                                h8 = data8[0]['height']

                                                                                xmin = x
                                                                                ymin = y
                                                                                wmin = w + w11 + w2 + w3 + w4 + w5 + w6 + w7 + w8 + 10
                                                                                # make changes from min function to max function
                                                                                hmin = (
                                                                                    min(h, h1, h2, h3, h4, h5, h6, h7,
                                                                                        h8))

                                                                                nearest = self.nearest_dist_key_pair(x,
                                                                                                                     y,
                                                                                                                     cordinates_name,
                                                                                                                     template_name)

                                                                                if (nearest):
                                                                                    parts = nearest.split('_')
                                                                                    val_data = parts[0].split(':')
                                                                                    text_val = str(
                                                                                        w1['text']) + " " + str(
                                                                                        data[0]['text']) + " " + str(
                                                                                        data2[0]['text']) + " " + str(
                                                                                        data3[0]['text']) + " " + str(
                                                                                        data4[0]['text']) + " " + str(
                                                                                        data5[0]['text'] + " " + str(
                                                                                            data6[0][
                                                                                                'text']) + " " + str(
                                                                                            data7[0][
                                                                                                'text']) + " " + str(
                                                                                            data8[0]['text']))

                                                                                    info_arr = {
                                                                                        'label': "Keyword",
                                                                                        'text': text_val,
                                                                                        'x': val_data[0],
                                                                                        'y': val_data[1],
                                                                                        'w': int(val_data[2]) - int(
                                                                                            val_data[0]),
                                                                                        'h': int(val_data[3]) - int(
                                                                                            val_data[1]),
                                                                                        'key_name': str(key_name),
                                                                                        'cordinates_name': str(
                                                                                            cordinates_name)
                                                                                    }
                                                                                    final_json_data.append(info_arr)
                                                                                    # print(w1)
                                                                                    # print(data[0])
                                                                                    # print(data2[0])
                                                                                    # print(data3[0])

                                                                                    # print(x,"<------------>",y,"=====",hmin,"<------------>",wmin)
                                                                                    val_arr = self.value_array_key_pair(
                                                                                        nearest, image, template_name)

                                                                                    value_json_data.append(val_arr)

                                                                                    final_array = {
                                                                                        'key': info_arr,
                                                                                        'value': val_arr
                                                                                    }

        elif word_length == 10:
            for w1 in word_arr[0]:
                # print(w1['top'])
                w1_top = w1['top']
                x = w1['left']
                y = w1['top']
                w = w1['width']
                h = w1['height']

                # print(w1)
                if (len(word_arr[1]) > 0):
                    data = self.matched_array(word_arr[1], w1_top, x, w)

                    # print(data)
                    if len(data) > 0:
                        x1 = data[0]['left']
                        y1 = data[0]['top']
                        w11 = data[0]['width']
                        h1 = data[0]['height']
                        if (len(word_arr[2]) > 0):
                            data2 = self.matched_array(word_arr[2], w1_top, x1, w11)

                            if len(data2) > 0:

                                x2 = data2[0]['left']
                                y2 = data2[0]['top']
                                w2 = data2[0]['width']
                                h2 = data2[0]['height']

                                if (len(word_arr[3]) > 0):
                                    data3 = self.matched_array(word_arr[3], w1_top, x2, w2)

                                    if len(data3) > 0:

                                        x3 = data3[0]['left']
                                        y3 = data3[0]['top']
                                        w3 = data3[0]['width']
                                        h3 = data3[0]['height']

                                        if (len(word_arr[4]) > 0):
                                            data4 = self.matched_array(word_arr[4], w1_top, x3, w3)

                                            if len(data4) > 0:

                                                x4 = data4[0]['left']
                                                y4 = data4[0]['top']
                                                w4 = data4[0]['width']
                                                h4 = data4[0]['height']

                                                if (len(word_arr[5]) > 0):
                                                    data5 = self.matched_array(word_arr[5], w1_top, x4, w4)

                                                    if len(data5) > 0:

                                                        x5 = data5[0]['left']
                                                        y5 = data5[0]['top']
                                                        w5 = data5[0]['width']
                                                        h5 = data5[0]['height']

                                                        if (len(word_arr[6]) > 0):
                                                            data6 = self.matched_array(word_arr[6], w1_top, x5, w5)

                                                            if len(data6) > 0:

                                                                x6 = data6[0]['left']
                                                                y6 = data6[0]['top']
                                                                w6 = data6[0]['width']
                                                                h6 = data6[0]['height']

                                                                if (len(word_arr[7]) > 0):
                                                                    data7 = self.matched_array(word_arr[7], w1_top, x6,
                                                                                               w6)

                                                                    if len(data7) > 0:

                                                                        x7 = data7[0]['left']
                                                                        y7 = data7[0]['top']
                                                                        w7 = data7[0]['width']
                                                                        h7 = data7[0]['height']

                                                                        if (len(word_arr[8]) > 0):
                                                                            data8 = self.matched_array(word_arr[8],
                                                                                                       w1_top, x7, w7)

                                                                            if len(data8) > 0:

                                                                                x8 = data8[0]['left']
                                                                                y8 = data8[0]['top']
                                                                                w8 = data8[0]['width']
                                                                                h8 = data8[0]['height']

                                                                                if (len(word_arr[9]) > 0):
                                                                                    data9 = self.matched_array(
                                                                                        word_arr[9], w1_top, x8, w8)

                                                                                    if len(data9) > 0:

                                                                                        x9 = data9[0]['left']
                                                                                        y9 = data9[0]['top']
                                                                                        w9 = data9[0]['width']
                                                                                        h9 = data9[0]['height']

                                                                                        xmin = x
                                                                                        ymin = y
                                                                                        wmin = w + w11 + w2 + w3 + w4 + w5 + w6 + w7 + w8 + w9 + 10
                                                                                        # make changes from min function to max function
                                                                                        hmin = (
                                                                                            min(h, h1, h2, h3, h4, h5,
                                                                                                h6, h7, h8, h9))

                                                                                        nearest = self.nearest_dist_key_pair(
                                                                                            x, y, cordinates_name,
                                                                                            template_name)

                                                                                        if (nearest):
                                                                                            text_val = str(
                                                                                                w1['text']) + " " + str(
                                                                                                data[0][
                                                                                                    'text']) + " " + str(
                                                                                                data2[0][
                                                                                                    'text']) + " " + str(
                                                                                                data3[0][
                                                                                                    'text']) + " " + str(
                                                                                                data4[0][
                                                                                                    'text']) + " " + str(
                                                                                                data5[0][
                                                                                                    'text'] + " " + str(
                                                                                                    data6[0][
                                                                                                        'text']) + " " + str(
                                                                                                    data7[0][
                                                                                                        'text']) + " " + str(
                                                                                                    data8[0][
                                                                                                        'text']) + " " + str(
                                                                                                    data9[0]['text']))
                                                                                            parts = nearest.split('_')
                                                                                            val_data = parts[0].split(
                                                                                                ':')
                                                                                            info_arr = {
                                                                                                'label': "Keyword",
                                                                                                'text': text_val,
                                                                                                'x': val_data[0],
                                                                                                'y': val_data[1],
                                                                                                'w': int(
                                                                                                    val_data[2]) - int(
                                                                                                    val_data[0]),
                                                                                                'h': int(
                                                                                                    val_data[3]) - int(
                                                                                                    val_data[1]),
                                                                                                'key_name': str(
                                                                                                    key_name),
                                                                                                'cordinates_name': str(
                                                                                                    cordinates_name)
                                                                                            }
                                                                                            final_json_data.append(
                                                                                                info_arr)
                                                                                            # print(w1)
                                                                                            # print(data[0])
                                                                                            # print(data2[0])
                                                                                            # print(data3[0])

                                                                                            # print(x,"<------------>",y,"=====",hmin,"<------------>",wmin)
                                                                                            val_arr = self.value_array_key_pair(
                                                                                                nearest, image,
                                                                                                template_name)

                                                                                            value_json_data.append(
                                                                                                val_arr)

                                                                                            final_array = {
                                                                                                'key': info_arr,
                                                                                                'value': val_arr
                                                                                            }

        else:

            final_array = {
                'key': "Use Manual Approch",
                'value': "Use Manual Approch"
            }

        # temp_docx_path = os.path.dirname(__file__) + "/plot_images"

        # if not os.path.exists(temp_docx_path):
        #     os.makedirs(temp_docx_path)

        # temp_docx_path = temp_docx_path + "/7.png"

        # cv2.imwrite(temp_docx_path, image)

        return final_array

    def read_key_file(self, template_name):
        try:
            # read by default 1st sheet of an excel file
            if template_name == "MedWatch":
                csv_file_path = os.path.dirname(__file__) + "/key_files/medwatch_key_file.xlsx"
            elif template_name == "CIOMS":
                csv_file_path = os.path.dirname(__file__) + "/key_files/cimos_key_file.xlsx"
            elif template_name == "IRMS":
                csv_file_path = os.path.dirname(__file__) + "/key_files/irms_key_file.xlsx"

            dataframe = pd.read_excel(csv_file_path)
            key_list = []
            key_cord = []
            for index, row in dataframe.iterrows():
                key_name = row['keywords']
                cordints = row['cordinates']
                key_list.append((list(key_name.split(" "))))
                key_cord.append(cordints)

            return {"key": key_list, "cord": key_cord}

        except Exception as e:
            print(e)

    def extract_second_page(self, file_id, page_no, template_name,tenant):

        """Key declarion for second page"""

        start_keys = ["B5. EVENT DESCRIPTION", "B.5. Describe Event or Problem [continued]", "B6. LABORATORY DATA",
                      "B.6. Relevant Tests/Laboratory Data", "B7. OTHER RELEVANT HISTORY",
                      "B.7. Other Relevant History, Including Preexisting Medical Conditions [continued]",
                      "C.1.#1. Name [continued]", "C.2.#1. Dose, Frequency & Route Used [continued]",
                      "C.3.#1. Therapy Dates [continued]", "C.1.#2 Name [continued]",
                      "C.2.#2. Dose, Frequency & Route Used [continued]", "C.3.#2. Therapy Dates",
                      "C4. DIAGNOSIS FOR USE", "C10. CONCOMITANT MEDICAL PRODUCTS", "G8. ADVERSE EVENT TERMS",
                      "G.8. Adverse Event Term(s) [continued]"]
        end_keys = ["B6. LABORATORY DATA", "B.6. Relevant Tests/Laboratory Data", "B.7. Other Relevant History",
                    "B7. OTHER RELEVANT HISTORY", "C.1.#1. Name", "C.2.#1. Dose, Frequency & Route Used",
                    "C.3.#1. Therapy Dates", "C.1.#2 Name", "C.2.#2. Dose, Frequency & Route Used",
                    "C.3.#2. Therapy Dates", "C4. DIAGNOSIS FOR USE", "C10. CONCOMITANT MEDICAL PRODUCTS",
                    "G8. ADVERSE EVENT TERMS", "G.8. Adverse Event Term(s)"]
        co_ordinates_key = ["describe_event_or_problem", "describe_event_or_problem", "relevant_dates",
                            "relevant_dates", "relevant_dates", "relevant_dates", "suspect_1_name",
                            "suspect_1_dose_used", "suspect_1_therapy_start_date", "suspect_1_name",
                            "suspect_1_dose_used", "suspect_1_therapy_start_date", "suspect_1_diagnosis_for_use",
                            "concomitant_medical", "adverse_event_term(s)", "adverse_event_term(s)"]

        file_data = File.objects.using(tenant).filter(id_file=file_id)
        file_arr = []
        final_array = []
        filter_final_data = []

        for file in file_data:

            page_count = int(file.pdf_page_count)
            data = ""

            for i in range(1, page_count + 1):
                if i == 1:
                    continue  # Skip the first number (i = 1)
                # print("Number", i)

                if file.file_format == 'application/pdf':
                    file_name = 'uploads/'+tenant+'/'+ str(file_id) + '/page_' + str(i) + '.png'
                elif file.file_format == 'image/jpeg' or file.file_format == 'image/png':
                    file_name = file.file_name
                file_arr.append(file_name)

                with default_storage.open(str(file_name), mode='rb') as img_buffer:

                    img_array = np.asarray(bytearray(img_buffer.read()), dtype=np.uint8)
                    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                    # Convert the image to grayscale
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                    # print(gray.shape[0])

                    # image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    # Crop the image from the beginning to a height of 150 pixels
                    cropped_image = gray[400:, :]
                    # cv2.imwrite('crop_problrm_detecttable_med_30_10_23_k3_v3.jpg',cropped_image)

                    # Apply thresholding
                    _, binary_image = cv2.threshold(cropped_image, 200, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                    # cv2.imwrite('binary_problrm_detecttable_med_30_10_23_k3_v3.jpg',binary_image)

                    # Define the number of rows to skip from the top
                    # rows_to_skip = 150  # Adjust this number as needed

                    # # Remove the specified number of rows from the top
                    # binary_image = binary_image[rows_to_skip:, :]

                    pil_img = Image.fromarray(binary_image)

                    # Use Tesseract to get OCR data from the image
                    data += pytesseract.image_to_string(pil_img)

                    # Check if any contours were found
                    if not contours:
                        print("No contours found in the image.")
                        return None

                    # Assuming the largest contour is the border
                    c = max(contours, key=cv2.contourArea)
                    x, y, w, h = cv2.boundingRect(c)

                    # print(x, y, w, h)

                    # crop_img = gray[y:(h), x:(w)]

                    # image_data = pytesseract.image_to_string(crop_img)

                    # print(image_data)

                    # Crop out the header
                    # cropped_image = gray.crop((0, 150, image.width, image.height))
                    # # Extract text from the cropped image
                    # text = pytesseract.image_to_string(cropped_image)

            # print(data)

            extracted_texts = {}
            # Search for the start keys in the combined text
            for start_key in start_keys:
                # Using regex, look for the start key and capture everything after it
                # until one of the end keys is encountered or until the end of the text.
                end_key_pattern = '|'.join(map(re.escape, end_keys))
                match = re.search(re.escape(start_key) + r'([\s\S]+?)(?=' + end_key_pattern + r'|$)', data)
                if match:
                    extracted_texts[start_key] = match.group(1).strip()

            # print(extracted_texts)

            # print("*",*20)

            for key, text in extracted_texts.items():
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                # print(f"'{key}':", lines)

                ignore_words = ["[continued]", "Continuing", "[continued]\n"]

                # Create a regular expression pattern to match the ignore words
                ignore_pattern = r'\b(?:' + '|'.join(map(re.escape, ignore_words)) + r')\b'

                # Use re.sub to replace the matched words with an empty string
                cleaned_text = re.sub(ignore_pattern, '', text, flags=re.IGNORECASE)

                final = {
                    'key': key,
                    'value': cleaned_text
                }
                # print("----------")

                final_array.append(final)
            # print(final_array)

            for index, entry in enumerate(final_array):
                # print(index,"-----",entry["key"])
                for i, start_key in enumerate(start_keys):
                    if entry["key"] == start_key:
                        # print(i)
                        # print(i,"-------",co_ordinates_key[i])
                        value = {
                            'key': start_key,
                            'value': entry["value"],
                            'co_ord': co_ordinates_key[i]
                        }
                        filter_final_data.append(value)
                    # else:
                    #     print("-1")

            task = {
                'data': filter_final_data
            }
            json_string = json.dumps(task, default=self.np_encoder)

            with open('second_page_medwatch_2.json', mode='w') as f:
                f.write(json_string)

        return json_string

