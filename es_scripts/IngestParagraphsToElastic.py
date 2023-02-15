
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
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    
    def generate_docs(self,files_dict,paragraphs):

        for para in paragraphs:
            paragraph_id = para['para_id']
            document_id = para['doc_id']
            document_name = para['doc_name']
            category_name = para['category_name'] if para['category_name'] is not None else 'نامشخص'
            year = para['year'] if para['year'] != None else 0
            
            para_text = para['para_text']

            text_bytes = bytes(para_text,encoding="utf8")
            base64_bytes = base64.b64encode(text_bytes)
            base64_text = (str(base64_bytes)[2:-1])
            base64_file = base64_text

            new_para = {
                "paragraph_id": paragraph_id,
                "document_id": document_id,
                "document_name": document_name,
                "category_name":category_name,
                'year':year,
                "data": base64_file
            }


            new_paragraph = {
                "_index": self.name,
                "_id": paragraph_id,
                "pipeline":"attachment",
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

        print(is_for_ref)
        
    country_lang = Country.language

    if country_lang in ["فارسی","استاندارد"]:
        settings = es_config.Paragraphs_Settings_2 if is_for_ref == 1 else es_config.Paragraphs_Settings_3
        mappings = es_config.Paragraphs_Mappings



    Paragraphs_Model = DocumentParagraphs

    paragraphs = Paragraphs_Model.objects.filter(
        document_id__country_id__id = Country.id).annotate(
            para_id = F('id')).annotate(
                doc_id = F('document_id__id')).annotate(
                doc_name = F('document_id__name'), 
                category_name = F('document_id__category_name'),
                year=Cast(Substr('document_id__date', 1, 4), IntegerField())).annotate(
                para_text = F('text')).values(

        'para_id','doc_id','doc_name',
        'para_text', 
        'year', 'category_name'
    )
    print(len(paragraphs))
    new_index = ParagraphIndex(index_name, settings, mappings)

    # If index exists -> delete it.
    if ES_Index.CLIENT.indices.exists(index=index_name):
        ES_Index.CLIENT.indices.delete(index=index_name, ignore=[400, 404])
        print(f"{index_name} deleted!")

    new_index.create()
    new_index.bulk_insert_documents(folder, paragraphs,do_parallel=True)

