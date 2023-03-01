from jdatetime import datetime as jdatetime
from django.shortcuts import redirect, get_object_or_404
import os
from random import randint
from hazm import *
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.utils.crypto import get_random_string
from django.forms import FileField
from doc.forms import ZipFileForm
from doc.models import *
from scripts import ZipFileExtractor, StratAutomating
from abdal import es_config
import shutil
import after_response
from django.db.models import Max, Min, F, IntegerField, Count, Q
from django.db.models.functions import Substr, Cast, Length
import datetime
from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from abdal import config
from pathlib import Path
import json
import math
from urllib.parse import urlparse
from itertools import chain, groupby
from collections import Counter
import numpy as np
import pandas as pd
from .decorators import allowed_users, unathenticated_user, is_login
from .const import *
import glob
from elasticsearch import Elasticsearch
from sklearn.metrics.pairwise import cosine_similarity
import string
from scripts.Persian.Preprocessing import standardIndexName


# ---------- elastic configs -------------------
es_url = es_config.ES_URL
client = Elasticsearch(es_url, timeout=30)
bucket_size = es_config.BUCKET_SIZE
search_result_size = es_config.SEARCH_RESULT_SIZE

book_index_name = es_config.Book_Index
doctic_doc_index = es_config.DOTIC_DOC_INDEX
doctic_para_index = es_config.DOTIC_PARA_INDEX

from doc.huggingface_views import *
import getpass
from persiantools.jdatetime import JalaliDate

SERVER_USER_NAME = config.SERVER_USER_NAME


# preprocessing function

@after_response.enable
def extractor(newdoc, newDoc, tasks_list):
    ZipFileExtractor.extractor(newdoc, newDoc, tasks_list, "")


def arabic_preprocessing(text):
    while "  " in text:
        text = text.replace("  ", " ")

    text = text.lstrip().rstrip().strip()
    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}

    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text


def deleter(name, filename, only_result):
    try:
        filename = str(os.path.basename(filename)).split(".")[0]
        result_path = os.path.join(config.RESULT_PATH, filename)
        shutil.rmtree(result_path)
        if not only_result:
            data_path = os.path.join(config.DATA_PATH, filename)
            doc_zip_path = os.path.join(config.ZIPS_PATH, filename + ".zip")
            shutil.rmtree(data_path)
            os.remove(doc_zip_path)
    except Exception as e:
        print(e)


def update_doc(request, id, language, ):
    host_url = urlparse(request.build_absolute_uri()).netloc

    file = get_object_or_404(Country, id=id)

    # file = Country.objects.get(file_id=id)
    # deleter(file.name, file.file.name, True)
    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]
    # start_automating.apply(folder_name)
    file.status = "Starting..."
    file.save()


    StratAutomating.apply.after_response(folder_name, file,
                                             "DocsParagraphsClustering_AIParagraphTopicLDA_LDAGraphData",
                                             host_url)  # AdvanceARIMAExtractor_ ActorTimeSeriesPrediction _DocsSubjectExtractor_DocsLevelExtractor_DocsReferencesExtractor_DocsActorsTimeSeriesDataExtractor_DocsCreateDocumentsListCubeData_DocsCreateSubjectCubeData_DocsCreateVotesCubeData_DocsCreateSubjectStatisticsCubeData_DocsCreateTemplatePanelsCubeData_DocsAnalysisLeadershipSlogan_DocsCreatePrinciplesCubeData_DocCreateBusinessAdvisorCubeData_DocsCreateRegularityLifeCycleCubeData_DocsExecutiveParagraphsExtractor_DocsClauseExtractor_DocsGraphCubeData_DocsCreateMandatoryRegulationsCubeData_DocsExecutiveClausesExtractor_DocsCreateActorInformationStackChartCubeData


    # from scripts.Persian import DocsParagraphVectorExtractor
    # DocsParagraphVectorExtractor.apply(folder_name, file)
    #DocsParagraphsClustering_AIParagraphTopicLDA_LDAGraphData
    # from es_scripts import IngestFullProfileAnalysisToElastic
    # IngestFullProfileAnalysisToElastic.apply.after_response(folder_name, file)

    # DocsSubjectExtractor2_DocsParagraphsClustering_AIParagraphTopicLDA_LDAGraphData
    # DocsSubjectAreaExtractor.apply(folder_name,file),DocsParagraphsClustering
    # AIParagraphTopicLDA_LDAGraphData-DocsActorsExtractor
    # DocsParagraphsClusteringCubeData,ClusteringGraphData

    # from scripts.Persian import DocsSubjectExtractor2
    # DocsSubjectExtractor2.apply.after_response(folder_name, file)

    # from scripts.Persian import DocProvisionsFullProfileAnalysis
    # DocProvisionsFullProfileAnalysis.apply.after_response(folder_name, file)

    return redirect('zip')


def Create_Folder():
    if not os.path.isdir(config.RESULT_PATH):
        os.mkdir(config.RESULT_PATH)
    if not os.path.isdir(config.DATA_PATH):
        os.mkdir(config.DATA_PATH)
    if not os.path.isdir(config.ZIPS_PATH):
        os.mkdir(config.ZIPS_PATH)


def UploadFile(request, country, language, tasks_list):
    Create_Folder()

    host_url = urlparse(request.build_absolute_uri()).netloc
    if request.method == 'POST':
        inputFile = request.FILES['inputFile']
        country_count = Country.objects.filter(name=country).count()
        file_ext = (inputFile.name).split(".")[-1]

        if country_count > 0:
            return JsonResponse({"response": "duplicate country"})
        elif file_ext != "zip":
            return JsonResponse({"response": "wrong format"})
        else:
            country_object = Country(name=country, language=language, file=inputFile, file_name=inputFile.name,
                                     status="Running")

            country_object.save()
            ZipFileExtractor.extractor(country_object, country_object, tasks_list, host_url)
            return JsonResponse({"response": "Ok"})


def get_task_list(request):
    file_path = str(Path(config.PERSIAN_PATH, 'TaskList.json'))
    data = json.load(open(file_path, encoding='utf-8'))
    return JsonResponse(data)


def get_book_maps(country_objects):
    dataset_map = {}
    # country_objects = country_objects.order_by("-id")
    country_objects = country_objects.order_by("id")
    for each in country_objects:
        id = each.id
        name = each.name
        language = each.language
        if language == "کتاب" and "کتاب" in name:
            dataset_map[id] = name
    return dataset_map

def fullProfileAnalysis(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocProvisionsFullProfileAnalysis2
    DocProvisionsFullProfileAnalysis2.apply(None, file)
    return redirect('zip')


def get_standard_maps(country_objects):
    dataset_map = {}
    # country_objects = country_objects.order_by("-id")
    country_objects = country_objects.order_by("id")
    for each in country_objects:
        id = each.id
        name = each.name
        language = each.language
        if language == "استاندارد":
            dataset_map[id] = name
    return dataset_map


def get_similarity_maps(graph_objects):
    dataset_map = {}
    for each in graph_objects:
        id = each.measure_id_id
        name = each.measure_id.name
        if id not in dataset_map:
            dataset_map[id] = name
    return dataset_map


# html load function

@allowed_users('admin_accept_user_comments')
def seeAllComment(request):
    comments = DocumentComment.objects.all().order_by('is_accept')

    result = []
    for c in comments:
        agreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=True).count()
        disagreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=False).count()

        result.append(
            {"comment": c.comment, "id": c.id, "first_name": c.user.first_name, "last_name": c.user.last_name,
             "agreed_count": agreed_count, "disagreed_count": disagreed_count, "document_name": c.document.name,
             "is_accept": c.is_accept, "time": c.time})

    return render(request, 'doc/admin_templates/admin_accept_user_comments.html', {'comments': result})


def seeAllComment2(request):
    comments = DocumentComment.objects.all()

    result = []
    for c in comments:
        agreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=True).count()
        disagreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=False).count()

        result.append(
            {"comment": c.comment, "id": c.id, "first_name": c.user.first_name, "last_name": c.user.last_name,
             "agreed_count": agreed_count, "disagreed_count": disagreed_count, "document_name": c.document.name,
             "is_accept": c.is_accept})

    return render(request, 'doc/admin_templates/admin_accept_user_comments2.html', {'comments': result})


@allowed_users('admin_accepted_user')
def seeAcceptedUser(request):
    activated_user = User.objects.all().filter(is_active=1)
    return render(request, 'doc/admin_templates/admin_accepted_user.html', {'activated_user': activated_user})


@allowed_users('admin_upload')
def admin_upload(request):
    return render(request, 'doc/admin_templates/admin_upload.html')


@allowed_users('super_admin_user_log')
def showUserLogs(request):
    users = User.objects.all().filter(is_active=1)
    return render(request, 'doc/admin_templates/admin_user_log.html', {'users': users})


@allowed_users('admin_user_recommendation')
def get_user_recommendation(request):
    recommendation = Recommendation.objects.all()
    return render(request, 'doc/admin_templates/admin_user_recommendation.html', {'recommendation': recommendation})


@allowed_users('admin_user_report_bug')
def get_user_report_bug(request):
    reports = ReportBug.objects.order_by('checked', 'date')
    return render(request, 'doc/admin_templates/admin_user_report_bug.html', {'report_bug': reports})


@allowed_users('admin_waiting_user')
def getRegisteredUser(request):
    data = User.objects.all().filter(enable=1, is_active=0)
    return render(request, 'doc/admin_templates/admin_waiting_user.html', {'data': data})


def getRegisteredUser2(request):
    data = User.objects.all().filter(enable=1, is_active=0)
    return render(request, 'doc/admin_templates/admin_waiting_user2.html', {'data': data})


