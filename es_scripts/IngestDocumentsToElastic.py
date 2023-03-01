
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


# ---------------------------------------------------------------------------------

class DocumentIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    
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
                        "name":JalaliDate.to_jalali(year, month, day).strftime('%B',locale = 'fa'),
                        "number": month
                    },
                    "day":{
                        "name":JalaliDate.to_jalali(year, month, day).strftime('%A',locale = 'fa'),
                        "number": day
                    },
                    "hour":doc_hour
                    }
                
                print(document_jalili_date)
            if doc_file_name in files_dict:
                base64_file = files_dict[doc_file_name]

                new_doc = {
                    "source_id":source_id,
                    "source_folder":source_folder,
                    "document_id": doc_id,
                    "document_name": doc_name,
                    "document_date": doc_date,
                    "document_year": doc_year,
                    "document_time": doc_time,
                    "document_hour":doc_hour,

                    "document_jalili_date":document_jalili_date,
                    "raw_file_name": doc_file_name,
                    "category_name": doc_category,
                    "source_name": doc_source,
                    "subject_name": doc_subject,
                    "subject_weight": doc_subject_weight,  
                    "data": base64_file
                }


                new_document = {
                    "_index": self.name,
                    "_id": doc_id,
                    "pipeline":"attachment",
                    "_source":new_doc,
                }
                yield new_document



class EN_DocumentIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    
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
                base64_file = files_dict[doc_file_name]

                new_doc = {
                    "source_id":source_id,
                    "source_folder":source_folder,
                    "document_id": doc_id,
                    "document_name": doc_name,
                    "document_date": doc_date,
                    "document_year": doc_year,
                    "document_time": doc_time,
                    "document_hour":doc_hour,
                    "raw_file_name": doc_file_name,
                    "category_name": doc_category,
                    "source_name": doc_source,
                    "subject_name": doc_subject,
                    "subject_weight": doc_subject_weight,  
                    "data": base64_file
                }


                new_document = {
                    "_index": self.name,
                    "_id": doc_id,
                    "pipeline":"attachment",
                    "_source":new_doc,
                }
                yield new_document





def apply(folder, Country):
    settings = {}
    mappings = {}
    model_name = Document.__name__
    index_name = standardIndexName(Country,model_name)

    new_index = None

    country_lang = Country.language
    documents = []

    if country_lang == "انگلیسی":
        settings = es_config.EN_Settings
        mappings = es_config.EN_Mappings
        new_index = EN_DocumentIndex(index_name, settings, mappings)
        documents = Document.objects.filter(country_id__id=Country.id).annotate(
            source_id = F('country_id__id'),
            source_folder = F('country_id__file'),
            source_name = F('country_id__name')).values()

    else:
        settings = es_config.FA_Settings
        mappings = es_config.FA_Mappings
        new_index = DocumentIndex(index_name, settings, mappings)

        documents = Document.objects.filter(country_id__id=Country.id).annotate(
            year=Cast(Substr('date', 1, 4), IntegerField()),
            source_id = F('country_id__id'),
            source_folder = F('country_id__file'),
            source_name = F('country_id__name')).values()


    # If index exists -> delete it.
    if ES_Index.CLIENT.indices.exists(index=index_name):
        ES_Index.CLIENT.indices.delete(index=index_name, ignore=[400, 404])
        print(f"{index_name} deleted!")

    new_index.create()
    new_index.bulk_insert_documents(folder,documents,do_parallel=True)

