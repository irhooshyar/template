
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Document, DocumentParagraphs
from django.db.models.functions import Substr, Cast
from django.db.models import Max, Min, F, IntegerField, Q
import pandas as pd
from pathlib import Path
import glob
import os
import docx2txt
import time
from es_scripts.ES_Index import ES_Index
from es_scripts.ES_Index import readFiles
import time
from elasticsearch import helpers
from collections import deque
from scripts.Persian.Preprocessing import standardIndexName
from persiantools.jdatetime import JalaliDate
from scripts.Persian import Preprocessing
from dateutil import parser


def standardFileName(name):
    name = name.replace(".", "")
    name = arabicCharConvert(name)
    name = persianNumConvert(name)
    name = name.strip()

    while "  " in name:
        name = name.replace("  "," ")

    return name

def persianNumConvert(text):
    persian_num_dict = {"۱": "1" ,"۲": "2", "۳": "3", "۴": "4", "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹":"9" , "۰": "0" }
    for key, value in persian_num_dict.items():
        text = text.replace(key, value)
    return text

def arabicCharConvert(text):
    arabic_char_dict = {"ى": "ی" ,"ك": "ک", "آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "  ":" ", "\n\n":"\n", "\n ":"\n" , }
    for key, value in arabic_char_dict.items():
        text = text.replace(key, value)

    return text

def arabic_preprocessing(text):
    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}
    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text

def numbers_preprocessing(text):
  persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
  arabicNumbers  = ['٠','١', '٢', '٣','٤', '٥', '٦','٧', '٨', '٩']
  for c in persianNumbers:
    text = text.replace(c, str(ord(c)-1776))
  for c in arabicNumbers:
    text = text.replace(c, str(ord(c)-1632))
  return text

def Local_preprocessing(text):
    space_list = [" ", "\u200c"]
    for s in space_list:
        text = text.replace(s, "")

    text = arabic_preprocessing(text)
    text = numbers_preprocessing(text)

    return text

def DataFrame2Dict(df, key_field, values_field):
    result_dict = {}
    for index, row in df.iterrows():
        data_list = {}
        for field in values_field:
            data_list[field] = row[field]
        result_dict[str(row[key_field])] = data_list

    return result_dict



# ---------------------------------------------------------------------------------

class DocumentIndex(ES_Index):
    def __init__(self, name, settings,mappings,attach_doc_file):
        super().__init__(name, settings,mappings,attach_doc_file)
    
    def generate_docs(self, files_dict, documents):

        for doc in documents:

            doc_id = int(doc['id'])
            source_id = int(doc['source_id'])
            source_folder = doc['source_folder'].split("/")[-1].split(".")[0]

            doc_name = doc['name']

            doc_file_name = ""

            if 'file_name' in doc and doc['file_name'] != None:
                doc_file_name = doc['file_name']
            else:
                doc_file_name = doc_name

            doc_subject = doc['subject_name'] if doc['subject_name'] != None else 'نامشخص'
            doc_subject_weight = doc['subject_weight'] if doc['subject_weight'] != None else 'نامشخص'
            doc_category = doc['category_name'] if doc['category_name'] != None else 'نامشخص'
            doc_source = doc['source_name']
            doc_year = doc['year'] if doc['year'] != None else 0
            doc_date = doc['date'] if doc['date'] != None else 'نامشخص'
            doc_time = doc['time'] if doc['time'] != None else 'نامشخص'
            doc_hour =  int(doc_time.split(':')[0].strip()) if doc_time != 'نامشخص' else 0
            
            document_jalili_date = {}
            
            if doc_date!= "نامشخص":
                year = int(doc_date.split('/')[0])  
                month = int(doc_date.split('/')[1])  
                day = int(doc_date.split('/')[2])  

                document_jalili_date = {
                    "year":doc_year,
                    "month":{
                        "name":JalaliDate(year, month, day,locale = 'fa').strftime('%B',locale = 'fa'),
                        "number": month
                    },
                    "day":{
                        "name":JalaliDate(year, month, day,locale = 'fa').strftime('%A',locale = 'fa'),
                        "number": day
                    },
                    "hour":doc_hour
                    }
                
            if doc_file_name in files_dict:
                document_content = files_dict[doc_file_name]

                new_doc = {
                    "source_id":source_id,
                    "source_folder":source_folder,
                    "source_name": doc_source,


                    "document_id": doc_id,
                    "document_name": doc_name,
                    "document_date": doc_date,
                    "document_year": doc_year,
                    "document_time": doc_time,

                    "document_jalili_date":document_jalili_date,
                    "raw_file_name": doc_file_name,
                    "category_name": doc_category,
                    "subject_name": doc_subject,
                    "subject_weight": doc_subject_weight,  

                }

                new_document = {}

                if self.attach_doc_file:
                    new_doc["data"] = document_content

                    new_document = {
                        "_index": self.name,
                        "_id": doc_id,
                        "_source":new_doc,
                        "pipeline":"attachment"
                    }

                else:
                    new_doc["attachment"] = {"content":document_content,"content_length":len(document_content)}
            
                    new_document = {
                        "_index": self.name,
                        "_id": doc_id,
                        "_source":new_doc,
                    }

                yield new_document