@allowed_users('AI_topics')
def AI_topics(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/main_templates/lda_clustering.html', {'countries': country_map})


# @allowed_users('AI_topics')
def paragrraph_clustering(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/main_templates/paragraph_clustering.html', {'countries': country_map})


def comparison(request):
    return render(request, 'doc/main_templates/references_comparison.html')


def recommendation(request):
    return render(request, 'doc/user_templates/recommendation.html')


def report_bug(request):
    return render(request, 'doc/user_templates/report_bug.html')


# @allowed_users('AI_topics')
def decision_tree(request, country_id, clustering_algorithm_id):
    country = Country.objects.get(id=country_id)

    result = {"id": country.id,
              "name": country.name,
              "folder": str(country.file.name.split("/")[-1].split(".")[0]),
              "language": country.language,
              "clustering_algorithm_id": clustering_algorithm_id
              }

    return render(request, 'doc/main_templates/decision_tree.html', {"country_info": result})


@allowed_users('advanced_graph')
def graph2(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/main_templates/graph.html', {'countries': country_map})


@allowed_users('es_search')
def es_search(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/main_templates/search.html', {'countries': country_map})


def dendrogram(request, country_id, ngram_type):
    country = Country.objects.get(id=country_id)
    folder = str(country.file.name.split("/")[-1].split(".")[0])
    file_path = "dendrogram_plots/" + folder + "_" + str(ngram_type) + '_dendrogram.png'

    return render(request, 'doc/main_templates/dendrogram.html', {"file_path": file_path})

def showDeployLogs(request):
    return render(request, 'doc/user_templates/deploy_server_time.html')


def index(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/main_templates/index.html', {'countries': country_map})


def information(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/main_templates/document_profile.html', {'countries': country_map})


def knowledgeGraph(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/main_templates/knowledge_graph.html', {'countries': country_map})


def following_document_comments(request):
    return render(request, 'doc/user_templates/following_document_comments.html')


def notes(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/user_templates/notes.html', {'countries': country_map})


@unathenticated_user
def signup(request):
    return render(request, "doc/user_templates/signup.html")


@unathenticated_user
def login(request):
    return render(request, "doc/user_templates/login.html")


@allowed_users()
def ManageUsersTab(request):
    return render(request, 'doc/admin_templates/manage_admins.html')


@allowed_users('ManualClustering')
def ManualClustering(request):
    country_list = Country.objects.all()
    country_map = get_country_maps(country_list)
    return render(request, 'doc/main_templates/manual_clustering.html', {'countries': country_map})


def ShowMyUserProfile(request):
    return render(request, "doc/user_templates/myprofile.html", {})


def ShowUserProfile(request):
    return render(request, "doc/user_templates/userprofile.html", {})


def sentiment_analysis_panel(request):
    return render(request, 'doc/main_templates/paragraph_profile.html')


def resource_profile(request):
    return render(request, 'doc/main_templates/resource_profile.html')


def upload_zip_file(request):
    # documents = ZipFile.objects.filter(uploader=request.user)
    query_set1 = Country.objects.filter()
    query_set2 = ''

    documents = chain(query_set1, query_set2)

    # if request.user.is_superuser:
    FileField(label='Select a file', help_text='max. 10 megabytes')
    # Handle file upload
    file_name = request.POST.get('file_name')
    language = request.POST.get('language')
    if Country.objects.filter(name=file_name):
        return render(request, 'doc/admin_templates/upload.html',
                      {'status': 'File with this name exists', 'color': 'red', 'form': ZipFileForm(),
                       'files': documents})
    if request.method == 'POST':
        if request.POST.get('delete_items') is not None:
            id = request.POST.get('delete_items')
            id = str(id).replace('delete ', '')
            file = Country.objects.get(file_id=id)
            file.delete()
            deleter(file.name, file.file.name, False)
            # documents = Country.objects.filter(uploader=request.user)
            query_set1 = Country.objects.filter()
            query_set2 = ''

            documents = chain(query_set1, query_set2)
            return render(request, 'doc/admin_templates/upload.html',
                          {'status': 'File deleted successfully', 'color': 'green', 'form': ZipFileForm(),
                           'files': documents})
        elif request.POST.get('update_items') is not None:
            id = request.POST.get('update_items')
            id = str(id).replace('update ', '')
            file = Country.objects.get(id=id)
            deleter(file.name, file.file.name, True)
            my_file = file.file.path
            my_file = str(os.path.basename(my_file))
            dot_index = my_file.rfind('.')
            folder_name = my_file[:dot_index]
            # start_automating.apply(folder_name)
            # file.status = "Processing"
            file.save()
            StratAutomating.apply.after_response(folder_name, file)
            # documents = Country.objects.filter(uploader=request.user)
            # query_set1 = Country.objects.filter()
            # query_set2 = en_model.Country.objects.filter()

            documents = Country.objects.filter()
            return render(request, 'doc/admin_templates/upload.html',
                          {'status': 'File updated successfully', 'form': ZipFileForm(), 'files': documents})
        else:
            cur_user = request.user
            cur_file = request.FILES['docfile']
            if '.rar' in str(cur_file):
                return render(request, 'doc/admin_templates/upload.html',
                              {'status': 'You can\'t choose rar files', 'form': ZipFileForm(), 'files': documents})
            founded_file = Country.objects.filter(name=file_name)
            if len(str(file_name)) == 0:
                return render(request, 'doc/admin_templates/upload.html',
                              {'status': 'No named entered', 'form': ZipFileForm(), 'files': documents})
            if len(founded_file) != 0:
                founded_file = Country.objects.get(name=file_name)
                founded_file.delete()
                deleter(founded_file.name, founded_file.file.name, True)
            # newdoc = Country(file=cur_file, name=file_name, status="Processing", uploader=cur_user)
            newdoc = Country(file=cur_file, file_name=cur_file,
                             name=file_name, language=language, status="Processing")
            newdoc.save()
            # zip_extractor.extractor(newdoc)
            extractor.after_response(newdoc, newdoc)
            return render(request, 'doc/admin_templates/upload.html',
                          {'status': 'File uploaded successfully', 'form': ZipFileForm(), 'files': documents})
    else:
        pass

    return render(request, 'doc/admin_templates/upload.html', {'form': ZipFileForm(), 'files': documents})


# upload page link

def static_data_import_db(request, id, language):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB
    StaticDataImportDB.apply(None, file)
    return redirect('zip')

def update_docs_from_excel(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB
    StaticDataImportDB.Update_Docs_fromExcel(file)
    return redirect('zip')


def insert_docs_to_rahbari_table(request, id):
    file = get_object_or_404(Country, id=id)

    from scripts.Persian import StaticDataImportDB
    StaticDataImportDB.Rahbari_Insert_fromExcel(file)

    return redirect('zip')


def revoked_types_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    StaticDataImportDB.revoked_types_to_db(Country)
    return redirect('zip')


def rahbari_update_fields_from_file(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    StaticDataImportDB.Rahbari_Update_Fields_From_File(folder_name, file)

    return redirect('zip')


def clustering_algorithms_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    StaticDataImportDB.clustering_algorithms_to_db(Country)
    return redirect('zip')


def rahbari_labels_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    StaticDataImportDB.rahbari_labels_to_db(Country)
    return redirect('zip')

def document_json_list(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocsCreateDocumentsListCubeData
    DocsCreateDocumentsListCubeData.apply(None, file)
    return redirect('zip')





def actors_static_data_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB
    # StaticDataImportDB.Actors_Insert()
    # StaticDataImportDB.Actor_Graph_Types_Insert()
    StaticDataImportDB.Area_SubArea_Insert()
    StaticDataImportDB.Update_ActorsArea()
    return redirect('zip')


def search_parameters_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    StaticDataImportDB.Search_Parameters_Insert(file)
    return redirect('zip')


def rahbari_search_parameters_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    StaticDataImportDB.Rahbari_Search_Parameters_Insert(file)
    return redirect('zip')


def subject_area_keywords_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    StaticDataImportDB.Subjects_area_Insert(file)
    return redirect('zip')


def create_judgments_table(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    StaticDataImportDB.create_judgments_table_from_excel(file)
    return redirect('zip')


@is_login
def Admin(request):
    username = request.COOKIES.get('username')
    user = User.objects.all().get(username=username)
    if user.is_super_user:
        return redirect('manage_users_tab')
    else:
        panels = UserPanels.objects.filter(user=user).order_by('panel__id')
        if panels:
            address = panels[0].panel.panel_english_name
            return redirect(address)
        else:
            return HttpResponse('You are not authorized to view this page')


def create_standards_table(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    StaticDataImportDB.create_standard_table_from_excel(folder_name, file)
    return redirect('zip')


def update_file_name_extention(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    StaticDataImportDB.update_file_name_extention(folder_name, file)
    return redirect('zip')




def regulators_static_import_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB
    StaticDataImportDB.Regulators_Insert()
    return redirect('zip')





def ingest_documents_to_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestDocumentsToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestDocumentsToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_document_actor_to_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestDocumentActorToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestDocumentActorToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_actor_supervisor_to_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestActorSupervisorToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestActorSupervisorToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_spatiotemporal_to_index(request, id):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestSpatioTemporalDataToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestSpatioTemporalDataToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_judgments_to_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestJudgmentsToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestJudgmentsToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_revoked_documents(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestRevokedDocument

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestRevokedDocument.apply(folder_name, file)
    return redirect('zip')


def ingest_paragraphs_to_index(request, id, language, is_for_ref):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestParagraphsToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestParagraphsToElastic.apply(folder_name, file, is_for_ref)
    return redirect('zip')


def ingest_clustering_paragraphs_to_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestClusteringParagraphsToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestClusteringParagraphsToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_standard_documents_to_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestStandardDocumentsToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestStandardDocumentsToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_standard_documents_to_sim_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestDocumentsToSimilarityIndex

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    similarity_list = ['BM25']

    for sim_type in similarity_list:
        IngestDocumentsToSimilarityIndex.apply(folder_name, file, sim_type)
    return redirect('zip')


def ingest_terminology_to_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestTerminologyToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestTerminologyToElastic.apply(folder_name, file)
    return redirect('zip')


def ingest_rahbari_to_index(request, id):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestRahbariToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestRahbariToElastic.apply(folder_name, file)

    return redirect('zip')


def ingest_document_collective_members_to_index(request, id):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestDocumentCollectiveMembersToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestDocumentCollectiveMembersToElastic.apply(folder_name, file)

    return redirect('zip')


def ingest_rahbari_to_sim_index(request, id):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestRahbariDocumentsToSimilarityIndex

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    similarity_list = ['BM25', 'DFR', 'DFI']

    for sim_type in similarity_list:
        IngestRahbariDocumentsToSimilarityIndex.apply(folder_name, file, sim_type)

    return redirect('zip')




def rahbari_similarity_calculation(request, id):
    file = get_object_or_404(Country, id=id)
    from es_scripts import RahbariDocsSimilarityCalculation

    RahbariDocsSimilarityCalculation.apply(None, file)
    return redirect('zip')


def paragraphs_similarity_calculation(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import ParagraphsSimilarityCalculation

    ParagraphsSimilarityCalculation.apply(None, file)
    return redirect('zip')



def rahbari_paragraphs_similarity_calculation(request, id):
    file = get_object_or_404(Country, id=id)
    from es_scripts import RahbariParagraphSimilarity

    RahbariParagraphSimilarity.apply(None, file)
    return redirect('zip')


def collective_static_data_to_db(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import StaticDataImportDB
    StaticDataImportDB.Collective_Actors_Insert()
    return redirect('zip')



def delete_doc(request, id, language):
    file = Country.objects.get(id=id)

    deleter(file.name, file.file.name, False)
    file.delete()
    return redirect('zip')


def get_country_maps(country_objects):
    dataset_map = {}
    # country_objects = country_objects.order_by("-id")
    country_objects = country_objects.order_by("id")
    for each in country_objects:
        id = each.id
        name = each.name
        language = each.language
        if language == "فارسی":
            dataset_map[id] = name
    return dataset_map


# views function

def GetDocumentsPredictSubjectLDA(request, country_id, number_of_topic):
    country_id = int(country_id)
    result_without = []
    result_difference = []

    para_id_list = list(AILDAParagraphToTopic.objects.filter(
        country_id=country_id, number_of_topic=number_of_topic).values_list("paragraph_id", flat=True))

    para_list = DocumentParagraphs.objects.filter(document_id__country_id__id=country_id).filter(
        ~Q(id__in=para_id_list)).annotate(
        doc_id=F('document_id__id')).annotate(
        doc_name=F('document_id__name')).annotate(
        category_name=F('document_id__category_name')).annotate(
        document_date=F('document_id__date')).annotate(
        subject_name=F('document_id__subject_name')).annotate(text_len=Length('text')).filter(
        text_len__gt=80)[:300]

    for row in para_list:
        res = {
            'paragraph_id': row.id,
            'paragraph_text': row.text,
            'document_id': row.doc_id,
            'document_name': row.doc_name,
            'subject_name': row.subject_name if row.subject_name != None else 'نامشخص',
            'category_name': row.category_name if row.category_name != None else 'نامشخص',
            'document_date': row.document_date if row.document_date != None else 'نامشخص',
        }
        result_without.append(res)

    filesList = AI_Paragraph_Subject_By_LDA.objects.filter(
        country_id=country_id, number_of_topic=number_of_topic, subject__isnull=False).order_by('-Accuracy').annotate(
        doc_id=F('paragraph__document_id__id')).annotate(
        doc_name=F('paragraph__document_id__name'))[:300]

    for row in filesList:
        res = {
            'doc_id': row.doc_id,
            'doc_name': row.doc_name,
            'paragraph_id': row.paragraph.id,
            'paragraph_text': row.paragraph.text,
            'document_subject': row.subject,
            'document_predict_subject': row.subject_predict,
            'topic_id': row.topic.id,
        }
        result_difference.append(res)

    return JsonResponse(
        {'documentsDifferenceSubjectLDA': result_difference, 'documentsWithoutSubjectLDA': result_without})


def AIGet_Topic_Centers_CahrtData(request, country_id, number_of_topic):
    heatmap_chart_data = AILDAResults.objects.get(
        country__id=country_id, number_of_topic=number_of_topic).heatmap_chart_data["data"]

    topic_list = AIParagraphLDATopic.objects.filter(
        country__id=country_id, number_of_topic=number_of_topic).values()

    cluster_size_chart_data = []

    for topic in topic_list:
        topic_name = topic["topic_name"]
        paragraph_count = topic["paragraph_count"]
        cluster_size_chart_data.append([topic_name, paragraph_count])

    return JsonResponse({'cluster_size_chart_data': cluster_size_chart_data,
                         "heatmap_chart_data": heatmap_chart_data})


def AIGetLDATopic(request, country_id, number_of_topic, username):
    lda_topics = []
    all_para_count = 0

    temp = AIParagraphLDATopic.objects.filter(country__id=country_id, number_of_topic=number_of_topic)

    user_topic_labels = UserLDATopicLabel.objects.filter(
        topic__country__id=country_id,
        topic__number_of_topic=number_of_topic,
        user__username=username).values()

    user_label_dict = {}

    if len(user_topic_labels) > 0:
        for row in user_topic_labels:
            user_label_dict[row['topic_id']] = row['label']

    for record in temp:
        record_id = record.id
        sorted_word_list = [k for k, v in sorted(record.words.items(), reverse=True, key=lambda item: float(item[1]))]
        user_label_value = user_label_dict[record_id] if record_id in user_label_dict else 'بدون برچسب'

        user_label_input = "<div>" + \
                           "<input id ='" + str(
            record_id) + "' class='form-control p-1 text-center d-block w-100' value ='" + user_label_value + "' type= 'text'/>" + \
                           "<button onclick=save_user_labelLDA('" + str(
            record_id) + "') class = 'btn btn-outline-success mt-1 p-0 d-block w-100'>ذخیره</button>" + \
                           "</div>"

        lda_topics.append({
            'id': record.id,
            'topic_id': record.topic_id,
            'topic_name': record.topic_name,
            'words': " - ".join(sorted_word_list),
            'entropy': record.correlation_score,
            'subject': record.dominant_subject_name,
            'paragraph_count': record.paragraph_count,
            'user_label': user_label_input
        })
        all_para_count += record.paragraph_count
    return JsonResponse({'lda_topics': lda_topics, 'all_para_count': all_para_count})


def BoostingSearchParagraph_Column_ES(request, country_id, field_name, field_value, curr_page, result_size):
    res_query = {"bool": {
        "filter": [
            {
                "term":
                    {
                        field_name: {
                            "value": field_value
                        }
                    }
            },
            {
                "range": {
                    "attachment.content_length": {
                        "gte": 80
                    }
                }
            }
        ],
        "must": {
            "bool": {
                "should": []
            }
        },
        "must_not": []
    }
    }

    keyword_score_dict = dict(request.POST)

    cluser_keyword_data = keyword_score_dict['cluser_keyword_data'][0].split(',')
    cluster_delete_data = keyword_score_dict['cluster_delete_data'][0].split(',')

    for index in range(0, len(cluser_keyword_data), 2):
        keyword = cluser_keyword_data[index]
        score = int(cluser_keyword_data[index + 1])

        title_query = {
            "multi_match": {
                "query": keyword,
                "type": "phrase",
                "fields": ["document_name"],
                "boost": score * 10
            }
        }
        res_query['bool']['must']['bool']['should'].append(title_query)

        word_query = {
            "multi_match": {
                "query": keyword,
                "type": "phrase",
                "fields": ["attachment.content"],
                "boost": score
            }
        }
        res_query['bool']['must']['bool']['should'].append(word_query)

    for delete_keyword in cluster_delete_data:
        delete_title_query = {
            "multi_match": {
                "query": delete_keyword,
                "type": "phrase",
                "fields": ["document_name"],
            }
        }
        res_query['bool']['must_not'].append(delete_title_query)

        delete_word_query = {
            "multi_match": {
                "query": delete_keyword,
                "type": "phrase",
                "fields": ["attachment.content"],
            }
        }
        res_query['bool']['must_not'].append(delete_word_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentParagraphs.__name__ + '_graph')
    # index_name = 'doticfull_documentparagraphs_graph'
    # index_name = 'fava_documentparagraphs_graph'

    from_value = (curr_page - 1) * result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name', 'paragraph_id', 'attachment.content'],

                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em class='text-primary fw-bold'>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }

                             )

    result = response['hits']['hits']
    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name)['count']

    response_dict = {
        'total_hits': total_hits,
        "curr_page": curr_page,
        "result": result
    }
    return JsonResponse(response_dict)


def BoostingSearchParagraph_ES(request, country_id, curr_page, result_size):
    res_query = {"bool": {
        "filter": [
            {
                "range": {
                    "attachment.content_length": {
                        "gte": 80
                    }
                }
            }
        ],
        "must": {
            "bool": {
                "should": []
            }
        },
        "must_not": []
    }
    }

    keyword_score_dict = dict(request.POST)

    cluser_keyword_data = keyword_score_dict['cluser_keyword_data'][0].split(',')
    cluster_delete_data = keyword_score_dict['cluster_delete_data'][0].split(',')

    for index in range(0, len(cluser_keyword_data), 2):
        keyword = cluser_keyword_data[index]
        score = int(cluser_keyword_data[index + 1])

        title_query = {
            "multi_match": {
                "query": keyword,
                "type": "phrase",
                "fields": ["document_name"],
                "boost": score * 10
            }
        }
        res_query['bool']['must']['bool']['should'].append(title_query)

        word_query = {
            "multi_match": {
                "query": keyword,
                "type": "phrase",
                "fields": ["attachment.content"],
                "boost": score
            }
        }
        res_query['bool']['must']['bool']['should'].append(word_query)

    for delete_keyword in cluster_delete_data:
        delete_title_query = {
            "multi_match": {
                "query": delete_keyword,
                "type": "phrase",
                "fields": ["document_name"],
            }
        }
        res_query['bool']['must_not'].append(delete_title_query)

        delete_word_query = {
            "multi_match": {
                "query": delete_keyword,
                "type": "phrase",
                "fields": ["attachment.content"],
            }
        }
        res_query['bool']['must_not'].append(delete_word_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentParagraphs.__name__ + '_graph')
    # index_name = 'doticfull_documentparagraphs_graph'

    # index_name = 'fava_documentparagraphs_graph'

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "subject-agg": {
            "terms": {
                "field": "subject_name.keyword",
                "size": bucket_size
            }
        },

        "category-agg": {
            "terms": {
                "field": "category_name.keyword",
                "size": bucket_size
            }
        },
        "document-year-agg": {
            "terms": {
                "field": "document_year",
                "size": bucket_size
            }
        }

    }

    from_value = (curr_page - 1) * result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name', 'paragraph_id', 'attachment.content'],
                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             aggregations=res_agg,
                             size=result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em class='text-primary fw-bold'>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }

                             )

    result = response['hits']['hits']
    aggregations = response['aggregations']
    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name)['count']

    response_dict = {
        'total_hits': total_hits,
        'aggregations': aggregations,
        "curr_page": curr_page,
        "result": result
    }
    return JsonResponse(response_dict)


def forgot_password(request):
    return render(request, 'doc/user_templates/forgot_password.html')


def forgot_password_by_email(request, email):
    users = User.objects.filter(email=email)
    if len(users) == 0:
        return JsonResponse({"status": "OK"})

    user = users[0]
    token = get_random_string(length=50)
    user.reset_password_token = token
    user.reset_password_expire_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
    user.save()

    template = """
    لطفا برای بازیابی کلمه عبور بر روی لینک زیر کلیک کنید.

    در صورتی که قصد بازیابی ندارید این پیام را نادیده بگیرید.
    """
    template += f'http://rahnamud.ir:7074/reset-password/{user.id}/{token}'

    send_mail(
        subject='بازیابی کلمه عبور',
        message=template,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email])

    return JsonResponse({"status": "OK"})


def reset_password_check(request, user_id, token):
    url_is_valid = False
    try:
        user = User.objects.get(pk=user_id)
        if (not (
                user.reset_password_token is None)) and user.reset_password_token == token and user.reset_password_expire_time >= timezone.now():
            url_is_valid = True
    except:
        user_id = ""

    return render(request, 'doc/user_templates/reset_password.html',
                  {"url_is_valid": url_is_valid, "user_id": user_id, "token": token})


def reset_password(request, user_id, token, password):
    user = User.objects.get(pk=user_id)

    if (not (
            user.reset_password_token is None)) and user.reset_password_token == token and user.reset_password_expire_time >= timezone.now():
        user.password = make_password(password)
        user.reset_password_token = None
        user.save()
        return JsonResponse({"status": "OK"})

    return JsonResponse({"status": "Not OK"})


def ChangePassword(request, old_password, new_password):
    username = request.COOKIES.get('username')
    user = User.objects.get(username=username)
    check = check_password(old_password, user.password)
    if check:
        user.password = make_password(new_password)
        user.save()
        return JsonResponse({"status": "OK"})
    else:
        return JsonResponse({"status": "wrong password"})


def SaveUserLog(user_id, ip, url):
    date_time = datetime.datetime.now()
    UserLogs.objects.create(user_id_id=user_id, user_ip=ip,
                            page_url=url, visit_time=date_time)


def CheckUserLogin(request, username, password, ip):
    user = User.objects.filter(username=username)

    if user.count() == 0:
        SaveUserLog(None, ip, "username not found")
        return JsonResponse({"status": "not found"})
    elif not check_password(password, user[0].password):
        SaveUserLog(user[0].id, ip, "wrong password")
        return JsonResponse({"status": "wrong password"})
    elif user[0].is_active == 0:
        SaveUserLog(user[0].id, ip, "not active check")
        return JsonResponse({"status": "not active"})
    elif user[0].is_active == -1:
        SaveUserLog(user[0].id, ip, "de active check")
        return JsonResponse({"status": "de active"})
    # elif user[0].is_super_user:
    #     last_login = datetime.datetime.now()
    #     user.update(last_login=last_login)
    #     return JsonResponse({"status": "found admin"})
    else:
        last_login = datetime.datetime.now()
        user.update(last_login=last_login)

        SaveUserLog(user[0].id, ip, "login")

        return JsonResponse({"status": "found user"})


@allowed_users()
def CreateOrDeleteUserPanel(request, panel_name, username):
    CreatePanel(request)
    panel = Panels.objects.all().get(panel_english_name=panel_name)
    user = User.objects.all().get(username=username)
    user_admin_panels = UserPanels.objects.filter(panel=panel, user=user)
    if user_admin_panels:
        UserPanels.objects.get(
            panel=panel,
            user=user
        ).delete()
        return JsonResponse({"status": "deleted"})
    else:
        UserPanels.objects.create(
            panel=panel,
            user=user
        )
        return JsonResponse({"status": "created"})


def CreateReportBug(request, username, report_bug_text, panel_id, branch_id):
    user = User.objects.get(username=username)
    main_panel = MainPanels.objects.all().get(id=panel_id)
    panel = Panels.objects.all().get(id=branch_id)
    ReportBug.objects.create(
        user=user,
        panel_id=main_panel,
        branch_id=panel,
        report_bug_text=report_bug_text,
        date=str(jdatetime.strftime(jdatetime.now(), "%H:%M:%S %Y-%m-%d"))
    )
    return JsonResponse({"status": "OK"})


def Excel_Topic_Paragraphs_ES(request, country_id, topic_id, result_size, curr_page, username):
    res_query = {"bool": {
        "must": [
            {
                "term": {
                    "topic_id.keyword": {
                        "value": topic_id}
                }
            }
        ],

        "should": []
    }}
    word_score_dict = ClusterTopic.objects.get(id=topic_id).words

    for word, score in word_score_dict.items():
        word = word.strip()
        integer_score = int(float(score) * 10000)
        boost_score = integer_score if integer_score > 0 else 1

        word_query = {
            "match_phrase": {
                "attachment.content": {
                    "query": word,
                    "boost": boost_score
                }
            }
        }

        res_query['bool']['should'].append(word_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, ParagraphsTopic.__name__)

    # ---------------------- Get Chart Data -------------------------

    from_value = (curr_page - 1) * result_size

    response = client.search(index=index_name,
                             _source_includes=['document_name'
                                 , 'attachment.content', 'topic_name',
                                               'score'],
                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size

                             )

    result = response['hits']['hits']

    result_range = str(from_value) + " تا " + str(from_value + len(result))

    paragraph_list = [
        [doc['_source']['document_name']
            , doc['_source']['attachment']['content'],
         doc['_source']['score']] for doc in result]

    cluster_name = ClusterTopic.objects.get(id=topic_id).name.replace('C', 'شماره ')

    try:
        user_topic_label = UserTopicLabel.objects.get(
            topic__id=topic_id,
            user__username=username).label
    except:
        user_topic_label = 'بدون برچسب'

    file_dataframe = pd.DataFrame(paragraph_list, columns=["نام خبر", "متن پاراگراف", "امتیاز"])

    file_name = country_obj.name + " - " + "احکام خوشه " + cluster_name + \
                " - " + user_topic_label + " - " + result_range + ".xlsx"

    file_path = os.path.join(config.MEDIA_PATH, file_name)
    file_dataframe.to_excel(file_path, index=False)

    return JsonResponse({"file_name": file_name})


@allowed_users()
def CreatePanel(request):
    for main_panel, panel in AllPanels.items():
        persian_name = panel['persian_name']
        parent = None
        try:
            parent = MainPanels.objects.create(
                panel_persian_name=persian_name,
                panel_english_name=main_panel
            )
        except:
            parent = MainPanels.objects.get(
                panel_persian_name=persian_name,
                panel_english_name=main_panel
            )
        sub_panels = panel['sub_panels']
        for epanel, ppanel in sub_panels.items():
            try:
                Panels.objects.create(
                    parent=parent,
                    panel_persian_name=ppanel,
                    panel_english_name=epanel
                )
            except:
                pass

    panels = Panels.objects.all().order_by('id')
    result = []
    for panel in panels:
        id = panel.id
        persian_name = panel.panel_persian_name
        english_name = panel.panel_english_name

        result.append({
            "id": id,
            "persian_name": persian_name,
            "english_name": english_name,
        })

    # for main_panel,persian_name in Other_Panels.items():
    #     parent = None
    #     try:
    #         parent = MainPanels.objects.create(
    #             panel_persian_name = persian_name,
    #             panel_english_name = main_panel
    #         )
    #     except:
    #         parent = MainPanels.objects.get(
    #             panel_persian_name = persian_name,
    #             panel_english_name = main_panel
    #         )

    #     try:
    #         Panels.objects.create(
    #             parent = parent,
    #             panel_persian_name = persian_name,
    #             panel_english_name = main_panel
    #         )
    #     except:
    #         pass
    return result


def GetAllPanels(request, username=None):
    CreatePanel(request)

    if username == None:
        username = request.COOKIES.get('username')
    user = User.objects.all().get(username=username)
    user_panels = UserPanels.objects.filter(user=user).order_by('panel__id')

    user_panel_ids = [user_panel.panel_id for user_panel in user_panels]

    main_panels = MainPanels.objects.all().order_by('id')
    ret_res = {'all_panels': []}

    for main_panel in main_panels:
        ret_res['all_panels'].append({'id': main_panel.id,
                                      'english_name': main_panel.panel_english_name,
                                      'persian_name': main_panel.panel_persian_name,
                                      'sub_panels': []})
        sub_panels = Panels.objects.all().filter(parent__id=main_panel.id).order_by('id')
        for panel in sub_panels:
            new_panel = {}
            new_panel['id'] = panel.id
            new_panel['english_name'] = panel.panel_english_name
            new_panel['persian_name'] = panel.panel_persian_name
            ret_res['all_panels'][-1]['sub_panels'].append(new_panel)

    for panel in ret_res['all_panels']:
        panel['sub_panels'] = list(filter(lambda sub: sub['id'] in user_panel_ids, panel['sub_panels']))

    ret_res['all_panels'] = list(filter(lambda panel: len(panel['sub_panels']) != 0, ret_res['all_panels']))

    return JsonResponse(ret_res)


@is_login
def GetAllowedPanels(request, username=None):
    if username == None:
        username = request.COOKIES.get('username')
    user = User.objects.all().get(username=username)
    panels = UserPanels.objects.filter(user=user).order_by('panel__id')
    user_panel = []
    for panel in panels:
        panel_name = panel.panel.panel_english_name
        user_panel.append(panel_name)

    ret_res = {'main_panels': {}}

    for main_panel, panel_info in AllPanels.items():
        ret_res['main_panels'][main_panel] = []
        for panel in panel_info['sub_panels'].keys():
            if panel in user_panel:
                ret_res['main_panels'][main_panel].append(panel)

    # temporary ------------------------------------
    if (user.is_super_user and
            'standards_analysis' in ret_res['main_panels'] and
            'books_analysis' in ret_res['main_panels'] and
            'approvals_analysis' in ret_res['main_panels']):
        del ret_res['main_panels']['standards_analysis']
        del ret_res['main_panels']['books_analysis']
    # temporary ------------------------------------

    result = []
    for panel in panels:
        panel_name = panel.panel.panel_english_name
        result.append(panel_name)
    ret_res['panels'] = result

    panels = Panels.objects.all()
    all_panels = []
    for panel in panels:
        english_name = panel.panel_english_name
        # temporary ------------------------------------
        if panel.parent.panel_english_name in ret_res['main_panels']:
            # temporary ------------------------------------

            all_panels.append(english_name)
    ret_res['all_panels'] = all_panels

    all_admin_panels = []
    for panel in AllPanels['admin_panels']['sub_panels'].keys():
        all_admin_panels.append(panel)
    ret_res['all_admin_panels'] = all_admin_panels

    ret_res['is_super_user'] = '0'
    if user.is_super_user:
        ret_res['is_super_user'] = '1'
        ret_res['panels'] = all_panels

    return JsonResponse(ret_res)


@is_login
def GetPermissions(request, username):
    user = User.objects.all().get(username=username)
    panels = UserPanels.objects.filter(user=user).order_by('panel__id')
    user_panel = []
    for panel in panels:
        panel_name = panel.panel.panel_english_name
        user_panel.append(panel_name)

    ret_res = {'all_panels': [], 'user_panels': user_panel}

    for main_panel, panel_info in AllPanels.items():
        ret_res['all_panels'].append(
            {'main_panel': main_panel, 'persian_name': panel_info['persian_name'], 'sub_panels': []})
        for panel in panel_info['sub_panels'].keys():
            new_panel = {}
            new_panel['english_name'] = panel
            new_panel['persian_name'] = panel_info['sub_panels'][panel]
            ret_res['all_panels'][-1]['sub_panels'].append(new_panel)

    return JsonResponse(ret_res)


@is_login
def GetPermissionsExcel(request):
    panels = CreatePanel(request)
    persian_panels = {panel['english_name']: panel['persian_name'] for panel in panels}
    activated_user = User.objects.all().filter(is_active=1, is_super_user=False)
    result = []

    for user in activated_user:
        new_user = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'phone': user.mobile,
        }
        user_admin_panel = UserPanels.objects.all().filter(user_id=user.id)
        user_panels = [panel.panel.panel_english_name for panel in user_admin_panel]
        for panel in panels:
            en_name = panel['english_name']
            if en_name in user_panels:
                new_user[en_name] = '✅'
            else:
                new_user[en_name] = '❌'

        result.append(new_user)

    return JsonResponse({"users": result, "panels": persian_panels})


def Get_Topic_Paragraphs_ES(request, country_id, topic_id, result_size, curr_page, get_paragraphs, get_aggregations):
    res_query = {"bool": {
        "must": [
            {
                "term": {
                    "topic_id.keyword": {
                        "value": topic_id}
                }
            }
        ],

        "should": []
    }}
    word_score_dict = ClusterTopic.objects.get(id=topic_id).words

    for word, score in word_score_dict.items():
        word = word.strip()
        integer_score = int(float(score) * 10000)
        boost_score = integer_score if integer_score > 0 else 1

        word_query = {
            "match_phrase": {
                "attachment.content": {
                    "query": word,
                    "boost": boost_score
                }
            }
        }

        res_query['bool']['should'].append(word_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, ParagraphsTopic.__name__)

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "category-agg": {
            "terms": {
                "field": "category_name.keyword",
                "size": bucket_size
            }
        },
        "subject-agg": {
            "terms": {
                "field": "subject_name.keyword",
                "size": bucket_size
            }
        },

        "document-year-agg": {
            "terms": {
                "field": "document_year",
                "size": bucket_size
            }
        }

    }

    from_value = (curr_page - 1) * result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name',
                                               'paragraph_id', 'attachment.content',
                                               'topic_id', 'topic_name',
                                               'score'],

                             request_timeout=40,
                             query=res_query,
                             aggregations=res_agg,
                             from_=from_value,
                             size=result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em class='text-primary fw-bold'>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }

                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    aggregations = response['aggregations']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    response_dict = {
        'total_hits': total_hits,
        "curr_page": curr_page,
        'aggregations': aggregations
    }
    if get_paragraphs == 1:
        response_dict["result"] = result

    if get_aggregations == 1:
        response_dict["aggregations"] = aggregations

    return JsonResponse(response_dict)



def GetAllNotesInTimeRange(request, username, time_start, time_end):
    user_notes = DocumentNote.objects.all().filter(user__username=username)

    if time_start != "0" and time_end != "0":
        user_notes = user_notes.filter(time__range=(
            time_start, time_end)).order_by("-time")
    elif time_start == "0" and time_end != "0":
        user_notes = user_notes.filter(time__lte=time_end).order_by("-time")
    elif time_start != "0" and time_end == "0":
        user_notes = user_notes.filter(time__gte=time_start).order_by("-time")
    else:
        user_notes = user_notes.order_by("-time")

    result = []
    hashTags = []
    labels = []
    for n in user_notes:
        result.append(
            {"note": n.note, "time": n.time, "document_name": n.document.name, "id": n.id, "label": n.docLabel,
             "starred": n.starred, "document_id": n.document.id, "document_country_id": n.document.country_id.id,
             "country_name": n.document.country_id.name})
        for ht in n.hash_tags.all():
            if (hashTags.__contains__(ht.hash_tag) == False):
                hashTags.append(ht.hash_tag)
        if (labels.__contains__(n.docLabel) == False):
            labels.append(n.docLabel)
    return JsonResponse({"notes": result, "hashtags": hashTags, "labels": labels})

    # user_logs = user_logs.filter(user_id__isnull=False).order_by("-time")
    # chart_data = {}
    # for log in user_logs:
    #     user_id_id = log.user_id
    #     if user_id_id not in chart_data:
    #         chart_data[user_id_id] = 1
    #     else:
    #         chart_data[user_id_id] += 1
    # chart_data_list = []
    # for user_id_id, count in chart_data.items():
    #     name = user_id_id.first_name + ' ' + user_id_id.last_name
    #     column = [name, count]
    #     chart_data_list.append(column)
    # return JsonResponse({'user_chart_data_list': chart_data_list})



def GetCountryById(request, id):
    country = Country.objects.get(id=id)
    result = {"id": country.id,
              "name": country.name,
              "folder": str(country.file.name.split("/")[-1].split(".")[0]),
              "language": country.language,
              }
    return JsonResponse({'country_information': [result]})


def GetKeywordLDAData(request, country_id, cluster_size, username, keyword):
    lda_topics = []
    all_para_count = 0
    temp = AIParagraphLDATopic.objects.filter(country__id=country_id, number_of_topic=cluster_size)

    user_topic_labels = UserLDATopicLabel.objects.filter(
        topic__country__id=country_id,
        topic__number_of_topic=cluster_size,
        user__username=username).values()

    user_label_dict = {}

    if len(user_topic_labels) > 0:
        for row in user_topic_labels:
            user_label_dict[row['topic_id']] = row['label']

    for record in temp:
        if keyword in record.words:
            record_id = record.id
            sorted_word_list = [k for k, v in
                                sorted(record.words.items(), reverse=True, key=lambda item: float(item[1]))]
            user_label_value = user_label_dict[record_id] if record_id in user_label_dict else 'بدون برچسب'

            user_label_input = "<div>" + \
                               "<input id ='" + str(
                record_id) + "' class='form-control p-1 text-center d-block w-100' value ='" + user_label_value + "' type= 'text'/>" + \
                               "<button onclick=save_user_label('" + str(
                record_id) + "') class = 'btn btn-outline-success mt-1 p-0 d-block w-100'>ذخیره</button>" + \
                               "</div>"

            lda_topics.append({
                'id': record.id,
                'topic_id': record.topic_id,
                'topic_name': record.topic_name,
                'words': " - ".join(sorted_word_list),
                'entropy': record.correlation_score,
                'subject': record.dominant_subject_name,
                'paragraph_count': record.paragraph_count,
                'user_label': user_label_input
            })

            all_para_count += record.paragraph_count
    return JsonResponse({'lda_topics': lda_topics, 'all_para_count': all_para_count})




def GetLDAGraphData(request, country_id, number_of_topic):
    ClusteringGraphData_Object = LDAGraphData.objects.get(country_id=country_id, number_of_topic=number_of_topic)
    Nodes_data, Edges_data = ClusteringGraphData_Object.centroids_nodes_data, ClusteringGraphData_Object.centroids_edges_data

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


def GetLDAKeywordGraphData(request, country_id, number_of_topic):
    ClusteringGraphData_Object = LDAGraphData.objects.get(country=country_id, number_of_topic=number_of_topic)
    Nodes_data, Edges_data = ClusteringGraphData_Object.subject_keywords_nodes_data, ClusteringGraphData_Object.subject_keywords_edges_data

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


def GetMyUserProfile(request):
    username = request.COOKIES.get('username')
    user = User.objects.get(username=username)
    user_expertise = User_Expertise.objects.filter(user_id=user.id)
    expertise = []
    expertise_ids = []
    for e in user_expertise:
        if e.experise_id.expertise == "سایر موارد":
            expertise.append(user.other_expertise)
        else:
            expertise.append(e.experise_id.expertise)
        expertise_ids.append(e.experise_id.id)
    expertise = " - ".join(expertise)

    if expertise == "":
        expertise = 'نامشخص'

    try:
        role = user.role.persian_name
    except:
        role = 'نامشخص'

    return JsonResponse({"profile": {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'mobile': user.mobile,
        'expertise': expertise,
        'role': role,
        'avatar': user.avatar
    }})


def GetNotesInTimeRangeFilterLabelHashtag(request, username, time_start, time_end, label, hashtag):
    user_notes = DocumentNote.objects.all().filter(user__username=username)

    if time_start != "0" and time_end != "0":
        user_notes = user_notes.filter(time__range=(
            time_start, time_end)).order_by("-time")
    elif time_start == "0" and time_end != "0":
        user_notes = user_notes.filter(time__lte=time_end).order_by("-time")
    elif time_start != "0" and time_end == "0":
        user_notes = user_notes.filter(time__gte=time_start).order_by("-time")
    else:
        user_notes = user_notes.order_by("-time")

    if (label != "همه"):
        user_notes = user_notes.filter(docLabel=label)

    if (hashtag != "همه"):
        user_notes = user_notes.filter(hash_tags__in=[hashtag])

    result = []
    # hashTags = []
    # labels = []
    for n in user_notes:
        result.append(
            {"note": n.note, "time": n.time, "document_name": n.document.name, "id": n.id, "label": n.docLabel,
             "starred": n.starred, "document_id": n.document.id, "document_country_id": n.document.country_id.id,
             "country_name": n.document.country_id.name})
        # for ht in n.hash_tags.all():
        #     if (hashTags.__contains__(ht.hash_tag) == False):
        #         hashTags.append(ht.hash_tag)
        # if (labels.__contains__(n.docLabel) == False):
        #     labels.append(n.docLabel)
    return JsonResponse({"notes": result})
    # return JsonResponse({"notes": result , "hashtags":hashTags , "labels":labels})


def GetParagraph_Clusters(request, country_id, algorithm_name, vector_type, cluster_count, ngram_type, username):
    clusters_data = {}

    algorithm_id = ClusteringAlgorithm.objects.get(
        name=algorithm_name,
        input_vector_type=vector_type,
        cluster_count=cluster_count,
        ngram_type=ngram_type
    ).id

    try:

        algorithm_result_data = CUBE_Clustering_TableData.objects.get(country__id=country_id,
                                                                      algorithm__id=algorithm_id)

        clusters_data = algorithm_result_data.clusters_data
        table_data = algorithm_result_data.table_data['data']
        dict_table_data = algorithm_result_data.dict_table_data['data']

        user_topic_labels = UserTopicLabel.objects.filter(
            topic__algorithm__id=algorithm_id,
            topic__country__id=country_id,
            user__username=username).values()

        final_table_data = []

        if len(user_topic_labels) > 0:

            for row in user_topic_labels:
                topic_id = row['topic_id']
                table_row = dict_table_data[topic_id]
                table_row['user_label'] = table_row['user_label'].replace('بدون برچسب', row['label'])

            for topic_id, table_row in dict_table_data.items():
                final_table_data.append(table_row)

        else:
            final_table_data = table_data

    except:
        final_table_data = []
    return JsonResponse({
        "table_data": final_table_data,
        "clusters_data": clusters_data,
        'clustering_algorithm_id': algorithm_id
    })



def getNeighbourforNode(node_id, edge_data, node_parents, edge_count_limit):
    edge_list = list(filter(lambda x: (x["source"] == node_id or x["target"] == node_id) and
                                      (x["source"] not in node_parents or x["target"] not in node_parents), edge_data))

    if edge_list.__len__() > edge_count_limit:
        return sorted(edge_list, key=lambda k: k['weight'], reverse=True)[:edge_count_limit]
    elif edge_list.__len__() > 0:
        return sorted(edge_list, key=lambda k: k['weight'], reverse=True)[:edge_count_limit]
    else:
        return []



def exact_search_text(res_query, place, text, ALL_FIELDS):
    text = text.replace('>', '/').replace('<', '\\')

    if place == 'keyword':
        keyword_query = {
            "match_phrase": {
                "keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = keyword_query
        else:
            res_query['bool']['must'].append(keyword_query)

    elif place == 'keyword-term':
        keyword_query = {
            "term": {
                "keyword.keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = keyword_query
        else:
            res_query['bool']['must'].append(keyword_query)

    elif place == 'عنوان':
        text_list = text.split("__")
        if text_list.__len__() == 1:
            title_query = {
                "match_phrase": {
                    "document_name": text
                }
            }
        else:
            title_query = {
                "terms": {
                    "document_name.keyword": text_list
                }
            }

        if ALL_FIELDS:
            res_query = title_query
        else:
            res_query['bool']['must'].append(title_query)


    elif place == 'متن':
        content_query = {
            "match_phrase": {
                "attachment.content": text
            }
        }

        if ALL_FIELDS:
            res_query = content_query
        else:
            res_query['bool']['must'].append(content_query)


    elif place == 'شماره دادنامه':
        text = "*" + text + "*"
        judgment_number_query = {
            "wildcard": {
                "judgment_number.keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = judgment_number_query
        else:
            res_query['bool']['must'].append(judgment_number_query)

    elif place == 'ICS':
        text = "*" + text + "*"
        ICS_query = {
            "wildcard": {
                "ICS.keyword": text
            }
        }
        if ALL_FIELDS:
            res_query = ICS_query
        else:
            res_query['bool']['must'].append(ICS_query)

    elif place == 'standard_number':
        text = "*" + text + "*"
        standard_number_query = {
            "wildcard": {
                "standard_number.keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = standard_number_query
        else:
            res_query['bool']['must'].append(standard_number_query)


    else:
        title_content_query = {
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "document_name": text
                        }
                    },
                    {
                        "match_phrase": {
                            "attachment.content": text
                        }
                    }
                ]
            }
        }

        if ALL_FIELDS:
            res_query = title_content_query
        else:
            res_query['bool']['must'].append(title_content_query)
    return res_query


def boolean_search_text(res_query, place, text, operator, ALL_FIELDS):
    text = text.replace('>', '/').replace('<', '\\')

    if place == 'عنوان':
        title_query = {
            "match": {
                "document_name": {
                    "query": text,
                    "operator": operator
                }
            }
        }

        if ALL_FIELDS:
            res_query = title_query
        else:
            res_query['bool']['must'].append(title_query)

    elif place == 'متن':
        content_query = {
            "match": {
                "attachment.content": {
                    "query": text,
                    "operator": operator
                }
            }
        }

        if ALL_FIELDS:
            res_query = content_query
        else:
            res_query['bool']['must'].append(content_query)


    elif place == 'شماره دادنامه':
        text = "*" + text + "*"
        judgment_number_query = {
            "wildcard": {
                "judgment_number.keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = judgment_number_query
        else:
            res_query['bool']['must'].append(judgment_number_query)

    elif place == 'ICS':
        text = "*" + text + "*"
        ICS_query = {
            "wildcard": {
                "ICS.keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = ICS_query
        else:
            res_query['bool']['must'].append(ICS_query)

    elif place == 'standard_number':
        text = "*" + text + "*"
        standard_number_query = {
            "wildcard": {
                "standard_number.keyword": text
            }
        }

        if ALL_FIELDS:
            res_query = standard_number_query
        else:
            res_query['bool']['must'].append(standard_number_query)

    else:
        title_content_query = {
            "bool": {

                "should": [
                    {
                        "match": {
                            "document_name": {
                                "query": text,
                                "operator": operator
                            }
                        }
                    },
                    {
                        "match": {
                            "attachment.content": {
                                "query": text,
                                "operator": operator
                            }
                        }
                    }
                ]
            }
        }

        if ALL_FIELDS:
            res_query = title_content_query
        else:
            res_query['bool']['must'].append(title_content_query)

    return res_query



def GetUserExpertise(request):
    expertise = UserExpertise.objects.all()
    result = []
    for e in expertise:
        result.append({'id': e.id, 'expertise': e.expertise})
    return JsonResponse({"result": result})


def GetUserProfile(request, id):
    user = User.objects.get(id=id)
    user_expertise = User_Expertise.objects.filter(user_id=id)

    expertise = []
    for e in user_expertise:
        expertise.append(e.experise_id.expertise)
    expertise = " - ".join(expertise)

    if expertise == "":
        expertise = 'نامشخص'

    try:
        role = user.role.persian_name
    except:
        role = 'نامشخص'

    return JsonResponse({"profile": {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'email': user.email,
        'expertise': expertise,
        'role': role,
        'avatar': user.avatar
    }})


def GetUserRole(request):
    roles = UserRole.objects.filter(persian_name__isnull=False)
    result = []
    for role in roles:
        id = role.id
        persian_name = role.persian_name

        result.append({
            "id": id,
            "name": persian_name
        })
    return JsonResponse({"user_roles": result})


@allowed_users()
def ManageUsers(request):
    panels = CreatePanel(request)
    activated_user = User.objects.all().filter(is_active=1)
    result = []

    for user in activated_user:
        new_user = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'phone': user.mobile,
            'panels': []
        }
        user_admin_panel = UserPanels.objects.all().filter(user_id=user.id)
        for panel in user_admin_panel:
            panel_name = panel.panel.panel_english_name
            new_user['panels'].append(panel_name)

        result.append(new_user)

    return JsonResponse({"admins": result, "main_panels": AllPanels, "panels": panels})


def Recommendations(request, first_name, last_name, email, recommendation_text, rating_value):
    Recommendation.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        recommendation_text=recommendation_text,
        rating_value=rating_value,
    )
    return JsonResponse({"status": "OK"})


def save_lda_topic_label(request, topic_id, username, label):
    result_response = ""

    user = User.objects.get(username=username)
    topic = AIParagraphLDATopic.objects.get(id=topic_id)

    try:

        user_topic_label = UserLDATopicLabel.objects.get(
            topic=topic,
            user=user)

        user_topic_label.label = label
        user_topic_label.save()
        result_response = ".برچسب موضوع تغییر یافت"

    except:
        UserLDATopicLabel.objects.create(
            topic=topic,
            user=user,
            label=label)
        result_response = ".برچسب جدید ایجاد شد"

    return JsonResponse({
        "result_response": result_response
    })


def save_topic_label(request, topic_id, username, label):
    result_response = ""

    user = User.objects.get(username=username)
    topic = ClusterTopic.objects.get(id=topic_id)

    try:

        user_topic_label = UserTopicLabel.objects.get(
            topic=topic,
            user=user)

        user_topic_label.label = label
        user_topic_label.save()
        result_response = ".برچسب موضوع تغییر یافت"

    except:
        UserTopicLabel.objects.create(
            topic=topic,
            user=user,
            label=label)
        result_response = ".برچسب جدید ایجاد شد"

    return JsonResponse({
        "result_response": result_response
    })

def CreateEmailCode():
    range_start = 10 ** 3
    range_end = (10 ** 4) - 1
    return randint(range_start, range_end)

def confirm_email(user):
    email_code = CreateEmailCode()

    token = get_random_string(length=50)
    user.account_activation_token = token
    user.account_acctivation_expire_time = datetime.datetime.now() + datetime.timedelta(days=2)
    user.email_confirm_code = email_code
    user.save()

    template = f"""
    لطفا برای تایید ثبت نام خود روی لینک زیر کلیک کنید. 
    دقت فرمایید که مهلت استفاده از این کد، "دو روز" است و در صورت منقضی شدن لینک، باید مجددا وارد بخش ثبت‌نام سامانه شوید و روی لینک ارسال مجدد کد تایید، کلیک فرمایید. 
    کد تایید ایمیل: {email_code}
    """
    template += f'http://rahnamud.ir:7074/Confirm-Email/{user.id}/{token}'
    print("template: ", template)


    send_mail(subject='کد تایید ایمیل', message=template, from_email=settings.EMAIL_HOST_USER,recipient_list=[user.email])

def resend_email(request):
    return render(request, 'doc/user_templates/resend_email.html')

def resend_email_code(request, email):
    users = User.objects.filter(email=email)
    user = users[0]
    if user.account_acctivation_expire_time < timezone.now() and user.enable == 0:
        confirm_email(user)
    return JsonResponse({ "status": "OK" })

def email_check(request, user_id, token):
    url_is_valid = False
    try:
        user = User.objects.get(pk=user_id)
        if (not (user.account_activation_token is None)) and user.account_activation_token == token and user.account_acctivation_expire_time >= timezone.now():
            url_is_valid = True
    except:
        user_id = ""

    return render(request, 'doc/user_templates/confirm_email.html', {"url_is_valid": url_is_valid, "user_id": user_id, "token": token})

def user_activation(request, user_id, token, code):
    user = User.objects.get(pk=user_id)

    if (not (user.account_activation_token is None)) and user.account_activation_token == token and user.account_acctivation_expire_time >= timezone.now():
        print("code: ",code)
        print("user_code: ", user.email_confirm_code)
        if(user.email_confirm_code == code):
            user.account_activation_token = None
            user.enable = 1
            user.save()
            return JsonResponse({ "status": "OK" })
        else:
            user.save()
            return JsonResponse({ "status": "Not OK" })


    return JsonResponse({ "status": "Not OK" })

def SaveUser(request, firstname, lastname,email, phonenumber, role, username, password, ip, expertise, other_expertise):
    user_username = User.objects.filter(username=username)
    user_email = User.objects.filter(email=email)
    if user_username.count() > 0:
        return JsonResponse({"status": "duplicated username"})
    elif user_email.count() > 0:
        return JsonResponse({"status": "duplicated email"})
    else:
        hashed_pwd = make_password(password)
        last_login = datetime.datetime.now()
        user = User.objects.create(first_name=firstname, last_name=lastname,email=email,
                                   role_id=role,
                                   mobile=phonenumber, username=username, password=hashed_pwd, last_login=last_login,
                                   is_super_user=0, is_active=0, other_expertise=other_expertise)

        for e in expertise.split(','):
            User_Expertise.objects.create(user_id_id=user.id, experise_id_id=e)
        SaveUserLog(user.id, ip, "signup")
        confirm_email(user)

    return JsonResponse({"status": "OK"})

def SetMyUserProfile(request):
    if request.method != 'POST':
        return JsonResponse({"status": "Method not supported"})

    data = json.loads(request.body)
    firstname = data["firstname"]
    lastname = data["lastname"]
    email = data["email"]
    phonenumber = data["phonenumber"]
    role = data["role"]

    username = request.COOKIES.get('username')
    user = User.objects.get(username=username)
    user_email = User.objects.filter(email=email).exclude(username=username)
    role = UserRole.objects.get(id=role)

    if user_email.count() > 0:
        return JsonResponse({"status": "duplicated email"})
    else:
        if "avatar" in data:
            avatar = data["avatar"]
        else:
            avatar = user.avatar
        User.objects.filter(username=username).update(
            first_name=firstname,
            last_name=lastname,
            email=email,
            mobile=phonenumber,
            role=role, avatar=avatar)

    return JsonResponse({"status": "OK"})


def ToggleNoteStar(request, note_id):
    starred = DocumentNote.objects.get(id=note_id)
    if (starred.starred == True):
        starred.starred = False
    else:
        starred.starred = True
    starred.save()
    return JsonResponse({
        'starred': starred.starred
    })


def UserLogSaved(request, username, url, sub_url='0', ip='0'):
    # print(request.POST)
    host_url = request.get_host()
    user_id = User.objects.get(username=username).id
    date_time = datetime.datetime.now()

    visit_time = str(date_time).replace(' ', "T").split('.')[0] + 'Z'

    year = int(visit_time[0:4])
    month = int(visit_time[5:7])
    day = int(visit_time[8:10])
    hour = int(visit_time[11:13])

    jalili_visit_time = {
        "year": year,
        "month": {"number": month,
                  "name": JalaliDate.to_jalali(year, month, day).strftime('%B', locale='fa')},
        "day": {
            "number": day,
            "name": JalaliDate.to_jalali(year, month, day).strftime('%A', locale='fa')
        },

        "hour": hour
    }

    if url == "0":
        url = None

    paeg_url = url

    if sub_url != "0":
        paeg_url = url + "/" + sub_url

    # save to DB (temporary)
    UserLogs.objects.create(user_id_id=user_id, user_ip=ip,
                            page_url=paeg_url, visit_time=date_time,
                            detail_json=request.POST)

    user_info = User.objects.get(id=user_id)

    user_object = {"id": user_id,
                   "first_name": user_info.first_name,
                   "last_name": user_info.last_name}

    machine_user_name = getpass.getuser()
    if machine_user_name == SERVER_USER_NAME:
        index_name = es_config.SERVE_USER_LOG_INDEX
    else:
        index_name = es_config.LOCAL_USER_LOG_INDEX

    new_log = {
        "user": user_object,
        "user_ip": ip,
        "page_url": paeg_url,
        "visit_time": visit_time,
        "jalili_visit_time": jalili_visit_time,
        "detail_json": request.POST}

    client.index(
        index=index_name,
        document=new_log,
        op_type='create',
        refresh=True)

    # client.indices.flush([index_name])

    return JsonResponse({"status": "OK"})


def UserDeployLogSaved(request, username, detail):
    user_id = User.objects.get(username=username).id
    date_time = datetime.datetime.now()

    DeployServer.objects.create(user_id_id=user_id, deploy_time=date_time, detail=detail)

    return JsonResponse({"status": "OK"})


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


def getUserChartLogs(request, user_id, time_start, time_end):
    if time_start != "0" and time_end != "0":
        user_logs = UserLogs.objects.all().filter(visit_time__range=(
            time_start, time_end)).order_by("-visit_time")

    elif time_start == "0" and time_end != "0":
        user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end).order_by("-visit_time")

    elif time_start != "0" and time_end == "0":
        user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start).order_by("-visit_time")

    else:
        user_logs = UserLogs.objects.all().order_by("-visit_time")

    user_logs = user_logs.filter(user_id__isnull=False).order_by("-visit_time")

    chart_data = {}
    for log in user_logs:
        user_id_id = log.user_id
        if user_id_id not in chart_data:
            chart_data[user_id_id] = 1
        else:
            chart_data[user_id_id] += 1

    chart_data_list = []
    for user_id_id, count in chart_data.items():
        name = user_id_id.first_name + ' ' + user_id_id.last_name
        column = [name, count]
        chart_data_list.append(column)

    return JsonResponse({'user_chart_data_list': chart_data_list})


def GetDocumentCommentVoters(request, document_comment_id, agreed):
    if agreed == "true":
        agreed = True
    else:
        agreed = False
    votes = DocumentCommentVote.objects.filter(document_comment=document_comment_id, agreed=agreed)
    result = []
    for v in votes:
        created_at = str(jdatetime.strftime(jdatetime.utcfromtimestamp(v.created_at.timestamp()), "%H:%M:%S %Y-%m-%d"))
        modified_at = str(
            jdatetime.strftime(jdatetime.utcfromtimestamp(v.modified_at.timestamp()), "%H:%M:%S %Y-%m-%d"))
        result.append({"first_name": v.user.first_name, "last_name": v.user.last_name, "created_at": created_at
                          , "modified_at": modified_at})
    return JsonResponse({"result": result})


@allowed_users('admin_accept_user_comments')
def changeCommentState(request, comment_id, state):
    comment = DocumentComment.objects.get(pk=comment_id)

    if state == "accepted":
        comment.is_accept = 1
    elif state == "rejected":
        comment.is_accept = -1

    comment.save()

    return JsonResponse({"status": state})


@allowed_users('admin_waiting_user', 'admin_accepted_user')
def changeUserState(request, user_id, state):
    if state == "accepted":
        accepted_user = User.objects.get(pk=user_id)
        accepted_user.is_active = 1
        accepted_user.save()

        template = f"""
        ثبت‌نام شما با موفقیت انجام شده است. تایید شما توسط ادمین انجام شد. هم‌اکنون، می‌توانید وارد سامانه شوید.
        """
        template += f'http://rahnamud.ir:707/login/'
        print("template: ", template)
        send_mail(subject='تایید عملیات ثبت‌نام', message=template, from_email=settings.EMAIL_HOST_USER,recipient_list=[accepted_user.email])


        return JsonResponse({"status": "accepted"})
    elif state == "rejected":
        accepted_user = User.objects.get(pk=user_id)
        accepted_user.is_active = -1
        accepted_user.save()

        template = f"""
        متاسفانه ثبت‌نام شما توسط ادمین رد شده است.
        """
        print("template: ", template)
        send_mail(subject='عدم تایید عملیات ثبت‌نام', message=template, from_email=settings.EMAIL_HOST_USER,recipient_list=[accepted_user.email])


        return JsonResponse({"status": "rejected"})


def DeleteUser(request, user_id):
    user = User.objects.get(pk=user_id)
    user.delete()
    return JsonResponse({"status": "deleted"})


def getChartLogs(request, user_id, time_start, time_end):
    if user_id == 0:
        if time_start != "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__range=(
                time_start, time_end)).order_by("-visit_time")

        elif time_start == "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end).order_by("-visit_time")

        elif time_start != "0" and time_end == "0":
            user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start).order_by("-visit_time")

        else:
            user_logs = UserLogs.objects.all().order_by("-visit_time")
    else:
        if time_start != "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__range=(
                time_start, time_end), user_id=user_id).order_by("-visit_time")

        elif time_start == "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end,
                                                      user_id=user_id).order_by("-visit_time")

        elif time_start != "0" and time_end == "0":
            user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start,
                                                      user_id=user_id).order_by("-visit_time")

        else:
            user_logs = UserLogs.objects.all().filter(
                user_id=user_id).order_by("-visit_time")

    convert_month = {1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد', 4: 'تیر', 5: 'مرداد',
                     6: 'شهریور', 7: 'مهر', 8: 'آبان', 9: 'آذر', 10: 'دی',
                     11: 'بهمن', 12: 'اسفند'}

    month_chart_data = {}
    hour_chart_data = {}
    for log in user_logs:
        time = log.visit_time
        year = int(time[0:4])
        month = int(time[5:7])
        day = int(time[8:10])
        hour = int(time[11:13])
        jalali = gregorian_to_jalali(year, month, day)

        month_name = convert_month[jalali[1]]
        if month_name not in month_chart_data:
            month_chart_data[month_name] = 1
        else:
            month_chart_data[month_name] += 1

        if hour not in hour_chart_data:
            hour_chart_data[hour] = 1
        else:
            hour_chart_data[hour] += 1

    month_chart_data_list = []
    for month, count in month_chart_data.items():
        column = [month, count]
        month_chart_data_list.append(column)

    hour_chart_data_list = []
    for hour, count in hour_chart_data.items():
        column = [hour, count]
        hour_chart_data_list.append(column)

    chart_data = {}
    for log in user_logs:
        url = log.page_url
        if url == None:
            url = 'home'
        if url not in chart_data:
            chart_data[url] = 1
        else:
            chart_data[url] += 1

    chart_data_list = []
    for url, count in chart_data.items():
        column = [url, count]
        chart_data_list.append(column)

    panels = {'search': {'chart_dict': {}, 'chart_list': []},
              'graph': {'chart_dict': {}, 'chart_list': []}
              }

    for panel in panels:
        panel_chart_data = panels[panel]['chart_dict']

        if user_id == 0:
            user_logs = UserLogs.objects.all().filter(
                page_url=panel).order_by("-visit_time")
        else:
            user_logs = UserLogs.objects.all().filter(
                page_url=panel, user_id=user_id).order_by("-visit_time")

        for log in user_logs:
            detail_type = log.detail_json['detail_type']
            if detail_type not in panel_chart_data:
                panel_chart_data[detail_type] = 1
            else:
                panel_chart_data[detail_type] += 1

        for detail_type, count in panel_chart_data.items():
            column = [detail_type, count]
            panels[panel]['chart_list'].append(column)

        panels[panel]['result_data'] = panels[panel]['chart_list']

    # 'chart_data_information': panels['information']['chart_list'],
    return JsonResponse({'chart_data_list': chart_data_list, 'chart_data_search': panels['search']['chart_list'],
                         'chart_data_graph': panels['graph']['chart_list'],
                         'month_chart_data_list': month_chart_data_list, 'hour_chart_data_list': hour_chart_data_list})


def getTableUserLogs(request, user_id, time_start, time_end):
    if user_id == 0:
        if time_start != "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__range=(
                time_start, time_end)).order_by("-visit_time")

        elif time_start == "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end).order_by("-visit_time")

        elif time_start != "0" and time_end == "0":
            user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start).order_by("-visit_time")

        else:
            user_logs = UserLogs.objects.all().order_by("-visit_time")
    else:
        if time_start != "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__range=(
                time_start, time_end), user_id=user_id).order_by("-visit_time")

        elif time_start == "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end,
                                                      user_id=user_id).order_by("-visit_time")

        elif time_start != "0" and time_end == "0":
            user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start,
                                                      user_id=user_id).order_by("-visit_time")

        else:
            user_logs = UserLogs.objects.all().filter(
                user_id=user_id).order_by("-visit_time")

    keyword_table_data = {}
    for log in user_logs:
        if log.page_url == "search":
            if log.detail_json['detail_type'] == "نتایج جست و جو":
                keyword = log.detail_json['search_text']
                if keyword not in keyword_table_data:
                    keyword_table_data[keyword] = 1
                else:
                    keyword_table_data[keyword] += 1

    keyword_table_data_list = []
    i = 1
    for keyword_name, count in keyword_table_data.items():
        column = [i, keyword_name, count]
        keyword_table_data_list.append(column)
        i += 1

    return JsonResponse({'keyword_table_data_list': keyword_table_data_list})


