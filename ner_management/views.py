from django.shortcuts import render
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Q, F, Func, Value, CharField, OuterRef, Subquery
from django.db.models.functions import (
    Concat,
    ExtractDay, ExtractYear, ExtractMonth, ExtractHour, ExtractMinute, ExtractSecond
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework import status
import pytesseract
from pytesseract import Output, TesseractError
import pdf2image
from PIL import Image, ImageFilter
from bs4 import BeautifulSoup
import re
import os
import io
import random
import unidecode
from autocorrect import Speller
import numpy as np
import spacy as sp
from spacy.tokens import DocBin
from spacy.training import Example
from spacy.cli.train import train
from spacy.cli.init_config import init_config_cli, Optimizations
from pathlib import Path
from spacy.util import minibatch, compounding, filter_spans
import warnings
from tqdm import tqdm
from datetime import datetime
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
import mimetypes

from .dictionary import Dictionary
from .models import NERTrainingFiles, TrainingStatus
from .serializers import NERTrainingFilesListSerializer, NERTrainingFilesSerializer
from configuration.aws import S3Bucket
import shutil
from data_ingestion import settings
from file_management.models import File
from R2xml.views import R2xmlLitrature
from .NerRelationExtractor import NerRelationExtractor
from authorization.views import VerifyTenant


class TrainedModel(S3Bucket):
    def load_model(self, text=""):
        try:
            if text != "":
                nlp = sp.load(os.path.join(settings.STATICFILES_LOCAL,
                                           "data/models/output/ner/training_gpu_ner_05-12-2023/model-best"))
                doc = nlp(text)
                return (doc)
            return None
        except Exception as e:
            print(e)

    def get_ner(self, doc=None):
        try:
            result_json = dict()
            json_result = []
            if doc is not None:
                for entity in doc.ents:
                    category = entity.label_
                    if category in result_json:
                        if isinstance(result_json[category], str):
                            cat = list()
                            cat.append(result_json[category])
                            result_json[category] = cat
                        result_json[category].append(entity.text)
                        result_json[category] = list(set(result_json[category]))
                    else:
                        result_json.update({entity.label_: entity.text})
            for key in result_json.keys():
                json_result.append({"key": key, "value": result_json[key]})

            return json_result
        except Exception as e:
            print(e)


class ReadFile(TrainedModel, Dictionary, S3Bucket, R2xmlLitrature):
    def post(self, request):
        try:
            data = json.loads(request.body)
            file_id = data['file_id']
            call_type = data['type']
            tenant = VerifyTenant(request.META['HTTP_TENANT_CODE']).GetTenant()
            file_db_data = File.objects.using(tenant).filter(id_file=file_id)

            if (len(file_db_data) > 0):
                for file in file_db_data:
                    text = ""
                    if str(file.file_name).endswith(".pdf"):
                        print("file", str(file.file_name))
                        file_data = self.load_s3bucket_file(str(file.file_name))
                        print(file_data)
                        # images = tqdm(pdf2image.convert_from_bytes(file_data.read(), 500, poppler_path = r'C:\Program Files\poppler-0.68.0\bin'))
                        images = pdf2image.convert_from_bytes(file_data.read(), fmt="png", grayscale=True,
                                                              transparent=True)

                        for i in tqdm(range(len(images))):
                            pil_im = images[i]
                            pil_im.filter(ImageFilter.SHARPEN)
                            ocr_dict = pytesseract.image_to_data(pil_im, lang='eng', output_type=Output.DICT)
                            # ocr_dict now holds all the OCR info including text and location on the image
                            text += " ".join(ocr_dict['text'])
                            # ocr_dict = pytesseract.image_to_string(pil_im)
                            # text += ocr_dict


                    elif str(file.file_name).endswith(".png") or str(file.file_name).endswith(".jpg") or str(
                            file.file_name).endswith(".jpeg"):
                        with default_storage.open(str(file.file_name), mode='rb') as image:
                            mimetype, encoding = mimetypes.guess_type(image.name)
                            img_data = self.file_memory(
                                image, "image_file", mimetype
                            )
                            image = Image.open(img_data)
                            # image.filter(ImageFilter.SHARPEN)
                            ocr_dict = pytesseract.image_to_data(image, lang='eng', output_type=Output.DICT)

                            text += " ".join(ocr_dict['text'])

                    elif str(file.file_name).endswith(".txt"):
                        file_data = self.load_s3bucket_file(str(file.file_name))
                        text = file_data.read()
                    else:
                        return Response({"data": "file format is wrong", "result": ""}, status=status.HTTP_200_OK)

                    # print(text.replace('\n',' '))
                    # exit(1)
                    # text = open('input/current_file1.txt', 'r', encoding="utf8").read()
                    text = self.text_preprocessing(text)

                    # current_file = open('current_file_03_11_2023.txt', 'w')
                    # print(text, file=current_file)
                    # current_file.close()
                    # exit(1)
                    # current_file = open('input/test_input.txt', 'r', encoding="utf8").read()
                    doc = self.load_model(text)
                    result_json = self.get_ner(doc)
                    # print(result_json)
                    print("heree")
                    result_relation = NerRelationExtractor(text).get_ner_relations()
                    print("result_relation:",result_relation)
                    # print("**************************************")
                    if call_type == 'xml_download':
                        print(data)
                        sender = data['sender']
                        receiver = data['receiver']
                        xml_type = data['xmlType']
                        xml_resp = self.downloadXML(result_json, result_relation, "data_ingestion", sender, receiver,
                                                    xml_type)
                        return Response({"error": 0, "data": xml_resp["data"]}, status=status.HTTP_200_OK)
                    elif call_type == 'json':
                        return Response({"text": str(doc), "annotations": result_json, "error": 0},
                                        status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": 1, "msg": str(e)}, status=status.HTTP_200_OK)

    def file_memory(self, file_obj, field_name, content_type):
        return InMemoryUploadedFile(
            file=file_obj,
            field_name=field_name,
            name=file_obj.name,
            content_type=content_type,
            size=file_obj.size,
            charset=None
        )

    def text_preprocessing(self, text=""):
        # text = self.expand_contractions(text)
        text = self.strip_html_tags(text)
        text = self.remove_whitespace(text)
        text = self.accented_characters_removal(text)
        return text

    def strip_html_tags(self, text):
        # Initiating BeautifulSoup object soup.
        soup = BeautifulSoup(text, "html.parser")
        # Get all the text other than html tags.
        stripped_text = soup.get_text(separator=" ")
        return stripped_text

    def remove_whitespace(self, text):
        # text=text.replace('\n',' ')
        pattern = re.compile(r'\s+')
        Without_whitespace = re.sub(pattern, ' ', text)
        # There are some instances where there is no space after '?' & ')', 
        # So I am replacing these with one space so that It will not consider two words as one token.
        text = Without_whitespace.replace('?', ' ? ').replace(')', ') ').replace('\r\n', ' ').replace('\n', ' ')
        text = text.replace('-', ' ').replace('- ', '').replace(' -', '')
        return text

    def accented_characters_removal(self, text):
        # this is a docstring
        """
        The function will remove accented characters from the 
        text contained within the Dataset.
        
        arguments:
            input_text: "text" of type "String". 
                        
        return:
            value: "text" with removed accented characters.
            
        Example:
        Input : Málaga, àéêöhello
        Output : Malaga, aeeohello    
            
        """
        # Remove accented characters from text using unidecode.
        # Unidecode() - It takes unicode data & tries to represent it to ASCII characters. 
        text = unidecode.unidecode(text)
        return text

    def expand_contractions(self, text=""):
        contractions_dict = self.get_contraction_dictionary()
        print(contractions_dict)
        # Regular expression for finding contractions
        contractions_re = re.compile('(%s)' % '|'.join(contractions_dict.keys()))

        def replace(match):
            return contractions_dict[match.group(0)]

        return contractions_re.sub(replace, text)
        # # Tokenizing text into tokens.
        # list_Of_tokens = text.split(' ')

        # # Check whether Word is in lidt_Of_tokens or not.
        # for Word in list_Of_tokens: 
        #     # Check whether found word is in dictionary "Contraction Map" or not as a key. 
        #     if Word in CONTRACTION_MAP: 
        #             # If Word is present in both dictionary & list_Of_tokens, replace that word with the key value.
        #             list_Of_tokens = [item.replace(Word, CONTRACTION_MAP[Word]) for item in list_Of_tokens]

        # # Converting list of tokens to String.
        # String_Of_tokens = ' '.join(str(e) for e in list_Of_tokens) 
        # return String_Of_tokens

    def removing_special_characters(self, text):
        """Removing all the special characters except the one that is passed within 
        the regex to match, as they have imp meaning in the text provided.
    
        
        arguments:
            input_text: "text" of type "String".
            
        return:
            value: Text with removed special characters that don't require.
            
        Example: 
        Input : Hello, K-a-j-a-l. Thi*s is $100.05 : the payment that you will recieve! (Is this okay?) 
        Output :  Hello, Kajal. This is $100.05 : the payment that you will recieve! Is this okay?
        
        """
        # The formatted text after removing not necessary punctuations.
        Formatted_Text = re.sub(r"[^a-zA-Z0-9:$-,%.?!]+", ' ', text)
        # In the above regex expression,I am providing necessary set of punctuations that are frequent in this particular dataset.
        return Formatted_Text

    def spelling_correction(self, text):
        ''' 
        This function will correct spellings.
        
        arguments:
            input_text: "text" of type "String".
            
        return:
            value: Text after corrected spellings.
            
        Example: 
        Input : This is Oberois from Dlhi who came heree to studdy.
        Output : This is Oberoi from Delhi who came here to study.
        
        
        '''
        # Check for spellings in English language
        spell = Speller(lang='en')
        Corrected_text = spell(text)
        return Corrected_text

    def generate_r2xml(self, json):
        pass


class TestModel(TrainedModel):
    def get(self, request):
        self.check_testing_files("data/test")
        data = self.load_testing_files("data/test")
        result_json = list()
        for i, text in enumerate(data):
            text = self.strip_html_tags(text)
            # text = self.remove_whitespace(text)
            doc = self.load_model(text)
            ner = self.get_ner(doc)

            html = sp.displacy.render(doc, style='ent', page=True, jupyter=False)
            output_file = Path(staticfiles_storage.path("output_html/ent_output_" + str(i) + ".html"))
            output_file.open('w', encoding='utf-8').write(html)

            result_json.append({"text": text, "entities": ner})

        return Response({"data": result_json}, status=status.HTTP_200_OK)

    def strip_html_tags(self, text):
        # Initiating BeautifulSoup object soup.
        soup = BeautifulSoup(text, "html.parser")
        # Get all the text other than html tags.
        stripped_text = soup.get_text(separator=" ")
        return stripped_text

    def remove_whitespace(self, text):
        pattern = re.compile(r'\s+')
        Without_whitespace = re.sub(pattern, ' ', text)
        # There are some instances where there is no space after '?' & ')', 
        # So I am replacing these with one space so that It will not consider two words as one token.
        text = Without_whitespace.replace('?', ' ? ').replace(')', ') ').replace('\r\n', ' ').replace('\n', ' ')
        return text

    def check_testing_files(self, folder):
        for x in os.listdir(staticfiles_storage.path(folder)):
            if x.endswith(".json"):
                fname = x.split(".json")[0]
                if len(fname) > 100:
                    name = (fname[:90]).strip().replace("(", "").replace(")", "").replace(" ", "_")
                    filename = f"{staticfiles_storage.path(folder)}/{name}.json"
                    os.rename(Path(f"{staticfiles_storage.path(folder)}/{x}"), Path(filename))

    def load_data(self, file):
        with open(file, "r", encoding="utf-8") as f:
            data = f.read()
            f.close()
        return (data)

    def load_testing_files(self, folder_url):
        data = []
        for x in os.listdir(staticfiles_storage.path(folder_url)):
            data.append(self.load_data(staticfiles_storage.path(folder_url + "/" + x)))
        return (data)


class TrainCreateModel(S3Bucket):
    def get(self, request):
        try:
            tStatus = TrainingStatus.objects.order_by("-ts_id")
            if len(tStatus) == 0:
                trn = TrainingStatus(training_status=True)
                trn.save()
                can_process = True
            elif len(tStatus) > 0:
                if tStatus[0].training_status == False:
                    can_process = True
                else:
                    can_process = False
            else:
                can_process = False

            if can_process == True:
                DATA = self.load_training_files()
                TRAINING_DATA = []
                for d in DATA:
                    for annotation in d['annotations']:
                        TRAINING_DATA.append(annotation)
                self.train_ner(TRAINING_DATA, 200, None, 'data/models/', 'en_cust_ner_model')
                TrainingStatus.objects.all().delete()
                return Response(
                    {"data": "completed_train_creared_model"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"data": "Another Training Process is in progress. Please train later"},
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            print(str(e))
            return Response(
                {"data": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def load_training_files(self):
        data = []
        qs = NERTrainingFiles.objects.all()
        for file in qs:
            file_loc = str(file.file_name)
            if file_loc.endswith(".json"):
                df = (self.load_s3bucket_file(file_loc)).read().decode()
                data.append(json.loads(df))
        return (data)

    def train_ner(self, TRAINING_DATA, iterations, model=None, output_dir=None, model_name=None):
        if model is not None:
            nlp = sp.load(model)
        else:
            nlp = sp.blank("en")
            nlp.add_pipe("sentencizer")

        if 'ner' not in nlp.pipe_names:
            # source_nlp = sp.load("en_core_web_lg")
            # ner = nlp.add_pipe("ner", source=source_nlp)
            ner = nlp.add_pipe("ner", last=True)
        else:
            ner = nlp.get_pipe('ner')

        for _, annotations in TRAINING_DATA:
            for ent in annotations.get('entities'):
                ner.add_label(ent[2])

        # if model is None:
        #     optimizer = nlp.begin_training()
        # else:
        #     # optimizer = nlp.create_optimizer()
        # nlp.resume_training()

        example = []
        pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
        unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
        with nlp.disable_pipes(*unaffected_pipes), warnings.catch_warnings():
            # show warnings for misaligned entity spans once
            warnings.filterwarnings("once", category=UserWarning, module='spacy')
            examples = []

            for text, annots in TRAINING_DATA:
                if model is not None:
                    doc = nlp(text)
                    entities = [(e.start_char, e.end_char, e.label_) for e in doc.ents]
                    examples.append(Example.from_dict(doc, {"entities": entities}))
                examples.append(Example.from_dict(nlp.make_doc(text), annots))

            if model is None:
                nlp.initialize(lambda: examples)
            else:
                optimizer = nlp.resume_training()
                nlp.rehearse(examples, sgd=optimizer)

            for itn in tqdm(range(iterations)):
                random.shuffle(examples)
                # batch up the examples using spaCy's minibatch
                batches = minibatch(examples, size=compounding(1.0, 4.0, 1.001))
                for batch in batches:
                    nlp.update(batch, drop=0.2)
        if output_dir is not None:
            # output_dir = Path(staticfiles_storage.url(output_dir))
            static_dir = settings.STATICFILES_LOCAL
            model_path = Path(os.path.join(static_dir, output_dir))
            if not model_path.exists():
                model_path.mkdir()
            nlp.to_disk(os.path.join(model_path, model_name))
            # shutil.make_archive(model_path, "gztar", model_path)
            # shutil.rmtree(model_path)
            # self.delete_s3bucket_file("{}{}.tar.gz".format(output_dir, model_name))
            # self.upload_file_to_s3bucket("{}{}.tar.gz".format(output_dir, model_name), Path(os.path.join(static_dir, "{}{}".format(model_name, '.tar.gz'))))
            # os.remove(Path(os.path.join(static_dir, "{}{}".format(model_name, '.tar.gz'))))
            # self.unzip_file("{}{}.tar.gz".format(output_dir, model_name), "{}{}".format(output_dir, model_name))
            # self.delete_s3bucket_file("{}{}.tar.gz".format(output_dir, model_name))


class IntialTraining(APIView):
    def get(self, request):
        self.create_config_file()
        training_file = staticfiles_storage.path('training/data/ner_training.json')
        TRAIN_DATA = self.load_data(training_file)
        random.shuffle(TRAIN_DATA)
        self.create_spacy_training(TRAIN_DATA, "en_core_web_lg")
        self.train_spacy()
        return Response(
            {"data": "Training completed and 'en_cust_ner_model' created successfully"},
            status=status.HTTP_200_OK
        )

    def create_config_file(self):
        try:
            if not Path(staticfiles_storage.path("training/config/config.cfg")).exists():
                with open(staticfiles_storage.path("config.cfg"), "a+") as f:
                    f.close()
            init_config_cli(
                output_file=Path(staticfiles_storage.path("training/config/config.cfg")),
                lang="en",
                pipeline="ner",
                optimize=Optimizations.accuracy,
                gpu=False,
                pretraining=True,
                force_overwrite=True
            )
        except Exception as e:
            print(e)

    def load_data(self, file):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return (data)

    def create_spacy_training(self, TRAINING_DATA, model=None):
        if model is not None:
            nlp = sp.load(model)
        else:
            nlp = sp.blank("en")

        if 'ner' not in nlp.pipe_names:
            nlp.add_pipe("ner")

        ner = nlp.get_pipe('ner')

        for _, annotations in TRAINING_DATA:
            for ent in annotations.get('entities'):
                ner.add_label(ent[2])

        db = DocBin()
        for text, annotations in TRAINING_DATA:
            doc = nlp.make_doc(text)
            ents = []
            for start, end, label in annotations["entities"]:
                span = doc.char_span(start, end, label=label, alignment_mode="contract")
                if span is None:
                    print("Skipping entity")
                else:
                    ents.append(span)
            doc.ents = ents
            db.add(doc)
        db.to_disk(staticfiles_storage.path("training/data/training.spacy"))

    def train_spacy(self):
        train(
            staticfiles_storage.path("training/config/config.cfg"),
            output_path=staticfiles_storage.path("model/output"),
            overrides={
                "paths.train": staticfiles_storage.path("training/data/training.spacy"),
                "paths.dev": staticfiles_storage.path("training/data/training.spacy")
            }
        )


class TrainingFiles(S3Bucket):
    def get(self, request, perPage, page):
        data = []
        try:
            filter_by = data['filter_by']
        except Exception:
            filter_by = {}
        order_column = 'file_id'

        if "order_by" in data:
            order_column = data['order_by']

        sort_order = 'desc'  # data['sort_order']
        if sort_order == 'desc':
            order_column = '-' + order_column

        start_index = (page - 1) * perPage
        page_size = perPage * page
        queryset = (
            NERTrainingFiles
            .objects
            .annotate(
                created_date_time=Concat(
                    ExtractDay('created_datetime'), Value('-'),
                    ExtractMonth('created_datetime'), Value('-'),
                    ExtractYear('created_datetime'), Value(' '),
                    ExtractHour('created_datetime'), Value(':'),
                    ExtractMinute('created_datetime'), Value(':'),
                    ExtractSecond('created_datetime'),
                    output_field=CharField()
                )
            )
            .filter(**filter_by)
            .order_by(order_column)
        )
        result_records = NERTrainingFilesListSerializer(queryset[start_index: page_size], many=True).data
        response_data = {
            "status_code": 200,
            "error": 0,
            "data": result_records,
            "total": len(queryset)
        }

        return Response(
            response_data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        return Response(
            {"data": []},
            status=status.HTTP_200_OK
        )

    def delete(self, request, perPage, page):
        data = json.loads(request.body)
        resp = ""
        for d in data:
            db_file = NERTrainingFiles.objects.filter(file_id=d)
            if len(db_file) > 0:
                for df in db_file:
                    try:
                        self.delete_s3bucket_file(str(df.file_name))
                        df.delete()
                        resp = "deleted"
                    except Exception as e:
                        resp = str(e)
        return Response(
            {"data": resp}, status=status.HTTP_200_OK
        )


class ViewTrainingFile(S3Bucket):
    def get(self, request, file_id):
        file = NERTrainingFiles.objects.filter(file_id=file_id)
        data = []
        if len(file) > 0:
            for f in file:
                if str(f.file_name).endswith(".json"):
                    f_data = json.loads(self.load_s3bucket_file(str(f.file_name)).read().decode())
                    TRAINING_DATA = []
                    for annotation in f_data['annotations']:
                        TRAINING_DATA.append(annotation)
                    data = self.create_data(TRAINING_DATA)
        return Response(
            {"data": data},
            status=status.HTTP_200_OK
        )

    def create_data(self, TRAINING_DATA):
        nlp = sp.blank("en")
        data = []
        for text, annotations in (TRAINING_DATA):
            doc = nlp.make_doc(text)
            ent = []
            for start, end, label in annotations["entities"]:
                span = doc.char_span(start, end, label=label, alignment_mode="strict")
                if span is not None:
                    ent.append({"key": str(span), "label": label})
            data.append({"text": text, "tags": ent})
        return (data)


class SaveTrainingFiles(S3Bucket):
    def get(self, request):
        return Response(
            {"data": []},
            status=status.HTTP_200_OK
        )

    def post(self, request):
        try:
            if request.FILES != None:
                for index in dict(request.FILES).keys():
                    original_file_name = request.FILES[index].name
                    fname = str(original_file_name).lower()
                    fnameArray = fname.split(".")
                    extn = fnameArray[-1]
                    file_name = (
                            "".join(fnameArray[:-1]) + "_"
                            + str(round(datetime.now().timestamp())) + "." + extn)

                    file_size = request.FILES[index].size
                    file_type = request.FILES[index].content_type
                    training_file = NERTrainingFiles()
                    training_file.file_name = "data/train/" + file_name
                    training_file.original_file_name = original_file_name
                    training_file.file_uploaded_type = "manual"
                    training_file.file_format = file_type
                    training_file.file_size = file_size
                    self.upload_to_s3("/data/train", file_name, request.FILES[index])
                    training_file.save()
                return Response(
                    {"data": "uploaded"},
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response(
                {"data": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
