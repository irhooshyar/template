from abdal import config
from pathlib import Path
from scripts.Persian import Preprocessing
from doc.models import Document,DocumentParagraphs,ParagraphVector,ParagraphVectorType
import pandas as pd
import math
from itertools import chain
import time
import threading
from es_scripts import IngestParagraphsVectorsToElastic
# -----------------------------------
from IPython import display

import numpy as np
import pandas as pd

import hazm
import requests
import time

import torch
from sentence_transformers import models, SentenceTransformer, util


    
def load_st_model(model_name_or_path):
    word_embedding_model = models.Transformer(model_name_or_path)
    pooling_model = models.Pooling(
        word_embedding_model.get_word_embedding_dimension(),
        pooling_mode_mean_tokens=True,
        pooling_mode_cls_token=False,
        pooling_mode_max_tokens=False)
    
    model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
    return model

 # Load the Sentence-Transformer
farstail_model = 'm3hrdadfi/bert-fa-base-uncased-farstail-mean-tokens'
wikinli_model = 'm3hrdadfi/bert-fa-base-uncased-wikinli-mean-tokens'
wikitriplet_model = 'm3hrdadfi/bert-fa-base-uncased-wikitriplet-mean-tokens'

embedder = load_st_model(wikitriplet_model)

def apply(folder_name, Country):
    ParagraphVector.objects.filter(paragraph__document_id__country_id__id = Country.id).delete()
    
    batch_size = 1000

    t = time.time()

    # get country paragraphs
    paragraph_list = DocumentParagraphs.objects.filter(document_id__country_id__id = Country.id)[:]
    print(len(paragraph_list))

    paragraph_dict = {}
    i = 0
    for para_obj in paragraph_list:
        paragraph_dict[i] = para_obj
        i += 1

    # create corpus
    corpus = []
    for index,para_obj in paragraph_dict.items():
        print(index)
        corpus.append(para_obj.text)

    t = time.time()
    print('started...')

    corpus_embeddings = embedder.encode(corpus,batch_size = 128, convert_to_tensor=False, show_progress_bar=True)
    
    print("time ", time.time() - t)

    # save vectors to db
    vector_type = None
    try:
        vector_type = ParagraphVectorType.objects.get(name = 'wikitriplet_vector')
    except:
        vector_type = ParagraphVectorType.objects.create(name = 'wikitriplet_vector')

    create_list = []
    for i in range(len(paragraph_list)):
        para_vector = (list(corpus_embeddings[i]))
        para_vector = [float(num) for num in para_vector]

        row_obj = ParagraphVector(
            paragraph = paragraph_dict[i],
            vector_value = {"data":para_vector},
            vector_type = vector_type
        )
        create_list.append(row_obj)


        if create_list.__len__() > batch_size:
            ParagraphVector.objects.bulk_create(create_list)
            create_list = []


    ParagraphVector.objects.bulk_create(create_list)

    
    IngestParagraphsVectorsToElastic.apply(folder_name,Country,0)