def getUserLogs(request, user_id, time_start, time_end):
    if user_id == 0:
        if time_start != "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__range=(
                time_start, time_end)).order_by("-visit_time")

        elif time_start == "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end).order_by("-visit_time")

        elif time_start != "0" and time_end == "0":
            user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start).order_by("-visit_time")

        else:
            user_logs = UserLogs.objects.all().order_by("-visit_time")
    else:
        if time_start != "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__range=(
                time_start, time_end), user_id=user_id).order_by("-visit_time")

        elif time_start == "0" and time_end != "0":
            user_logs = UserLogs.objects.all().filter(visit_time__lte=time_end,
                                                      user_id=user_id).order_by("-visit_time")

        elif time_start != "0" and time_end == "0":
            user_logs = UserLogs.objects.all().filter(visit_time__gte=time_start,
                                                      user_id=user_id).order_by("-visit_time")

        else:
            user_logs = UserLogs.objects.all().filter(
                user_id=user_id).order_by("-visit_time")

    user_logs = user_logs.filter(user_id__isnull=False).order_by("-visit_time")[:100]

    result = []
    for log in user_logs:
        id = log.id
        name = log.user_id.first_name + ' ' + log.user_id.last_name
        url = log.page_url
        if url == None:
            url = 'home'
        time = log.visit_time
        year = int(time[0:4])
        month = int(time[5:7])
        day = int(time[8:10])
        hours = time[11:19]
        jalali = gregorian_to_jalali(year, month, day)
        Date = str(jalali[0]) + '/' + str(jalali[1]) + '/' + str(jalali[2]) + ' ' + hours

        detail = log.detail_json

        result.append({
            "id": id,
            "name": name,
            'url': url,
            'time': Date,
            'detail': detail
        })

    return JsonResponse({'user_logs': result})


