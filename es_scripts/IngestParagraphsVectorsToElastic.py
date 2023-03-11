
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
import after_response
import numpy as np
# ---------------------------------------------------------------------------------

class ParagraphVectorIndex(ES_Index):
    def __init__(self, name, settings,mappings,attach_doc_file):
        super().__init__(name, settings,mappings,attach_doc_file)
    
    def generate_docs(self,files_dict,paragraphs):

        for para in paragraphs:
            paragraph_id = para['para_id']

            document_id = para['doc_id']
            document_name = para['doc_name']
            para_text = para['para_text']

            vector_value = list(para['vector_value'])

            new_para = {
                # "paragraph_id": paragraph_id,
                "wikitriplet_vector":vector_value,
                # "document_id": document_id,
                # "document_name": document_name,
            }


            new_paragraph = {
                "_index": self.name,
                "_id": paragraph_id,
                "_source":new_para,
            }
            yield new_paragraph


@after_response.enable
def apply(folder, Country,is_for_ref):
    settings = {}
    mappings = {}
    model_name = DocumentParagraphs.__name__
    
    index_name = standardIndexName(Country,model_name)

    if is_for_ref == 1:
        index_name = index_name + "_graph"

    index_name = index_name + "_vectors"    
    country_lang = Country.language

    if country_lang in ["فارسی","استاندارد"]:
        settings = es_config.Paragraphs_Settings_2 if is_for_ref == 1 else es_config.Paragraphs_Settings_3
        mappings = es_config.Paragraphs_Vector_Mappings

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
    # paragraphs = []

    # If index exists -> delete it.
    if ES_Index.CLIENT.indices.exists(index=index_name):
        ES_Index.CLIENT.indices.delete(index=index_name, ignore=[400, 404])
        print(f"{index_name} deleted!")


    print(len(paragraphs))
    new_index = ParagraphVectorIndex(index_name, settings, mappings,attach_doc_file=False)
    new_index.create()
    new_index.bulk_insert_documents(folder, paragraphs)

def get_paragraphs_list(Country):

    result_paragraphs_list = []

    # get country paragraphs
    paragraph_list = DocumentParagraphs.objects.filter(document_id__country_id__id = Country.id)

    paragraph_dict = {}
    i = 0
    for para_obj in paragraph_list:
        print("a", i/paragraph_list.__len__())
        i+=1
        para_res_obj = {
            "para_id":para_obj.id,
            "para_text":para_obj.text,
            "doc_id":para_obj.document_id.id,
            "doc_name":para_obj.document_id.name,
            "vector_value": []
        }
        paragraph_dict[para_obj.id] = para_res_obj

    print("paragraph_dict created...")

    vectorFile = str(Path(config.PERSIAN_PATH, "weights", "khabar_online_vector_result.json"))
    file = open(vectorFile).read()
    file_data = json.loads(file)

    ctr = 0
    for para_id,para_vector in file_data.items():
        para_id = int(para_id)
        try:
            paragraph_dict[para_id]["vector_value"] = para_vector
            result_paragraphs_list.append(paragraph_dict[para_id])
            ctr += 1
            print("b", ctr/file_data.keys().__len__())
        except:
            print('Paragraph id not existed!')

    print(f"{ctr}/{len(file_data.keys())} paragraphs found.")

    return result_paragraphs_list