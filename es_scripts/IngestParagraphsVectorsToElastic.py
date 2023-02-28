
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import Document, DocumentParagraphs,ParagraphVector,ParagraphVectorType
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
import json

# ---------------------------------------------------------------------------------

class ParagraphVectorIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)
    
    def generate_docs(self,files_dict,paragraphs):

        for para in paragraphs:
            paragraph_id = para['para_id']
            document_id = para['doc_id']
            document_name = para['doc_name']

            para_text = para['para_text']

            vector_value = list(para['vector_value']['data'])

            text_bytes = bytes(para_text,encoding="utf8")
            base64_bytes = base64.b64encode(text_bytes)
            base64_text = (str(base64_bytes)[2:-1])
            base64_file = base64_text

            new_para = {
                "paragraph_id": paragraph_id,
                "wikitriplet_vector":vector_value,
                "document_id": document_id,
                "document_name": document_name,
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

    index_name = index_name + "_vectors"    
    country_lang = Country.language

    if country_lang in ["فارسی","استاندارد"]:
        settings = es_config.Paragraphs_Settings_2 if is_for_ref == 1 else es_config.Paragraphs_Settings_3
        mappings = es_config.Paragraphs_Mappings

    elif country_lang == "انگلیسی":
        settings = es_config.EN_Settings
        mappings = es_config.EN_Paragraphs_Mappings




    # Paragraphs_Model = ParagraphVector 

    # paragraphs = Paragraphs_Model.objects.filter(
    #     paragraph__document_id__country_id__id = Country.id).annotate(
    #             para_id = F('paragraph_id')).annotate(
    #             doc_id = F('paragraph__document_id__id')).annotate(
    #             doc_name = F('paragraph__document_id__name'), 
    #             para_text = F('paragraph__text')).values(

    #     'para_id','doc_id','doc_name',
    #     'para_text','vector_value'
    # )

    paragraphs = get_paragraphs_list(Country)

    print(len(paragraphs))
    new_index = ParagraphVectorIndex(index_name, settings, mappings)
    new_index.create()
    new_index.bulk_insert_documents(folder, paragraphs,do_parallel=True)

def get_paragraphs_list(Country):

    result_paragraphs_list = []

    # get country paragraphs
    paragraph_list = DocumentParagraphs.objects.filter(document_id__country_id__id = Country.id)

    paragraph_dict = {}
    for para_obj in paragraph_list:
        para_res_obj = {
            "para_id":para_obj.id,
            "para_text":para_obj.text,
            "doc_id":para_obj.document_id.id,
            "doc_name":para_obj.document_id.name,
            "vector_value":[]
        }
        paragraph_dict[para_obj.id] = para_res_obj

    
    vectorFile = str(Path(config.PERSIAN_PATH, 'vector_result.json'))
    file = open(vectorFile)
    file_data = json.load(file)

    ctr = 0
    for para_id,para_vector in file_data.items():
        para_id = int(para_id)
        try:
            paragraph_dict[para_id]["vector_value"] = para_vector
            result_paragraphs_list.append(paragraph_dict[para_id])
            ctr += 1
        except:
            print('Paragraph id not existed!')

    file.close()
    print(f"{ctr}/{len(file_data.keys())} paragraphs found.")

    return result_paragraphs_list