@allowed_users('admin_user_report_bug')
def ChangeReportBugCheckStatus(request, report_bug_id):
    report_bug = ReportBug.objects.get(id=report_bug_id)
    if report_bug.checked == False:
        report_bug.checked = True
    else:
        report_bug.checked = False
    report_bug.save()

    return JsonResponse({"status": "OK"})


@allowed_users('admin_user_report_bug')
def GetReportBugByFilter(request, panel_id, branch_id, status):
    if status == "T":
        status = True
    elif status == "F":
        status = False
    reports = ReportBug.objects.all().order_by('checked', 'date')
    if panel_id != "all":
        panel_id = int(panel_id)
        reports = reports.filter(panel_id=panel_id)
    if branch_id != "all":
        branch_id = int(branch_id)
        reports = reports.filter(branch_id=branch_id)
    if status != "all":
        reports = reports.filter(checked=status)

    report_bug = []
    branches = {}
    for report in reports:
        report_bug.append({
            'id': report.id,
            'first_name': report.user.first_name,
            'last_name': report.user.last_name,
            'email': report.user.email,
            'panel_name': report.panel_id.panel_persian_name,
            'branch_name': report.branch_id.panel_persian_name,
            'report_bug_text': report.report_bug_text,
            'date': report.date,
            'checked': report.checked,
        })
        branch = branches.get(report.branch_id.panel_persian_name)
        if branch:
            branches[report.branch_id.panel_persian_name] += 1
        else:
            branches[report.branch_id.panel_persian_name] = 1

    return JsonResponse({'report_bug': report_bug, 'branches_count': branches})


def AILDADocFromTopic(request, topic_id):
    topic_paragraphs = []
    temp = AILDAParagraphToTopic.objects.filter(topic__id=topic_id).order_by('-score').values()[:100]
    keywords = AIParagraphLDATopic.objects.get(id=topic_id).words
    sorted_word_list = [k for k, v in sorted(keywords.items(), reverse=True, key=lambda item: float(item[1]))]
    keywords = " - ".join(sorted_word_list)
    for record in temp:
        paragraph_id = record['paragraph_id']
        paragraph = DocumentParagraphs.objects.get(id=paragraph_id)
        try:
            subjects_name = ParagraphsSubject.objects.get(paragraph__id=paragraph_id)

            topic_paragraphs.append({

                "paragraph_text": paragraph.text,
                "paragraph_id": paragraph.id,
                "document_id": paragraph.document_id.id,
                "document_name": paragraph.document_id.name,
                "subject1_name": subjects_name.subject1_name,
                "subject2_name": subjects_name.subject2_name,
                "subject3_name": subjects_name.subject3_name,
                "score": record['score']
            })
        except:
            topic_paragraphs.append({
                "paragraph_text": paragraph.text,
                "paragraph_id": paragraph.id,

                "document_id": paragraph.document_id.id,
                "document_name": paragraph.document_id.name,
                "subject1_name": 0,
                "subject2_name": None,
                "subject3_name": None,
                "score": record['score']
            })

    return JsonResponse({'topic_paragraphs': topic_paragraphs, 'keywords': keywords})


def AILDAWordCloudTopic(request, topic_id):
    Could_data = []
    keywords = AIParagraphLDATopic.objects.get(id=topic_id)

    for key, value in keywords.words.items():
        Could_data.append({"x": key, "value": value})

    return JsonResponse({'Could_data': Could_data})


def AILDASubjectChartTopic(request, topic_id):
    data = AIParagraphLDATopic.objects.get(id=topic_id)

    chart_data = data.subjects_list_chart_data_json['data']
    paragraph_count = data.paragraph_count
    dominant_subject_name = data.dominant_subject_name
    correlation_score = data.correlation_score

    return JsonResponse({'chart_data': chart_data,
                         'paragraph_count': paragraph_count,
                         'dominant_subject_name': dominant_subject_name,
                         'correlation_score': correlation_score})


def get_stopword_list(file_name):
    stop_words = []

    stop_words_file = str(Path(config.PERSIAN_PATH, file_name))
    with open(stop_words_file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            stop_words.append(line)
    f.close()
    return stop_words




def GetDoticSimDocument_ByTitle(request, document_name):
    res_query = {
        'bool': {
            'must': [],
            'filter': [
                {
                    'terms': {
                        'level_name.keyword': ['قانون', 'اسناد بالادستی']
                    }
                }
            ]
        }
    }
    stopword_list = get_stopword_list('rahbari_doc_name_stopwords.txt')

    like_query = {
        "more_like_this": {
            "analyzer": "persian_custom_analyzer",
            "fields": ["name"],
            "like": document_name,
            "min_term_freq": 1,
            "max_query_terms": 200,
            "min_doc_freq": 1,
            "max_doc_freq": 150000,
            "min_word_length": 3,
            "minimum_should_match": "40%",
            "stop_words": stopword_list
        }
    }

    res_query['bool']['must'].append(like_query)
    response = client.search(index=doctic_doc_index,
                             _source_includes=['name'],
                             request_timeout=40,
                             query=res_query,
                             size=10,
                             highlight={
                                 "type": "fvh",
                                 "fields": {
                                     "name":
                                         {"pre_tags": ["<span class='text-primary fw-bold'>"], "post_tags": ["</span>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }

                             )

    result_doc = response['hits']['hits']
    print(response)
    result_doc_list = []
    for doc in result_doc:
        doc_id = doc['_id']
        doc_name = doc["highlight"]["name"][0]
        doc_score = doc['_score']
        result_doc_list.append([doc_id, doc_name, doc_score])

    return JsonResponse({'result_doc_list': result_doc_list})


def GetDocumentById(request, id):
    document = Document.objects.get(id=id)

    date = "نامشخص"
    if document.date != None:
        date = document.date

    category_name = "نامشخص"
    if document.category_name != None:
        category_name = document.category_name

    subject_name = "نامشخص"
    if document.subject_name != None:
        subject_name = document.subject_name

    result = {"id": document.id,
              "name": document.name,
              "file_name": document.file_name,
              "country_id": document.country_id_id,
              "country": document.country_id.name,
              "subject": subject_name,
              "date": date,
              "category": category_name,
              }

    return JsonResponse({'document_information': [result]})


def getUserDeployLogs(request):
    user_logs = DeployServer.objects.all().order_by("-deploy_time")

    result = []
    for log in user_logs:
        time = log.deploy_time
        year = int(time[0:4])
        month = int(time[5:7])
        day = int(time[8:10])
        hour = time[11:13]
        minute = time[14:16]
        jalali = gregorian_to_jalali(year, month, day)

        Date = str(jalali[0]) + '/' + str(jalali[1]) + '/' + str(jalali[2])
        name = log.user_id.first_name + ' ' + log.user_id.last_name
        time = hour + ':' + minute

        result.append({
            "id": log.id,
            "name": name,
            'date': Date,
            'time': time,
            'detail': log.detail
        })

    return JsonResponse({'user_logs': result})


def GetUnknownDocuments(request):
    docs = Document.objects.filter(level_id=None)
    result = []
    for d in docs:
        doc = {"name": d.name,
               "reference": d.approval_reference_name,
               "reference_date": d.approval_date
               }
        if not d.type_id is None:
            doc["type"] = d.type_id.name
        else:
            doc["type"] = '-'

        if not d.subject_id is None:
            doc["subject"] = d.subject_id.name
        else:
            doc["subject"] = '-'

        if not d.country_id is None:
            doc["collection"] = d.country_id.name
        else:
            doc["collection"] = '-'

        result.append(doc)
    return JsonResponse({"result": result})


def GetSearchParameters(request, country_id):
    search_parameters = SearchParameters.objects.all()
    parameters_result = {}


    if country_id != 0:
        search_parameters = SearchParameters.objects.filter(country__id=country_id)
        print("country_id")
        print(country_id)

    for param in search_parameters:
        para_name = param.parameter_name
        parameters_result[para_name] = ""

    for param in search_parameters:
        para_name = param.parameter_name
        options = param.parameter_values["options"]

        parameters_result[para_name] += options

    return JsonResponse({"parameters_result": parameters_result}, )



def Local_preprocessing(text):
    space_list = [" ", "\u200c"]
    for s in space_list:
        text = text.replace(s, "")

    arabic_char = {"آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "ك": "ک", "َ": "", "ُ": "", "ِ": "",
                   "": ""}
    for key, value in arabic_char.items():
        text = text.replace(key, value)

    return text


def filter_doc_fields(res_query, category_id, subject_id,
                      from_year, to_year):


    # ---------------------------------------------------------
    if subject_id != 0:
        subject_name = Subject.objects.get(id=subject_id).name
        subject_query = {
            "term": {
                "subject_name.keyword": subject_name
            }
        }
        res_query['bool']['filter'].append(subject_query)

    if category_id != 0:
        category_name = Category.objects.get(id=category_id).name
        subject_query = {
            "term": {
                "category_name.keyword": category_name
            }
        }
        res_query['bool']['filter'].append(subject_query)



    # ----

    # ----------------------------------------------------------

    First_Year = 1000
    Last_Year = 1403

    if from_year != 0 or to_year != 0:
        from_year = from_year if from_year != 0 else First_Year
        to_year = to_year if to_year != 0 else Last_Year

        year_query = {
            "range": {
                "document_year": {
                    "gte": from_year,
                    "lte": to_year,
                }
            }
        }

        res_query['bool']['filter'].append(year_query)

    # ----------------------------------------------------------

    return res_query


def SearchDocument_ES(request, country_id, category_id, subject_id, from_year, to_year,

                    place, text, search_type, curr_page):

    fields = [category_id, subject_id, from_year, to_year]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_doc_fields(res_query, category_id, subject_id, from_year,
                                      to_year)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    # print('search_query')
    # print(res_query)

    index_name = None

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "subject-agg": {
            "terms": {
                "field": "subject_name.keyword",
                "size": bucket_size
            }
        },
        "category-agg": {
            "terms": {
                "field": "category_name.keyword",
                "size": bucket_size
            }
        },

        "date-agg": {
            "terms": {
                "field": "document_date.keyword",
                "size": bucket_size
            }
        },

        "year-agg": {
            "terms": {
                "field": "document_year",
                "size": bucket_size
            }
        },

        "month-agg": {
            "terms": {
                "field": "document_jalili_date.month.name.keyword",
                "size": bucket_size
            }
        },

        "day-agg": {
            "terms": {
                "field": "document_jalili_date.day.name.keyword",
                "size": bucket_size
            }
        },

          "hour-agg": {
            "terms": {
                "field": "document_hour",
                "size": bucket_size
            }
        },
        "source-name-agg": {
            "terms": {
                "field": "source_name.keyword",
                "size": bucket_size
            }
        },

    }

    from_value = (curr_page - 1) * search_result_size

    if country_id == 0:
        index_name_list = []
        country_list = Country.objects.filter(language = "فارسی").exclude(name="تابناک- تست")
        for country in country_list:
            index_name = standardIndexName(country, Document.__name__)
            index_name_list.append(index_name)

        index_name =  index_name_list
    else:

        country_obj = Country.objects.get(id=country_id)
        index_name = standardIndexName(country_obj, Document.__name__)

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name', 'document_date',
                                               'subject_name', 'category_name', 'document_year',
                                               'raw_file_name','source_id','source_folder',
                                               'source_name','document_time'],
                             request_timeout=40,
                             query=res_query,
                             aggregations=res_agg,
                             from_=from_value,
                             size=search_result_size

                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    aggregations = response['aggregations']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    response = client.search(index=index_name,
                             request_timeout=40,
                             query=res_query
                             )
    max_score = response['hits']['hits'][0]['_score'] if total_hits > 0 else 1
    max_score = max_score if max_score > 0 else 1
    print(index_name)
    print(res_query)
    print(result)
    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        'max_score': max_score,
        "curr_page": curr_page,
        'aggregations': aggregations})



def GetSentimentTrend_ChartData(request, country_id, category_id, subject_id, from_year, to_year,
            place, text, search_type, curr_page):
    
    fields = [category_id, subject_id, from_year, to_year]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_doc_fields(res_query, category_id, subject_id, from_year,
                                      to_year)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    # print('search_query')
    # print(res_query)

    index_name = None

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "date-sentiment-agg": {
            "multi_terms": {
                "terms": [{
                "field": "document_date.keyword" 
                }, {
                "field": "sentiment.keyword"
                }],
                "size": bucket_size
            }
            
        },


    }

    from_value = (curr_page - 1) * search_result_size

    if country_id == 0:
        index_name_list = []
        country_list = Country.objects.filter(language = "فارسی").exclude(name="تابناک- تست")
        for country in country_list:
            index_name = standardIndexName(country, FullProfileAnalysis.__name__)
            index_name_list.append(index_name)

        index_name =  index_name_list
    else:

        country_obj = Country.objects.get(id=country_id)
        index_name = standardIndexName(country_obj, FullProfileAnalysis.__name__)

    response = client.search(index=index_name,
                             _source_includes=[],
                             request_timeout=40,
                             query=res_query,
                             aggregations=res_agg,
                             from_=from_value,
                             size=search_result_size

                             )

  
    total_hits = response['hits']['total']['value']

    aggregations = response['aggregations']
    date_sentiment_buckets = aggregations['date-sentiment-agg']['buckets']

    date_sentiment_dict = {}
    for bucket in date_sentiment_buckets:
        date = bucket['key'][0]
        sentiment = bucket['key'][1]
        doc_count = bucket['doc_count']
        if date not in date_sentiment_dict:
            date_sentiment_dict[date] = {
                "احساس بسیار مثبت":0,
                "احساس بسیار منفی":0,
                "احساس مثبت":0,
                "احساس منفی":0,
                "بدون ابراز احساسات":0,
                "احساس خنثی یا ترکیبی از مثبت و منفی":0
            }
        else:
            date_sentiment_dict[date][sentiment] = doc_count
    
    date_sentiment_chart_data = []
    for date,value in date_sentiment_dict.items():
        date_sentiment_chart_data.append([date,
                                        value['احساس بسیار منفی'],
                                        value['احساس منفی'],
                                        value['احساس مثبت'],
                                        value['احساس بسیار مثبت']]
                                        )

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    response = client.search(index=index_name,
                             request_timeout=40,
                             query=res_query
                             )
    max_score = response['hits']['hits'][0]['_score'] if total_hits > 0 else 1
    max_score = max_score if max_score > 0 else 1

    return JsonResponse({
        'total_hits': total_hits,
        'max_score': max_score,
        "curr_page": curr_page,
        'date_sentiment_chart_data': date_sentiment_chart_data})




