
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



# ---------------------------------------------------------------------------------

class ParagraphIndex(ES_Index):
    def __init__(self, name, settings,mappings,attach_doc_file):
        super().__init__(name, settings,mappings,attach_doc_file)
    
    def generate_docs(self,files_dict,paragraphs):

        for para in paragraphs:
            paragraph_id = para['para_id']
            document_id = para['doc_id']
            document_name = para['doc_name']
            category_name = para['category_name'] if para['category_name'] is not None else 'نامشخص'
            subject_name = para['subject_name'] if para['subject_name'] is not None else 'نامشخص'
            document_year = para['year'] if para['year'] != None else 0
            
            para_text = para['para_text']

            new_para = {
                "paragraph_id": paragraph_id,
                "document_id": document_id,
                "document_name": document_name,
                "document_year": document_year,
                "category_name":category_name,
                "subject_name":subject_name,
                "attachment":{"content":para_text,"content_length":len(para_text)}
            }

            new_paragraph = {
                "_index": self.name,
                "_id": paragraph_id,
                "_source":new_para,
            }

            yield new_paragraph




class EN_ParagraphIndex(ES_Index):
    def __init__(self, name, settings,mappings,attach_doc_file):
        super().__init__(name, settings,mappings,attach_doc_file)
    
    def generate_docs(self,files_dict,paragraphs):

        for para in paragraphs:
            paragraph_id = para['para_id']
            document_id = para['doc_id']
            document_name = para['doc_name']
            category_name = para['category_name'] if para['category_name'] is not None else 'unknown'
            subject_name = para['subject_name'] if para['subject_name'] is not None else 'unknown'
            document_year =int(para['date'].split(' ')[2]) if para['date'] != None and len(para['date'].split(' ')) == 3 else 2023

            para_text = para['para_text']

            new_para = {
                "paragraph_id": paragraph_id,
                "document_id": document_id,
                "document_name": document_name,
                "document_year": document_year,
                "category_name":category_name,
                "subject_name":subject_name,
                "attachment":{"content":para_text,"content_length":len(para_text)}
            }
            
            new_paragraph = {
                "_index": self.name,
                "_id": paragraph_id,
                "_source":new_para,
            }

            yield new_paragraph



def apply(folder, Country,is_for_ref):
    settings = {}
    mappings = {}
    model_name = DocumentParagraphs.__name__
    
    index_name = standardIndexName(Country,model_name)

    if is_for_ref == 1:
        index_name = index_name + "_graph"
        
    country_lang = Country.language
    new_index = None
    paragraphs = []

    if country_lang in ["فارسی","استاندارد"]:
        settings = es_config.Paragraphs_Settings_2 if is_for_ref == 1 else es_config.Paragraphs_Settings_3
        mappings = es_config.Paragraphs_Mappings
        new_index = ParagraphIndex(index_name, settings, mappings,attach_doc_file=False) 
        paragraphs = DocumentParagraphs.objects.filter(
            document_id__country_id__id = Country.id).annotate(
                para_id = F('id')).annotate(
                doc_id = F('document_id__id')).annotate(
                doc_name = F('document_id__name'), 
                category_name = F('document_id__category_name'),
                subject_name = F('document_id__subject_name'),
                year=Cast(Substr('document_id__date', 1, 4), IntegerField())).annotate(
                para_text = F('text')).values()


    elif country_lang == "انگلیسی":
        settings = es_config.EN_Settings
        mappings = es_config.EN_Paragraphs_Mappings
        new_index = EN_ParagraphIndex(index_name, settings, mappings,attach_doc_file=False)

        paragraphs = DocumentParagraphs.objects.filter(
            document_id__country_id__id = Country.id).annotate(
            para_id = F('id')).annotate(
                doc_id = F('document_id__id')).annotate(
                doc_name = F('document_id__name'), 
                date = F('document_id__date'), 
                category_name = F('document_id__category_name'),
                subject_name = F('document_id__subject_name'),                    
                para_text = F('text')).values()
    
    
    print(f"{len(paragraphs)} paragraphs collected.")
    
        
    # If index exists -> delete it.
    if ES_Index.CLIENT.indices.exists(index=index_name):
        ES_Index.CLIENT.indices.delete(index=index_name, ignore=[400, 404])
        print(f"{index_name} deleted!")

    new_index.create()
    new_index.bulk_insert_documents(folder, paragraphs)

