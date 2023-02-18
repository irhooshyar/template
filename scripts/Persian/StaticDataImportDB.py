import json
from dateutil import parser
import pandas as pd
from django.db.models import Max, Min, F, IntegerField, QuerySet, Sum, Count, Q
from openpyxl import load_workbook
from abdal import config
from doc.models import ActorArea, CUBE_DocumentJsonList, DocumentActor, Subject
from doc.models import UserRole
from doc.models import Document, DocumentParagraphs
from doc.models import Actor, ActorCategory, ActorType, Category
from doc.models import SearchParameters
from doc.models import ClusteringAlgorithm,FeatureSelectionAlgorithm
from django.shortcuts import get_object_or_404
from pathlib import Path
import glob
import os
import time

def standardFileName(name):
    name = name.replace(".", "")
    name = arabicCharConvert(name)
    name = persianNumConvert(name)
    name = name.strip()

    while "  " in name:
        name = name.replace("  "," ")

    return name

def extractTime(date_time):
    time = date_time.split('-')[1].strip()
    return time


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

def CheckDate(date):
    try:
        format = '%Y-%m-%d'
        parser.parse(date)
        return date
    except ValueError:
        return None

def DataFrame2Dict(df, key_field, values_field):
    result_dict = {}
    for index, row in df.iterrows():
        data_list = {}
        for field in values_field:
            data_list[field] = row[field]
        result_dict[str(row[key_field])] = data_list

    return result_dict

def Roles_Insert():
    rolesFile = str(Path(config.PERSIAN_PATH, 'Roles.txt'))
    with open(rolesFile, encoding="utf8") as f:
        lines = f.readlines()
        for role in lines:
            role = role.replace("\n", "")
            result_count = UserRole.objects.filter(persian_name=role).count()
            if result_count == 0:
                UserRole.objects.create(persian_name=role)
    f.close()


def Update_Docs_fromExcel(Country):
    # Category.objects.all().delete()

    documentList = Document.objects.filter(country_id=Country)
    excelFile = str(Path(config.PERSIAN_PATH, 'data.xlsx'))

    df = pd.read_excel(excelFile)
    df['title'] = df['title'].apply(lambda x: standardFileName(x))
    df['date_time'] = df['date_time'].apply(lambda x: extractTime(x))

    # documents update
    dataframe_dictionary = DataFrame2Dict(df, "title", ["category", "date","date_time"])

    for document in documentList:
        document_id = document.id
        document_name = standardFileName(document.name)

        if document_name in dataframe_dictionary:
            date = CheckDate(str(dataframe_dictionary[document_name]['date']))
            category_name = str(dataframe_dictionary[document_name]['category'])
            time = str(dataframe_dictionary[document_name]['date_time'])

            category_name = category_name.replace("»", "-")
            category_name = category_name.replace("صفحه نخست-", "")

            if category_name == "nan":
                category_name = "نامشخص"

            try:
                category_id = Category.objects.get(name=category_name).id
            except Exception as e:
                category = Category.objects.create(name=category_name)
                category_id = category.id

            Document.objects.filter(id=document_id).update(date=date,time = time,
                                                            category_id=category_id, category_name=category_name)



def ActorRolePatternKeywords_Insert():
    ActorRolePatternKeywordsFile = str(Path(config.PERSIAN_PATH, 'ActorRolePatternKeywords.json'))
    f = open(ActorRolePatternKeywordsFile,encoding="utf-8")
    ActorRolePatternKeywords = json.load(f)
    f.close()
    for actor_role,keywords in ActorRolePatternKeywords.items():
        role_kws = '/'.join(keywords)
        result_count = ActorType.objects.filter(name=actor_role).count()
        if result_count == 0:
            ActorType.objects.create(name=actor_role,pattern_keywords = role_kws)
        else:
            ActorType.objects.filter(name=actor_role).update(pattern_keywords = role_kws)