def filter_doc_actor_fields(res_query, level_id, subject_id, type_id, approval_reference_id,
                            from_year, to_year, from_advisory_opinion_count, from_interpretation_rules_count,
                            revoked_type_id, organization_type_id):

    # ---------------------------------------------------------
    if subject_id != 0:
        subject_name = Subject.objects.get(id=subject_id).name
        subject_query = {
            "term": {
                "document_subject_name.keyword": subject_name
            }
        }
        res_query['bool']['filter'].append(subject_query)

    # ---------------------------------------------------------
    if organization_type_id != '0':
        organization_type_name = organization_type_id
        organization_type_name_query = {
            "match_phrase": {
                "document_organization_type_name": organization_type_name
            }
        }
        res_query['bool']['filter'].append(organization_type_name_query)

    # ----------------------------------------------------------

    First_Year = 1000
    Last_Year = 1403

    if from_year != 0 or to_year != 0:
        from_year = from_year if from_year != 0 else First_Year
        to_year = to_year if to_year != 0 else Last_Year

        year_query = {
            "range": {
                "document_approval_year": {
                    "gte": from_year,
                    "lte": to_year,
                }
            }
        }

        res_query['bool']['filter'].append(year_query)

    # ----------------------------------------------------------

    if from_advisory_opinion_count != 0:
        advisory_opinion_count_query = {
            "range": {
                "document_advisory_opinion_count": {
                    "gte": from_advisory_opinion_count,
                }
            }
        }

        res_query['bool']['filter'].append(advisory_opinion_count_query)

    # ----------------------------------------------------------

    if from_interpretation_rules_count != 0:
        interpretation_rules_count_query = {
            "range": {
                "document_interpretation_rules_count": {
                    "gte": from_interpretation_rules_count,
                }
            }
        }

        res_query['bool']['filter'].append(interpretation_rules_count_query)

    return res_query


def exact_search_text_doc_actor(res_query, place, text, ALL_FIELDS):
    text = text.replace('>', '/').replace('<', '\\')

    if place == 'عنوان':
        title_query = {
            "match_phrase": {
                "document_name": text
            }
        }

        if ALL_FIELDS:
            res_query = title_query
        else:
            res_query['bool']['must'].append(title_query)

    elif place == 'متن':
        content_query = {
            "match_phrase": {
                "attachment.content": text
            }
        }

        if ALL_FIELDS:
            res_query = content_query
        else:
            res_query['bool']['must'].append(content_query)

    else:
        title_content_query = {
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "document_name": text
                        }
                    },
                    {
                        "match_phrase": {
                            "attachment.content": text
                        }
                    }
                ]
            }
        }

        if ALL_FIELDS:
            res_query = title_content_query
        else:
            res_query['bool']['must'].append(title_content_query)

    return res_query


def boolean_search_text_doc_actor(res_query, place, text, operator, ALL_FIELDS):
    text = text.replace('>', '/').replace('<', '\\')

    if place == 'عنوان':
        title_query = {
            "match": {
                "document_name": {
                    "query": text,
                    "operator": operator
                }
            }
        }

        if ALL_FIELDS:
            res_query = title_query
        else:
            res_query['bool']['must'].append(title_query)

    elif place == 'متن':
        content_query = {
            "match": {
                "attachment.content": {
                    "query": text,
                    "operator": operator
                }
            }
        }

        if ALL_FIELDS:
            res_query = content_query
        else:
            res_query['bool']['must'].append(content_query)


    else:
        title_content_query = {
            "bool": {

                "should": [
                    {
                        "match": {
                            "document_name": {
                                "query": text,
                                "operator": operator
                            }
                        }
                    },
                    {
                        "match": {
                            "attachment.content": {
                                "query": text,
                                "operator": operator
                            }
                        }
                    }
                ]
            }
        }

        if ALL_FIELDS:
            res_query = title_content_query
        else:
            res_query['bool']['must'].append(title_content_query)

    return res_query


def entropy(numbers):
    s = sum(numbers)
    if s > 0:
        probabilities = [n / s for n in numbers]
    else:
        probabilities = [0] * len(numbers)
    etp = 0
    for p in probabilities:
        try:
            etp -= (p * math.log2(p))
        except:
            continue
    return round(etp, 2)


def chart_entropy(chart_data):
    # if len(chart_data) == 0:
    #     return {'sum_columns':[0]}, {'sum_columns':['صفر']}, {'sum_columns':[0]}, {'sum_columns':[0]}
    chart_entropies, chart_parallelism, chart_mean, chart_std, chart_normal_entropies = {
                                                                                            'sum_columns': []}, {}, {}, {}, {}
    for instance in chart_data:
        instance_sum = 0
        for j in range(1, len(instance)):
            instance_sum += instance[j]
            try:
                chart_entropies['column_' + str(j)].append(instance[j])
            except:
                chart_entropies['column_' + str(j)] = [instance[j]]

        chart_entropies['sum_columns'].append(instance_sum)

    temp = math.log2(len(chart_data))
    for key, value in chart_entropies.items():
        e = entropy(value)
        chart_mean[key] = round(np.mean(value), 2)
        chart_std[key] = round(np.std(value), 2)
        try:
            normal_e = round(e / temp, 2)
        except:
            normal_e = 0
        chart_normal_entropies[key] = normal_e
        if normal_e > 0.8:
            plr = 'خیلی زیاد'
        elif normal_e > 0.6:
            plr = 'زیاد'
        elif normal_e > 0.4:
            plr = 'متوسط'
        elif normal_e > 0.2:
            plr = 'کم'
        elif normal_e > 0.0:
            plr = 'خیلی کم'
        elif normal_e == 0.0:
            plr = 'صفر'
        chart_parallelism[key] = plr
        chart_entropies[key] = e

    return chart_entropies, chart_parallelism, chart_mean, chart_std, chart_normal_entropies


def GetActorsChartData_ES_2(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year,
                            to_year, from_advisory_opinion_count,
                            from_interpretation_rules_count, revoked_type_id, place, text, search_type):
    organization_type_id = '0'

    fields = [level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
              from_advisory_opinion_count, from_interpretation_rules_count, revoked_type_id, organization_type_id]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_doc_actor_fields(res_query, level_id, subject_id, type_id, approval_reference_id, from_year,
                                            to_year, from_advisory_opinion_count, from_interpretation_rules_count,
                                            revoked_type_id, organization_type_id)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text_doc_actor(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text_doc_actor(res_query, place, text, search_type, ALL_FIELDS)

    # print('chart_query')
    # print(res_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentActor.__name__)

    res_agg = {
        "actor-name-agg": {
            "multi_terms": {
                "terms": [{
                    "field": "actor_name.keyword",
                },
                    {
                        "field": "actor_id",
                    }],
                "size": bucket_size
            },
            "aggs": {
                "actor-type-name-agg": {
                    "terms": {
                        "field": "actor_type_name.keyword",
                        "size": bucket_size
                    }
                },
            },
        },
    }

    response = client.search(index=index_name,
                             _source_includes=['paragraph_id'],
                             request_timeout=40,
                             query=res_query,
                             aggregations=res_agg,
                             # from_=from_value,
                             size=0,
                             # track_total_hits=True,
                             )

    aggregations = response['aggregations']

    # Calculate role frequency of actors
    actors_chart_data = []
    for actor in aggregations['actor-name-agg']['buckets']:
        actor_id = actor["key"][1]
        actor_name = actor["key"][0]
        roles = actor["actor-type-name-agg"]['buckets']
        motevali_count = 0
        hamkar_count = 0
        salahiat_count = 0

        for item in roles:
            if item['key'] == 'متولی اجرا':
                motevali_count = item['doc_count']
            elif item['key'] == 'همکار':
                hamkar_count = item['doc_count']
            elif item['key'] == 'دارای صلاحیت اختیاری':
                salahiat_count = item['doc_count']

        column_data = [actor_name, motevali_count, hamkar_count, salahiat_count]
        actors_chart_data.append(column_data)

    if len(actors_chart_data) < 1:
        temp = {'sum_columns': 0, 'column_1': 0, 'column_2': 0, 'column_3': 0}
        entropy_dict, parallelism_dict, mean_dict, std_dict, normal_entropy_dict = temp, \
                                                                                   {'sum_columns': 'صفر',
                                                                                    'column_1': 'صفر',
                                                                                    'column_2': 'صفر',
                                                                                    'column_3': 'صفر'}, \
                                                                                   temp, temp, temp
    else:
        entropy_dict, parallelism_dict, mean_dict, std_dict, normal_entropy_dict = chart_entropy(actors_chart_data)

    return JsonResponse({"actors_chart_data": actors_chart_data,
                         'entropy_dict': entropy_dict,
                         'parallelism_dict': parallelism_dict,
                         'mean_dict': mean_dict,
                         'std_dict': std_dict,
                         'normal_entropy_dict': normal_entropy_dict,
                         'column_1': 'salahiat',
                         'column_2': 'hamkaran',
                         'column_3': 'motevalian',
                         })





def filter_doc_fields_COLUMN(res_query, category_name, subject_name,
                             from_year, to_year):

    # ---------------------------------------------------------
    if category_name != "همه":
        level_query = {
            "term": {
                "category_name.keyword": category_name
            }
        }
        res_query['bool']['filter'].append(level_query)

    # ---------------------------------------------------------
    if subject_name != "همه":
        subject_query = {
            "term": {
                "subject_name.keyword": subject_name
            }
        }
        res_query['bool']['filter'].append(subject_query)

    # ---------------------------------------------------------

    First_Year = 1000
    Last_Year = 1403

    if from_year != "همه" or to_year != "همه":
        from_year = int(from_year) if from_year != "همه" else First_Year
        to_year = int(to_year) if to_year != "همه" else Last_Year

        year_query = {
            "range": {
                "document_year": {
                    "gte": from_year,
                    "lte": to_year,
                }
            }
        }

        res_query['bool']['filter'].append(year_query)

    return res_query


def SearchDocuments_Column_ES(request, country_name, category_name, subject_name,
                              from_year, to_year
                              , place, text, search_type, curr_page):

    country_id = Country.objects.get(name = country_name).id if country_name != 'همه' else 0
    index_name = None
    res_query = {
        "bool": {}
    }

    ALL_FIELDS = False

    res_query['bool']['filter'] = []
    res_query = filter_doc_fields_COLUMN(res_query, category_name, subject_name,
                                         from_year, to_year)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    if country_id == 0:
        index_name_list = []
        country_list = Country.objects.filter(language = "فارسی").exclude(name="تابناک- تست")
        for country in country_list:
            index_name = standardIndexName(country, Document.__name__)
            index_name_list.append(index_name)

        index_name =  index_name_list
    else:

        country_obj = Country.objects.get(id=country_id)
        index_name = standardIndexName(country_obj, Document.__name__)

    from_value = (curr_page - 1) * search_result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name', 'document_date',
                                               'subject_name','source_id','source_folder','source_name',
                                               "category_name", 'raw_file_name'],
                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=search_result_size

                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        "curr_page": curr_page})


def GetActorsDict(request):
    actorsDict = {}
    actors = Actor.objects.all().values('id', 'name',
                                        'actor_category_id__id',
                                        'actor_category_id__name',
                                        'forms')

    for actor in actors:
        actorsDict[actor['id']] = {
            'name': actor['name'],
            'category_id': actor['actor_category_id__id'],
            'category_name': actor['actor_category_id__name'],
            'forms': actor['forms'].split('/')
        }

    return JsonResponse({"actorsDict": actorsDict})


def GetActorsList(request):
    actorsList = []
    actors = Actor.objects.all().values('forms')

    for actor in actors:
        forms_list = actor['forms'].split('/')
        for actor_form in forms_list:
            actorsList.append(actor_form)

    return JsonResponse({"actorsList": actorsList})


def filter_document_actor_fields(res_query, role_ids=None, area_id=0, actor_id=0, actor_ids=None, actor_name='',
                                 role_name='', doc_year=0):
    if role_ids is not None:
        role_ids = [int(item) for item in role_ids]
    if actor_ids is not None:
        actor_ids = [int(item) for item in actor_ids]

    if role_ids is not None and 0 not in role_ids:
        approval_ref_query = {
            "terms": {
                "actor_type_id": role_ids
            }
        }
        res_query['bool']['filter'].append(approval_ref_query)

    # ---------------------------------------------------------
    if area_id != 0:
        level_query = {
            "term": {
                "actor_area_id": area_id
            }
        }
        res_query['bool']['filter'].append(level_query)

    # ---------------------------------------------------------
    if doc_year != 0:
        year_query = {
            "term": {
                "document_approval_year": doc_year
            }
        }
        res_query['bool']['filter'].append(year_query)

    # ---------------------------------------------------------
    if actor_id != 0:
        actor_query = {
            "term": {
                "actor_id": actor_id
            }
        }
        res_query['bool']['filter'].append(actor_query)

    # ---------------------------------------------------------
    if actor_ids is not None and 0 not in actor_ids:
        subject_query = {
            "terms": {
                "actor_id": actor_ids
            }
        }
        res_query['bool']['filter'].append(subject_query)

    # ---------------------------------------------------------
    if actor_name != '':
        actor_name_query = {
            "term": {
                "actor_name.keyword": actor_name
            }
        }
        res_query['bool']['filter'].append(actor_name_query)

    # ---------------------------------------------------------
    if role_name != '' and role_name != 'برآیند نقش\u200cها':
        role_name_query = {
            "term": {
                "actor_type_name.keyword": role_name
            }
        }
        res_query['bool']['filter'].append(role_name_query)

    return res_query


def GetColumnParagraphsByActorRoleName_Modal_es_2(request, actor_name, role_name, curr_page,
                                                  country_id, level_id, subject_id, type_id, approval_reference_id,
                                                  from_year, to_year, from_advisory_opinion_count,
                                                  from_interpretation_rules_count, revoked_type_id, place,
                                                  text, search_type):
    organization_type_id = '0'

    fields = [level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
              from_advisory_opinion_count, from_interpretation_rules_count, revoked_type_id, organization_type_id]

    detail_result_size = 10
    res_query = {
        "bool": {
        }
    }

    res_query['bool']['filter'] = []
    res_query = filter_document_actor_fields(
        res_query,
        role_name=role_name,
        actor_name=actor_name)

    if not all(field == 0 for field in fields):
        res_query = filter_doc_actor_fields(res_query, level_id, subject_id, type_id, approval_reference_id, from_year,
                                            to_year, from_advisory_opinion_count, from_interpretation_rules_count,
                                            revoked_type_id, organization_type_id)

    if len(res_query['bool']['filter']) == 0:
        del res_query['bool']['filter']

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text_doc_actor(res_query, place,
                                                    text, 'filter' not in res_query['bool'])
        else:
            res_query = boolean_search_text_doc_actor(res_query, place,
                                                      text,
                                                      search_type, 'filter' not in res_query['bool'])

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentActor.__name__)

    from_value = (curr_page - 1) * detail_result_size

    # print(res_query)

    response = client.search(index=index_name,
                             _source_includes=['paragraph_id',
                                               'actor_name',
                                               'actor_name',
                                               'document_id',
                                               "document_name",
                                               'attachment.content',
                                               'actor_type_name',
                                               'current_actor_form',
                                               'general_definition_text',
                                               'ref_paragraph_text'],
                             request_timeout=40,
                             query=res_query,
                             # aggregations=res_agg,
                             from_=from_value,
                             size=detail_result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             },
                             # size=0,
                             # track_total_hits=True,
                             )

    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    max_page = ((total_hits - 1) // detail_result_size) + 1

    # print(response['hits']['hits'][0]['highlight'])

    actor_paragraphs_result = {}
    for res in response['hits']['hits']:
        # highlight =
        paragraph_id = res["_source"]["paragraph_id"]
        document_id = res["_source"]["document_id"]
        document_name = res["_source"]["document_name"]
        paragraph_text = res["_source"]["attachment"]['content'] if (
                text == "empty" or 'highlight' not in res.keys()) else res["highlight"]["attachment.content"][0]
        paragraph_actor_role = res["_source"]["actor_type_name"]
        paragraph_actor_form = res["_source"]["current_actor_form"]
        paragraph_actor_name = res["_source"]["actor_name"]

        ref_text = ''
        para_ref_to_general_def_text = ''
        if res["_source"]["general_definition_text"] != 'نامشخص':
            para_ref_to_general_def_text = res["_source"]["general_definition_text"]
            ref_text = para_ref_to_general_def_text

        para_ref_to_para_text = ''
        if res["_source"]["ref_paragraph_text"] != 'نامشخص':
            para_ref_to_para_text = res["_source"]["ref_paragraph_text"]
            ref_text = para_ref_to_para_text

        is_ref_actor = (para_ref_to_general_def_text != 'نامشخص' or para_ref_to_para_text != 'نامشخص')

        paragraph_info = {
            'document_id': document_id,
            'document_name': document_name,
            'text': paragraph_text,
            'actor_form': paragraph_actor_form,
            'actor_name': paragraph_actor_name,
            'is_ref_actor': is_ref_actor,
            'ref_text': ref_text
        }

        if paragraph_id not in actor_paragraphs_result:
            actor_paragraphs_result[paragraph_id] = paragraph_info

    return JsonResponse({"actor_paragraphs_result": actor_paragraphs_result,
                         'max_page': max_page})


def GetSearchDetails_ES_Rahbari(request, document_id, search_type, text):
    document = Document.objects.get(id=document_id)
    country = Country.objects.get(id=document.country_id.id)

    local_index = standardIndexName(country, Document.__name__)

    result_text = ''
    place = 'متن'

    res_query = {
        "bool": {
            "filter": {
                "term": {
                    "document_id": document_id
                }
            }
        }
    }

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, False)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, False)

    response = client.search(index=local_index,
                             _source_includes=['document_id', 'paragraph_id', 'name', 'attachment.content'],
                             request_timeout=40,
                             query=res_query,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }}
                             )

    if len(response['hits']['hits']) > 0 and 'highlight' in response['hits']['hits'][0]:
        result_text = response['hits']['hits'][0]["highlight"]["attachment.content"][0]
    else:
        response = client.get(index=local_index, id=document_id,
                              _source_includes=['document_id', 'paragraph_id', 'name', 'attachment.content']
                              )
        result_text = response['_source']['attachment']['content']

    result_text = arabic_preprocessing(result_text)

    return JsonResponse({"result": result_text})


def GetSearchDetails_ES_2(request, document_id, search_type, text):
    document = Document.objects.get(id=document_id)
    country = Country.objects.get(id=document.country_id.id)

    local_index = standardIndexName(country, DocumentParagraphs.__name__) + "_graph"
    # local_index = "doticfull_documentparagraphs_graph"

    result_text = ''
    place = 'متن'

    res_query = {
        "bool": {
            "filter": {
                "term": {
                    "document_id": document_id
                }
            }
        }
    }

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, False)
        else:
            if search_type == "and":
                search_type = "or"
            res_query = boolean_search_text(res_query, place, text, search_type, False)

    response = client.search(index=local_index,
                             _source_includes=['document_id', 'paragraph_id', 'document_name', 'attachment.content'],
                             request_timeout=40,
                             query=res_query,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<span class='text-primary fw-bold'>"], "post_tags": ["</span>"],
                                          "number_of_fragments": 0
                                          }
                                 }}
                             )

    print("======= res query =============")
    print(res_query)
    result = response['hits']['hits']

    return JsonResponse({"result": result})


def GetAllUsers_Commented(reauest, user_name, user_type):
    all_other_users = User.objects.filter(is_active=1).exclude(username=user_name).values(
        'id').distinct()

    followed_users = UserFollow.objects.filter(follower__username=user_name,
                                               follower__is_active=1).values('following__id').distinct()

    un_followed_users = User.objects.filter(is_active=1).exclude(
        username=user_name).exclude(id__in=followed_users).values('id').distinct()

    if user_type == 'دنبال شده':
        other_users = User.objects.filter(id__in=followed_users)

    elif user_type == 'دنبال نشده':
        other_users = User.objects.filter(id__in=un_followed_users)

    else:
        other_users = User.objects.filter(id__in=all_other_users)

    other_users = other_users.exclude(username=user_name)

    other_user_result = []

    for user in other_users:
        user_info = {
            "id": user.id,
            "user_name": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        other_user_result.append(user_info)

    return JsonResponse({"other_users_info": other_user_result})


def GetAllUserCommentHashtags(request):
    tags = DocumentCommentHashTag.objects.all()
    result = []
    for t in tags:
        result.append({"id": t.id, "name": t.hash_tag})
    return JsonResponse({"hash_tags": result})


def follow(request, follower_username, following_user_id):
    try:
        follow_info = UserFollow.objects.get(follower__username=follower_username, following__id=following_user_id)
        return JsonResponse({"status": "already followed!"})
    except:
        follower = User.objects.get(username=follower_username)
        following = User.objects.get(id=following_user_id)
        UserFollow.objects.create(follower=follower, following=following)
        return JsonResponse({"status": "follow_request_sent!"})


def unfollow(request, follower_username, following_user_id):
    try:
        follow_info = UserFollow.objects.get(follower__username=follower_username, following__id=following_user_id)
        follow_info.delete()
        return JsonResponse({"status": "successfully unfollowed!"})
    except:
        return JsonResponse({"status": "already unfollowed!"})


def GetUserComments(request, user_id, hashtag_id):
    username = request.COOKIES.get('username')

    result = []
    comments = []

    if user_id == 0 and hashtag_id == 0:
        return JsonResponse({"comments": result})

    if hashtag_id == 0:
        follow = UserFollow.objects.get(follower__username=username, following__id=user_id)
        if follow.accepted:
            comments = DocumentComment.objects.filter(is_accept=1, show_info=True, user__id=user_id)
    elif user_id == 0:
        comments = DocumentComment.objects.filter(is_accept=1, show_info=True, hash_tags__id=hashtag_id)
    else:
        follow = UserFollow.objects.get(follower__username=username, following__id=user_id)
        if follow.accepted:
            comments = DocumentComment.objects.filter(is_accept=1, show_info=True, user__id=user_id,
                                                       hash_tags__id=hashtag_id)

    for c in comments:
        agreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=True).count()
        disagreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=False).count()
        result.append({"comment": c.comment, "id": c.id, "first_name": c.user.first_name, "last_name": c.user.last_name,
                       "agreed_count": agreed_count, "disagreed_count": disagreed_count, "time": c.time,
                       "user_id": c.user.id,
                       "document_name": c.document.name, "document_id": c.document.id})
    return JsonResponse({"comments": result})


