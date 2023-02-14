
from elasticsearch import Elasticsearch
from abdal import config
from abdal import es_config
import base64
import csv
from doc.models import User,UserLogs
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
#from en_doc import models as en_model
from persiantools.jdatetime import JalaliDate
import datetime

# ---------------------------------------------------------------------------------


def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if (gm > 2):
        gy2 = gy + 1
    else:
        gy2 = gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if (days > 365):
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if (days < 186):
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return [jy, jm, jd]



class UserLogsIndex(ES_Index):
    def __init__(self, name, settings,mappings):
        super().__init__(name, settings,mappings)

    def generate_docs(self, files_dict, documents):

        for doc in documents:

            index_doc_id = doc['id']
            user_ip = doc['user_ip']
            page_url = doc['page_url']
            visit_time  = str(doc['visit_time']).replace(' ',"T").split('.')[0] + 'Z'

            year = int(visit_time[0:4])
            month = int(visit_time[5:7])
            day = int(visit_time[8:10])
            hour = int(visit_time[11:13])

            detail_json = doc['detail_json']
            jalili_visit_time = {
                "year":year,
                "month":{"number":month,
                         "name":JalaliDate.to_jalali(year, month, day).strftime('%B',locale = 'fa')},
                "day":{
                  "number":day,
                    "name":JalaliDate.to_jalali(year, month, day).strftime('%A',locale = 'fa')  
                },
                
                "hour":hour
            }

            user_id = doc['user_id_id']
            user_first_name = doc['user_first_name']
            user_last_name = doc['user_last_name']

            user_object = {
                "id":user_id,
                "first_name":user_first_name,
                "last_name":user_last_name
            }

            new_doc = {
                'user_ip':user_ip,
                'page_url':page_url,
                'visit_time':visit_time,
                "jalili_visit_time":jalili_visit_time,
                'detail_json':detail_json,
                'user':user_object

            }


            new_document = {
                "_index": self.name,
                "_id": index_doc_id,
                #"pipeline":"attachment",
                "_source":new_doc,
            }
            yield new_document


def apply(folder, Country,machine_user):
    
    
    if  machine_user == config.SERVER_USER_NAME:
        index_name = es_config.SERVE_USER_LOG_INDEX
    else:
        index_name = es_config.LOCAL_USER_LOG_INDEX


    settings = es_config.FA_Settings
    mappings = es_config.UserLog_Mappings

    UserLogDocs = UserLogs.objects.all().annotate(
        user_first_name=F('user_id__first_name'),
        user_last_name=F('user_id__last_name')).values()

    new_index = UserLogsIndex(index_name, settings, mappings)


    # If index exists -> delete it.
    if ES_Index.CLIENT.indices.exists(index=index_name):
        ES_Index.CLIENT.indices.delete(index=index_name, ignore=[400, 404])
        print(f"{index_name} deleted!")

    new_index.create()
    new_index.bulk_insert_documents(folder,UserLogDocs,do_parallel=True)