def Actors_Insert():

    fullActorsInformationFile = str(Path(config.PERSIAN_PATH, 'fullActorsInformation.json'))

    f = open(fullActorsInformationFile, encoding="utf-8")
    fullActorsInformation = json.load(f)
    f.close()

    for category in fullActorsInformation:
        category_count = ActorCategory.objects.filter(name=category).count()

        # if not exist, creat
        if category_count == 0:
            actor_category = ActorCategory.objects.create(name=category)
        else:
            actor_category = ActorCategory.objects.get(name=category)

        actors = fullActorsInformation[category]

        for actor in actors:
            actor_forms = actors[actor]
            actor_forms = '/'.join(actor_forms)

            actor_count = Actor.objects.filter(name=actor, actor_category_id=actor_category).count()

            # if not exist, creat
            if actor_count == 0:
                Actor.objects.create(name=actor, actor_category_id=actor_category,
                                     forms=actor_forms)
            else:
                # if exist, update
                Actor.objects.filter(
                    name=actor, actor_category_id=actor_category).update(forms=actor_forms)

    print('Actors updated.')

def Update_ActorsArea():
    batch_size = 10000

    excelFile = str(Path(config.PERSIAN_PATH, 'حوزه های تنظیمگری و زیرحوزها1401415.xlsx'))
    all_sheets = pd.read_excel(excelFile,sheet_name=None)

    arabic_char_dict = {"ك": "ک", "آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "  ": " ", "\u200c": " "}

    actor_area_dict = {}

    for area in all_sheets:
        main_area = area.replace('حوزه','').strip()

        for actor in all_sheets[area]['کنشگران ذیصلاح']:
            actor = actor.strip()
            if actor != 'اتاق ایران':
                actor = actor.replace(' ایران','').strip()

            actor = actor.replace(' ','').replace('‌','')

            for key, value in arabic_char_dict.items():
                actor = actor.replace(key, value)

            actor_area_dict[actor] = main_area


    actor_list = Actor.objects.all()
    c = 0
    for actor in actor_list:
        actor_forms = actor.forms.split('/')

        actor_forms2 = [actor_form.replace(' ','').replace('‌','') for actor_form in actor_forms]

        for actor_form in actor_forms2:

            for key, value in arabic_char_dict.items():
                actor_form = actor_form.replace(key, value)


        if any (actor_form in actor_area_dict for actor_form in actor_forms2):
            c += 1

            current_actor_form =''
            for af in actor_forms2:
                if af in actor_area_dict:
                    current_actor_form = af

                    area_name = actor_area_dict[current_actor_form]
                    print(area_name)

                    try:
                        area_obj = ActorArea.objects.get(name = area_name)

                        actor.area = area_obj
                    except:
                        pass
                    break




    Actor.objects.bulk_update(
        actor_list,['area'],batch_size)

    print(f'Updated {c} Actor`s Area.')


def add_parameter_values(Country, parameter, model_name):
    value = parameter + "_id"
    order_by = value + "__name"

    documents_list = Document.objects.filter(country_id_id=Country.id).values(value).order_by(order_by).distinct()

    result_tag = ""
    for row in documents_list:
        parameter_id = row[value]
        if parameter_id is not None:
            para_obj = model_name.objects.get(id=parameter_id)
            parameter_id = para_obj.id
            parameter_name = para_obj.name

            tag = "<option value=" + str(parameter_id) + " >" + parameter_name + "</option>"

            if parameter_name not in ["", " ", None]:
                result_tag += tag

    json_result = {
        "options": result_tag
    }
    SearchParameters.objects.create(
        country=Country, parameter_name=parameter, parameter_values=json_result)


def Search_Parameters_Insert(Country):

    SearchParameters.objects.filter(country__id=Country.id).delete()

    parameters = {
        "category": Category,
        "subject": Subject,
    }

    for parameter, model_name in parameters.items():
        add_parameter_values(Country, parameter, model_name)

    # ----------------------------------------------
    result_tag = ''

    documents_list = Document.objects.filter(country_id_id=Country.id, date__isnull=False)

    min_year_res = -1
    max_year_res = -1
    if documents_list.count() > 0:
        max_year = documents_list.aggregate(Max('date'))["date__max"][0:4]
        min_year = documents_list.aggregate(Min('date'))["date__min"][0:4]
        min_year_res = int(min_year)
        max_year_res = int(max_year)

    if max_year_res != -1 and min_year_res != -1:
        for i in range(max_year_res ,(min_year_res-1), -1):
            tag = "<option value=" + str(i) + " >" + str(i) + "</option>"
            result_tag += tag

        json_result = {
            "options": result_tag
        }

        SearchParameters.objects.create(
            country=Country, parameter_name="FromYear", parameter_values=json_result)

        SearchParameters.objects.create(
            country=Country, parameter_name="ToYear", parameter_values=json_result)



def clustering_algorithms_to_db(Country):
    CreateList = []

    algorithm_abbreviation_dict = {
        "K-Means":"KMS",
        "Agglomerative":"AGG",
        "FCM":"FCM",
        "LDA":"LDA"
    }

    vector_abbreviation_dict = {
        "TF-IDF":"T",
        "LDA":"L",
        "BERT":"B"
    }

    min_k = 2
    max_k = 100
    step = 1

    ClusteringAlgorithm.objects.all().delete()

    ClusteringAlgorithmsFile = str(Path(config.PERSIAN_PATH, 'ClusteringAlgorithms.txt'))
    DocumentVectorTypesFile = str(Path(config.PERSIAN_PATH, 'DocumentVectorTypes.txt'))

    vector_names = []

    with open(DocumentVectorTypesFile, encoding="utf8") as f:
        lines = f.readlines()
        for vector_name in lines:
            vector_name = vector_name.replace("\n", "")
            vector_names.append(vector_name)
    f.close()

    ngram_types = [(1,1),(2,2)]
    with open(ClusteringAlgorithmsFile, encoding="utf8") as f:
        lines = f.readlines()
        for c_name in lines:
            c_name = c_name.replace("\n", "")

            for vector_name in vector_names:

                for cluster_count in range(min_k, (max_k + 1), step):

                    for ngram in ngram_types:
                        ngram = str(ngram)
                        result_count = ClusteringAlgorithm.objects.filter(
                        name=c_name,
                        ngram_type = ngram,
                        input_vector_type = vector_name,
                        cluster_count = cluster_count).count()

                        alg_abbreviation = algorithm_abbreviation_dict[c_name]
                        vec_abbreviation = vector_abbreviation_dict[vector_name]

                        res_abbreviation = alg_abbreviation + "-" + str(cluster_count) + "-" + ngram + "-" + vec_abbreviation


                        if result_count == 0:
                            ClusteringAlgorithm_obj = ClusteringAlgorithm(name=c_name,
                            input_vector_type = vector_name,
                            cluster_count = cluster_count,
                            ngram_type = ngram,
                            abbreviation = res_abbreviation)
                            CreateList.append(ClusteringAlgorithm_obj)
                        else:

                            ClusteringAlgorithm.objects.filter(
                            name=c_name,
                            ngram_type = ngram,
                            input_vector_type = vector_name,
                            cluster_count = cluster_count
                            ).update(
                                abbreviation = res_abbreviation)


    f.close()



    ClusteringAlgorithm.objects.bulk_create(CreateList)

    feature_selection_algorithms_to_db(Country)


def feature_selection_algorithms_to_db(Country):

    FeatureSelectionAlgorithmsFile = str(Path(config.PERSIAN_PATH, 'FeatureSelectionAlgorithms.txt'))

    with open(FeatureSelectionAlgorithmsFile, encoding="utf8") as f:
        lines = f.readlines()
        for f_name in lines:
            f_name = f_name.replace("\n", "")
            result_count = FeatureSelectionAlgorithm.objects.filter(name=f_name).count()

            if result_count == 0:
                FeatureSelectionAlgorithm.objects.create(name=f_name)
    f.close()


def apply(folder_name, Country):

    t = time.time()

    print("Roles_Insert ...")
    Roles_Insert()

    print("Update_Docs_fromExcel ...")
    Update_Docs_fromExcel(Country)

    print("ActorRolePatternKeywords_Insert ...")
    ActorRolePatternKeywords_Insert()

    print("Actors_Insert ...")
    Actors_Insert()


    print("Update_ActorsArea ...")
    Update_ActorsArea()

    print("Search_Parameters_Insert ...")
    Search_Parameters_Insert(Country)


    print("clustering_algorithms_to_db ...")
    clustering_algorithms_to_db(Country)


    print("feature_selection_algorithms_to_db ...")
    feature_selection_algorithms_to_db(Country)

    print("time ", time.time() - t)