def get_pending_followers(request):
    username = request.COOKIES.get('username')
    followers = UserFollow.objects.filter(following__username=username, accepted=False)
    result = []
    for f in followers:
        result.append({'id': f.id, 'user_id': f.follower.id, 'first_name': f.follower.first_name,
                       'last_name': f.follower.last_name})
    return JsonResponse({'result': result})


def accept_follower(request, id):
    u = UserFollow.objects.get(id=id)
    u.accepted = True
    u.save()
    return JsonResponse({})


def reject_follower(request, id):
    u = UserFollow.objects.get(id=id)
    u.delete()
    return JsonResponse({})


def self(request):
    username = request.COOKIES.get('username')
    user = User.objects.get(username=username)
    return JsonResponse({"name": user.first_name + ' ' + user.last_name + ' '})




def GetSubjectsByCountryId(request, country_id):
    documents_subjects_list = Subject.objects.all().order_by("id")

    result = []
    for row in documents_subjects_list:
        subject_id = row.id
        subject_name = row.name
        res = {
            "id": subject_id,
            "subject": subject_name
        }
        result.append(res)
    return JsonResponse({'documents_subject_list': result})


def GetDocumentsByCountryId_Modal(request, country_id=None, start_index=None, end_index=None):
    data = list(CUBE_DocumentJsonList.objects.filter(country_id__id=country_id)
                .values_list('json_text', flat=True))
    doc_count = data.__len__()
    if end_index > 0:
        data = data[start_index: end_index]

    return JsonResponse({'documentsList': data, 'document_count': doc_count})

def GetGeneralDefinition2(request, document_id):
    result = []
    paragraphs = DocumentParagraphs.objects.filter(document_id=document_id)
    black_list = ["سوم", "از قبیل", "از جمله", "مرحله", "پیوست", "تبصره", "ماده", "اصل", "تاریخ", "عبارتند از", "بخش",
                  "فصل"]
    for paragraph in paragraphs:
        paragraph_text = paragraph.text
        paragraph_index = paragraph_text.index(paragraph_text)

        for i in range(paragraph_index, len(paragraph_text)):
            if paragraph_text[i] == ':' and i != (len(paragraph_text) - 1):
                word = paragraph_text[paragraph_index: i]
                for j in range(paragraph_index, len(word)):
                    if word[j] == '-' or word[j] == '–' or word[j] == 'ـ' or word[j] == '.':
                        word = word[j + 2:len(word)]
                        break

                if len(word) < 4 or len(word) > 50 or any(x in word for x in black_list):
                    continue
                definition = ''
                word_index = paragraph_text.find(':')
                for j in range(word_index, len(paragraph_text)):
                    definition = paragraph_text[word_index + 1: j + 1]

                result.append({'word': word, 'definition': definition})

    return JsonResponse({'result': result})


def GetActorsPararaphsByDocumentId(request, document_id):
    document_motevali_ejra_paragraphs = {}
    document_salahiat_ekhtiar_paragraphs = {}
    document_hamkaran_paragraphs = {}

    role_info_list = [
        {'role_name': 'متولی اجرا',
         'result_dict': document_motevali_ejra_paragraphs
         },
        {'role_name': 'همکار',
         'result_dict': document_hamkaran_paragraphs
         },
        {'role_name': 'دارای صلاحیت اختیاری',
         'result_dict': document_salahiat_ekhtiar_paragraphs
         }
    ]

    for role_info in role_info_list:

        role_name = role_info['role_name']
        result_dict = role_info['result_dict']

        actor_paragraphs = DocumentActor.objects.filter(document_id__id=document_id,
                                                        actor_type_id__name=role_name)

        for para_info in actor_paragraphs:
            para_id = para_info.paragraph_id.id
            para_text = para_info.paragraph_id.text
            para_actor_name = para_info.actor_id.name
            para_actor_form = para_info.current_actor_form

            para_ref_to_general_def = para_info.ref_to_general_definition

            para_ref_to_general_def_text = ''
            if para_ref_to_general_def:
                para_ref_to_general_def_text = para_info.general_definition_id.text

            para_ref_to_paragraph = para_info.ref_to_paragraph
            para_ref_to_para_text = ''

            if para_ref_to_paragraph:
                para_ref_to_para_text = para_info.ref_paragraph_id.text

            is_ref_actor = (para_ref_to_general_def or para_ref_to_paragraph)

            ref_text = ''

            if para_ref_to_general_def:
                ref_text = para_ref_to_general_def_text
            elif para_ref_to_paragraph:
                ref_text = para_ref_to_para_text

            result_dict[para_id] = {
                'text': para_text,
                'actor_name': para_actor_name,
                'actor_form': para_actor_form,
                'actor_role': role_name,
                'ref_to_general_def': para_ref_to_general_def,
                'ref_general_text': para_ref_to_general_def_text,

                'ref_to_paragraph': para_ref_to_paragraph,
                'ref_para_text': para_ref_to_para_text,

                'is_ref_actor': is_ref_actor,
                'ref_text': ref_text

            }

    actors_paragraphs = {
        'document_motevali_ejra_paragraphs': document_motevali_ejra_paragraphs,
        'document_salahiat_ekhtiar_paragraphs': document_salahiat_ekhtiar_paragraphs,
        'document_hamkaran_paragraphs': document_hamkaran_paragraphs
    }
    return JsonResponse({"actors_paragraphs": actors_paragraphs})


def GetBM25Similarity(request, document_id):
    sim_docs = []
    # index_name = Document.objects.get(id = document_id).country_id.name.replace(' ','_')
    country_obj = Document.objects.get(id=document_id).country_id
    index_name = standardIndexName(country_obj, Document.__name__)

    sim_query = {
        "more_like_this": {
            "analyzer": "persian_custom_analyzer",
            "fields": ["attachment.content"],
            "like": [
                {
                    "_index": index_name,
                    "_id": "{}".format(document_id),

                }

            ],
            "min_term_freq": 50,
            "max_query_terms": 100000
        }
    }

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'approval_date', 'approval_reference_name'],
                             request_timeout=40,
                             query=sim_query
                             )

    sim_docs = response['hits']['hits']

    return JsonResponse({'docs': sim_docs})

def GetDocumentsSimilarity(request, document_id, ):
    sim_docs = []

    document_country_object = Document.objects.get(id=document_id).country_id
    main_document_index_name = standardIndexName(document_country_object, Document.__name__)

    country_objects = Country.objects.all()
    similarity_types = ["BM25"]
    for country_obj in country_objects:
        index_name = standardIndexName(country_obj, Document.__name__)

        stopword_list = []
        all_stopwords = get_stopword_list("all_stopwords.txt")
        rahbari_stopwords = get_stopword_list("all_stopwords.txt")

        stopword_list.extend(all_stopwords)
        stopword_list.extend(rahbari_stopwords)

        sim_query = {
            "more_like_this": {
                "analyzer": "persian_custom_analyzer",
                "fields": ["attachment.content"],
                "like": [
                    {
                        "_index": main_document_index_name,
                        "_id": "{}".format(document_id),
                    }
                ],
                "min_term_freq": 10,
                "min_word_length": 2,
                "max_query_terms": 100000,
                "minimum_should_match": "50%",
                "stop_words": stopword_list
            }
        }

        response = client.search(index=index_name,
                                 _source_includes=['document_id', 'document_name', 'document_date'],
                                 request_timeout=40,
                                 query=sim_query,
                                 size=100
                                 )

        result = response['hits']['hits']

        for item in result:
            newItem = {"document_id": item["_source"]["document_id"],
                       "document_name": item["_source"]["document_name"],
                       "document_date": item["_source"]["document_date"],
                       "BM25_score": item["_score"],
                       "country_name": country_obj.name
                       }
            sim_docs.append(newItem)

        sim_docs.sort(key=return_score, reverse=True)
    return JsonResponse({'docs': sim_docs[:20]})

def return_score(item):
    return item["BM25_score"]
def similarityDetail(request, main_document_id, selected_document_id, selected_country_name):
    country_obj = Document.objects.get(id=main_document_id).country_id
    base_index_name = standardIndexName(country_obj, Document.__name__)

    selected_country_object = Country.objects.get(name=selected_country_name)
    selected_index_name = standardIndexName(selected_country_object, Document.__name__)

    # if similarity_type == "BM25":
    #     index_name = base_index_name + "_bm25_index"
    # elif similarity_type == "DFI":
    #     index_name = base_index_name + "_dfi_index"
    # elif similarity_type == "DFR":
    #     index_name = base_index_name + "_dfr_index"

    res_query = {
        "bool": {
            "must": [],
            "filter": [
                {
                    "term": {"document_id": selected_document_id}
                }
            ]
        }
    }
    stopword_list = []
    all_stopwords = get_stopword_list("all_stopwords.txt")
    rahbari_stopwords = get_stopword_list("all_stopwords.txt")

    stopword_list.extend(all_stopwords)
    stopword_list.extend(rahbari_stopwords)
    sim_query = {
        "more_like_this": {
            "analyzer": "persian_custom_analyzer",
            "fields": ["attachment.content"],
            "like": [
                {
                    "_index": base_index_name,
                    "_id": "{}".format(main_document_id),
                }
            ],
            "min_term_freq": 5,
            "min_word_length": 2,
            "max_query_terms": 100000,
            "minimum_should_match": "20%",
            "stop_words": stopword_list
        }
    }

    res_query["bool"]["must"].append(sim_query)

    response = client.search(index=selected_index_name,
                             _source_includes=['document_id', 'document_name'],
                             request_timeout=40,
                             query=res_query,
                             highlight={
                                 "type": "fvh",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<span class='text-primary fw-bold'>"], "post_tags": ["</span>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }
                             )

    result = response['hits']['hits']

    highlighted_result = result[0]['highlight']['attachment.content'][0]
    splited_list = highlighted_result.split("<span class='text-primary fw-bold'>")

    new_res_query = {
        "bool": {
            "filter": [
                {"term": {
                    "document_id": main_document_id
                }
                }
            ],
            "should": []
        }
    }

    for item in splited_list:
        highlighted_word = item.split("</span>")[0]
        new_res_query["bool"]["should"].append({"match_phrase": {"attachment.content": highlighted_word}})

    new_response = client.search(index=base_index_name,
                                 _source_includes=['document_id', 'document_name'],
                                 request_timeout=40,
                                 query=new_res_query,
                                 highlight={
                                     "fields": {
                                         "attachment.content":
                                             {"pre_tags": ["<span class='text-primary fw-bold'>"],
                                              "post_tags": ["</span>"],
                                              "number_of_fragments": 0
                                              }
                                     }
                                 }
                                 )

    new_result = new_response['hits']['hits']

    return JsonResponse({"similarity_result": result, "main_doc_result": new_result})

def GetDocActorParagraphs_Column_Modal(request, document_id, actor_name, role_name):
    actor_paragraphs = {}
    result_paragraphs = DocumentActor.objects.filter(
        document_id__id=document_id,
        actor_id__name=actor_name,
        actor_type_id__name=role_name
    )

    for para_info in result_paragraphs:
        para_id = para_info.paragraph_id.id
        para_text = para_info.paragraph_id.text
        para_actor_name = para_info.actor_id.name
        para_actor_form = para_info.current_actor_form

        para_ref_to_general_def = para_info.ref_to_general_definition

        para_ref_to_general_def_text = ''
        if para_ref_to_general_def:
            para_ref_to_general_def_text = para_info.general_definition_id.text

        para_ref_to_paragraph = para_info.ref_to_paragraph
        para_ref_to_para_text = ''

        if para_ref_to_paragraph:
            para_ref_to_para_text = para_info.ref_paragraph_id.text

        is_ref_actor = (para_ref_to_general_def or para_ref_to_paragraph)

        ref_text = ''

        if para_ref_to_general_def:
            ref_text = para_ref_to_general_def_text
        elif para_ref_to_paragraph:
            ref_text = para_ref_to_para_text

        actor_paragraphs[para_id] = {
            'text': para_text,
            'actor_name': para_actor_name,
            'actor_form': para_actor_form,
            'actor_role': role_name,
            'ref_to_general_def': para_ref_to_general_def,
            'ref_general_text': para_ref_to_general_def_text,

            'ref_to_paragraph': para_ref_to_paragraph,
            'ref_para_text': para_ref_to_para_text,

            'is_ref_actor': is_ref_actor,
            'ref_text': ref_text

        }

    return JsonResponse({"actor_paragraphs": actor_paragraphs})




def GetDocumentContent(request, document_id):
    document_paragraphs = []
    paragraphs = DocumentParagraphs.objects.filter(document_id=document_id)

    for paragraph in paragraphs:
        document_name = paragraph.document_id.name
        paragraph_text = paragraph.text
        paragraph_id = paragraph.id
        paragraph_subject = ParagraphsSubject.objects.filter(paragraph=paragraph)
        if paragraph_subject.count() > 0:
            paragraph_subject = paragraph_subject[0].subject1_name
        else:
            paragraph_subject = ""
        document_paragraphs.append(
            {'paragraph_text': paragraph_text, 'paragraph_id': paragraph_id, 'document_name': document_name,
             'subject_name': paragraph_subject})

    return JsonResponse({'document_paragraphs': document_paragraphs})


def GetDocumentSubjectContent(request, document_id, version_id):
    document_paragraphs = []
    paragraphs = DocumentParagraphs.objects.filter(document_id=document_id)

    for paragraph in paragraphs:
        document_name = paragraph.document_id.name
        paragraph_text = paragraph.text
        paragraph_subject = ParagraphsSubject.objects.filter(paragraph=paragraph, version_id=version_id)

        if paragraph_subject.count() > 0:
            subject1_name = paragraph_subject[0].subject1_name
            subject1_score = round(paragraph_subject[0].subject1_score, 3)
            subject1_keywords = " - ".join([keyword + " (" + str(round(score, 2)) + ")" for keyword, score in
                                            dict(paragraph_subject[0].subject1_keywords).items()])

            subject1_row = "<tr>" + "<td  class ='subject_table_cell'>1</td>" + \
                           "<td class ='subject_table_cell'>" + subject1_name + "</td>" + \
                           "<td class ='subject_table_cell'>" + str(subject1_score) + "</td>" + \
                           "<td class ='subject_table_cell'>" + subject1_keywords + "</td></tr>"

            subject2_row = ""
            if paragraph_subject[0].subject2_name is not None:
                subject2_name = paragraph_subject[0].subject2_name
                subject2_score = round(paragraph_subject[0].subject2_score, 3)
                subject2_keywords = " - ".join([keyword + " (" + str(round(score, 2)) + ")" for keyword, score in
                                                dict(paragraph_subject[0].subject2_keywords).items()])
                subject2_row = "<tr>" + "<td class ='subject_table_cell'>2</td>" + \
                               "<td class ='subject_table_cell'>" + subject2_name + "</td>" + \
                               "<td class ='subject_table_cell'>" + str(subject2_score) + "</td>" + \
                               "<td class ='subject_table_cell'>" + subject2_keywords + "</td></tr>"

            subject3_row = ""
            if paragraph_subject[0].subject3_name is not None:
                subject3_name = paragraph_subject[0].subject3_name
                subject3_score = round(paragraph_subject[0].subject3_score, 3)
                subject3_keywords = " - ".join([keyword + " (" + str(round(score, 2)) + ")" for keyword, score in
                                                dict(paragraph_subject[0].subject3_keywords).items()])
                subject3_row = "<tr>" + "<td class ='subject_table_cell'>3</td>" + \
                               "<td class ='subject_table_cell'>" + subject3_name + "</td>" + \
                               "<td class ='subject_table_cell'>" + str(subject3_score) + "</td>" + \
                               "<td class ='subject_table_cell'>" + subject3_keywords + "</td></tr>"

            subject_row = subject1_row + subject2_row + subject3_row
            subject_table = '<table class="table-striped" style="margin: auto;width: 100%;">' \
                            '<thead>' \
                            '<tr>' \
                            '<th class="col-1 subject_table_cell">ردیف</th>' \
                            '<th class="col-3 subject_table_cell">موضوع</th>' \
                            '<th class="col-2 subject_table_cell">امتیاز (نرمال)</th>' \
                            '<th class="col-6 subject_table_cell">کلیدواژه (امتیاز)</th>' \
                            '</tr>' \
                            '</thead>' \
                            '<tbody>' + subject_row + '</tbody>' \
                                                      '</table>'
        else:
            subject_table = ""
        document_paragraphs.append(
            {'paragraph_text': paragraph_text, 'document_name': document_name, 'subject_name': subject_table})

    return JsonResponse({'document_paragraphs': document_paragraphs})



def CreateDocumentComment(request, document, comment, username, comment_show_info, time):
    user = User.objects.filter(username=username).first()
    doc = Document.objects.filter(id=document).first()
    show_info = False
    if comment_show_info == 'true':
        show_info = True
    comment = DocumentComment.objects.create(document=doc, comment=comment, user=user, show_info=show_info,
                                              time=str(jdatetime.strftime(jdatetime.now(), "%H:%M:%S %Y-%m-%d")))

    return JsonResponse({"comment_id": comment.id})


def CreateHashTagForDocumentComment(request, comment_id, hash_tag):
    # createdDocumentComment = DocumentComment2.objects.get(id=comment_id)
    try:
        ht = DocumentCommentHashTag.objects.get(hash_tag=hash_tag)

    except:
        ht = DocumentCommentHashTag.objects.create(hash_tag=hash_tag)

    # createdDocumentComment.hash_tags.add(ht)
    # createdDocumentComment.save()
    DocumentComment.objects.filter(id=comment_id).update(hash_tags=ht)

    return JsonResponse({"hash_tags": ht.hash_tag})


def CreateDocumentNote(request, document, note, username, time, label):
    user = User.objects.filter(username=username).first()
    doc = Document.objects.filter(id=document).first()
    DocumentNote.objects.create(document=doc, note=note, user=user, time=time, docLabel=label)
    createdNote = DocumentNote.objects.last()
    # createdNote = DocumentNote.objects.create(document=doc, note=note, user=user,time =time , docLabel = label)

    return JsonResponse({"note_id": createdNote.id})


def CreateHashTagForNote(request, note_id, hash_tag):
    createdNote = DocumentNote.objects.filter(id=note_id).first()
    # createdNote = DocumentNote.objects.last()
    ht = NoteHashTag(hash_tag=hash_tag)
    ht.save()
    createdNote.hash_tags.add(ht)
    createdNote.save()

    return JsonResponse({"hash_tags": createdNote.hash_tags.last().hash_tag})
    # return JsonResponse({})


def GetDocumentComments(request, document, username):
    followings = UserFollow.objects.filter(follower__username=username)
    follows = {}
    for f in followings:
        if f.accepted:
            follows[f.following.id] = 1
        else:
            follows[f.following.id] = -1

    user_comments = DocumentComment.objects.filter(document=document, user__username=username)
    other_user_comments = DocumentComment.objects.filter(document=document, is_accept=1).exclude(
        user__username=username)
    result = []
    for c in other_user_comments:
        agreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=True).count()
        disagreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=False).count()

        if c.show_info:
            # not followed
            followed = 0
            if c.user.id in follows:
                followed = follows[c.user.id]
            result.append(
                {"comment": c.comment, "id": c.id, "first_name": c.user.first_name, "last_name": c.user.last_name,
                 "agreed_count": agreed_count, "disagreed_count": disagreed_count, "time": c.time, "user_id": c.user.id,
                 "followed": followed})
        else:
            result.append(
                {"comment": c.comment, "id": c.id, "first_name": '*', "last_name": '*', "agreed_count": agreed_count,
                 "disagreed_count": disagreed_count, "time": c.time})

    for c in user_comments:
        agreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=True).count()
        disagreed_count = DocumentCommentVote.objects.filter(document_comment=c.id, agreed=False).count()
        result.append({"comment": c.comment, "id": c.id, "first_name": c.user.first_name, "last_name": c.user.last_name,
                       "agreed_count": agreed_count, "disagreed_count": disagreed_count, "time": c.time,
                       "user_id": c.user.id, "accepted": c.is_accept})
    return JsonResponse({"comments": result})


def GetDocumentNotes(request, document, username):
    notes = DocumentNote.objects.filter(document=document, user__username=username)
    result = []
    for n in notes:
        result.append({"note": n.note, "time": n.time, "label": n.docLabel, "starred": n.starred, "id": n.id,
                       "document_name": n.document.name})
    return JsonResponse({"notes": result})


def changeVoteState(request, username, document_comment, state):
    agreed = False
    if state == "agree":
        agreed = True
    # voted or not yet?
    try:
        vote = DocumentCommentVote.objects.get(user__username=username, document_comment=document_comment)
        vote.agreed = agreed
        vote.modified_at = datetime.datetime.utcnow()
        vote.save()
    except:
        user = User.objects.filter(username=username).first()
        document_comment = DocumentComment.objects.filter(id=document_comment).first()
        DocumentCommentVote.objects.create(user=user,
                                           document_comment=document_comment,
                                           agreed=agreed)
    return JsonResponse({})


def GetFollowings(request, follower_username):
    followings = UserFollow.objects.filter(follower__username=follower_username, accepted=True)
    follows = {}
    for f in followings:
        follows[f.following.id] = {"first_name": f.following.first_name, "last_name": f.following.last_name,
                                   "id": f.following.id}
    return JsonResponse({"follows": list(follows.values())})


def GetAllKnowledgeGraphList(request, username):
    KnowledgeGraphVersionList = KnowledgeGraphVersion.objects.filter(Q(username=username) | Q(username="default"))
    result = []
    for row in KnowledgeGraphVersionList:
        id = row.id
        name = row.name
        username = row.username
        result.append({"id": id, "name": name, "username": username})

    return JsonResponse({"knowledge_graph_list": result})


def GetKnowledgeGraphData(request, version_id):
    graph_data = KnowledgeGraphData.objects.get(version_id=version_id)

    Nodes_data, Edges_data = graph_data.nodes, graph_data.edges

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