class EN_DocumentIndex(ES_Index):
    def __init__(self, name, settings,mappings,attach_doc_file):
        super().__init__(name, settings,mappings,attach_doc_file)
    
    def generate_docs(self, files_dict, documents):

        for doc in documents:

            doc_id = int(doc['id'])
            source_id = int(doc['source_id'])
            source_folder = doc['source_folder'].split("/")[-1].split(".")[0]

            doc_name = doc['name']

            doc_file_name = ""

            if 'file_name' in doc and doc['file_name'] != None:
                doc_file_name = doc['file_name']
            else:
                doc_file_name = doc_name

            doc_subject = doc['subject_name'] if doc['subject_name'] != None else 'unknown'
            doc_subject_weight = doc['subject_weight'] if doc['subject_weight'] != None else 'unknown'
            doc_category = doc['category_name'] if doc['category_name'] != None else 'unknown'
            doc_source = doc['source_name']
            
            doc_date = doc['date'] if doc['date'] != None else 'unknown'
            doc_year = int(doc_date.split(' ')[2]) if doc_date != "unknown" and len(doc_date.split(' ')) == 3 else 2023

            doc_time = doc['time'] if doc['time'] != None else 'unknown'
            doc_hour =  int(doc_time.split(':')[0].strip()) if doc_time != 'unknown' else 0

            if doc_file_name in files_dict:
                document_content = files_dict[doc_file_name]

                new_doc = {
                    "source_id":source_id,
                    "source_folder":source_folder,
                    "source_name": doc_source,

                    "document_id": doc_id,
                    "document_name": doc_name,
                    "document_date": doc_date,
                    "document_year": doc_year,
                    "document_time": doc_time,
                    "document_hour":doc_hour,
                    "raw_file_name": doc_file_name,
                    "category_name": doc_category,
                    "subject_name": doc_subject,
                    "subject_weight": doc_subject_weight,  
                }


                new_document = {}

                if self.attach_doc_file:
                    new_doc["data"] = document_content

                    new_document = {
                        "_index": self.name,
                        "_id": doc_id,
                        "_source":new_doc,
                        "pipeline":"attachment"
                    }

                else:
                    new_doc["attachment"] = {"content":document_content,"content_length":len(document_content)}
            
                    new_document = {
                        "_index": self.name,
                        "_id": doc_id,
                        "_source":new_doc,
                    }
                    
                yield new_document



def CheckDate(date):
    try:
        format = '%Y-%m-%d'
        parser.parse(date)
        return date
    except ValueError:
        return None


def extractTime(date_time,Country):
    time = None

    if Country.name == 'تابناک':
        time = date_time.split('-')[1].strip()
    elif Country.name == 'خبر آنلاین':
        time = date_time.split(" ")[1].strip()
    elif Country.name == 'عصر ایران':
        time = date_time.strip()
    elif Country.name == 'ایسنا':
        time = date_time.split(' ')[3].strip() 

    elif Country.name == 'BBC':
        time = date_time.split(' ')[0].strip() 

    return time



def apply(folder, Country):
    settings = {}
    mappings = {}
    model_name = Document.__name__
    index_name = standardIndexName(Country,model_name)

    new_index = None

    country_lang = Country.language
    documents = []

    excelFile = str(Path(config.PERSIAN_PATH, config.COUNTRY_EXCEL_FILE_DICT[Country.name]))
    
    df = pd.read_excel(excelFile)
    df['title'] = df['title'].apply(lambda x: standardFileName(x))
    df['date_time'] = df['date_time'].apply(lambda x: extractTime(x,Country))

    dataframe_dictionary = {}
    if country_lang == "فارسی":
        dataframe_dictionary = DataFrame2Dict(df, "id", ["title","category", "date","date_time"])
    elif country_lang == "انگلیسی":
        dataframe_dictionary = DataFrame2Dict(df, "title", ["id","category", "date","date_time"])


    dataPath = str(Path(config.DATA_PATH, folder))
    all_files = Preprocessing.readFiles(dataPath, readContent=False)
    all_files = list(set(all_files.keys()))

    print(f"{len(all_files)} files found!")

    idx = 0
    for file in all_files:
        idx += 1
        file = str(file)

        if file in dataframe_dictionary:
            document_id = file if country_lang == "فارسی" else dataframe_dictionary[file]['id']
            document_name = dataframe_dictionary[file]['title'] if country_lang == "فارسی" else file

            date = CheckDate(str(dataframe_dictionary[file]['date']))

            year = None
            if country_lang == "فارسی":
                year = int(date.split('/')[0]) if date != None else 0
    

            category_name = str(dataframe_dictionary[file]['category'])
            time = str(dataframe_dictionary[file]['date_time'])

            category_name = category_name.replace("»", "-")
            category_name = category_name.replace("صفحه نخست-", "")

            if category_name == "nan":
                category_name = None


            doc_obj = {
                "id":document_id,
                "name":document_name,
                "source_id":Country.id,
                "source_folder":Country.file.name,
                "source_name":Country.name,
                "file_name":file,
                "date":date,
                "time":time,
                "year":year,
                "category_name":category_name,
                "subject_name":None,
                "subject_weight":None,

                }
            documents.append(doc_obj)


    if country_lang == "فارسی":
        settings = es_config.FA_Settings
        mappings = es_config.FA_Mappings
        new_index = DocumentIndex(index_name, settings, mappings,attach_doc_file = False)
    elif country_lang == "انگلیسی":
        settings = es_config.EN_Settings
        mappings = es_config.EN_Mappings
        new_index = EN_DocumentIndex(index_name, settings, mappings,attach_doc_file = False)
       
    # If index exists -> delete it.
    if ES_Index.CLIENT.indices.exists(index=index_name):
        ES_Index.CLIENT.indices.delete(index=index_name, ignore=[400, 404])
        print(f"{index_name} deleted!")

    new_index.create()
    new_index.bulk_insert_documents(folder,documents)