def SaveKnowledgeGraph(request, graph_name, username, graph_id):
    nodes_data = np.array(request.POST.get('nodes_data').split(",")).reshape(-1, 4)
    edges_data = np.array(request.POST.get('edges_data').split(",")).reshape(-1, 7)

    nodes_list = []
    for row in nodes_data:
        res = {"id": row[0], "name": row[1], "EN_name": row[2], "weight": row[3], "label": row[1]}
        nodes_list.append(res)

    edges_list = []
    for row in edges_data:
        res = {"source": row[0], "source_name": row[1], "source_En_name": row[2],
               "target": row[3], "target_name": row[4], "target_EN_name": row[5],
               "weight": row[6], "label": row[6]}
        edges_list.append(res)

    if graph_id == 0:
        version = KnowledgeGraphVersion.objects.create(name=graph_name, username=username)
        KnowledgeGraphData.objects.create(version=version, nodes=nodes_list, edges=edges_list)
        return JsonResponse({'version_id': version.id})
    else:
        version = KnowledgeGraphVersion.objects.get(id=graph_id)
        KnowledgeGraphVersion.objects.filter(id=graph_id).update(name=graph_name)
        KnowledgeGraphData.objects.filter(version=version).update(nodes=nodes_list, edges=edges_list)
        return JsonResponse({'version_id': 0})


def DeleteKnowledgeGraph(request, graph_id):
    KnowledgeGraphVersion.objects.filter(id=graph_id).delete()
    return JsonResponse({'responce': "OK"})


def BoostingSearchKnowledgeGraph_ES(request, country_id, field_name, field_value, language, search_type, curr_page,
                                    result_size):
    country_obj = Country.objects.get(id=country_id)
    keyword_score_dict = dict(request.POST)
    cluser_keyword_data = np.array(keyword_score_dict['cluser_keyword_data'][0].split(',')).reshape(-1, 3)

    if language == "IRI":

        cluser_keyword_data = cluser_keyword_data[:, [0, 2]]

        if search_type == "AND":
            search_type = "must"
            index_name = standardIndexName(country_obj, DocumentParagraphs.__name__ + '_graph')
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "OR":
            search_type = "should"
            index_name = standardIndexName(country_obj, DocumentParagraphs.__name__ + '_graph')
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "AND_DOC":
            search_type = "must"
            index_name = standardIndexName(country_obj, Document.__name__)
            result_field = ['document_id', 'document_name', 'attachment.content']

    if language == "UK":

        cluser_keyword_data = cluser_keyword_data[:, [1, 2]]

        if search_type == "AND":
            search_type = "must"
            index_name = "uk-full-fixed_documentparagraphs_graph"
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "OR":
            search_type = "should"
            index_name = "uk-full-fixed_documentparagraphs_graph"
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "AND_DOC":
            search_type = "must"
            index_name = "uk-full-fixed_document"
            result_field = ['document_id', 'name', 'attachment.content']

    if language == "US":

        cluser_keyword_data = cluser_keyword_data[:, [1, 2]]

        if search_type == "AND":
            search_type = "must"
            index_name = "us-fixed_documentparagraphs_graph"
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "OR":
            search_type = "should"
            index_name = "us-fixed_documentparagraphs_graph"
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "AND_DOC":
            search_type = "must"
            index_name = "us-fixed_document"
            result_field = ['document_id', 'name', 'attachment.content']

    if language == "BBC":

        cluser_keyword_data = cluser_keyword_data[:, [1, 2]]

        if search_type == "AND":
            search_type = "must"
            index_name = "bbc_full_documentparagraphs_graph"
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "OR":
            search_type = "should"
            index_name = "bbc_full_documentparagraphs_graph"
            result_field = ['document_id', 'document_name', 'paragraph_id', 'attachment.content']

        elif search_type == "AND_DOC":
            search_type = "must"
            index_name = "bbc_full_document"
            result_field = ['document_id', 'document_name', 'attachment.content']


    res_query = {"bool": {
        "filter": [
            {
                "range": {
                    "attachment.content_length": {
                        "gte": 2
                    }
                }
            }
        ],
        "must": {
            "bool": {
                search_type: []
            }
        }
    }}

    if field_name != "0":
        res_query["bool"]["filter"].append({"term": {field_name: {"value": field_value}}})

    for row in cluser_keyword_data:
        keyword = row[0]
        score = row[1]

        word_query = {
            "multi_match": {
                "query": keyword,
                "type": "phrase",
                "fields": ["attachment.content"],
                "boost": score
            }
        }
        res_query['bool']['must']['bool'][search_type].append(word_query)

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "subject-agg": {
            "terms": {
                "field": "subject_name.keyword",
                "size": bucket_size
            }
        },

        "category-agg": {
            "terms": {
                "field": "category_name.keyword",
                "size": bucket_size
            }
        },
        "year-agg": {
            "terms": {
                "field": "document_year",
                "size": bucket_size
            }
        }

    }

    from_value = (curr_page - 1) * result_size

    response = client.search(index=index_name,
                             _source_includes=result_field,
                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             aggregations=res_agg,
                             size=result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em class='text-primary fw-bold'>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }
                             )

    result = response['hits']['hits']
    aggregations = response['aggregations']
    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name)['count']

    response_dict = {
        'total_hits': total_hits,
        'aggregations': aggregations,
        "curr_page": curr_page,
        "result": result
    }
    return JsonResponse(response_dict)

def GetActorsByDocumentIdActorType(document_id, actor_type_name):
    actor_dict = {}

    document_actors = DocumentActor.objects.filter(document_id_id=document_id,
                                                   actor_type_id__name=actor_type_name).annotate(
        actor_name=F('actor_id__name')).values('actor_name')

    # fill actor dict
    for actor in document_actors:
        actor_name = actor['actor_name']

        if actor_name not in actor_dict:
            actor_dict[actor_name] = 1
        else:
            actor_dict[actor_name] += 1

    return actor_dict


def GetDocumentById_Local(id):
    document = Document.objects.get(id=id)
    document_actors = {}

    motevalian_dict = GetActorsByDocumentIdActorType(id, 'متولی اجرا')
    hamkaran_dict = GetActorsByDocumentIdActorType(id, 'همکار')
    salahiat_dict = GetActorsByDocumentIdActorType(id, 'دارای صلاحیت اختیاری')

    document_actors['motevalian'] = motevalian_dict
    document_actors['hamkaran'] = hamkaran_dict
    document_actors['salahiat'] = salahiat_dict

    approval_ref = "نامشخص"
    if document.approval_reference_id != None:
        approval_ref = document.approval_reference_name

    approval_date = "نامشخص"
    approval_year = "نامشخص"
    if document.approval_date != None:
        approval_date = document.approval_date
        approval_year = approval_date[0:4]

    communicated_date = "نامشخص"
    if document.communicated_date != None:
        communicated_date = document.communicated_date

    type_name = "سایر"
    if document.type_id != None:
        type_name = document.type_name

    level_name = "نامشخص"
    if document.level_id != None:
        level_name = document.level_name

    subject_name = "نامشخص"
    if document.subject_id != None:
        subject_name = document.subject_name

    result = {"id": document.id,
              "name": document.name,
              "country_id": document.country_id_id,
              "country": document.country_id.name,
              "level_id": document.level_id_id,
              "level": level_name,
              "subject_id": document.subject_id_id,
              "subject": subject_name,
              "type_id": document.type_id_id,
              "type": type_name,
              "approval_reference_id": document.approval_reference_id_id,
              "approval_reference": approval_ref,
              "approval_date": approval_date,
              "approval_year": approval_year,
              "communicated_date": communicated_date,
              "word_count": document.word_count,
              "distinct_word_count": document.distinct_word_count,
              "stopword_count": document.stopword_count,
              "actors": document_actors
              }
    return result


def Get_Clustering_Vocabulary(request, country_id, vector_type, ngram_type):
    res_features = ParagraphsFeatures.objects.get(country__id=country_id,
                                                  feature_extractor=vector_type,
                                                  ngram_type=ngram_type).features

    table_data = []
    i = 0
    for feature in res_features:
        i += 1
        term = feature[0],
        IDF = feature[1]
        row = {'index': i, 'term': term, "IDF": IDF}
        table_data.append(row)

    return JsonResponse({
        'table_data': table_data
    })


def Get_ClusterCenters_ChartData(request, country_id, algorithm_name, vector_type, cluster_count, ngram_type):
    algorithm_id = ClusteringAlgorithm.objects.get(
        name=algorithm_name,
        input_vector_type=vector_type,
        cluster_count=cluster_count,
        ngram_type=ngram_type
    ).id

    try:

        heatmap_chart_data = ClusteringResults.objects.get(
            country__id=country_id,
            algorithm__id=algorithm_id
        ).heatmap_chart_data["data"]

        cluster_size_chart_data = ClusteringResults.objects.get(
            country__id=country_id,
            algorithm__id=algorithm_id
        ).cluster_size_chart_data["data"]

    except:
        heatmap_chart_data = []
        cluster_size_chart_data = []

    return JsonResponse({
        'heatmap_chart_data': heatmap_chart_data,
        'cluster_size_chart_data': cluster_size_chart_data
    })


def Get_ClusteringAlgorithm_DiscriminatWords_ChartData(request, country_id, algorithm_name, vector_type, cluster_count,
                                                       ngram_type):
    algorithm_id = ClusteringAlgorithm.objects.get(
        name=algorithm_name,
        input_vector_type=vector_type,
        cluster_count=cluster_count,
        ngram_type=ngram_type
    ).id

    try:

        anova_chart_data = FeatureSelectionResults.objects.get(
            country__id=country_id,
            c_algorithm__id=algorithm_id,
            f_algorithm__name="ANOVA"
        ).important_words_chart_data["data"]

        decision_tree_chart_data = FeatureSelectionResults.objects.get(
            country__id=country_id,
            c_algorithm__id=algorithm_id,
            f_algorithm__name="DecisionTree"
        ).important_words_chart_data["data"]

    except:

        anova_chart_data = []
        decision_tree_chart_data = []

    return JsonResponse({
        'anova_chart_data': anova_chart_data,
        'decision_tree_chart_data': decision_tree_chart_data
    })


def Get_ClusteringEvaluation_Silhouette_ChartData(request, country_id, algorithm_name, vector_type, ngram_type):
    eval_result = ClusteringEvaluationResults.objects.get(
        country__id=country_id,
        name=algorithm_name,
        input_vector_type=vector_type,
        ngram_type=ngram_type
    )

    silhouette_score_chart_data = eval_result.silhouette_score_chart_data
    elbow_inertia_chart_data = eval_result.elbow_inertia_chart_data

    return JsonResponse({
        'silhouette_score_chart_data': silhouette_score_chart_data,
        "elbow_inertia_chart_data": elbow_inertia_chart_data
    })


def Get_ANOVA_Word_Paragraphs_Column_ES(request, country_id, topic_id, word, curr_page, result_size):
    res_query = {"bool": {
        "must": [
            {
                "term": {
                    "topic_id.keyword": {
                        "value": topic_id}
                }
            },
            {
                "bool": {
                    "should": [
                        {
                            "match_phrase": {
                                "attachment.content": {
                                    "query": word
                                }
                            }
                        },
                        {
                            "match_phrase": {
                                "preprocessed_text": {
                                    "query": word
                                }
                            }
                        }
                    ]
                }
            }
        ]
    }}

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, ParagraphsTopic.__name__)

    # ---------------------- Get Chart Data -------------------------

    from_value = (curr_page - 1) * result_size
    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name',
                                               'paragraph_id', 'attachment.content',
                                               'topic_id', 'topic_name',
                                               'score'],

                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em class='text-primary fw-bold'>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }

                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    response_dict = {
        'total_hits': total_hits,
        "curr_page": curr_page,
        "result": result
    }

    return JsonResponse(response_dict)


def Export_ANOVA_Word_Paragraphs_Column_ES(request, country_id, topic_id, word, username, curr_page, result_size):
    res_query = {"bool": {
        "must": [
            {
                "term": {
                    "topic_id.keyword": {
                        "value": topic_id}
                }
            },
            {
                "match_phrase": {
                    "attachment.content": {
                        "query": word
                    }
                }
            }
        ]
    }}

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, ParagraphsTopic.__name__)

    # ---------------------- Get Chart Data -------------------------

    from_value = (curr_page - 1) * result_size
    response = client.search(index=index_name,
                             _source_includes=['document_name', 'paragraph_id',
                                               'attachment.content', 'topic_name',
                                               'score'],

                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size,

                             )

    result = response['hits']['hits']

    result_range = str(from_value) + " تا " + str(from_value + len(result))

    paragraph_list = [
        [doc['_source']['document_name']
            , doc['_source']['attachment']['content'],
         doc['_source']['score']] for doc in result]

    cluster_name = ClusterTopic.objects.get(id=topic_id).name.replace('C', 'شماره ')

    try:
        user_topic_label = UserTopicLabel.objects.get(
            topic__id=topic_id,
            user__username=username).label
    except:
        user_topic_label = 'بدون برچسب'

    file_dataframe = pd.DataFrame(paragraph_list, columns=["نام خبر", "متن پاراگراف", "امتیاز"])

    file_name = country_obj.name + " - " + "واژه: " + word + " در " + "احکام خوشه " + cluster_name + \
                " - " + user_topic_label + " - " + result_range + ".xlsx"

    file_path = os.path.join(config.MEDIA_PATH, file_name)
    file_dataframe.to_excel(file_path, index=False)

    return JsonResponse({"file_name": file_name})


def Get_Topic_Paragraphs_Column_ES(request, country_id, topic_id, field_name, field_value, curr_page, result_size):
    res_query = {"bool": {
        "must": [
            {
                "term": {
                    "topic_id.keyword": {
                        "value": topic_id}
                }
            },
            {
                "term":
                    {
                        field_name: {
                            "value": field_value
                        }
                    }
            }
        ],

        "should": []
    }}
    word_score_dict = ClusterTopic.objects.get(id=topic_id).words

    for word, score in word_score_dict.items():
        word = word.strip()
        integer_score = int(float(score) * 10000)
        boost_score = integer_score if integer_score > 0 else 1

        word_query = {
            "match_phrase": {
                "attachment.content": {
                    "query": word,
                    "boost": boost_score
                }
            }
        }

        res_query['bool']['should'].append(word_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, ParagraphsTopic.__name__)

    # ---------------------- Get Chart Data -------------------------

    from_value = (curr_page - 1) * result_size
    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name',
                                               'paragraph_id', 'paragraph_id',
                                               'topic_id', 'topic_name',
                                               'score'],

                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em class='text-primary fw-bold'>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          }
                                 }
                             }

                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    response_dict = {
        'total_hits': total_hits,
        "curr_page": curr_page,
        "result": result
    }

    return JsonResponse(response_dict)


def Get_Topic_Anova_ChartData(request, country_id, topic_id):
    discriminant_words_chart_data = TopicDiscriminantWords.objects.get(
        country__id=country_id,
        f_algorithm__name="ANOVA",
        topic__id=topic_id
    ).discriminant_words_chart_data["data"]

    return JsonResponse({
        "discriminant_words_chart_data": discriminant_words_chart_data
    })


def Get_Topic_TagCloud_ChartData(request, country_id, topic_id):
    tag_cloud_chart_data = []

    word_dict = ClusterTopic.objects.get(
        country__id=country_id,
        id=topic_id
    ).words

    for word, score in word_dict.items():
        tag_cloud_chart_data.append({"x": word, "value": score})

    return JsonResponse({
        "tag_cloud_chart_data": tag_cloud_chart_data
    })


def GetClusteringGraphData(request, country_id, algorithm_name, algorithm_vector_type, cluster_size, ngram_type):
    algorithm = ClusteringAlgorithm.objects.get(name=algorithm_name, input_vector_type=algorithm_vector_type,
                                               cluster_count=cluster_size, ngram_type=ngram_type)

    try:

        ClusteringGraphData_Object = ClusteringGraphData.objects.get(country_id=country_id, algorithm=algorithm)
        Nodes_data, Edges_data = ClusteringGraphData_Object.centroids_nodes_data, ClusteringGraphData_Object.centroids_edges_data
    except:
        Nodes_data, Edges_data = [], []

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


def GetClusterKeywordGraphData(request, country_id, algorithm_name, algorithm_vector_type, cluster_size, ngram_type):
    algorithm = ClusteringAlgorithm.objects.get(name=algorithm_name, input_vector_type=algorithm_vector_type,
                                               cluster_count=cluster_size, ngram_type=ngram_type)

    try:
        ClusteringGraphData_Object = ClusteringGraphData.objects.get(country_id=country_id, algorithm=algorithm)
        Nodes_data, Edges_data = ClusteringGraphData_Object.subject_keywords_nodes_data, ClusteringGraphData_Object.subject_keywords_edges_data
    except:
        Nodes_data, Edges_data = [], []
    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


def GetKeywordClustersData(request, country_id, algorithm_name, algorithm_vector_type, cluster_size, keyword):
    algorithm_id = ClusteringAlgorithm.objects.get(
        name=algorithm_name,
        input_vector_type=algorithm_vector_type,
        cluster_count=cluster_size
    ).id

    algorithm_result_data = CUBE_Clustering_TableData.objects.get(country__id=country_id, algorithm__id=algorithm_id)
    table_data = algorithm_result_data.table_data['data']

    result_table_data = []
    for row in table_data:
        if keyword in row["word_list"].split(" - "):
            result_table_data.append(row)

    return JsonResponse({
        "table_data": result_table_data
    })


def GetDetailDocumentById(request, country_id, document_id):
    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, FullProfileAnalysis.__name__)

    res_query = {
        "term": {
            "document_id": document_id
        }
    }
    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_date', 'category_name', 'document_name'],
                             request_timeout=40,
                             query=res_query)
    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    document = Document.objects.get(id=document_id)

    date = "نامشخص"
    year = "نامشخص"
    if document.date is not None:
        date = document.date
        year = date[0:4]

    category = "نامشخص"
    if document.category_name is not None:
        category = document.category_name

    subject = "نامشخص"
    if document.subject_name is not None:
        subject = document.subject_name

    return JsonResponse({
        "result": result,
        "subject": subject,
        "date": date,
        "category": category,
        'total_hits': total_hits,
    })


def rahbari_document_get_full_profile_analysis(request, country_id, document_id):
    res_query = {
        "term": {
            "document_id": document_id
        }
    }

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, FullProfileAnalysis.__name__)

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "rahbari-classification-subject-agg":
            {
                "terms": {
                    "field": "classification_subject.keyword",
                    "size": bucket_size
                }
            },
        "rahbari-person-agg":
            {
                "terms": {
                    "field": "persons.keyword",
                    "size": 10000
                }
            },
        "rahbari-location-agg":
            {
                "terms": {
                    "field": "locations.keyword",
                    "size": bucket_size
                }
            },
        "rahbari-organization-agg":
            {
                "terms": {
                    "field": "organizations.keyword",
                    "size": bucket_size
                }
            }
    }

    response = client.search(index=index_name,
                             request_timeout=40,
                             query=res_query,
                             aggregations=res_agg,
                             size=search_result_size)

    result = response['hits']['hits']
    total_hits = response['hits']['total']['value']
    aggregations = response['aggregations']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    response = client.search(index=index_name,
                             request_timeout=40,
                             query=res_query
                             )
    max_score = response['hits']['hits'][0]['_score'] if total_hits > 0 else 1
    max_score = max_score if max_score > 0 else 1
    print(aggregations)
    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        'max_score': max_score,
        'aggregations': aggregations})


def get_rahbari_document_actor(request, document_id):
    actor_contains = []
    actor_names = []

    paragraphs = DocumentParagraphs.objects.filter(document_id=document_id)
    actors = Actor.objects.all()

    for actor in actors:
        actor_forms = actor.forms.split("/")
        actor_names.extend(actor_forms)

    for actor in actor_names:
        actor_counter = 0
        for paragraph in paragraphs:
            if paragraph.text.__contains__(" " + actor + " "):
                actor_counter += 1
        if actor_counter > 0:
            actor_contains.append((actor, actor_counter))

    return JsonResponse({'result': actor_contains})


def rahbari_document_classification_chart_column(request, document_id, subject, curr_page, result_size):
    res_query = {
        "bool": {
            "filter": [
                {
                    "term": {
                        "document_id": document_id
                    }
                },
                {
                    "term": {
                        "classification_subject.keyword": subject
                    }
                }
            ]
        }
    }

    country_obj = Document.objects.get(id=document_id).country_id
    index_name = standardIndexName(country_obj, FullProfileAnalysis.__name__)

    # ---------------------- Get Chart Data -------------------------
    from_value = (curr_page - 1) * result_size
    response = client.search(index=index_name,
                             _source_includes=['attachment.content', 'document_name', 'paragraph_id', 'document_id'],
                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size
                             )

    result = response['hits']['hits']
    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        "curr_page": curr_page,
    })


def rahbari_document_name_chart_column(request, document_id, name, field_name, curr_page, result_size):
    res_query = {
        "bool": {
            "filter": [
                {
                    "term": {
                        "document_id": document_id
                    }
                },
                {
                    "term": {
                        field_name: name
                    }
                }
            ]
        }
    }

    country_obj = Document.objects.get(id=document_id).country_id
    index_name = standardIndexName(country_obj, FullProfileAnalysis.__name__)

    load_object = field_name.split(".")[0]
    load_object = load_object + "_object"
    # ---------------------- Get Chart Data -------------------------
    from_value = (curr_page - 1) * result_size
    response = client.search(index=index_name,
                             _source_includes=['attachment.content', 'document_name', 'paragraph_id', 'document_id',
                                               load_object],
                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size,
                             )

    result = response['hits']['hits']
    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        "curr_page": curr_page,
    })


def rahbari_document_actor_chart_column(request, document_id, name, curr_page, result_size):
    res_query = {
        "bool": {
            "filter": [
                {
                    "term": {
                        "document_id": document_id
                    }
                },
                {
                    "match_phrase": {
                        "attachment.content": name
                    }
                }
            ]
        }
    }

    country_obj = Document.objects.get(id=document_id).country_id
    index_name = standardIndexName(country_obj, FullProfileAnalysis.__name__)

    # ---------------------- Get Chart Data -------------------------
    from_value = (curr_page - 1) * result_size
    response = client.search(index=index_name,
                             _source_includes=['attachment.content', 'document_name', 'paragraph_id', 'document_id'],
                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size,
                             )

    result = response['hits']['hits']
    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        "curr_page": curr_page,
    })


def export_rahbari_document_chart_column(request, document_id, text, keyword, curr_page, result_size):
    res_query = {
        "bool": {
            "filter": [
                {
                    "term": {
                        "document_id": document_id
                    }
                },
                {
                    "match_phrase": {
                        keyword: text
                    }
                }
            ]
        }
    }

    country_obj = Document.objects.get(id=document_id).country_id
    index_name = standardIndexName(country_obj, FullProfileAnalysis.__name__)

    # ---------------------- Get Chart Data -------------------------
    from_value = (curr_page - 1) * result_size
    response = client.search(index=index_name,
                             _source_includes=['attachment.content', 'document_name'],
                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             size=result_size,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<span class='text-primary fw-bold'>"], "post_tags": ["</span>"],
                                          "number_of_fragments": 0
                                          }
                                 }}
                             )

    result = response['hits']['hits']

    result_range = str(from_value) + " تا " + str(from_value + len(result))

    paragraph_list = [
        [doc['_source']['document_name']
            , doc['_source']['attachment']['content']] for doc in result]

    file_dataframe = pd.DataFrame(paragraph_list, columns=["نام خبر", "متن پاراگراف"])

    file_name = country_obj.name + " - " + keyword.replace(".keyword",
                                                           "") + " : " + text + " - " + result_range + ".xlsx"

    file_path = os.path.join(config.MEDIA_PATH, file_name)
    file_dataframe.to_excel(file_path, index=False)

    return JsonResponse({"file_name": file_name})


def GetSearchDetails_ES(request, document_id, search_type, text):
    document = Document.objects.get(id=document_id)
    country = Country.objects.get(id=document.country_id.id)
    language = country.language

    local_index = standardIndexName(country, Document.__name__)

    result_text = ''
    place = 'متن'

    res_query = {
        "bool": {
            "filter": {
                "term": {
                    "document_id": document_id
                }
            }
        }
    }

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, False)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, False)

    # local_index = "doticfull_document"
    response = client.search(index=local_index,
                             _source_includes=['document_id', 'name', 'attachment.content'],
                             request_timeout=40,
                             query=res_query,
                             highlight={
                                 "order": "score",
                                 "fields": {
                                     "attachment.content":
                                         {"pre_tags": ["<em>"], "post_tags": ["</em>"],
                                          "number_of_fragments": 0
                                          #   "fragment_size":100000
                                          # "boundary_scanner" : "word"
                                          # "type":"plain"
                                          }
                                 }}

                             )

    if len(response['hits']['hits']) > 0:
        result_text = response['hits']['hits'][0]["highlight"]["attachment.content"][0]
    else:
        response = client.get(index=local_index, id=document_id,
                              _source_includes=['document_id', 'name', 'attachment.content']
                              )
        result_text = response['_source']['attachment']['content']

    return JsonResponse({
        "result": result_text})


def ingest_full_profile_analysis_to_elastic(request, id):
    file = get_object_or_404(Country, id=id)
    from es_scripts import IngestFullProfileAnalysisToElastic
    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    IngestFullProfileAnalysisToElastic.apply(folder_name, file)
    return redirect('zip')


def GetParagraphBy_ID(request, paragraph_id):
    paragraph_text = DocumentParagraphs.objects.get(id=paragraph_id).text
    country_name = DocumentParagraphs.objects.get(id=paragraph_id).document_id.country_id.name
    return JsonResponse({"paragraph_text": str(paragraph_text), "country_name": country_name})


def GetParagraphSubjectContent(request, paragraph_id, version_id):
    para_obj = DocumentParagraphs.objects.get(id=paragraph_id)
    para_text = para_obj.text
    document_id = para_obj.document_id.id
    document_name = para_obj.document_id.name

    paragraph_subject = ParagraphsSubject.objects.filter(paragraph=para_obj, version_id=version_id)

    if paragraph_subject.count() > 0:
        subject1_name = paragraph_subject[0].subject1_name
        subject1_score = round(paragraph_subject[0].subject1_score, 3)
        subject1_keywords = " - ".join([keyword + " (" + str(round(score, 2)) + ")" for keyword, score in
                                        dict(paragraph_subject[0].subject1_keywords).items()])

        subject1_row = "<tr>" + "<td  class ='subject_table_cell'>1</td>" + \
                       "<td class ='subject_table_cell'>" + subject1_name + "</td>" + \
                       "<td class ='subject_table_cell'>" + str(subject1_score) + "</td>" + \
                       "<td class ='subject_table_cell'>" + subject1_keywords + "</td></tr>"

        subject2_row = ""
        if paragraph_subject[0].subject2_name is not None:
            subject2_name = paragraph_subject[0].subject2_name
            subject2_score = round(paragraph_subject[0].subject2_score, 3)
            subject2_keywords = " - ".join([keyword + " (" + str(round(score, 2)) + ")" for keyword, score in
                                            dict(paragraph_subject[0].subject2_keywords).items()])
            subject2_row = "<tr>" + "<td class ='subject_table_cell'>2</td>" + \
                           "<td class ='subject_table_cell'>" + subject2_name + "</td>" + \
                           "<td class ='subject_table_cell'>" + str(subject2_score) + "</td>" + \
                           "<td class ='subject_table_cell'>" + subject2_keywords + "</td></tr>"

        subject3_row = ""
        if paragraph_subject[0].subject3_name is not None:
            subject3_name = paragraph_subject[0].subject3_name
            subject3_score = round(paragraph_subject[0].subject3_score, 3)
            subject3_keywords = " - ".join([keyword + " (" + str(round(score, 2)) + ")" for keyword, score in
                                            dict(paragraph_subject[0].subject3_keywords).items()])
            subject3_row = "<tr>" + "<td class ='subject_table_cell'>3</td>" + \
                           "<td class ='subject_table_cell'>" + subject3_name + "</td>" + \
                           "<td class ='subject_table_cell'>" + str(subject3_score) + "</td>" + \
                           "<td class ='subject_table_cell'>" + subject3_keywords + "</td></tr>"

        subject_row = subject1_row + subject2_row + subject3_row
        subject_table = '<table dir="rtl" class="table-striped" style="margin: auto;width: 100%;">' \
                        '<thead>' \
                        '<tr>' \
                        '<th class="col-1 subject_table_cell">ردیف</th>' \
                        '<th class="col-3 subject_table_cell">موضوع</th>' \
                        '<th class="col-2 subject_table_cell">امتیاز (نرمال)</th>' \
                        '<th class="col-6 subject_table_cell">کلیدواژه (امتیاز)</th>' \
                        '</tr>' \
                        '</thead>' \
                        '<tbody>' + subject_row + '</tbody>' \
                                                  '</table>'
    else:
        subject_table = ""

    return JsonResponse(
        {'paragraph_text': para_text,
         'document_name': document_name,
         'document_id': document_id,
         'subject_name': subject_table}
    )


# ES_USER_LOG

def getChartLogs_ES(request, user_id, time_start, time_end):
    res_query = get_user_log_query(user_id, time_start, time_end)

    machine_user_name = getpass.getuser()
    if machine_user_name == SERVER_USER_NAME:
        index_name = es_config.SERVE_USER_LOG_INDEX
    else:
        index_name = es_config.LOCAL_USER_LOG_INDEX

    response = client.search(index=index_name,
                             request_timeout=40,
                             query=res_query,
                             size=100,
                             sort=[
                                 {"visit_time": {"order": "desc"}}
                             ]
                             )

    user_logs = response['hits']['hits']
    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    convert_month = {1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد', 4: 'تیر', 5: 'مرداد',
                     6: 'شهریور', 7: 'مهر', 8: 'آبان', 9: 'آذر', 10: 'دی',
                     11: 'بهمن', 12: 'اسفند'}

    month_chart_data = {}
    hour_chart_data = {}
    for log in user_logs:
        time = log['_source']['visit_time']
        year = int(time[0:4])
        month = int(time[5:7])
        day = int(time[8:10])
        hour = int(time[11:13])
        print('time===================')
        print(time)
        print(f"{year},{month},{day},{hour}")
        jalali = gregorian_to_jalali(year, month, day)
        print(JalaliDate.today().strftime('%A', locale='fa'))
        print(JalaliDate.today().strftime('%B', locale='fa'))

        date_list = str(JalaliDate.to_jalali(year, month, day).strftime('%B', locale='fa')).split('-')

        jalali_date = [int(num) for num in date_list]
        print(jalali_date)
        month_name = convert_month[jalali[1]]
        if month_name not in month_chart_data:
            month_chart_data[month_name] = 1
        else:
            month_chart_data[month_name] += 1

        if hour not in hour_chart_data:
            hour_chart_data[hour] = 1
        else:
            hour_chart_data[hour] += 1

    month_chart_data_list = []
    for month, count in month_chart_data.items():
        column = [month, count]
        month_chart_data_list.append(column)

    hour_chart_data_list = []
    for hour, count in hour_chart_data.items():
        column = [hour, count]
        hour_chart_data_list.append(column)

    chart_data = {}
    for log in user_logs:
        url = log['_source']['page_url']
        if url == None:
            url = 'home'
        if url not in chart_data:
            chart_data[url] = 1
        else:
            chart_data[url] += 1

    chart_data_list = []
    for url, count in chart_data.items():
        column = [url, count]
        chart_data_list.append(column)

    panels = {'search': {'chart_dict': {}, 'chart_list': []},
              'graph2': {'chart_dict': {}, 'chart_list': []}
              }

    es_search_chart_data = getPanelDetailType_Aggregation(user_id, time_start, time_end, 'search')
    graph_chart_data = getPanelDetailType_Aggregation(user_id, time_start, time_end, 'graph2')

    # 'chart_data_information': panels['information']['chart_list'],
    return JsonResponse({'chart_data_list': chart_data_list,
                         'chart_data_search': es_search_chart_data,
                         'chart_data_graph': graph_chart_data,
                         'month_chart_data_list': month_chart_data_list, 'hour_chart_data_list': hour_chart_data_list})


def get_user_log_query(user_id, time_start, time_end):
    res_query = {
        "bool": {
            "filter": [],
            "must": {
                "exists": {
                    "field": "user.id"
                }
            }
        }
    }

    if user_id != 0:
        user_query = {
            "term": {
                "user.id": user_id
            }
        }

        res_query['bool']['filter'].append(user_query)

    if time_start != "0" or time_end != "0":
        time_query = {
            "range": {
                "visit_time": {}
            }
        }

        if time_start != "0":
            time_query['range']['visit_time']['gte'] = time_start
        if time_end != "0":
            time_query['range']['visit_time']['lte'] = time_end

        res_query['bool']['filter'].append(time_query)

    return res_query


def getPanelDetailType_Aggregation(user_id, time_start, time_end, panel_name):
    res_query = get_user_log_query(user_id, time_start, time_end)

    panel_filter = {
        'term': {
            'page_url.keyword': panel_name
        }
    }
    res_query['bool']['filter'].append(panel_filter)

    machine_user_name = getpass.getuser()
    if machine_user_name == SERVER_USER_NAME:
        index_name = es_config.SERVE_USER_LOG_INDEX
    else:
        index_name = es_config.LOCAL_USER_LOG_INDEX

    res_agg = {
        "detail-type-agg": {
            "terms": {
                "field": "detail_json.detail_type",
                "size": bucket_size
            }
        }
    }
    response = client.search(index=index_name,
                             request_timeout=40,
                             query=res_query,
                             aggregations=res_agg,
                             size=100,
                             sort=[
                                 {"visit_time": {"order": "desc"}}
                             ]
                             )

    total_hits = response['hits']['total']['value']
    aggregation_data = response['aggregations']['detail-type-agg']['buckets']

    chart_value_list = []

    for column in aggregation_data:
        key = column["key"]
        value = column["doc_count"]
        chart_value_list.append([key, value])

    return chart_value_list


def getUserLogs_ES(request, user_id, time_start, time_end, curr_page, page_size):
    # time_start = time_start + "T00:00:00"+ 'Z'
    # time_end = time_end + "T00:00:00"+ 'Z'

    res_query = get_user_log_query(user_id, time_start, time_end)

    machine_user_name = getpass.getuser()
    if machine_user_name == SERVER_USER_NAME:
        index_name = es_config.SERVE_USER_LOG_INDEX
    else:
        index_name = es_config.LOCAL_USER_LOG_INDEX

    res_agg = {
        "panel-agg": {
            "terms": {
                "field": "page_url.keyword",
                "size": bucket_size
            }
        },
        "user-agg": {
            "terms": {
                "field": "user.last_name.keyword",
                "size": bucket_size
            }
        },
        "month-agg": {
            "terms": {
                "field": "jalili_visit_time.month.name.keyword",
                "size": bucket_size
            }
        },
        "day-agg": {
            "terms": {
                "field": "jalili_visit_time.day.name.keyword",
                "size": bucket_size
            }
        },
        "hour-agg": {
            "terms": {
                "field": "jalili_visit_time.hour",
                "size": bucket_size
            }
        }
    }

    from_value = (curr_page - 1) * page_size

    response = client.search(index=index_name,
                             request_timeout=40,
                             query=res_query,
                             aggregations=res_agg,
                             from_=from_value,
                             size=page_size,
                             sort=[
                                 {"visit_time": {"order": "desc"}}
                             ]
                             )
    result = response['hits']['hits']
    total_hits = response['hits']['total']['value']
    aggregations = response['aggregations']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    es_search_chart_data = getPanelDetailType_Aggregation(user_id, time_start, time_end, 'es_search')
    graph_chart_data = getPanelDetailType_Aggregation(user_id, time_start, time_end, 'graph2')

    return JsonResponse(
        {
            "result": result,
            'total_hits': total_hits,
            'curr_page': curr_page,
            'aggregations': aggregations,
            "es_search_chart_data": es_search_chart_data,
            "graph_chart_data": graph_chart_data
        }
    )



def getTableUserLogs_ES(request, user_id, time_start, time_end):
    res_query = get_user_log_query(user_id, time_start, time_end)
    detail_query = {
        "match_phrase": {
            "detail_json.detail_type": "نتایج جست و جو"
        }
    }
    search_query = {
        "term": {
            "page_url.keyword": "es_search"
        }
    }
    res_query['bool']['filter'].append(search_query)
    res_query['bool']['filter'].append(detail_query)

    machine_user_name = getpass.getuser()
    if machine_user_name == SERVER_USER_NAME:
        index_name = es_config.SERVE_USER_LOG_INDEX
    else:
        index_name = es_config.LOCAL_USER_LOG_INDEX

    res_agg = {
        "detail-type-agg": {
            "terms": {
                "field": "detail_json.search_text",
                "size": bucket_size
            }
        }
    }

    response = client.search(index=index_name,
                             request_timeout=40,
                             query=res_query,
                             aggregations=res_agg,
                             size=100,
                             sort=[{"visit_time": {"order": "desc"}}]
                             )
    total_hits = response['hits']['total']['value']
    aggregations = response['aggregations']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    i = 1
    keyword_table_data_list = []
    for column in aggregations['detail-type-agg']['buckets']:
        keyword_name = column['key']
        count = column['doc_count']
        column = [i, keyword_name, count]
        keyword_table_data_list.append(column)
        i += 1

    return JsonResponse({'keyword_table_data_list': keyword_table_data_list})


def userlogs_to_index(request, id, language):
    file = get_object_or_404(Country, id=id)

    from es_scripts import IngestUserLogToElastic

    my_file = file.file.path
    my_file = str(os.path.basename(my_file))
    dot_index = my_file.rfind('.')
    folder_name = my_file[:dot_index]

    machine_user_name = getpass.getuser()

    IngestUserLogToElastic.apply(folder_name, file, machine_user_name)
    return redirect('zip')

def GetSimilarParagraphs_ByParagraphID(request, paragraph_id):
    similar_paragraphs = []
    para_obj = DocumentParagraphs.objects.get(id=paragraph_id)
    document_id = para_obj.document_id.id
    country_obj = para_obj.document_id.country_id
    index_name = standardIndexName(country_obj, DocumentParagraphs.__name__)
    # index_name = "doticfull_documentparagraphs"

    sim_query = {
        "bool": {
            "filter": [
                {
                    "more_like_this": {
                        "analyzer": "persian_custom_analyzer",
                        "fields": [
                            "attachment.content"
                        ],
                        "like": [
                            {
                                "_index": index_name,
                                "_id": str(paragraph_id)
                            }
                        ],
                        "min_term_freq": 2,
                        "max_query_terms": 400,
                        "min_word_length": 4,
                        "min_doc_freq": 2,
                        "minimum_should_match": "55%"
                    }
                }
            ]
        }
    }

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name', 'attachment.content'],
                             request_timeout=40,
                             query=sim_query
                             )

    similar_paragraphs = response['hits']['hits']

    return JsonResponse({'similar_paragraphs': similar_paragraphs})


def GetSemanticSimilarParagraphs_ByParagraphID(request, paragraph_id):

    # get paragraph vector
    vector_query = {
        'term':{
            'paragraph_id':paragraph_id
        }
    }
    country_obj = DocumentParagraphs.objects.get(id=paragraph_id).document_id.country_id
    index_name = standardIndexName(country_obj, DocumentParagraphs.__name__ + "_vectors")

    response = client.search(index=index_name,
                            _source_includes=['wikitriplet_vector'],
                            request_timeout=40,
                            query=vector_query
                            )

    para_vector = list(response['hits']['hits'][0]['_source']['wikitriplet_vector'])
    # create knn query
    knn_qeury = {
        "script_score": {
            "query" : {
                "bool":{
                    "must_not":{
                        "term":{
                            "paragraph_id":paragraph_id
                        }
                    }
                }
            },
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'wikitriplet_vector') + 1.0",
                "params": {
                "query_vector": para_vector
                }
            }
        }
    }

    # search and get result
    response = client.search(index=index_name,
                            _source_includes=['document_id', 'document_name', 'attachment.content'],
                            request_timeout=40,
                            size = 10,
                            query=knn_qeury
                            )


    similar_paragraphs = response['hits']['hits']

    return JsonResponse({'similar_paragraphs': similar_paragraphs})


def AILDASubjectChartTopicGetInformation(request, topic_id, subject_name, curr_page, result_size):
    topic_paragraphs = []
    from_value = (curr_page - 1) * result_size
    to_value = from_value + result_size
    temp = AILDAParagraphToTopic.objects.filter(topic__id=topic_id).order_by('-score').values()

    all_paragraph_count = AIParagraphLDATopic.objects.get(id=topic_id).subjects_list_chart_data_json['data']
    paragraph_count = 0
    for item in all_paragraph_count:
        if item[0] == subject_name:
            paragraph_count = item[1]

    for record in temp:
        if (len(topic_paragraphs) == curr_page * result_size) or (len(topic_paragraphs) == paragraph_count):
            break
        paragraph_id = record['paragraph_id']
        try:
            subjects_name = ParagraphsSubject.objects.get(paragraph__id=paragraph_id)

            if subjects_name.subject1_name == subject_name:
                paragraph = DocumentParagraphs.objects.get(id=paragraph_id)
                topic_paragraphs.append({"_source": {
                    "attachment": {
                        "content": paragraph.text
                    },
                    "paragraph_id": paragraph.id,
                    "document_id": paragraph.document_id.id,
                    "document_name": paragraph.document_id.name,
                    # "subject1_name": subjects_name.subject1_name,
                }})
                print("ADD", paragraph_id)
        except:
            if subject_name == "نامشخص":
                paragraph = DocumentParagraphs.objects.get(id=paragraph_id)
                topic_paragraphs.append({"_source": {
                    "attachment": {
                        "content": paragraph.text
                    },
                    "paragraph_id": paragraph.id,
                    "document_id": paragraph.document_id.id,
                    "document_name": paragraph.document_id.name,
                    # "subject1_name": subjects_name.subject1_name,
                }})
                print("ADD", paragraph_id)
            else:
                print("ERROR", paragraph_id)

    return JsonResponse({'result': topic_paragraphs[from_value: to_value], 'total_hits': paragraph_count})


def AILDASubjectChartTopicGetInformationExport(request, topic_id, subject_name, curr_page, result_size):
    topic_paragraphs = []
    from_value = (curr_page - 1) * result_size
    temp = AILDAParagraphToTopic.objects.filter(topic__id=topic_id).order_by('-score').values()
    to_value = from_value + result_size
    all_paragraph_count = AIParagraphLDATopic.objects.get(id=topic_id).subjects_list_chart_data_json['data']
    paragraph_count = 0
    for item in all_paragraph_count:
        if item[0] == subject_name:
            paragraph_count = item[1]

    if to_value > paragraph_count:
        to_value = paragraph_count

    for record in temp:
        if (len(topic_paragraphs) == curr_page * result_size) or (len(topic_paragraphs) == paragraph_count):
            break
        paragraph_id = record['paragraph_id']
        try:
            subjects_name = ParagraphsSubject.objects.get(paragraph__id=paragraph_id)

            if subjects_name.subject1_name == subject_name:
                paragraph = DocumentParagraphs.objects.get(id=paragraph_id)
                topic_paragraphs.append({"_source": {
                    "attachment": {
                        "content": paragraph.text
                    },
                    "paragraph_id": paragraph.id,
                    "document_id": paragraph.document_id.id,
                    "document_name": paragraph.document_id.name,
                    # "subject1_name": subjects_name.subject1_name,
                }})
                print("ADD", paragraph_id)
        except:
            if subject_name == "نامشخص":
                paragraph = DocumentParagraphs.objects.get(id=paragraph_id)
                topic_paragraphs.append({"_source": {
                    "attachment": {
                        "content": paragraph.text
                    },
                    "paragraph_id": paragraph.id,
                    "document_id": paragraph.document_id.id,
                    "document_name": paragraph.document_id.name,
                    # "subject1_name": subjects_name.subject1_name,
                }})
                print("ADD", paragraph_id)
            else:
                print("ERROR", paragraph_id)

    result_range = str(from_value) + " تا " + str(to_value)

    paragraph_list = [
        [doc['_source']['document_name']
            , doc['_source']['attachment']['content']] for doc in topic_paragraphs[from_value:to_value]]

    file_dataframe = pd.DataFrame(paragraph_list, columns=["نام خبر", "متن پاراگراف"])

    file_name = "احکام با موضوع " + subject_name + " " + result_range + ".xlsx"

    file_path = os.path.join(config.MEDIA_PATH, file_name)
    file_dataframe.to_excel(file_path, index=False)

    return JsonResponse({"file_name": file_name})

def GetResourceInformation(request):
    document_object = Document.objects.all().values("country_id_id", "country_id__name").annotate(
        doc_count=Count("id"),
        min_date=Min("date"),
        max_date=Max("date"),
    )
    result = []
    for row in document_object:
        res = {
            "country_id": row["country_id_id"],
            "country_name": row["country_id__name"],
            "doc_count": row["doc_count"],
            "min_date": row["min_date"],
            "max_date": row["max_date"],
        }
        result.append(res)

    return JsonResponse({"resource_information": result})
