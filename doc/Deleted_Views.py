
def GetAllNotesUser(request, username):
    notes = DocumentNote.objects.filter(user__username=username)
    result = []
    for n in notes:
        result.append({"note": n.note, "time": n.time, "document_name": n.document.file_name, "id": n.document.id})
    return JsonResponse({"notes": result})


def GetSyns(request):
    slogan_synonymous_words_list = SloganSynonymousWords.objects.all()
    slogan_map_synonymous_words = {i.year: i.words for i in slogan_synonymous_words_list}
    return JsonResponse({'syns': slogan_map_synonymous_words})


# ---------------- query ------------------------











def GetBookDocumentById(request, document_id):
    document = Document.objects.get(id=document_id)
    book = Book.objects.get(document_id=document)

    book_name = "نامشخص"
    if book.name != None:
        book_name = book.name

    subject = "نامشخص"
    if book.subject != None:
        subject = book.subject

    publisher_name = "نامشخص"
    if book.publisher_name != None:
        publisher_name = book.publisher_name

    pagecount = "نامشخص"
    if book.pagecount != None:
        pagecount = book.pagecount

    year = "نامشخص"
    if book.year != None:
        year = book.year

    result = {"document_id": document.id,
              "book_id": book.id,
              "book_name": book_name,
              "subject": subject,
              "publisher_name": publisher_name,
              "pagecount": pagecount,
              "year": year
              }
    return JsonResponse({'book_information': [result]})


def Get_SubjectArea_Documents(request, country_id, SubjectAreaSelect_id,
                              multiselect_SubjectSubArea_value, ValidationSelect, RevokedSizeSelect, SubTypeSelect):
    subjects_sub_area_id_list = multiselect_SubjectSubArea_value.split("__")

    result_docs = CUBE_DocumentSubjectArea_TableData.objects.filter(country_id__id=country_id,
                                                                    subject_area_id=SubjectAreaSelect_id,
                                                                    subject_sub_area_id__in=subjects_sub_area_id_list)

    documents_information_list = []

    for res in result_docs:
        filtered_result = []
        for doc in res.table_data:
            if doc['revoked_type_name'] == ValidationSelect or ValidationSelect == "0":
                if doc['revoked_size'] == RevokedSizeSelect or RevokedSizeSelect == "0":
                    if doc['revoked_sub_type'] == SubTypeSelect or SubTypeSelect == "0":
                        filtered_result.append(doc)

        documents_information_list += filtered_result

    sorted_documents_information_list = documents_information_list

    if len(subjects_sub_area_id_list) > 1:
        sorted_documents_information_list = sorted(documents_information_list, reverse=True,
                                                   key=lambda d: d['doc_subject_sub_area_weight'])

        # Edit index number
        for i in range(0, len(sorted_documents_information_list)):
            sorted_documents_information_list[i]['id'] = i + 1

    return JsonResponse(
        {'documentsList': sorted_documents_information_list, 'document_count': len(documents_information_list)})


def GetDocumentByListId(request, db_name):
    List_id = [int(id) for id in request.POST.get('documents_id_list').split(',')]
    print(List_id)
    documents_list = Document.objects.using(db_name).filter(id__in=List_id)
    result_list = []
    for document in documents_list:
        approval_ref = "نامشخص"
        if document.approval_reference_id != None:
            approval_ref = document.approval_reference_id.name

        approval_date = "نامشخص"
        if document.approval_date != None:
            approval_date = document.approval_date

        type_name = "سایر"
        if document.type_id != None:
            type_name = document.type_id.name

        level_name = "نامشخص"
        if document.level_id != None:
            level_name = document.level_id.name

        subject_name = "نامشخص"
        if document.subject_id != None:
            subject_name = document.subject_id.name

        result = {"id": document.id,
                  "name": document.name,
                  "country_id": document.country_id_id,
                  "country": document.country_id.name,
                  "level": level_name,
                  "subject": subject_name,
                  "type": type_name,
                  "approval_reference": approval_ref,
                  "approval_date": approval_date,
                  }
        result_list.append(result)
    return JsonResponse({'document_information': result_list})


def GetTypeByName(request, name):
    type = Type.objects.get(name=name)
    result = {"id": type.id, "name": type.name}
    return JsonResponse({'type': result})







def GetDocumentsByCountryType_Modal(request, country_id=None, type_id=None):
    country_id = int(country_id)
    type_id = int(type_id)

    filesList = Document.objects.filter(
        country_id_id=country_id, type_id=type_id).order_by('name')
    result_list = []
    i = 1

    for doc in filesList:
        id = doc.id
        doc_info = GetDocumentById_Local(id)
        name = doc.name
        function = "SelectDocumentFunction(this)"
        tag = '<input ' \
              'type="checkbox" ' \
              'value="' + str(id) + '" ' \
                                    'class="doc_checkbox form-check-input d-inline-block" ' \
                                    'onchange="' + function + '"' \
                                                              'checked />' + '</input>'

        result_list.append({"id": i,
                            "document_name": name,
                            "tag": tag,
                            "value": id,
                            "document_subject": doc_info['subject'],
                            "document_year": doc_info['approval_date'],
                            "document_ref": doc_info['approval_reference']})
        i += 1

    return JsonResponse({'documentsList': result_list})


def GetDocumentsWithoutSubject(request, country_id=None, measure_id=1):
    country_id = int(country_id)
    filesList = Document.objects.filter(
        country_id_id=country_id, subject_id__isnull=True).order_by('name')
    result = []
    for doc in filesList:
        document_information = GetDocumentById_Local(doc.id)
        res = {
            'id': doc.id,
            'document_name': doc.name,
            'document_subject': document_information['subject'],
            'document_approval_reference': document_information['approval_reference'],
            'document_approval_date': document_information['approval_date'],
            'document_level': document_information['level']
        }
        result.append(res)

    return JsonResponse({'documentsWithoutSubject': result})


def GetDocumentsWithoutSubject_ES(request, curr_page, country_id=None):
    organization_type_id = '0'

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    # if not all(field==0 for field in fields):
    ALL_FIELDS = False
    res_query['bool']['filter'] = []
    subject_query = {
        "term": {
            "subject_name.keyword": "نامشخص",  # null
        }
        # "terms": {
        #     "subject_name.keyword": ["نامشخص", None],
        # }
    }
    res_query['bool']['filter'].append(subject_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, Document.__name__)

    # ---------------------- Get Chart Data -------------------------
    # res_agg = {
    # "approval-ref-agg": {
    #     "terms": {
    #         "field": "approval_reference_name.keyword",
    #         "size": bucket_size
    #         }
    #     }
    # }

    from_value = (curr_page - 1) * search_result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'approval_reference_name', 'approval_date',
                                               'subject_name',
                                               "level_name",
                                               # 'type_name','approval_year','communicated_date','raw_file_name',
                                               # 'advisory_opinion_count', 'interpretation_rules_count','revoked_type_name'
                                               ],
                             request_timeout=40,
                             query=res_query,
                             # aggregations = res_agg,
                             # from_ = from_value,
                             size=search_result_size

                             )

    result = response['hits']['hits']
    total_hits = response['hits']['total']['value']
    # aggregations = response['aggregations']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        "curr_page": curr_page,
        #    'aggregations':aggregations
    })









def GetDefinitionByDocumentId(request, document_id):
    regexes = [
        r'[“"].*?[”"] means [\s\S]*?[\.;]',
        r'[“"].*?[”"] \(.*?\) means [\s\S]*?[\.;]',
        r'[“"].*?[”"] has the meaning [\s\S]*?[\.;]',
        r'[“"].*?[”"] \(.*?\) has the meaning [\s\S]*?[\.;]',
    ]
    document_definition = DocumentDefinition.objects.get(
        document_id_id=document_id)
    definition_text = document_definition.text
    definition_keywords = ""
    keywords = []
    definitions = []
    if definition_text != "":
        keyword_list = ExtractedKeywords.objects.filter(
            definition_id=document_definition)
        for keyword in keyword_list:
            definition_keywords += keyword.word + " - "
        definition_keywords = definition_keywords[:-3]

        for regex in regexes:
            pair = re.compile(regex)
            search__ = pair.findall(definition_text)
            for search_ in search__:
                keyword = (" " + search_).replace("“",
                                                  '"').replace("”", '"').split('"')[1]
                keywords.append(keyword)
                if "means" in search_:
                    definition_ = search_.split("means")[1]
                else:
                    definition_ = search_.split("has the meaning")[1]
                if definition_.startswith("-"):
                    definition_ = definition_[1:]
                if definition_.startswith("—"):
                    definition_ = definition_.replace("—", "", 1)
                definitions.append(definition_)
    else:
        definition_text = "بخش تعاریف و اصطلاحات برای این سند توسط سامانه پیدا نشد."

    if definition_keywords == "":
        definition_keywords = "هیچ کلمه کلیدی برای این سند توسط سامانه پیدا نشد."

    result = {"id": document_definition.id,
              "text": definition_text,
              "keywords": definition_keywords
              }
    return JsonResponse({'documents_definition': [result], 'keywords': keywords, 'definitions': definitions})







def GetAdvisoryOpinionsReferencesByDocumentId(request, doc_id):
    result = []
    document_citation_list = Graph.objects.filter(dest_document_id_id=doc_id, measure_id_id=2).filter(
        src_document_id__type_id__name='نظر مشورتی').order_by('-weight')
    for row in document_citation_list:
        new_ref = {}
        new_ref['doc_id'] = row.src_document_id_id
        new_ref['doc_name'] = row.src_document_id.name

        result.append(new_ref)

    return JsonResponse({'document_references_list': result})


def GetAdvisoryChartInformation(request, doc_id):
    result = []
    document_citation_list = Graph.objects.filter(dest_document_id_id=doc_id, measure_id_id=2).filter(
        src_document_id__type_id__name='نظر مشورتی').order_by('-weight')
    for row in document_citation_list:
        new_ref = {}
        new_ref['doc_id'] = row.src_document_id_id
        new_ref['doc_name'] = row.src_document_id.name
        new_ref['doc_subject_name'] = row.src_document_id.subject_name
        new_ref['doc_level'] = row.src_document_id.level_name
        new_ref['doc_approval_year'] = row.src_document_id.approval_date[
                                       :4] if row.src_document_id.approval_date else 'نامشخص'
        new_ref['doc_approval_reference_name'] = row.src_document_id.approval_reference_name

        result.append(new_ref)

    return JsonResponse({'result': result})


def GetAreaChartInformation(request, doc_id):
    result = {}
    document = Document.objects.get(id=doc_id)
    subject_area_id = document.subject_area_id_id
    document_citation_list = DocumentSubjectSubArea.objects.filter(document_id__id=doc_id).order_by('-weight')

    result['doc_id'] = document.id
    result['doc_name'] = document.name
    result['details'] = [{
        'subject_sub_area_id': row.subject_sub_area_id.id,
        'subject_sub_area_name': row.subject_sub_area_id.name,
        'weight': row.weight * 100
    } for row in document_citation_list if row.weight]

    return JsonResponse({'result': result})


def GetGraphEdgesByDocumentsList_AdvisoryOpinions(request, measure_id):
    documents_id_list = [int(id) for id in request.POST.get('documents_id_list').split(',')]
    graph_edge_list = Graph.objects.filter(
        src_document_id__in=documents_id_list, dest_document_id__in=documents_id_list,
        measure_id__id=measure_id, src_document_id__type_id__name='نظر مشورتی')

    result = []
    for edge in graph_edge_list:

        src_id = edge.src_document_id_id
        src_name = edge.src_document_id.name
        src_color = "#0"
        if edge.src_document_id.type_id != None:
            src_color = edge.src_document_id.type_id.color

        dest_id = edge.dest_document_id_id
        dest_name = edge.dest_document_id.name
        dest_color = "#0"
        if edge.dest_document_id.type_id != None:
            dest_color = edge.dest_document_id.type_id.color

        weight = edge.weight

        res = {
            "src_id": src_id,
            "src_name": src_name,
            "src_color": src_color,
            "dest_id": dest_id,
            "dest_name": dest_name,
            "dest_color": dest_color,
            "weight": weight,
        }

        result.append(res)

    graph_type = Measure.objects.get(id=measure_id).type

    return JsonResponse({'graph_edge_list': result, "graph_type": graph_type})


def create_advisory_opinion_count(request, id, language):
    file = get_object_or_404(Country, id=id)

    from scripts.Persian import CreateAdvisoryOpinionsReferences

    CreateAdvisoryOpinionsReferences.apply(file)
    return redirect('zip')


def create_interpretation_rules_count(request, id, language):
    file = get_object_or_404(Country, id=id)

    from scripts.Persian import CreateInterpretationRulesReferences

    CreateInterpretationRulesReferences.apply(file)
    return redirect('zip')




def GetDocumentsByCountrySubject(request, country_id=None, subjects_id=None):
    subjects_id = subjects_id.split("__")

    result_docs = CUBE_Subject_TableData.objects.filter(country_id__id=country_id,
                                                        subject_id__id__in=subjects_id)

    print(result_docs)

    documents_information_list = []

    for res in result_docs:
        documents_information_list += res.table_data['data']

    sorted_documents_information_list = documents_information_list

    if len(subjects_id) > 1:
        sorted_documents_information_list = sorted(documents_information_list, reverse=True,
                                                   key=lambda d: d['document_subject_weight'])

        # Edit index number
        for i in range(0, len(sorted_documents_information_list)):
            sorted_documents_information_list[i]['id'] = i + 1

    return JsonResponse(
        {'documentsList': sorted_documents_information_list, 'document_count': len(documents_information_list)})


def GetDocumentsByCountrySubject_ES(request, curr_page, country_id=None, subjects_ids=None):
    # organization_type_id = '0'

    fields = [subjects_ids]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []

        subjects_ids = subjects_ids.split("__")
        if "0" not in subjects_ids:
            subject_name_list = Subject.objects.filter(id__in=subjects_ids)
            subject_name_list = [s.name for s in subject_name_list]
            subject_name_query = {
                "terms": {
                    "subject_name.keyword": subject_name_list,
                }
            }
        else:
            subject_name_query = {
                "bool": {
                    "must_not": {
                        "term": {
                            "subject_name.keyword": "نامشخص",
                        }
                    }
                }
            }
        res_query['bool']['filter'].append(subject_name_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, Document.__name__)

    # ---------------------- Get Chart Data -------------------------
    # res_agg = {

    # "subject-sub-area-agg": {
    #     "terms": {
    #         "field": "subject_sub_area_name.keyword",
    #         "size": bucket_size
    #     }
    # },
    # }

    from_value = (curr_page - 1) * search_result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'approval_date', 'subject_name',
                                               'revoked_type_id', 'revoked_type_name', 'approval_reference_name',
                                               'level_name', 'subject_weight'  # document_subject_weight ??
                                               # 'revoked_size', 'subject_area_name', 'subject_sub_area_name', 'organization_type_name',
                                               # 'subject_sub_area_weight', 'subject_sub_area_entropy', 'approval_year'
                                               ],
                             request_timeout=40,
                             query=res_query,
                             # aggregations = res_agg,
                             from_=from_value,
                             size=search_result_size

                             )

    result = response['hits']['hits']
    total_hits = response['hits']['total']['value']
    # aggregations = response['aggregations']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        "curr_page": curr_page,
        #    'aggregations':aggregations
    })





def GetBookSimilarityMeasureByCountry(request, country_id):
    graph_list = DocumentSimilarity_Distribution_Cube.objects.filter(country_id_id=country_id).values(
        'similarity_type').distinct()
    result = []
    for row in graph_list:
        measure_id = row["similarity_type"]
        measure_name = SimilarityType.objects.get(id=measure_id).name
        res = {"id": measure_id, "name": measure_name}
        result.append(res)
    return JsonResponse({'measure_list': result})




def GetBookGraphDistribution(request, country_id, measure_id):
    graph_cube = DocumentSimilarity_Distribution_Cube.objects.filter(country_id_id=country_id,
                                                                     similarity_type_id=measure_id)
    result = []
    for row in graph_cube:
        res = {"similarity": row.threshold, "count": row.edge_count}
        result.append(res)

    return JsonResponse({'graph_distribution': result})





def GetSubjectKeywords(request, subject_id):
    subject_keywords_list = SubjectKeyWords.objects.filter(
        subject_id=subject_id).values('word')
    result = []
    for keyword in subject_keywords_list:
        result.append(keyword['word'])

    result = ' - '.join(result)
    return JsonResponse({'subject_keywords_list': result})





def GetLevelByCountryId(request, country_id):
    documents_level_list = Document.objects.filter(country_id_id=country_id).values("level_id").order_by(
        "level_id").distinct()
    result = []
    for row in documents_level_list:
        level_id = row["level_id"]
        if level_id is not None:
            level = Level.objects.get(id=level_id)
            level_name = level.name
            res = {
                "id": level_id,
                "level": level_name
            }
            result.append(res)
    return JsonResponse({'documents_level_list': result})


def GetApprovalReferencesByCountryId(request, country_id):
    documents_approval_list = Document.objects.filter(country_id_id=country_id).values(
        "approval_reference_id").order_by("approval_reference_id__name").distinct()
    result = []
    for row in documents_approval_list:
        approval_reference_id = row["approval_reference_id"]
        if approval_reference_id is not None:
            approval_reference = ApprovalReference.objects.get(
                id=approval_reference_id)
            approval_reference_name = approval_reference.name
            res = {
                "id": approval_reference_id,
                "approval_reference": approval_reference_name
            }
            result.append(res)
    return JsonResponse({'documents_approval_list': result})


def GetYearsBoundByCountryId(request, country_id):
    documents_list = Document.objects.filter(
        country_id_id=country_id, approval_date__isnull=False)
    if documents_list.count() > 0:
        max_year = documents_list.aggregate(Max('approval_date'))[
                       "approval_date__max"][0:4]
        min_year = documents_list.aggregate(Min('approval_date'))[
                       "approval_date__min"][0:4]
        return JsonResponse({'documents_approval_list': [int(min_year) - 1, int(max_year) + 1]})
    else:
        return JsonResponse({'documents_approval_list': [-1, -1]})


def GetBooksSearchParameters(request, country_id):
    search_parameters = Book.objects.filter(document_id__country_id_id=country_id)

    parameters_result = {
        "publishers": "",
        "subjects": "",
    }

    publishers = []
    subjects = []

    for row in search_parameters:
        if row.publisher_name not in publishers and row.publisher_name:
            option = "<option value='" + row.publisher_name + "'>" + row.publisher_name + "</option>"
            parameters_result["publishers"] += option
            publishers.append(row.publisher_name)
        if row.subject not in subjects and row.subject != None:
            option = "<option value='" + row.subject + "'>" + row.subject + "</option>"
            parameters_result["subjects"] += option
            subjects.append(row.subject)

    return JsonResponse({"parameters_result": parameters_result})





def GetJudgmentSearchParameters(request, country_id):
    search_parameters = JudgmentSearchParameters.objects.filter(country__id=country_id)
    parameters_result = {}

    for param in search_parameters:
        para_name = param.parameter_name
        options = param.parameter_values["options"]
        parameters_result[para_name] = options

    return JsonResponse({"parameters_result": parameters_result})





def GetDocumentByCountryTypeSubject_Modal(request, country_id, type_id, subject_id, tag):
    documents_list = Document.objects.filter(country_id_id=country_id)

    # type id Handle
    if type_id == -1:
        documents_list = documents_list.filter(type_id=None)
    elif type_id > 0:
        documents_list = documents_list.filter(type_id_id=type_id)

    # type id Handle
    if subject_id == -1:
        documents_list = documents_list.filter(subject_id=None)
    elif subject_id > 0:
        documents_list = documents_list.filter(subject_id_id=subject_id)

    filesList = documents_list.order_by('name')
    result_list = []
    i = 1
    for doc in filesList:
        id = doc.id
        name = doc.name
        subject = "نامشخص"
        if doc.subject_id != None:
            subject = doc.subject_id.name

        approval_reference = "نامشخص"
        if doc.approval_reference_id != None:
            approval_reference = doc.approval_reference_id.name

        approval_date = "نامشخص"
        if doc.approval_date != None:
            approval_date = doc.approval_date

        function = "SelectDocFunction('" + str(id) + "','" + tag + "')"
        button_tag = '<button ' \
                     'type="button" ' \
                     'class="btn modal_btn" ' \
                     'data-bs-toggle="modal" ' \
                     'onclick="' + function + '"' \
                                              '/>' + 'انتخاب' + '</button>'
        result_list.append({"id": i, "document_name": name,
                            "tag": button_tag, "document_id": id, "subject": subject,
                            "approval_date": approval_date, "approval_reference": approval_reference})
        i += 1

    return JsonResponse({'documents_type_subject_list': result_list})


def GetDocumentByCountryTypeSubject(request, country_id, type_id, subject_id):
    documents_list = Document.objects.filter(country_id_id=country_id)
    # type id Handle
    if type_id == -1:
        documents_list = documents_list.filter(type_id=None)
    elif type_id > 0:
        documents_list = documents_list.filter(type_id_id=type_id)
    # type id Handle
    if subject_id == -1:
        documents_list = documents_list.filter(subject_id=None)
    elif subject_id > 0:
        documents_list = documents_list.filter(subject_id_id=subject_id)
    filesList = documents_list.order_by('name')
    result_list = []
    for doc in filesList:
        id = doc.id
        result_list.append(id)

    return result_list


def GetGraphEdgesByDocumentIdMeasure(request, country_id, src_doc_id, src_type_id, src_subject_id,
                                     dest_doc_id, dest_type_id, dest_subject_id, measure_id, weight):
    # Filter Documents Source
    src_document_list = []
    if src_doc_id != 0:
        src_document_list.append(src_doc_id)
    else:
        src_document_list = GetDocumentByCountryTypeSubject(
            request, country_id, src_type_id, src_subject_id)

    # Filter Documents Destination
    dest_document_list = []
    if dest_doc_id != 0:
        dest_document_list.append(dest_doc_id)
    else:
        dest_document_list = GetDocumentByCountryTypeSubject(
            request, country_id, dest_type_id, dest_subject_id)

    # Select Graph by Measure and weight
    graph_edge_list = Graph.objects.filter(src_document_id__in=src_document_list,
                                           dest_document_id__in=dest_document_list,
                                           measure_id__id=measure_id, weight__gte=float(weight))

    result = []
    for edge in graph_edge_list:

        src_id = edge.src_document_id_id
        src_name = edge.src_document_id.name
        src_color = "#0"
        if edge.src_document_id.type_id != None:
            src_color = edge.src_document_id.type_id.color

        dest_id = edge.dest_document_id_id
        dest_name = edge.dest_document_id.name
        dest_color = "#0"
        if edge.dest_document_id.type_id != None:
            dest_color = edge.dest_document_id.type_id.color

        weight = edge.weight

        res = {
            "src_id": src_id,
            "src_name": src_name,
            "src_color": src_color,
            "dest_id": dest_id,
            "dest_name": dest_name,
            "dest_color": dest_color,
            "weight": weight,
        }

        result.append(res)

    graph_type = Measure.objects.get(id=measure_id).type

    return JsonResponse({'graph_edge_list': result, "graph_type": graph_type})





def GetBookGraphNodesEdges(request, country_id, measure_id, minimum_weight):
    Graph_Cube_OBJ = DocumentSimilarityCube.objects.get(country_id_id=country_id, similarity_type_id=measure_id,
                                                        threshold=float(minimum_weight))

    Nodes_data = Graph_Cube_OBJ.nodes_data
    Edges_data = Graph_Cube_OBJ.edges_data

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


def GetGraphEdgesByDocumentsList(request, measure_id):
    documents_id_list = [int(id) for id in request.POST.get('documents_id_list').split(',')]
    graph_edge_list = Graph.objects.filter(
        src_document_id__in=documents_id_list, dest_document_id__in=documents_id_list,
        measure_id__id=measure_id)

    result = []
    for edge in graph_edge_list:

        src_id = edge.src_document_id_id
        src_name = edge.src_document_id.name
        src_color = "#0"
        if edge.src_document_id.type_id != None:
            src_color = edge.src_document_id.type_id.color

        dest_id = edge.dest_document_id_id
        dest_name = edge.dest_document_id.name
        dest_color = "#0"
        if edge.dest_document_id.type_id != None:
            dest_color = edge.dest_document_id.type_id.color

        weight = edge.weight

        res = {
            "src_id": src_id,
            "src_name": src_name,
            "src_color": src_color,
            "dest_id": dest_id,
            "dest_name": dest_name,
            "dest_color": dest_color,
            "weight": weight,
        }

        result.append(res)

    graph_type = Measure.objects.get(id=measure_id).type

    return JsonResponse({'graph_edge_list': result, "graph_type": graph_type})


def GetSimiGraphEdgesByDocumentsList_Standard(request, measure_name):
    documents_id_list = [int(id) for id in request.POST.get('documents_id_list').split(',')]

    graph_edge_list = DocumentSimilarity.objects.filter(
        doc1__id__in=documents_id_list, doc2__id__in=documents_id_list,
        similarity_type__name=measure_name
    )

    Nodes_data = []
    Edges_data = []
    addedNode = []
    addedEdge = []
    for edge in graph_edge_list:

        src_id = str(edge.doc1.id)
        src_name = edge.doc1.name

        dest_id = str(edge.doc2.id)
        dest_name = edge.doc2.name

        weight = edge.similarity

        node1 = {"id": src_id, "name": src_name}
        if src_id not in addedNode:
            Nodes_data.append(node1)
            addedNode.append(src_id)

        node2 = {"id": dest_id, "name": dest_name}
        if dest_id not in addedNode:
            Nodes_data.append(node2)
            addedNode.append(dest_id)

        if [dest_id, src_id] not in addedEdge and [src_id, dest_id] not in addedEdge:
            edge_dict = {
                "source": src_id,
                "source_name": src_name,
                "target": dest_id,
                "target_name": dest_name,
                "weight": weight,
            }
            addedEdge.append([src_id, dest_id])

            Edges_data.append(edge_dict)

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})





def GetDocumentById_Local_ForSearch(document_list):
    documents = Document.objects.filter(id__in=document_list)
    result = []
    for document in documents:
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

        type_name = "نامشخص"
        if document.type_id != None:
            type_name = document.type_name

        level_name = "نامشخص"
        if document.level_id != None:
            level_name = document.level_name

        subject_name = "نامشخص"
        if document.subject_id != None:
            subject_name = document.subject_name

        res = {"id": document.id,
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
               }
        result.append(res)

    return result


def FilterSearchData(documents_list, level_id, subject_id, type_id, approval_reference_id, from_year, to_year):
    # Filter Documents
    documents_list = Document.objects.filter(id__in=documents_list)

    if level_id > 0:
        if level_id == 4:
            documents_list = documents_list.filter(level_id_id=None)
        else:
            documents_list = documents_list.filter(level_id_id=level_id)

    if subject_id > 0:
        documents_list = documents_list.filter(subject_id_id=subject_id)

    if type_id > 0:
        documents_list = documents_list.filter(type_id_id=type_id)

    if approval_reference_id > 0:
        documents_list = documents_list.filter(approval_reference_id_id=approval_reference_id)

    if from_year > 0 or to_year > 0:
        documents_list = documents_list.annotate(approval_year=Cast(Substr('approval_date', 1, 4), IntegerField()))
        if from_year > 0:
            documents_list = documents_list.filter(approval_year__gte=from_year)

        if to_year > 0:
            documents_list = documents_list.filter(approval_year__lte=to_year)

    return documents_list.values_list("id")


def GetWordCountByDocument(documents_list, search_type, place, words):
    if search_type == "And":
        if place in ("عنوان", "متن"):
            word_count = DocumentWords.objects.filter(document_id__in=documents_list, place=place, word__in=words)
            document_word_count = word_count.values("document_id").annotate(sum_count=Min('count'))
        elif place == 'تعاریف':
            document_word_count = DocumentGeneralDefinition.objects.filter(
                reduce(operator.and_, (Q(keyword__icontains=word) for word in words)),
                document_id__in=documents_list).count()
        else:
            word_count = DocumentWords.objects.filter(document_id__in=documents_list, word__in=words, place="متن")
            document_word_count = word_count.values("document_id").annotate(sum_count=Min('count'))

    else:
        document_word_count = None

    return document_word_count.values_list("document_id", "sum_count")


def SearchDocumentAnd(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
                      place, text):
    # preprocess and split search text
    text = arabic_preprocessing(text)
    words = Preprocessing.Preprocessing(text)

    print(words)

    # Search
    if place in ("عنوان", "متن"):
        documents_words = DocumentWords.objects.filter(country_id_id=country_id, place=place)
        querySet = None
        for word in words:
            if querySet is None:
                querySet = Q(word=word)
            else:
                querySet = querySet | Q(word=word)

        documents_words = documents_words.filter((querySet)).values("document_id").annotate(count=Count('document_id'))
        documents_list = documents_words.filter(count=words.__len__()).values_list("document_id")
        # print(documents_list)
    elif place == "تعاریف":
        words = text.split(" ")
        documents_list = DocumentGeneralDefinition.objects.filter(
            reduce(operator.and_, (Q(keyword__icontains=word) for word in words)),
            document_id__country_id_id=country_id).values(
            "document_id", "keyword").annotate(
            count=Count('keyword'), sum_count=Count('keyword')).order_by("-count")
        # unique documents
        result = {}
        for doc in documents_list:
            if not (doc["document_id"] in result):
                result[doc["document_id"]] = doc
        documents_list = result.values()

        list_id = []
        count_id = []
        for id in documents_list:
            list_id.append(id['document_id'])
            count_id.append(id['sum_count'])
    else:
        documents_words = DocumentWords.objects.filter(country_id_id=country_id)
        querySet = None
        for word in words:
            if querySet is None:
                querySet = Q(word=word)
            else:
                querySet = querySet | Q(word=word)
        documents_list = documents_words.filter(querySet).values("document_id").annotate(
            cnt=Count('word', distinct=True))
        documents_list = documents_list.filter(cnt__gte=words.__len__()).values_list("document_id")
        # print(documents_list)
    # Filter Search
    if level_id + subject_id + type_id + approval_reference_id + from_year + to_year > 0:
        documents_list = FilterSearchData(documents_list, level_id, subject_id, type_id, approval_reference_id,
                                          from_year, to_year)

    # ---------- Generate Data -------------

    if place == "تعاریف":
        documents_information_result = GetDocumentById_Local_ForSearch(list_id)
    else:
        documents_information_result = GetDocumentById_Local_ForSearch(documents_list)

    subject_data = {}
    approval_references_data = {}
    level_data = {}
    approval_year_data = {}
    type_data = {}

    if place == "تعاریف":
        pass
        # document_words_count = list(GetWordCountByDocument(documents_list, "And", place, words))
    else:
        document_words_count = list(GetWordCountByDocument(documents_list, "And", place, words))
        document_words_count = pd.DataFrame(document_words_count, columns=["id", "count"]).set_index("id").to_dict()[
            "count"]

    for i in range(documents_information_result.__len__()):

        doc = documents_information_result[i]

        if place != "تعاریف":
            documents_information_result[i]["count"] = document_words_count[doc["id"]]

        subject_id, subject_name = doc["subject_id"], doc["subject"]
        approval_references_id, approval_references_name = doc["approval_reference_id"], doc["approval_reference"]
        level_id, level_name = doc["level_id"], doc["level"]
        type_id, type_name = doc["type_id"], doc["type"]
        approval_year = doc["approval_year"]

        if subject_id not in subject_data:
            subject_data[subject_id] = {"name": subject_name, "count": 1}
        else:
            subject_data[subject_id]["count"] += 1

        if approval_references_id not in approval_references_data:
            approval_references_data[approval_references_id] = {"name": approval_references_name, "count": 1}
        else:
            approval_references_data[approval_references_id]["count"] += 1

        if level_id not in level_data:
            level_data[level_id] = {"name": level_name, "count": 1}
        else:
            level_data[level_id]["count"] += 1

        if type_id not in type_data:
            type_data[type_id] = {"name": type_name, "count": 1}
        else:
            type_data[type_id]["count"] += 1

        if approval_year not in approval_year_data:
            approval_year_data[approval_year] = {"name": approval_year, "count": 1}
        else:
            approval_year_data[approval_year]["count"] += 1

    # documents_information_result = sorted(documents_information_result, key=lambda i: i['count'], reverse=True)

    print("Irannnnnnnnnnnnnnnnnnn")

    doc_ids = [d['id'] for d in documents_information_result]
    actors_chart_data = getActorsChartData(words, doc_ids)
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

    return JsonResponse({'documents_information_result': documents_information_result,
                         'subject_chart_data': subject_data,
                         'approval_references_chart_data': approval_references_data,
                         'level_chart_data': level_data,
                         'approval_year_chart_data': approval_year_data,
                         'type_chart_data': type_data,
                         'actors_chart_data': actors_chart_data,
                         'entropy_dict': entropy_dict,
                         'parallelism_dict': parallelism_dict,
                         'mean_dict': mean_dict,
                         'std_dict': std_dict,
                         'normal_entropy_dict': normal_entropy_dict,
                         'column_1': 'salahiat',
                         'column_2': 'hamkaran',
                         'column_3': 'motevalian',
                         })











def SearchDocumentOR(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
                     place, text):
    # Filter Documents

    documents_list = Document.objects.filter(country_id_id=country_id, )

    if level_id > 0:
        if level_id == 4:
            documents_list = documents_list.filter(level_id_id=None)
        else:
            documents_list = documents_list.filter(level_id_id=level_id)

    if subject_id > 0:
        documents_list = documents_list.filter(subject_id_id=subject_id)

    if type_id > 0:
        documents_list = documents_list.filter(type_id_id=type_id)

    if approval_reference_id > 0:
        documents_list = documents_list.filter(
            approval_reference_id_id=approval_reference_id)

    documents_list = documents_list.annotate(
        approval_year=Cast(Substr('approval_date', 1, 4), IntegerField()))
    if from_year > 0:
        documents_list = documents_list.filter(approval_year__gte=from_year)

    if to_year > 0:
        documents_list = documents_list.filter(approval_year__lte=to_year)

    # preprocess and split search text
    text = arabic_preprocessing(text)
    words = Preprocessing.Preprocessing(text)

    # Search
    if place in ("عنوان", "متن"):
        documents_list = DocumentWords.objects.filter(
            document_id__in=documents_list, place=place, word__in=words)
        documents_list = documents_list.values("document_id").annotate(
            sum_count=Max('count')).order_by("-sum_count")

    elif place == "تعاریف":
        words = text.split(" ")
        documents_list = DocumentGeneralDefinition.objects.filter(
            reduce(operator.or_, (Q(keyword__icontains=word) for word in words)),
            document_id__in=documents_list).values(
            "document_id", "keyword").annotate(
            count=Count('keyword'), sum_count=Count('keyword')).order_by("-count")
        # show unique documents in result
        result = {}
        for doc in documents_list:
            if not (doc["document_id"] in result):
                result[doc["document_id"]] = doc
        documents_list = result.values()

    else:
        documents_list = DocumentWords.objects.filter(
            document_id__in=documents_list, word__in=words)

        documents_list = documents_list.values("document_id").annotate(
            sum_count=Max('count')).order_by("-sum_count")

    # ---------- Generate Data -------------

    subject_data = {}
    approval_references_data = {}
    level_data = {}
    approval_year_data = {}
    type_data = {}

    documents_information_result = []
    for doc in documents_list:

        # Generate Document List Table Data
        document_id = doc["document_id"]
        word_count = doc["sum_count"]

        if place == 'تعاریف':
            words = text.split(" ")
            word_count = DocumentGeneralDefinition.objects.filter(
                reduce(operator.or_, (Q(keyword__icontains=word) for word in words)),
                document_id=document_id).count()

        document_information = GetDocumentById_Local(document_id)
        document_information["count"] = word_count
        documents_information_result.append(document_information)

        # Generate chart Data
        subject_id = document_information["subject_id"]
        subject_name = document_information["subject"]
        approval_references_id = document_information["approval_reference_id"]
        approval_references_name = document_information["approval_reference"]
        level_id = document_information["level_id"]
        level_name = document_information["level"]
        type_id = document_information["type_id"]
        type_name = document_information["type"]
        doc_approval_year = document_information["approval_date"]
        if doc_approval_year != "نامشخص":
            doc_approval_year = document_information["approval_date"][0:4]

        if subject_id not in subject_data:
            subject_data[subject_id] = {"name": subject_name, "count": 1}
        else:
            subject_data[subject_id]["count"] += 1

        if approval_references_id not in approval_references_data:
            approval_references_data[approval_references_id] = {
                "name": approval_references_name, "count": 1}
        else:
            approval_references_data[approval_references_id]["count"] += 1

        if level_id not in level_data:
            level_data[level_id] = {"name": level_name, "count": 1}
        else:
            level_data[level_id]["count"] += 1

        if type_id not in type_data:
            type_data[type_id] = {"name": type_name, "count": 1}
        else:
            type_data[type_id]["count"] += 1

        if doc_approval_year not in approval_year_data:
            approval_year_data[doc_approval_year] = {
                "name": doc_approval_year, "count": 1}
        else:
            approval_year_data[doc_approval_year]["count"] += 1

    doc_ids = [d['document_id'] for d in documents_list]
    actors_chart_data = getActorsChartData(words, doc_ids)
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

    return JsonResponse({'documents_information_result': documents_information_result,
                         'subject_chart_data': subject_data,
                         'approval_references_chart_data': approval_references_data,
                         'level_chart_data': level_data,
                         'approval_year_chart_data': approval_year_data,
                         'type_chart_data': type_data,
                         'actors_chart_data': actors_chart_data,
                         'entropy_dict': entropy_dict,
                         'parallelism_dict': parallelism_dict,
                         'mean_dict': mean_dict,
                         'std_dict': std_dict,
                         'normal_entropy_dict': normal_entropy_dict,
                         'column_1': 'salahiat',
                         'column_2': 'hamkaran',
                         'column_3': 'motevalian',
                         })


def GetSearchCountExact(document_id, _text, place):
    count = 0

    if 'عنوان' in place:
        document_name = Document.objects.get(id=document_id).name
        count += document_name.count(_text)

    if 'متن' in place:
        document_paragraphs = DocumentParagraphs.objects.filter(
            document_id_id=document_id, text__icontains=_text)

        for paragraph in document_paragraphs:
            paragraph_text = paragraph.text
            count += paragraph_text.count(_text)

    if 'تعاریف' in place:
        count += DocumentGeneralDefinition.objects.filter(document_id__id=document_id,
                                                          keyword__icontains=_text).count()

    return count


# ----------------------  Preprocessing  -------------------
def standardFileName(name):
    name = name.replace(".", "")
    name = arabicCharConvert(name)
    name = persianNumConvert(name)
    name = name.strip()

    while "  " in name:
        name = name.replace("  ", " ")

    return name


def persianNumConvert(text):
    persian_num_dict = {"۱": "1", "۲": "2", "۳": "3", "۴": "4", "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9",
                        "۰": "0"}
    for key, value in persian_num_dict.items():
        text = text.replace(key, value)
    return text


def arabicCharConvert(text):
    arabic_char_dict = {"ى": "ی", "ك": "ک", "آ": "ا", "أ": "ا", "إ": "ا", "ي": "ی", "ة": "ه", "ۀ": "ه", "  ": " ",
                        "\n\n": "\n", "\n ": "\n", }
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
    arabicNumbers = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩']
    for c in persianNumbers:
        text = text.replace(c, str(ord(c) - 1776))
    for c in arabicNumbers:
        text = text.replace(c, str(ord(c) - 1632))
    return text




# ------------------- ES Search -----------------------------







def filter_doc_fields_with_subject_area(res_query, level_id, subject_area_name, subject_sub_area_name, type_id,
                                        approval_reference_id,
                                        from_year, to_year, from_advisory_opinion_count,
                                        from_interpretation_rules_count,
                                        revoked_type_id, organization_type_id):
    if approval_reference_id != 0:
        approval_reference_name = ApprovalReference.objects.get(id=approval_reference_id).name
        approval_reference_name = arabic_preprocessing(approval_reference_name)
        approval_ref_query = {
            "term": {
                "approval_reference_name.keyword": approval_reference_name
            }
        }
        res_query['bool']['filter'].append(approval_ref_query)

    # ---------------------------------------------------------
    if level_id != 0:
        level_name = Level.objects.get(id=level_id).name
        level_query = {
            "term": {
                "level_name.keyword": level_name
            }
        }
        res_query['bool']['filter'].append(level_query)

    # ---------------------------------------------------------
    if subject_area_name != "0":
        subject_area_name = SubjectArea.objects.get(id=subject_area_name).name
        subject_area_name_query = {
            "term": {
                "subject_area_name.keyword": subject_area_name
            }
        }
        res_query['bool']['filter'].append(subject_area_name_query)

    # ---------------------------------------------------------
    subject_sub_area_name = subject_sub_area_name.split('__')
    if "0" not in subject_sub_area_name:
        subject_sub_area_name_list = SubjectSubArea.objects.filter(id__in=subject_sub_area_name)
        subject_sub_area_name_list = [s.name for s in subject_sub_area_name_list]
        subject_sub_area_name_query = {
            "terms": {
                "subject_sub_area_name.keyword": subject_sub_area_name_list,
            }
        }
    else:
        subject_sub_area_name_query = {
            "bool": {
                "must_not": {
                    "term": {
                        "subject_sub_area_name.keyword": "نامشخص",
                    }
                }
            }
        }
    res_query['bool']['filter'].append(subject_sub_area_name_query)

    # ---------------------------------------------------------
    if type_id != 0:
        type_name = Type.objects.get(id=type_id).name

        type_name = Local_preprocessing(type_name)

        type_query = {
            "term": {
                "type_name.keyword": type_name
            }
        }
        res_query['bool']['filter'].append(type_query)

    # ---------------------------------------------------------
    if revoked_type_id != 0:
        revoked_type_name = RevokedType.objects.get(id=revoked_type_id).name
        revoked_type_name_query = {
            "term": {
                "revoked_type_name.keyword": revoked_type_name
            }
        }
        res_query['bool']['filter'].append(revoked_type_name_query)

    # ---------------------------------------------------------
    if organization_type_id != '0':
        organization_type_name = organization_type_id
        organization_type_name_query = {
            "match_phrase": {
                "organization_type_name": organization_type_name
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
                "approval_year": {
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
                "advisory_opinion_count": {
                    "gte": from_advisory_opinion_count,
                }
            }
        }

        res_query['bool']['filter'].append(advisory_opinion_count_query)

    # ----------------------------------------------------------

    if from_interpretation_rules_count != 0:
        interpretation_rules_count_query = {
            "range": {
                "interpretation_rules_count": {
                    "gte": from_interpretation_rules_count,
                }
            }
        }

        res_query['bool']['filter'].append(interpretation_rules_count_query)

    return res_query


# added for chart column pagination



def filter_doc_fields_COLUMN_validation(res_query, level_name, subject_area_name, subject_sub_area_name, type_name,
                                        approval_reference_name, from_year, to_year,
                                        from_advisory_opinion_count, from_interpretation_rules_count, revoked_type_name,
                                        RevokedType_text, RevokedSize_text):
    if approval_reference_name != "همه":
        approval_reference_name = arabic_preprocessing(approval_reference_name)
        approval_ref_query = {
            "term": {
                "approval_reference_name.keyword": approval_reference_name
            }
        }
        res_query['bool']['filter'].append(approval_ref_query)

    # ---------------------------------------------------------
    if level_name != "همه":
        level_query = {
            "term": {
                "level_name.keyword": level_name
            }
        }
        res_query['bool']['filter'].append(level_query)

    # ---------------------------------------------------------
    if subject_area_name != "همه":
        subject_query = {
            "term": {
                "subject_area_name.keyword": subject_area_name
            }
        }
        res_query['bool']['filter'].append(subject_query)

    # ---------------------------------------------------------
    if subject_sub_area_name != "همه":
        subject_query = {
            "term": {
                "subject_sub_area_name.keyword": subject_sub_area_name
            }
        }
        res_query['bool']['filter'].append(subject_query)

    # ---------------------------------------------------------
    if type_name != "همه":
        type_name = Local_preprocessing(type_name)

        type_query = {
            "term": {
                "type_name.keyword": type_name
            }
        }
        res_query['bool']['filter'].append(type_query)

    # ----------------------------------------------------------

    if revoked_type_name != "همه":
        revoked_type_name_query = {
            "term": {
                "revoked_type_name.keyword": revoked_type_name
            }
        }
        res_query['bool']['filter'].append(revoked_type_name_query)

    # ---------------------------------------------------------
    if RevokedType_text != "همه":
        revoked_type_name_query = {
            "term": {
                "revoked_type_name.keyword": RevokedType_text
            }
        }
        res_query['bool']['filter'].append(revoked_type_name_query)

    # ----------------------------------------------------------
    if RevokedSize_text != "همه":
        revoke_type_detail_query = {
            "term": {
                "revoked_size.keyword": RevokedSize_text
            }
        }
        res_query['bool']['filter'].append(revoke_type_detail_query)

    First_Year = 1000
    Last_Year = 1403

    if from_year != "همه" or to_year != "همه":
        from_year = int(from_year) if from_year != "همه" else First_Year
        to_year = int(to_year) if to_year != "همه" else Last_Year

        year_query = {
            "range": {
                "approval_year": {
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
                "advisory_opinion_count": {
                    "gte": from_advisory_opinion_count,
                }
            }
        }

        res_query['bool']['filter'].append(advisory_opinion_count_query)

    # ----------------------------------------------------------

    if from_interpretation_rules_count != 0:
        interpretation_rules_count_query = {
            "range": {
                "interpretation_rules_count": {
                    "gte": from_interpretation_rules_count,
                }
            }
        }

        res_query['bool']['filter'].append(interpretation_rules_count_query)

    print(res_query)
    return res_query


def filter_SubjectArea_fields(res_query, subject_area_name, subject_sub_area_name, organization_name, type_id,
                              revoked_size, revoked_type_id, organization_type_id):
    if subject_area_name != "0":
        subject_area_name = SubjectArea.objects.get(id=subject_area_name).name
        subject_area_name_query = {
            "term": {
                "subject_area_name.keyword": subject_area_name
            }
        }
        res_query['bool']['filter'].append(subject_area_name_query)

        # ---------------------------------------------------------
    subject_sub_area_name = subject_sub_area_name.split('__')
    if "0" not in subject_sub_area_name:
        subject_sub_area_name_list = SubjectSubArea.objects.filter(id__in=subject_sub_area_name)
        subject_sub_area_name_list = [s.name for s in subject_sub_area_name_list]
        subject_sub_area_name_query = {
            "terms": {
                "subject_sub_area_name.keyword": subject_sub_area_name_list,
            }
        }
    else:
        subject_sub_area_name_query = {
            "bool": {
                "must_not": {
                    "term": {
                        "subject_sub_area_name.keyword": "نامشخص",
                    }
                }
            }
        }
    res_query['bool']['filter'].append(subject_sub_area_name_query)

    # ---------------------------------------------------------
    if organization_name != "0":
        organization_name_query = {
            "term": {
                "organization_type_name.keyword": organization_name
            }
        }
        res_query['bool']['filter'].append(organization_name_query)

    # ---------------------------------------------------------
    if type_id != 0:
        type_name = Type.objects.get(id=type_id).name

        type_name = Local_preprocessing(type_name)

        type_query = {
            "term": {
                "type_name.keyword": type_name
            }
        }
        res_query['bool']['filter'].append(type_query)

    # ---------------------------------------------------------
    if revoked_size != "0":
        revoked_size_query = {
            "term": {
                "revoked_size.keyword": revoked_size
            }
        }
        res_query['bool']['filter'].append(revoked_size_query)

    # ---------------------------------------------------------
    if revoked_type_id != "0":
        revoked_type_name = RevokedType.objects.get(id=revoked_type_id).name
        revoked_type_name_query = {
            "term": {
                "revoked_type_name.keyword": revoked_type_name
            }
        }
        res_query['bool']['filter'].append(revoked_type_name_query)

    return res_query


def filter_judge_fields(res_query, JudgeName, SubjectTypeDisplayName, Judgmenttype, Categories, from_year, to_year,
                        from_advisory_opinion_count, from_interpretation_rules_count):
    if JudgeName != 0:
        judge_name = JudgmentJudge.objects.get(id=JudgeName).name
        judge_name = arabic_preprocessing(judge_name)
        judge_name_query = {
            "term": {
                "judge_name.keyword": judge_name
            }
        }
        res_query['bool']['filter'].append(judge_name_query)

    # ---------------------------------------------------------
    if SubjectTypeDisplayName != 0:
        subject_type_display_name = JudgmentSubjectTypeDisplayName.objects.get(id=SubjectTypeDisplayName).name
        subject_type_display_name_query = {
            "term": {
                "subject_type_display_name.keyword": subject_type_display_name
            }
        }
        res_query['bool']['filter'].append(subject_type_display_name_query)

    # ---------------------------------------------------------
    if Judgmenttype != 0:
        judgment_type = JudgmentType.objects.get(id=Judgmenttype).name
        judgment_type_query = {
            "term": {
                "judgment_type.keyword": judgment_type
            }
        }
        res_query['bool']['filter'].append(judgment_type_query)

    # ---------------------------------------------------------
    if Categories != 0:
        categories = JudgmentCategories.objects.get(id=Categories).name
        categories_query = {
            "term": {
                "categories.keyword": categories
            }
        }
        res_query['bool']['filter'].append(categories_query)

    # ----------------------------------------------------------
    First_Year = 1000
    Last_Year = 1403

    if from_year != 0 or to_year != 0:
        from_year = from_year if from_year != 0 else First_Year
        to_year = to_year if to_year != 0 else Last_Year

        year_query = {
            "range": {
                "judgment_year": {
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
                "advisory_opinion_count": {
                    "gte": from_advisory_opinion_count,
                }
            }
        }

        res_query['bool']['filter'].append(advisory_opinion_count_query)

    # ----------------------------------------------------------

    if from_interpretation_rules_count != 0:
        interpretation_rules_count_query = {
            "range": {
                "interpretation_rules_count": {
                    "gte": from_interpretation_rules_count,
                }
            }
        }

        res_query['bool']['filter'].append(interpretation_rules_count_query)

    return res_query





def filter_book_fields(res_query, subject, publisher_name):
    if subject != '0':
        subject_query = {
            "term": {
                "subject_name.keyword": subject
            }
        }
        res_query['bool']['filter'].append(subject_query)

    # ---------------------------------------------------------
    if publisher_name != '0':
        publisher_query = {
            "term": {
                "publisher_name.keyword": publisher_name
            }
        }
        res_query['bool']['filter'].append(publisher_query)

    return res_query


def filter_definition_fields(res_query, type):
    if type != 'all':
        type = 0 if type == 'definition' else 1

        approval_ref_query = {
            "match_phrase": {
                "is_abbreviation": type
            }
        }
        res_query['bool']['must'].append(approval_ref_query)

    return res_query














def SearchDocument_ES_Book(request, country_id, subject, publisher_name, place, text, search_type):
    fields = [subject, publisher_name]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_book_fields(res_query, subject, publisher_name)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    response = client.search(index=book_index_name,
                             _source_includes=['document_id', 'book_name', 'publisher_name', 'subject_name',
                                               'published_year', 'pages_count'],
                             request_timeout=40,
                             query=res_query,
                             size=100

                             )

    # print("Got %d Hits:" % response['hits']['total']['value'])
    total_hits = response['hits']['total']['value']

    return JsonResponse({
        "result": response['hits']['hits'],
        'total_hits': total_hits})











def SearchDocumentsValidation_Column_ES(request, country_id, level_name, subject_area_name, subject_sub_area_name,
                                        type_name, approval_reference_name, from_year, to_year,
                                        from_advisory_opinion_count, from_interpretation_rules_count, revoked_type_name,
                                        revoke_type_detail, place, text, search_type, curr_page):
    # approvalsList_ES_2(request, country_id, level_id, subject_area_text, subject_sub_area_text, type_id, approval_reference_id, from_year, to_year,
    #                  from_advisory_opinion_count,
    #                  from_interpretation_rules_count, revoked_type_id, revoke_type_detail, place, text, search_type):

    revoke_type_detail = revoke_type_detail.replace('موقوف الاجرا', 'موقوفالاجرا')
    revoke_type_detail = revoke_type_detail.replace('لغوملغی', 'لغو/ملغی')
    RevokedType_text, RevokedSize_text = (revoke_type_detail + " 0").split(' ')[:2]
    RevokedType_text = RevokedType_text.replace('موقوفالاجرا', 'موقوف الاجرا')

    revoked_type_name = revoked_type_name.replace('>', '/').replace('>', '/')

    if (RevokedSize_text == "0"):
        RevokedSize_text = "همه"

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = False

    res_query['bool']['filter'] = []
    res_query = filter_doc_fields_COLUMN_validation(res_query, level_name, subject_area_name, subject_sub_area_name,
                                                    type_name, approval_reference_name, from_year, to_year,
                                                    from_advisory_opinion_count, from_interpretation_rules_count,
                                                    revoked_type_name, RevokedType_text, RevokedSize_text)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text_revoke(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text_revoked(res_query, place, text, search_type, ALL_FIELDS)

    print(res_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, RevokedDocument.__name__)

    from_value = (curr_page - 1) * search_result_size

    response = client.search(index=index_name,
                             _source_includes=['dest_document_id', 'dest_document_name', 'approval_reference_name',
                                               'dest_approval_date', 'subject_name', 'dest_file_name',
                                               "level_name", 'type_name'],
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


def SearchDocumentSubjectArea_ES(request, country_id, revoked_type_id, subject_area_name, subject_sub_area_name,
                                 organization_name, type_id, revoked_size, place, text, search_type,
                                 from_advisory_opinion_count, from_interpretation_rules_count,
                                 curr_page):
    organization_type_id = '0'

    fields = [revoked_type_id, subject_area_name, subject_sub_area_name, organization_name, type_id,
              revoked_size, from_advisory_opinion_count, from_interpretation_rules_count, organization_type_id]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_SubjectArea_fields(res_query, subject_area_name, subject_sub_area_name, organization_name,
                                              type_id,
                                              revoked_size, revoked_type_id, organization_type_id)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, Document.__name__)

    # ---------------------- Get Chart Data -------------------------
    res_agg = {

        "subject-sub-area-agg": {
            "terms": {
                "field": "subject_sub_area_name.keyword",
                "size": bucket_size
            }
        },
        "approval-ref-agg": {
            "terms": {
                "field": "approval_reference_name.keyword",
                "size": bucket_size
            }
        },
        "level-agg": {
            "terms": {
                "field": "level_name.keyword",
                "size": bucket_size
            }
        },
        "approval-year-agg": {
            "terms": {
                "field": "approval_year",
                "size": bucket_size
            }
        }

    }

    from_value = (curr_page - 1) * search_result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'approval_date', 'revoked_type_id',
                                               'revoked_type_name',
                                               'revoked_size', 'subject_area_name', 'subject_sub_area_name',
                                               'organization_type_name',
                                               'subject_sub_area_weight', 'subject_sub_area_entropy',
                                               'approval_reference_name', 'level_name', 'approval_year'],
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

    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        "curr_page": curr_page,
        'aggregations': aggregations})


def filter_subject_area_doc_fields(res_query, SubjectAreaSelect_id, subjects_sub_area_id_list):
    if "0" in subjects_sub_area_id_list:
        subject_area = SubjectArea.objects.get(id=SubjectAreaSelect_id).name
        subject_area_query = {
            "term": {
                "subject_area.keyword": subject_area
            }
        }
        res_query['bool']['filter'].append(subject_area_query)
    else:
        res_query['bool']['should'] = []

        for sub_area_id in subjects_sub_area_id_list:
            print(sub_area_id)

            sub_area = SubjectSubArea.objects.get(id=int(sub_area_id)).name
            print(sub_area)

            sub_area_query = {
                "term": {
                    "subject_sub_area.keyword": sub_area
                }
            }
            res_query['bool']['should'].append(sub_area_query)

    return res_query


def GetDocumentWithAreaKeywords(request, document_id):
    sub_area_id = Document.objects.get(
        id=document_id).subject_sub_area_id.id

    doc_name = Document.objects.get(
        id=document_id).name

    word_list = list(SubjectSubAreaKeyWords.objects.filter(
        subject_sub_area_id__id=sub_area_id).values_list('word', flat=True).distinct())

    print(len(word_list))

    temp_paragraphs = list(DocumentParagraphs.objects.filter(
        reduce(operator.or_, (Q(text__icontains=" " + word + " ") for word in word_list)),
        document_id__id=document_id).order_by('number').values_list('text', flat=True))

    result_paragraphs = []

    for para in temp_paragraphs:
        for word in word_list:
            word_tag = "<strong class='text-primary bold'>" + word + "</strong>"

            para = para.replace(" " + word + " ", " " + word_tag + " ")

        result_paragraphs.append(para)

    return JsonResponse({
        "result_paragraph": result_paragraphs,
        "doc_name": doc_name
    })


def GetParagraphWithAreaKeywords(request, document_id):
    doc = Document.objects.get(id=document_id)
    doc_name = doc.name
    subject_area_id = doc.subject_area_id.id
    document_citation_list = DocumentSubjectSubArea.objects.filter(document_id__id=document_id).order_by('-weight')

    subject_sub_areas = [{
        'subject_sub_area_id': row.subject_sub_area_id.id,
        'subject_sub_area_name': row.subject_sub_area_id.name,
        'weight': row.weight * 100,
    } for row in document_citation_list if row.weight]

    subject_sub_area_id_dict = {row['subject_sub_area_id']: row['subject_sub_area_name'] for row in subject_sub_areas}

    word_list = SubjectSubAreaKeyWords.objects.filter(
        subject_sub_area_id__id__in=subject_sub_area_id_dict.keys()).values_list('word',
                                                                                 'subject_sub_area_id').distinct()

    sub_area_words_dict = {}
    for word in word_list:
        if word[1] in sub_area_words_dict:
            sub_area_words_dict[word[1]].append(word[0])
        else:
            sub_area_words_dict[word[1]] = [word[0]]

    sub_area_paragraph = []
    keywords = []
    for sub_area_id, words in sub_area_words_dict.items():
        new_sub_area = {'sub_area_id': sub_area_id, 'sub_area_name': subject_sub_area_id_dict[sub_area_id],
                        'words_count': {}}
        temp_paragraphs = list(DocumentParagraphs.objects.filter(
            reduce(operator.or_, (Q(text__icontains=" " + word + " ") for word in words)),
            document_id__id=document_id).order_by('number').values_list('text', flat=True))

        result_paragraphs = []

        for para in temp_paragraphs:
            for word in list(set(words)):
                word_tag = "<strong class='text-primary bold'>" + word + "</strong>"

                para = para.replace(" " + word + " ", " " + word_tag + " ")
                if new_sub_area['words_count'].get(word):
                    new_sub_area['words_count'][word] += para.count(word_tag)
                else:
                    new_sub_area['words_count'][word] = para.count(word_tag)

            result_paragraphs.append(para)

        sub_area_paragraph.append(
            {'sub_area_id': sub_area_id,
             'sub_area_name': subject_sub_area_id_dict[sub_area_id],
             'paragraphs': result_paragraphs}
        )
        keywords_text = ""
        new_sub_area['words_count'] = sorted(new_sub_area['words_count'].items(), key=lambda x: x[1], reverse=True)
        for word, count in new_sub_area['words_count']:
            if count > 0:
                keywords_text += word + " (" + str(count) + "), "
        new_sub_area['words_count'] = keywords_text[:-2]

        keywords.append(new_sub_area)

    return JsonResponse({
        "sub_area_paragraph": sub_area_paragraph,
        "doc_name": doc_name,
        "keywords": keywords
    })


def documentSubjecArea_ES(request, country_id, SubjectAreaSelect_id, multiselect_SubjectSubArea_value):
    subjects_sub_area_id_list = multiselect_SubjectSubArea_value.split("__")

    organization_type_id = '0'

    fields = []

    res_query = {
        "bool": {}
    }

    res_query['bool']['filter'] = []
    res_query = filter_subject_area_doc_fields(res_query, SubjectAreaSelect_id, subjects_sub_area_id_list)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, Document.__name__)

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "approval-ref-agg": {
            "terms": {
                "field": "approval_reference_name.keyword",
                "size": bucket_size
            }
        },
        "subject-agg": {
            "terms": {
                "field": "subject_name.keyword",
                "size": bucket_size
            }
        },
        "level-agg": {
            "terms": {
                "field": "level_name.keyword",
                "size": bucket_size
            }
        },
        "type-agg": {
            "terms": {
                "field": "type_name.keyword",
                "size": bucket_size
            }
        },
        "approval-year-agg": {
            "terms": {
                "field": "approval_year",
                "size": bucket_size
            }
        },
        "subject-area-year-agg": {
            "terms": {
                "field": "subject_area.keyword",
                "size": bucket_size
            }
        },
        "subject-sub-area-year-agg": {
            "terms": {
                "field": "subject_sub_area.keyword",
                "size": bucket_size
            }
        }

    }

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'approval_reference_name', 'approval_date',
                                               'subject_name',
                                               "level_name", 'type_name', 'approval_year', 'communicated_date',
                                               'advisory_opinion_count', 'interpretation_rules_count',
                                               'revoked_type_name'],
                             request_timeout=40,
                             query=res_query,
                             aggregations=res_agg,
                             size=2000

                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    aggregations = response['aggregations']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        'aggregations': aggregations})


def approvalsList_ES(request, country_id, level_id, subject_area_name, subject_sub_area_name, type_id,
                     approval_reference_id, from_year, to_year, from_advisory_opinion_count,
                     from_interpretation_rules_count, revoked_type_id, organization_type_id, place, text, search_type,
                     curr_page):
    fields = [level_id, subject_area_name, subject_sub_area_name, type_id, approval_reference_id, from_year, to_year,
              from_advisory_opinion_count, from_interpretation_rules_count, revoked_type_id, organization_type_id]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_doc_fields_with_subject_area(res_query, level_id, subject_area_name, subject_sub_area_name,
                                                        type_id, approval_reference_id, from_year, to_year,
                                                        from_advisory_opinion_count, from_interpretation_rules_count,
                                                        revoked_type_id, organization_type_id)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, Document.__name__)

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "approval-ref-agg": {
            "terms": {
                "field": "approval_reference_name.keyword",
                "size": bucket_size
            }
        },
        "subject-sub-area-agg": {
            "terms": {
                "field": "subject_sub_area_name.keyword",
                "size": bucket_size
            }
        },
        "level-agg": {
            "terms": {
                "field": "level_name.keyword",
                "size": bucket_size
            }
        },
        "type-agg": {
            "terms": {
                "field": "type_name.keyword",
                "size": bucket_size
            }
        },

        "organization-type-agg": {
            "terms": {
                "field": "organization_type_name.keyword",
                "size": bucket_size
            }
        },
        "approval-year-agg": {
            "terms": {
                "field": "approval_year",
                "size": bucket_size
            }
        }

    }

    from_value = (curr_page - 1) * search_result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'approval_reference_name', 'approval_date',
                                               'subject_area_name', 'subject_sub_area_name',
                                               "level_name", 'type_name', 'approval_year', 'communicated_date',
                                               'advisory_opinion_count', 'interpretation_rules_count',
                                               'revoked_type_name', 'organization_type_name'],
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

    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        "curr_page": curr_page,
        'aggregations': aggregations})


def approvalsList_RefGraph_ES(request, country_id, level_id, subject_area_name, subject_sub_area_name, type_id,
                              approval_reference_id, from_year, to_year, from_advisory_opinion_count,
                              from_interpretation_rules_count, revoked_type_id, organization_type_id, place, text,
                              search_type):
    fields = [level_id, subject_area_name, subject_sub_area_name, type_id, approval_reference_id, from_year, to_year,
              from_advisory_opinion_count, from_interpretation_rules_count, revoked_type_id, organization_type_id]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_doc_fields_with_subject_area(res_query, level_id, subject_area_name, subject_sub_area_name,
                                                        type_id, approval_reference_id, from_year, to_year,
                                                        from_advisory_opinion_count, from_interpretation_rules_count,
                                                        revoked_type_id, organization_type_id)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, Document.__name__)

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name'],
                             request_timeout=40,
                             query=res_query,
                             size=500

                             )

    documents_id_list = [row['_id'] for row in response['hits']['hits']]

    graph_edge_list = Graph.objects.filter(
        src_document_id__id__in=documents_id_list, dest_document_id__id__in=documents_id_list)

    nodes_list = []
    added_node = []
    edges_list = []
    added_edge = []

    for edge in graph_edge_list:

        src_id = str(edge.src_document_id_id)
        src_name = edge.src_document_id.name
        src_color = str(edge.src_document_id.type_id.color) if edge.src_document_id.type_id is not None else "#000000"

        src_node = {"id": src_id, "name": src_name, "style": {"fill": src_color}}

        dest_id = str(edge.dest_document_id_id)
        dest_name = edge.dest_document_id.name
        dest_color = str(
            edge.dest_document_id.type_id.color) if edge.dest_document_id.type_id is not None else "#000000"

        dest_node = {"id": dest_id, "name": dest_name, "style": {"fill": dest_color}}

        weight = edge.weight

        if src_id not in added_node:
            nodes_list.append(src_node)
            added_node.append(src_id)

        if dest_id not in added_node:
            nodes_list.append(dest_node)
            added_node.append(dest_id)

        edge_obj = {"source": src_id, "source_name": src_name,
                    "target": dest_id, "target_name": dest_name,
                    "weight": weight}

        if [dest_id, src_id] not in added_edge and src_id != dest_id:
            edges_list.append(edge_obj)
            added_edge.append([src_id, dest_id])

    return JsonResponse({"Nodes_data": nodes_list, "Edges_data": edges_list})


def approvalsList_ES_2(request, country_id, level_id, subject_area_text, subject_sub_area_text, type_id,
                       approval_reference_id, from_year, to_year,
                       from_advisory_opinion_count,
                       from_interpretation_rules_count, revoked_type_id, revoke_type_detail, place, text, search_type,
                       curr_page):
    revoke_type_detail = revoke_type_detail.replace('موقوف الاجرا', 'موقوفالاجرا')
    revoke_type_detail = revoke_type_detail.replace('لغوملغی', 'لغو/ملغی')
    RevokedType_text, RevokedSize_text = (revoke_type_detail + " 0").split(' ')[:2]
    RevokedType_text = RevokedType_text.replace('موقوفالاجرا', 'موقوف الاجرا')
    fields = [RevokedType_text, RevokedSize_text]
    fields += [level_id, subject_area_text, subject_sub_area_text, type_id, approval_reference_id, from_year, to_year,
               from_advisory_opinion_count, from_interpretation_rules_count, revoked_type_id]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_revoked_fields(res_query, RevokedType_text, RevokedSize_text, '0')
        res_query = filter_doc_fields(res_query, level_id, 0, type_id, approval_reference_id, from_year,
                                      to_year, from_advisory_opinion_count, from_interpretation_rules_count,
                                      revoked_type_id, '0')
        if subject_area_text != '0':
            temp_query = {
                "term": {
                    "subject_area_name.keyword": subject_area_text
                }
            }
            res_query['bool']['filter'].append(temp_query)
        if subject_sub_area_text != '0':
            temp_query = {
                "term": {
                    "subject_sub_area_name.keyword": subject_sub_area_text
                }
            }
            res_query['bool']['filter'].append(temp_query)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text_revoke(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text_revoked(res_query, place, text, search_type, ALL_FIELDS)

    print(res_query)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, RevokedDocument.__name__)

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "approval-ref-agg": {
            "terms": {
                "field": "approval_reference_name.keyword",
                "size": bucket_size
            }
        },
        "subject-agg": {
            "terms": {
                "field": "subject_name.keyword",
                "size": bucket_size
            }
        },
        "level-agg": {
            "terms": {
                "field": "level_name.keyword",
                "size": bucket_size
            }
        },
        "type-agg": {
            "terms": {
                "field": "type_name.keyword",
                "size": bucket_size
            }
        },
        "approval-year-agg": {
            "terms": {
                "field": "approval_year",  # ???
                "size": bucket_size
            }
        },
        "revoked-sub-type": {  # صریح ، ضمنی
            "terms": {
                "field": "revoked_sub_type.keyword",
                "size": bucket_size
            }
        },
        "revoked-size": {  # کلی ، جزیی
            "terms": {
                "field": "revoked_size.keyword",
                "size": bucket_size
            }
        },
        "revoked-type-name": {
            "terms": {
                "field": "revoked_type_name.keyword",
                "size": bucket_size
            }
        },
        "subject-area-name": {
            "terms": {
                "field": "subject_area_name.keyword",
                "size": bucket_size
            }
        },
        "subject-sub-area-name": {
            "terms": {
                "field": "subject_sub_area_name.keyword",
                "size": bucket_size
            }
        }
    }

    from_value = (curr_page - 1) * search_result_size

    response = client.search(index=index_name,
                             _source_includes=['src_document_id', 'src_document_name',
                                               'dest_document_id', 'dest_document_name', 'revoked_type_name',
                                               'revoked_sub_type', 'revoked_size', 'src_para_id', 'dest_para_id',
                                               'src_approval_date', 'dest_approval_date', 'revoked_clauses'],
                             request_timeout=40,
                             query=res_query,
                             size=search_result_size,  # 100
                             aggregations=res_agg,
                             from_=from_value,
                             )

    # print("Got %d Hits:" % response['hits']['total']['value'])
    total_hits = response['hits']['total']['value']
    print(response['hits']['total'])
    aggregations = response['aggregations']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    return JsonResponse({
        "result": response['hits']['hits'],
        "curr_page": curr_page,
        'aggregations': aggregations,
        'total_hits': total_hits})


def exact_search_text_revoke(res_query, place, text, ALL_FIELDS):
    text = text.replace('>', '/').replace('<', '\\')
    print('exact')
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

        two_title_query = {
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "dest_document_name": text
                        }
                    },
                    {
                        "match_phrase": {
                            "src_document_name": text
                        }
                    }
                ]
            }
        }

        if ALL_FIELDS:
            res_query = two_title_query
        else:
            res_query['bool']['must'].append(two_title_query)

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


    else:
        title_content_query = {
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "dest_document_name": text
                        }
                    },
                    {
                        "match_phrase": {
                            "src_document_name": text
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


def boolean_search_text_revoked(res_query, place, text, operator, ALL_FIELDS):
    text = text.replace('>', '/').replace('<', '\\')
    print('and')
    if place == 'عنوان':

        two_title_query = {
            "bool": {

                "should": [
                    {
                        "match": {
                            "dest_document_name": {
                                "query": text,
                                "operator": operator
                            }
                        }
                    },
                    {
                        "match": {
                            "src_document_name": {
                                "query": text,
                                "operator": operator
                            }
                        }
                    }
                ]
            }
        }

        if ALL_FIELDS:
            res_query = two_title_query
        else:
            res_query['bool']['must'].append(two_title_query)

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


    else:
        title_content_query = {
            "bool": {

                "should": [
                    {
                        "match": {
                            "dest_document_name": {
                                "query": text,
                                "operator": operator
                            }
                        }
                    },
                    {
                        "match": {
                            "src_document_name": {
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


def SearchDocument_ES_web(request, text):
    country_id = 1
    level_id = 0
    subject_id = 0
    type_id = 0
    approval_reference_id = 0
    from_year = 0
    to_year = 0
    from_advisory_opinion_count = 0
    from_interpretation_rules_count = 0
    revoked_type_id = 0
    organization_type_id = 0
    place = 'عنوان'
    search_type = 'exact'

    fields = [level_id, subject_id, type_id, approval_reference_id, from_year, to_year, from_advisory_opinion_count,
              from_interpretation_rules_count, revoked_type_id]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_doc_fields(res_query, level_id, subject_id, type_id, approval_reference_id, from_year,
                                      to_year,
                                      from_advisory_opinion_count, from_interpretation_rules_count, revoked_type_id,
                                      organization_type_id)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    index_name = es_config.DOTIC_DOC_INDEX

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'approval_reference_name', 'approval_date'],
                             request_timeout=40,
                             query=res_query,
                             size=10

                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    return JsonResponse({
        "result": result,
        'total_hits': total_hits})


def SearchJudgment_ES(request, country_id, JudgeName,
                      SubjectTypeDisplayName, JudgmentType, Categories, from_year, to_year,
                      from_advisory_opinion_count, from_interpretation_rules_count, place, text, search_type,
                      curr_page):
    fields = [JudgeName, SubjectTypeDisplayName, JudgmentType, Categories, from_year, to_year,
              from_advisory_opinion_count, from_interpretation_rules_count]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_judge_fields(res_query, JudgeName, SubjectTypeDisplayName, JudgmentType, Categories,
                                        from_year, to_year, from_advisory_opinion_count,
                                        from_interpretation_rules_count)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, Judgment.__name__)
    # index_name = "doticfull_judgment"

    # ---------------------- Get Chart Data -------------------------
    res_agg = {
        "subject-type-display-name-agg": {
            "terms": {
                "field": "subject_type_display_name.keyword",
                "size": bucket_size
            }
        },
        "judgment-type-agg": {
            "terms": {
                "field": "judgment_type.keyword",
                "size": bucket_size
            }
        },
        "complaint-from-agg": {
            "terms": {
                "field": "complaint_from.keyword",
                "size": bucket_size
            }
        },
        "judge-name-agg": {
            "terms": {
                "field": "judge_name.keyword",
                "size": bucket_size
            }
        },
        "categories-agg": {
            "terms": {
                "field": "categories.keyword",
                "size": bucket_size
            }
        },
        "judgment-year-agg": {
            "terms": {
                "field": "judgment_year",
                "size": bucket_size
            }
        }

    }
    from_value = (curr_page - 1) * search_result_size

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'document_file_name',
                                               'judgment_id', 'judgment_number', 'judgment_date', 'judgment_year',
                                               'complaint_serial', 'conclusion_display_name',
                                               'subject_type_display_name',
                                               'judgment_type', 'complainant', 'complaint_from', 'categories',
                                               'affected_document_name', 'judge_name'],
                             request_timeout=40,
                             query=res_query,
                             aggregations=res_agg,
                             from_=from_value,
                             size=search_result_size,
                             )

    result = response['hits']['hits']

    total_hits = response['hits']['total']['value']

    aggregations = response['aggregations']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    # added --------------
    response = client.search(index=index_name,
                             request_timeout=40,
                             query=res_query
                             )
    max_score = response['hits']['hits'][0]['_score'] if total_hits > 0 else 1
    max_score = max_score if max_score > 0 else 1
    # added --------------

    return JsonResponse({
        "result": result,
        'total_hits': total_hits,
        'max_score': max_score,
        'aggregations': aggregations,
        "curr_page": curr_page,
    })




















def GetSearchDetails_ES_Judgment(request, document_id, search_type, text):
    document = Document.objects.get(id=document_id)
    country = Country.objects.get(id=document.country_id.id)

    local_index = standardIndexName(country, Judgment.__name__)

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
                             _source_includes=['document_id', 'name', 'attachment.content', 'subject_complaint',
                                               'affected_document_name'],
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
        subject_complaint = response['hits']['hits'][0]['_source']['subject_complaint']
        affected_document_name = response['hits']['hits'][0]['_source']['affected_document_name']
    else:
        response = client.get(index=local_index, id=document_id,
                              _source_includes=['document_id', 'name', 'attachment.content', 'subject_complaint',
                                                'affected_document_name']
                              )
        result_text = response['_source']['attachment']['content']
        subject_complaint = response['_source']['subject_complaint']
        affected_document_name = response['_source']['affected_document_name']

    result_text = arabic_preprocessing(result_text)

    return JsonResponse({
        "result": result_text,
        "subject_complaint": subject_complaint,
        "affected_document_name": affected_document_name})


def GetActorsChartData_ES(request, text, doc_ids_text):
    # ---------- Generate Data -------------

    doc_ids = doc_ids_text.split(',')

    words = text.split(" ")
    actors_chart_data = getActorsChartData(words, doc_ids)
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

    return JsonResponse({
        'actors_chart_data': actors_chart_data,
        'entropy_dict': entropy_dict,
        'parallelism_dict': parallelism_dict,
        'mean_dict': mean_dict,
        'std_dict': std_dict,
        'normal_entropy_dict': normal_entropy_dict,
        'column_1': 'salahiat',
        'column_2': 'hamkaran',
        'column_3': 'motevalian',
    })




# ------------------------------------------------------------------


def SearchDocumentExact(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year, to_year,
                        place, text):
    # Filter Documents
    documents_list = Document.objects.filter(country_id_id=country_id, )

    if level_id > 0:
        if level_id == 4:
            documents_list = documents_list.filter(level_id_id=None)
        else:
            documents_list = documents_list.filter(level_id_id=level_id)

    if subject_id > 0:
        documents_list = documents_list.filter(subject_id_id=subject_id)

    if type_id > 0:
        documents_list = documents_list.filter(type_id_id=type_id)

    if approval_reference_id > 0:
        documents_list = documents_list.filter(
            approval_reference_id_id=approval_reference_id)

    documents_list = documents_list.annotate(
        approval_year=Cast(Substr('approval_date', 1, 4), IntegerField()))

    if from_year > 0:
        documents_list = documents_list.filter(approval_year__gte=from_year)

    if to_year > 0:
        documents_list = documents_list.filter(approval_year__lte=to_year)

    # preprocess and split search text
    text = arabic_preprocessing(text).replace("  ", " ")
    if place == "عنوان":
        documents_list = documents_list.filter(Q(name__startswith=text + " ") | Q(name__icontains=" " + text + " ") | Q(
            name__endswith=" " + text)).annotate(document_id=F('id')).values("document_id")

    elif place == "متن":
        documents_list = DocumentParagraphs.objects.filter(Q(document_id__in=documents_list) & (
                Q(text__startswith=text + " ") | Q(text__icontains=" " + text + " ") | Q(
            text__endswith=" " + text))).values("document_id")

    elif place == "تعاریف":
        documents_list = DocumentGeneralDefinition.objects.filter(
            (Q(keyword__startswith=text + " ") | Q(keyword__icontains=" " + text + " ") | Q(
                keyword__endswith=" " + text)) & Q(document_id__in=documents_list)).values("document_id")

    else:
        documents_list_title = documents_list.filter(
            Q(name__startswith=text + " ") | Q(name__icontains=" " + text + " ") | Q(
                name__endswith=" " + text)).annotate(document_id=F('id')).values("document_id")
        documents_list_text = DocumentParagraphs.objects.filter(Q(document_id__in=documents_list) & (
                Q(text__startswith=text + " ") | Q(text__icontains=" " + text + " ") | Q(
            text__endswith=" " + text))).values("document_id")
        documents_list = documents_list_title.union(documents_list_text)

    # documents_list = documents_list.distinct()
    # ---------- Generate Data -------------

    subject_data = {}
    approval_references_data = {}
    level_data = {}
    approval_year_data = {}
    type_data = {}

    documents_information_result = []

    for doc in documents_list:

        # Generate Document List Table Data
        document_id = doc["document_id"]
        word_count = str(GetSearchCountExact(document_id, text, place))
        document_information = GetDocumentById_Local(document_id)
        document_information["count"] = word_count
        document_information["searched_word"] = text
        document_information["keywords_count"] = 1
        documents_information_result.append(document_information)

        # Generate chart Data
        subject_id = document_information["subject_id"]
        subject_name = document_information["subject"]
        approval_references_id = document_information["approval_reference_id"]
        approval_references_name = document_information["approval_reference"]
        level_id = document_information["level_id"]
        level_name = document_information["level"]
        type_id = document_information["type_id"]
        type_name = document_information["type"]
        doc_approval_year = document_information["approval_date"]
        if doc_approval_year != "نامشخص":
            doc_approval_year = document_information["approval_date"][0:4]

        if subject_id not in subject_data:
            subject_data[subject_id] = {"name": subject_name, "count": 1}
        else:
            subject_data[subject_id]["count"] += 1

        if approval_references_id not in approval_references_data:
            approval_references_data[approval_references_id] = {
                "name": approval_references_name, "count": 1}
        else:
            approval_references_data[approval_references_id]["count"] += 1

        if level_id not in level_data:
            level_data[level_id] = {"name": level_name, "count": 1}
        else:
            level_data[level_id]["count"] += 1

        if type_id not in type_data:
            type_data[type_id] = {"name": type_name, "count": 1}
        else:
            type_data[type_id]["count"] += 1

        if doc_approval_year not in approval_year_data:
            approval_year_data[doc_approval_year] = {
                "name": doc_approval_year, "count": 1}
        else:
            approval_year_data[doc_approval_year]["count"] += 1

    doc_ids = [d['document_id'] for d in documents_list]
    actors_chart_data = getActorsChartData([text], doc_ids)
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

    return JsonResponse({'documents_information_result': documents_information_result,
                         'subject_chart_data': subject_data,
                         'approval_references_chart_data': approval_references_data,
                         'level_chart_data': level_data,
                         'approval_year_chart_data': approval_year_data,
                         'type_chart_data': type_data,
                         'actors_chart_data': actors_chart_data,
                         'entropy_dict': entropy_dict,
                         'parallelism_dict': parallelism_dict,
                         'mean_dict': mean_dict,
                         'std_dict': std_dict,
                         'normal_entropy_dict': normal_entropy_dict,
                         'column_1': 'salahiat',
                         'column_2': 'hamkaran',
                         'column_3': 'motevalian',
                         })


def SearchDocumentWithoutText(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year,
                              to_year):
    # Filter Documents
    documents_list = Document.objects.filter(country_id_id=country_id)

    if level_id > 0:
        if level_id == 4:
            documents_list = documents_list.filter(level_id_id=None)
        else:
            documents_list = documents_list.filter(level_id_id=level_id)

    if subject_id > 0:
        documents_list = documents_list.filter(subject_id_id=subject_id)

    if type_id > 0:
        documents_list = documents_list.filter(type_id_id=type_id)

    if approval_reference_id > 0:
        documents_list = documents_list.filter(
            approval_reference_id_id=approval_reference_id)

    documents_list = documents_list.annotate(
        approval_year=Cast(Substr('approval_date', 1, 4), IntegerField()))

    if from_year > 0:
        documents_list = documents_list.filter(approval_year__gte=from_year)

    if to_year > 0:
        documents_list = documents_list.filter(approval_year__lte=to_year)

    # ---------- Generate Data -------------

    subject_data = {}
    approval_references_data = {}
    level_data = {}
    approval_year_data = {}
    type_data = {}

    # documents_information_result = list(documents_list.values_list('json_text', flat=True))
    documents_information_result = []

    for doc in documents_list:

        # Generate Document List Table Data
        document_id = doc.id
        document_information = GetDocumentById_Local(document_id)
        documents_information_result.append(document_information)

        # Generate chart Data
        if doc.subject_id is not None:
            subject_id = doc.subject_id.id
            subject_name = doc.subject_name
        else:
            subject_id = None
            subject_name = "نامشخص"

        if doc.approval_reference_id is not None:
            approval_references_id = doc.approval_reference_id.id
            approval_references_name = doc.approval_reference_name
        else:
            approval_references_id = None
            approval_references_name = "نامشخص"

        if doc.level_id is not None:
            level_id = doc.level_id.id
            level_name = doc.level_name
        else:
            approval_references_id = None
            level_name = "نامشخص"

        if doc.type_id is not None:
            type_id = doc.type_id.id
            type_name = doc.type_name
        else:
            type_id = None
            type_name = "نامشخص"

        if doc.approval_date is not None:
            doc_approval_year = doc.approval_date[0:4]
        else:
            doc_approval_year = "نامشخص"

        if subject_id not in subject_data:
            subject_data[subject_id] = {"name": subject_name, "count": 1}
        else:
            subject_data[subject_id]["count"] += 1

        if approval_references_id not in approval_references_data:
            approval_references_data[approval_references_id] = {
                "name": approval_references_name, "count": 1}
        else:
            approval_references_data[approval_references_id]["count"] += 1

        if level_id not in level_data:
            level_data[level_id] = {"name": level_name, "count": 1}
        else:
            level_data[level_id]["count"] += 1

        if type_id not in type_data:
            type_data[type_id] = {"name": type_name, "count": 1}
        else:
            type_data[type_id]["count"] += 1

        if doc_approval_year not in approval_year_data:
            approval_year_data[doc_approval_year] = {
                "name": doc_approval_year, "count": 1}
        else:
            approval_year_data[doc_approval_year]["count"] += 1

    doc_ids = [d.id for d in documents_list]
    actors_chart_data = getActorsChartData([], doc_ids)
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

    return JsonResponse({'documents_information_result': documents_information_result,
                         'subject_chart_data': subject_data,
                         'approval_references_chart_data': approval_references_data,
                         'level_chart_data': level_data,
                         'approval_year_chart_data': approval_year_data,
                         'type_chart_data': type_data,
                         'actors_chart_data': actors_chart_data,
                         'entropy_dict': entropy_dict,
                         'parallelism_dict': parallelism_dict,
                         'mean_dict': mean_dict,
                         'std_dict': std_dict,
                         'normal_entropy_dict': normal_entropy_dict,
                         'column_1': 'salahiat',
                         'column_2': 'hamkaran',
                         'column_3': 'motevalian',
                         })


def getActorsChartData(words, doc_ids):
    # generate actors chart data
    actors_information_dict = {}

    actor_docs = DocumentActor.objects.filter(document_id__in=doc_ids)
    actors_result = []
    if len(words) > 0:
        for word in words:
            actors_result += actor_docs.filter(paragraph_id__text__icontains=(
                    word + ' '))  ####################################################################
    else:
        actors_result = actor_docs

    for res in actors_result:
        actor_id = res.actor_id.id
        actor_name = res.actor_id.name
        actor_role_name = res.actor_type_id.name
        actor_paragraph_id = res.paragraph_id.id

        if actor_id not in actors_information_dict:
            actors_information_dict[actor_id] = {
                'actor_name': actor_name,
                'roles_info': {
                    'متولی اجرا': [],
                    'همکار': [],
                    'دارای صلاحیت اختیاری': []
                }

            }
            actor_roles_info = actors_information_dict[actor_id]['roles_info']
            actor_roles_info[actor_role_name].append(actor_paragraph_id)
            actors_information_dict[actor_id]['roles_info'] = actor_roles_info

        else:
            actor_roles_info_2 = actors_information_dict[actor_id]['roles_info']
            if actor_paragraph_id not in actor_roles_info_2[actor_role_name]:
                actor_roles_info_2[actor_role_name].append(actor_paragraph_id)
                actors_information_dict[actor_id]['roles_info'] = actor_roles_info_2

    # Calculate role frequency of actors
    actors_chart_data = []
    for actor_id in actors_information_dict:
        actor_name = actors_information_dict[actor_id]['actor_name']
        motevali_count = len(actors_information_dict[actor_id]['roles_info']['متولی اجرا'])
        hamkar_count = len(actors_information_dict[actor_id]['roles_info']['همکار'])
        salahiat_count = len(actors_information_dict[actor_id]['roles_info']['دارای صلاحیت اختیاری'])
        column_data = [actor_name, motevali_count, hamkar_count, salahiat_count]
        actors_chart_data.append(column_data)

    return actors_chart_data


def SearchDocumentByname(request, country_id, text):
    text = arabic_preprocessing(text)

    document_list = Document.objects.filter(country_id_id=country_id, name__icontains=text)

    data = list(CUBE_DocumentJsonList.objects.filter(document_id__in=document_list).values_list('json_text', flat=True))
    document_count = data.__len__()

    return JsonResponse({'documentsList': data, 'document_count': document_count})


def GetSearchDetailsAndOR(request, document_id, text, where, mode):
    words = arabic_preprocessing(text).split(" ")
    if where == 'تعاریف':
        if mode == 'OR':
            document_definitions = DocumentGeneralDefinition.objects.filter(
                reduce(operator.or_, (Q(keyword__icontains=word) for word in words)), document_id=document_id)
            document_name = document_definitions[0].document_id.name
        else:
            document_definitions = DocumentGeneralDefinition.objects.filter(
                reduce(operator.and_, (Q(keyword__icontains=word) for word in words)), document_id=document_id)
            document_name = document_definitions[0].document_id.name

        result = [(d.keyword + ':' + d.text) for d in document_definitions]
    else:
        document_paragraphs = DocumentParagraphs.objects.filter(
            document_id_id=document_id).order_by("number")
        document_name = document_paragraphs[0].document_id.name
        result = []

        for paragraph in document_paragraphs:
            paragraph_text = paragraph.text
            for word in words:
                if paragraph_text.__contains__(word):
                    result.append(paragraph_text)
                    break

    result = list(set(result))

    return JsonResponse({'document_paragraphs_result': result, "document_name": [document_name],
                         "preprocess_text": [arabic_preprocessing(text)]})


def GetSearchDetailsExact(request, document_id, text, where):
    if where == 'تعاریف':
        document_definitions = DocumentGeneralDefinition.objects.filter(keyword__icontains=text,
                                                                        document_id=document_id)
        document_name = document_definitions[0].document_id.name
        result = [(d.keyword + ':' + d.text) for d in document_definitions]
    else:
        text = arabic_preprocessing(text).replace("  ", " ")
        document_paragraphs = DocumentParagraphs.objects.filter(
            document_id_id=document_id, text__icontains=text).order_by("number")

        document_name = document_paragraphs[0].document_id.name
        result = []
        for paragraph in document_paragraphs:
            paragraph_text = paragraph.text
            result.append(paragraph_text)

    result = list(set(result))

    return JsonResponse({'document_paragraphs_result': result, "document_name": [document_name],
                         "preprocess_text": [arabic_preprocessing(text)]})


def GetSelectedAraDetails(request, documents_id):
    # Filter Documents
    documents_id_list = documents_id.split(',')
    ara_list = Document.objects.filter(id__in=documents_id_list)

    subject_data = {}
    level_data = {}
    approval_year_data = {}
    keywords_data = {}
    approval_references_data = {}
    type_data = {}
    documents_information_result = []

    for doc in ara_list:

        document_id = doc.id
        document_information = GetDocumentById_Local(document_id)
        document_keywords_list = []

        # Generate document keywords Data
        document_keywords = DocumentKeywords.objects.filter(document_id=document_id).values(
            'keyword_id__word', 'keyword_id').order_by('keyword_id__word').distinct()

        for keword in document_keywords:

            keyword_id = keword['keyword_id']
            keyword_name = keword['keyword_id__word']
            document_keywords_list.append(keyword_name)

            if keyword_id not in keywords_data:
                keywords_data[keyword_id] = {"name": keyword_name, "count": 1}
            else:
                keywords_data[keyword_id]["count"] += 1

        document_information['keywords_count'] = len(document_keywords_list)
        document_information['keywords_list'] = ' - '.join(
            document_keywords_list)

        documents_information_result.append(document_information)

        # Generate chart Data
        subject_id = document_information["subject_id"]
        subject_name = document_information["subject"]
        approval_references_id = document_information["approval_reference_id"]
        approval_references_name = document_information["approval_reference"]
        level_id = document_information["level_id"]
        level_name = document_information["level"]
        type_id = document_information["type_id"]
        type_name = document_information["type"]
        doc_approval_year = document_information["approval_date"]
        if doc_approval_year != "نامشخص":
            doc_approval_year = document_information["approval_date"][0:4]

        if subject_id not in subject_data:
            subject_data[subject_id] = {"name": subject_name, "count": 1}
        else:
            subject_data[subject_id]["count"] += 1

        if approval_references_id not in approval_references_data:
            approval_references_data[approval_references_id] = {
                "name": approval_references_name, "count": 1}
        else:
            approval_references_data[approval_references_id]["count"] += 1

        if level_id not in level_data:
            level_data[level_id] = {"name": level_name, "count": 1}
        else:
            level_data[level_id]["count"] += 1

        if type_id not in type_data:
            type_data[type_id] = {"name": type_name, "count": 1}
        else:
            type_data[type_id]["count"] += 1

        if doc_approval_year not in approval_year_data:
            approval_year_data[doc_approval_year] = {
                "name": doc_approval_year, "count": 1}
        else:
            approval_year_data[doc_approval_year]["count"] += 1

    # Sort keywords chart data
    keywords_data = dict(sorted(keywords_data.items(),
                                key=lambda item: item[1]['count'], reverse=True))
    # Sort keywords table data
    documents_information_result = sorted(
        documents_information_result, key=lambda d: d['keywords_count'], reverse=True)

    return JsonResponse({'documents_information_result': documents_information_result,
                         'subject_chart_data': subject_data,
                         'approval_references_chart_data': approval_references_data,
                         'level_chart_data': level_data,
                         'approval_year_chart_data': approval_year_data,
                         'type_chart_data': type_data,
                         'keywords_chart_data': keywords_data
                         })








def GetKeywordsDetailsExact(request, document_id, text):
    keywords = text.split(',')
    paragraph_result = []

    document_name = Document.objects.get(id=document_id).name

    document_paragraphs = DocumentParagraphs.objects.filter(
        reduce(operator.or_, (Q(text__icontains=kw) for kw in keywords)),
        document_id_id=document_id).order_by("number")

    for paragraph in document_paragraphs:
        paragraph_text = paragraph.text
        paragraph_result.append(paragraph_text)

    document_paragraph_result = list(set(paragraph_result))

    return JsonResponse({'document_paragraphs_result': document_paragraph_result, "document_name": document_name,
                         "preprocess_text": [arabic_preprocessing(text)]})


def UploadDraft(request):
    if request.method == 'POST':
        window_length = 100
        hamkaran_punctuations = ['،', ')', ':']

        file = request.FILES['draft_file']
        keywords = request.POST.get('keywords')
        preprocessed_keywords = arabic_preprocessing(keywords)
        keyword_list = preprocessed_keywords.split(',')

        country_id = request.POST.get('country_id')
        country_file_name = Country.objects.get(id=country_id).file_name
        country_file_name = country_file_name.split('.')[0]
        folder = 'media_cdn/draft/' + country_file_name
        file_url = folder + '/' + file.name

        if not os.path.exists(file_url):
            fs = FileSystemStorage(location=folder)
            filename = fs.save(file.name, file)
            # file_url = fs.url(filename)

        file_text = docx2txt.process(file_url)
        preprocessed_file_text = arabic_preprocessing(file_text)
        paragraphs = preprocessed_file_text.split('\n')
        selected_paragraphs = []

        for paragraph in paragraphs:
            for keyword in keyword_list:
                if (' ' + keyword + ' ') in paragraph or (' ' + keyword) in paragraph:
                    selected_paragraphs.append(paragraph)

        selected_paragraphs = list(set(selected_paragraphs))

    return JsonResponse({'selected_paragraphs': selected_paragraphs, 'draft_text': preprocessed_file_text})


def getDraftActors(request, country_id, draft_name):
    country_file_name = Country.objects.get(id=country_id).file_name
    country_file_name = country_file_name.split('.')[0]
    folder = 'media_cdn/draft/' + country_file_name
    file_url = folder + '/' + draft_name

    # read draft file and get text of it
    file_text = docx2txt.process(file_url)
    preprocessed_file_text = arabic_preprocessing(file_text)
    draft_paragraphs = preprocessed_file_text.split('\n')

    window_length = 100
    hamkaran_punctuations = ['،', ')', ':']

    motevalian_dict = {}
    salahiat_dict = {}
    hamkaran_dict = {}

    draft_actors = {}

    for paragraph in draft_paragraphs:

        # pattern keywords
        motevalianPatternKeywordsList = ['مکلف است', 'موظف است']
        hamkaranPatternKeywordsList = ['با همکاری', 'باهمکاری']
        salahiatPatternKeywordsList = [
            'مختار است', 'اختیار دارد', 'می‌تواند', 'می تواند', 'میتواند', 'مجاز است']

        actorsList = Actor.objects.all().values('name').distinct()

        # motevalian
        for pattern_keyword in motevalianPatternKeywordsList:
            for actor in actorsList:
                if (actor['name'] + ' ' + pattern_keyword) in paragraph and actor['name'] not in motevalian_dict:
                    motevalian_dict[actor['name']] = 1
                elif (actor['name'] + ' ' + pattern_keyword) in paragraph and actor['name'] in motevalian_dict:
                    motevalian_dict[actor['name']] += 1

        # salahiat
        for pattern_keyword in salahiatPatternKeywordsList:
            for actor in actorsList:
                if (actor['name'] + ' ' + pattern_keyword) in paragraph and actor['name'] not in salahiat_dict:
                    salahiat_dict[actor['name']] = 1
                elif (actor['name'] + ' ' + pattern_keyword) in paragraph and actor['name'] in salahiat_dict:
                    salahiat_dict[actor['name']] += 1

        # hamkaran
        for pattern_keyword in hamkaranPatternKeywordsList:
            indices = [m.start()
                       for m in re.finditer(pattern_keyword, paragraph)]

            for index in indices:
                start_index = index + len(pattern_keyword)
                end_index = (start_index + window_length)
                sub_string = paragraph[start_index:end_index]

                for actor in actorsList:
                    actor_flag = False

                    if (' ' + actor['name'] + ' ') in sub_string or ('(' + actor['name'] + ')') in sub_string:
                        actor_flag = True

                    for symbol in hamkaran_punctuations:
                        if (' ' + actor['name'] + symbol) in sub_string:
                            actor_flag = True

                    actor_without_affix = actor['name'].replace('وزارت ', '').replace(
                        'سازمان ', '').replace(' جمهوری اسلامی ایران', '')

                    if (
                            actor_without_affix != 'اطلاعات' and actor_without_affix != 'فناوری اطلاعات' and actor_without_affix != 'کشور' and
                            actor['name'] not in sub_string):

                        if (' ' + actor_without_affix + ' ') in sub_string or (
                                '(' + actor_without_affix + ')') in sub_string:
                            actor_flag = True

                        for symbol in hamkaran_punctuations:
                            if (' ' + actor_without_affix + symbol) in sub_string:
                                actor_flag = True

                    if actor_flag and actor['name'] not in hamkaran_dict:
                        hamkaran_dict[actor['name']] = 1

                    elif actor_flag and actor['name'] in hamkaran_dict:
                        hamkaran_dict[actor['name']] += 1

    draft_actors['motevalian'] = motevalian_dict
    draft_actors['hamkaran'] = hamkaran_dict
    draft_actors['salahiat'] = salahiat_dict

    return JsonResponse({"draft_actors": draft_actors})















def GetActorsKeywordsGraphByDocumentsIdKeywords(request, document_ids_text, keywords_text):
    documents_id_list = document_ids_text.split(',')
    keywords_list = keywords_text.split(',')
    temp_nodes = []
    nodes = []
    edges = []
    chart_data = {}

    for keyword in keywords_list:

        keyword_node = {'id': keyword, 'group': 'keywords'}
        nodes.append(keyword_node)

        for doc_id in documents_id_list:
            actors_list = DocumentActor.objects.filter(document_id_id=doc_id,
                                                       paragraph_id__text__icontains=(' ' + keyword + ' ')).annotate(
                actor_name=F('actor_id__name')).values('actor_name').distinct()

            for actor in actors_list:
                actor_name = actor['actor_name']

                if actor_name not in temp_nodes:
                    temp_nodes.append(actor_name)
                    actor_node = {'id': actor_name, 'group': 'actors', 'fill': {
                        'src': "../../static/icons/actors_icons/actor_icon3.png"
                    }}
                    nodes.append(actor_node)

                edge = {'from': actor_name, 'to': keyword}
                edges.append(edge)

    chart_data['nodes'] = nodes
    chart_data['edges'] = edges

    return JsonResponse({"chart_data": chart_data})


def GetActorParaphraphsByDocumentsIdActorNameKeyword_Modal(request, documents_id_text, actor_name, keyword):
    result_info = []
    documents_id_list = documents_id_text.split(',')

    actors_info = DocumentActor.objects.filter(document_id__id__in=documents_id_list, actor_id__name=actor_name,
                                               paragraph_id__text__icontains=(' ' + keyword + ' ')).annotate(
        document_name=F('document_id__name')).annotate(
        paragraph=F('paragraph_id__text')).annotate(
        actor_name=F('actor_id__name')).annotate(
        actor_type=F('actor_type_id__name')).values_list(
        'document_id', 'document_name', 'paragraph', 'actor_name', 'actor_type', 'current_actor_form').distinct()

    for info in actors_info:
        temp_info = {}

        temp_info['document_id'] = info[0]
        temp_info['document_name'] = info[1]
        temp_info['paragraph'] = info[2]
        temp_info['actor_name'] = info[3]
        temp_info['actor_type'] = info[4]
        temp_info['current_actor_form'] = info[5]

        result_info.append(temp_info)

    return JsonResponse({"result_info": result_info})





























@allowed_users()
def GetAcceseToAllUsers(request):
    CreatePanel(request)
    panels = Panels.objects.all()
    users = User.objects.all().filter(is_super_user=False, is_active=1)
    for user in users:
        curr_user = User.objects.all().get(id=user.id)
        for panel in panels:
            curr_panel = Panels.objects.all().get(id=panel.id)
            user_admin_panels = UserPanels.objects.filter(panel=curr_panel, user=curr_user)
            if not user_admin_panels:
                UserPanels.objects.create(
                    panel=panel,
                    user=user
                )
    return JsonResponse({"status": "created"})














def UploadCompressedPdfs(request):
    if request.method == 'POST':
        file = request.FILES['compressed_file']

        folder = 'media_cdn/pdf2text/'
        date_time = str(datetime.datetime.now()).replace(':', '-')
        date_time = date_time.replace('.', '-')
        name = os.path.splitext(os.path.basename(file.name))
        name = name[0] + '_' + date_time + name[1]
        file_url = folder + '/' + name
        if not os.path.exists(file_url):
            fs = FileSystemStorage(location=folder)
            filename = fs.save(name, file)
        return JsonResponse({'status': 'file uploaded successfully', 'saved_path': file_url})
    return JsonResponse({'status': 'failed!'})


def read_english_pdf(pdf_path):
    print(f'reading {pdf_path} ......')
    pdf_file = pdfplumber.open(pdf_path)
    all_text = ''
    for page in pdf_file.pages:
        single_page_text = page.extract_text()
        all_text += '\n' + str(single_page_text)
    return all_text


def read_persian_pdf(pdf_path):
    print(f'reading {pdf_path} ......')
    pdf_document = PDF_Document(
        document_path=pdf_path,
        language='fas'
    )
    pdf2text = PDF2Text(document=pdf_document)
    content = pdf2text.extract()

    all_text = ''
    for page in content:
        all_text += page['text']

    return all_text


def read_russian_pdf(pdf_path):
    print(f'reading {pdf_path} ......')
    all_text = 'russian is not implemented yet!'

    return all_text


def extract_zip(zip_path):
    out_dir = os.path.dirname(zip_path)
    out_dir += '/extracted_' + os.path.splitext(os.path.basename(zip_path))[0]
    with ZipFile(zip_path, 'r') as zipObj:
        zipObj.extractall(out_dir)
    return out_dir


def zip_directory(dir_path):
    zip_path = os.path.dirname(
        dir_path) + '/' + os.path.splitext(os.path.basename(dir_path))[0] + '.zip'
    with ZipFile(zip_path, 'w') as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(dir_path):
            for filename in filenames:
                # create complete filepath of file in directory
                filePath = os.path.join(folderName, filename)
                # Add file to zip
                zipObj.write(filePath, os.path.basename(filePath))
    return zip_path


def pdf2text_converter(zip_path, language):
    pdfs_dir = extract_zip(zip_path)
    results_dir = os.path.dirname(
        zip_path) + '/results_' + os.path.splitext(os.path.basename(zip_path))[0]
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
    pdfs_list = [p for p in os.listdir(pdfs_dir) if p.lower().endswith('.pdf')]
    for pdf_path in pdfs_list:
        if language == 'Persian':
            result_txt = read_persian_pdf(os.path.join(pdfs_dir, pdf_path))
        elif language == 'Russian':
            result_txt = read_russian_pdf(os.path.join(pdfs_dir, pdf_path))
        else:
            result_txt = read_english_pdf(os.path.join(pdfs_dir, pdf_path))
        text_file_path = results_dir + '/' + \
                         os.path.splitext(pdf_path)[0] + '.txt'
        with open(text_file_path, 'w', encoding="utf-8") as f:
            f.write(result_txt)

    results_zip = zip_directory(results_dir)
    return results_zip


def DownloadPdfTexts(request):
    zip_result = pdf2text_converter(request.POST.get(
        'compressed_path'), request.POST.get('language'))
    return JsonResponse({'saved_path': zip_result, 'status': 'converted to text files successfully!'})


def GetRegularityAreaList(request):
    RegularityAreaList = []

    area_list = RegularityArea.objects.all().values(
        'id', 'name').order_by("name").distinct()

    for area in area_list:
        res = {
            'id': area['id'],
            'area_name': area['name']
        }

        RegularityAreaList.append(res)

    return JsonResponse({"RegularityAreaList": RegularityAreaList})


def GetRegularityToolsList(request):
    RegularityToolsList = []

    tool_list = RegularityTools.objects.all().values(
        'id', 'name').order_by("name").distinct()

    for tool in tool_list:
        res = {
            'id': tool['id'],
            'tool_name': tool['name']
        }

        RegularityToolsList.append(res)

    return JsonResponse({"RegularityToolsList": RegularityToolsList})


def GetRegularityLifeCycleList(request):
    RegularityLifeCycleList = ['صدور',
                               'تمدید',
                               'اصلاح',
                               'لغو',
                               'ابطال',
                               'تعلیق',
                               'کاهش مدت اعتبار',
                               'انتقال']
    RegularityLifeCycleListWithID = []
    for index_, life_cycle in enumerate(RegularityLifeCycleList):
        res = {
            'id': index_ + 1,
            'life_cycle_name': life_cycle
        }

        RegularityLifeCycleListWithID.append(res)

    return JsonResponse({"RegularityLifeCycleList": RegularityLifeCycleListWithID})


def GetCollectiveActorList(request):
    CollectiveActorList = []

    Actor_list = CollectiveActor.objects.all().values(
        'id', 'name').order_by("name").distinct()

    for actor in Actor_list:
        res = {
            'id': actor['id'],
            'tool_name': actor['name']
        }

        CollectiveActorList.append(res)

    return JsonResponse({"CollectiveActorList": CollectiveActorList})


# Regularity panel
def GetRegulatorsByAreaId(reauest, area_id):
    RegulatorsList = []
    regulators = []

    if area_id == 0:
        regulators = Regulator.objects.all().values(
            'id', 'name').distinct().order_by('name')
    else:
        regulators = Regulator.objects.filter(area_id__id=area_id).values(
            'id', 'name').distinct().order_by('name')

    for regulator in regulators:
        res = {
            'id': regulator['id'],
            'regulator_name': regulator['name']
        }

        RegulatorsList.append(res)

    return JsonResponse({"RegulatorsList": RegulatorsList})


def SearchDocumentsByRegulatorsKeywords(request, country_id, tools_id, area_id, regulator_id, keywords_text):
    documents_information_dict = {}
    tools_distribution_data_dict = {}
    doc_paragraphs = []
    tools_id = tools_id.split("__")

    # Filter by tool
    if '0' not in tools_id:
        doc_paragraphs = DocumentRegulator.objects.filter(
            document_id__country_id__id=country_id, tool_id__id__in=tools_id).values('id')

    else:
        doc_paragraphs = DocumentRegulator.objects.filter(
            document_id__country_id__id=country_id).values('id')

    # Filter by regulator
    if regulator_id != 0:
        doc_paragraphs = DocumentRegulator.objects.filter(
            id__in=doc_paragraphs, regulator_id__id=regulator_id)
    else:
        # Filter by area
        if area_id != 0:
            doc_paragraphs = DocumentRegulator.objects.filter(
                id__in=doc_paragraphs, regulator_id__area_id__id=area_id)
        else:
            # all area
            doc_paragraphs = DocumentRegulator.objects.filter(
                id__in=doc_paragraphs)

    # Filter by keywords
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')

        doc_paragraphs = doc_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_id__text__icontains=word) for word in keywords_list)))

    # Fill documents information dict
    Result_DocumentRegulator_PKs = []

    for res in doc_paragraphs:

        doc_id = res.document_id.id
        Result_DocumentRegulator_PKs.append(res.id)
        doc_info = {}
        document_information = GetDocumentById_Local(doc_id)
        doc_info['id'] = doc_id
        doc_info['name'] = res.document_id.name
        doc_info['subject'] = document_information["subject"]
        doc_info['approval_reference'] = document_information["approval_reference"]
        doc_info['approval_date'] = document_information["approval_date"]
        doc_info['tool_name'] = res.tool_id.name

        if doc_id not in documents_information_dict:

            regulator_name = 'نامشخص'
            if res.regulator_id != None:
                regulator_name = res.regulator_id.name

            regulator_name += ' (' + res.tool_id.name + ')'

            doc_info['regulators'] = [regulator_name]

            documents_information_dict[doc_id] = doc_info

        else:

            regulator_name = 'نامشخص'
            if res.regulator_id != None:
                regulator_name = res.regulator_id.name

            doc_regulators = documents_information_dict[doc_id]['regulators']

            regulator_name += ' (' + res.tool_id.name + ')'

            if regulator_name not in doc_regulators:
                doc_regulators.append(regulator_name)
                doc_info['regulators'] = doc_regulators
                documents_information_dict[doc_id] = doc_info

    # Fill tool distribution data
    tool_distribution = doc_paragraphs.filter(id__in=Result_DocumentRegulator_PKs).values('tool_id',
                                                                                          'tool_id__name').annotate(
        tool_name=F('tool_id__name')).annotate(
        tool_count=Count('tool_id')).order_by('tool_count')

    for info in tool_distribution:
        tool_info = {}
        tool_info['tool_id'] = info['tool_id']
        tool_info['tool_name'] = info['tool_name']
        tool_info['tool_count'] = info['tool_count']
        tools_distribution_data_dict[info['tool_id']] = tool_info

    return JsonResponse({"documents_information_dict": documents_information_dict,
                         "tools_distribution_data_dict": tools_distribution_data_dict})


def SearchDocumentsByRegulatorsLifeCycleAndKeywords(request, country_id, tools_id, life_cycles, keywords_text):
    documents_information_dict = {}
    tools_id = tools_id.split("__")
    life_cycles = life_cycles.split("__")

    doc_paragraphs = CUBE_RegularityLifeCycle_TableData.objects.filter(country_id__id=country_id)
    # Filter by tool
    if '0' not in tools_id:
        doc_paragraphs = doc_paragraphs.filter(tool_id__id__in=tools_id)

    # Filter by life_cycles
    doc_paragraphs = doc_paragraphs.filter(regularity_life_cycle__in=life_cycles)

    DocumentRegulator_ids = [doc_paragraph.table_data['document_regulator_id'] for doc_paragraph in doc_paragraphs]

    doc_paragraphs = DocumentRegulator.objects.filter(id__in=DocumentRegulator_ids)

    # Filter by keywords
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')

        doc_paragraphs = doc_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_id__text__icontains=word) for word in keywords_list)))

    for res in doc_paragraphs:

        doc_id = res.document_id.id
        doc_info = {}
        tool_name = res.tool_id.name
        para = res.paragraph_id.text
        doc_info['life_cycle_name'] = []
        for life_cycle in life_cycles:
            if para.__contains__(life_cycle):
                doc_info['life_cycle_name'].append(life_cycle + " " + tool_name)

        if doc_id not in documents_information_dict.keys():
            document_information = GetDocumentById_Local(doc_id)
            doc_info['name'] = res.document_id.name
            doc_info['subject'] = document_information["subject"]
            documents_information_dict[doc_id] = doc_info
        else:
            documents_information_dict[doc_id]['life_cycle_name'] = \
                list(set(documents_information_dict[doc_id]['life_cycle_name'] + doc_info['life_cycle_name']))

    return JsonResponse({"documents_information_dict": documents_information_dict})


def SearchDocumentsByRegulators1(request, country_id, area_id, regulator_id, person_id):
    documents_information_dict = {}
    documents_information_dict = CUBE_Business_Advisor_TableData.objects.get(country_id__id=country_id,
                                                                             area_id=area_id, regulator_id=regulator_id,
                                                                             person_id=person_id).table_data['data']

    # print(documents_information_dict)
    return JsonResponse({"documents_information_dict": documents_information_dict})


# def SearchDocumentsByRegulators(request, country_id, area_id, regulator_id, person_id):
#     documents_information_dict = {}
#     tools_distribution_data_dict = {}
#     doc_paragraphs = []
#
#
#     # Filter by regulator
#     if regulator_id != 0:
#         doc_paragraphs = DocumentRegulator.objects.filter(
#             document_id__country_id__id=country_id, regulator_id__id=regulator_id)
#     else:
#         # Filter by area
#         if area_id != 0:
#             doc_paragraphs = DocumentRegulator.objects.filter(
#                 document_id__country_id__id=country_id, regulator_id__area_id__id=area_id)
#         else:
#             # all area
#             doc_paragraphs = DocumentRegulator.objects.filter(
#                 document_id__country_id__id=country_id)
#
#
#     result = []
#
#     if person_id == "حقیقی":
#         words = ['اشخاص حقیقی','شخص حقیقی']
#         result = doc_paragraphs. \
#             filter(reduce(operator.or_, (Q(paragraph_id__text__icontains=word) for word in words)))
#
#     if person_id == "حقوقی":
#         words = ['اشخاص حقوقی', 'شخص حقوقی']
#         result = doc_paragraphs. \
#             filter(reduce(operator.or_, (Q(paragraph_id__text__icontains=word) for word in words)))
#
#
#
#
#     # Fill documents information dict
#     Result_DocumentRegulator_PKs = []
#     for res in result:
#
#         doc_id = res.document_id.id
#         Result_DocumentRegulator_PKs.append(res.id)
#         doc_info = {}
#         document_information = GetDocumentById_Local(doc_id)
#         doc_info['id'] = doc_id
#         doc_info['name'] = res.document_id.name
#         doc_info['subject'] = document_information["subject"]
#         doc_info['approval_reference'] = document_information["approval_reference"]
#         doc_info['approval_date'] = document_information["approval_date"]
#         doc_info['tool_name'] = res.tool_id.name
#
#         if doc_id not in documents_information_dict:
#
#             regulator_name = 'نامشخص'
#             if res.regulator_id != None:
#                 regulator_name = res.regulator_id.name
#
#             regulator_name += ' (' + res.tool_id.name + ')'
#
#             doc_info['regulators'] = [regulator_name]
#
#             documents_information_dict[doc_id] = doc_info
#
#         else:
#
#             regulator_name = 'نامشخص'
#             if res.regulator_id != None:
#                 regulator_name = res.regulator_id.name
#
#             doc_regulators = documents_information_dict[doc_id]['regulators']
#
#             regulator_name += ' (' + res.tool_id.name + ')'
#
#             if regulator_name not in doc_regulators:
#                 doc_regulators.append(regulator_name)
#                 doc_info['regulators'] = doc_regulators
#                 documents_information_dict[doc_id] = doc_info
#
#
#
#     return JsonResponse({"documents_information_dict": documents_information_dict})


def make_chart_data_business_advisor(request, country_id, area_id, regulator_id, person_id):
    result_data = CUBE_Business_Advisor_ChartData.objects.filter(country_id__id=country_id, area_id=area_id,
                                                                 regulator_id=regulator_id, person_id=person_id) \
        .values('subject_chart_data', 'level_chart_data', 'approval_reference_chart_data', 'approval_year_chart_data')

    for res in result_data:
        subject_data = res['subject_chart_data']['data']
        approval_references_data = res['approval_reference_chart_data']['data']
        level_data = res['level_chart_data']['data']
        approval_year_data = res['approval_year_chart_data']['data']

    return JsonResponse({'subject_chart_data': subject_data,
                         'approval_references_chart_data': approval_references_data,
                         'level_chart_data': level_data,
                         'approval_year_chart_data': approval_year_data,
                         })


def RegularityLifeCycle(request, country_id, tools_id, area_id, regulator_id, keywords_text):
    documents_information_dict = {}
    tools_distribution_data_dict = {}
    doc_paragraphs = []
    tools_id = tools_id.split("__")

    # Filter by tool
    if '0' not in tools_id:
        doc_paragraphs = DocumentRegulator.objects.filter(
            document_id__country_id__id=country_id, tool_id__id__in=tools_id).values('id')

    else:
        doc_paragraphs = DocumentRegulator.objects.filter(
            document_id__country_id__id=country_id).values('id')

    # Filter by regulator
    if regulator_id != 0:
        doc_paragraphs = DocumentRegulator.objects.filter(
            id__in=doc_paragraphs, regulator_id__id=regulator_id)
    else:
        # Filter by area
        if area_id != 0:
            doc_paragraphs = DocumentRegulator.objects.filter(
                id__in=doc_paragraphs, regulator_id__area_id__id=area_id)
        else:
            # all area
            doc_paragraphs = DocumentRegulator.objects.filter(
                id__in=doc_paragraphs)

    # Filter by keywords
    result = []
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')

        for keyword in keywords_list:
            result += doc_paragraphs.filter(
                paragraph_id__text__icontains=keyword)
    else:
        result = doc_paragraphs

    # Fill documents information dict
    Result_DocumentRegulator_PKs = []
    for res in result:

        doc_id = res.document_id.id
        Result_DocumentRegulator_PKs.append(res.id)
        doc_info = {}
        document_information = GetDocumentById_Local(doc_id)
        doc_info['id'] = doc_id
        doc_info['name'] = res.document_id.name
        doc_info['subject'] = document_information["subject"]
        doc_info['approval_reference'] = document_information["approval_reference"]
        doc_info['approval_date'] = document_information["approval_date"]
        doc_info['tool_name'] = res.tool_id.name

        if doc_id not in documents_information_dict:

            regulator_name = 'نامشخص'
            if res.regulator_id != None:
                regulator_name = res.regulator_id.name

            regulator_name += ' (' + res.tool_id.name + ')'

            doc_info['regulators'] = [regulator_name]

            documents_information_dict[doc_id] = doc_info

        else:

            regulator_name = 'نامشخص'
            if res.regulator_id != None:
                regulator_name = res.regulator_id.name

            doc_regulators = documents_information_dict[doc_id]['regulators']

            regulator_name += ' (' + res.tool_id.name + ')'

            if regulator_name not in doc_regulators:
                doc_regulators.append(regulator_name)
                doc_info['regulators'] = doc_regulators
                documents_information_dict[doc_id] = doc_info

    # Fill tool distribution data
    tool_distribution = doc_paragraphs.filter(id__in=Result_DocumentRegulator_PKs).values('tool_id',
                                                                                          'tool_id__name').annotate(
        tool_name=F('tool_id__name')).annotate(
        tool_count=Count('tool_id')).order_by('tool_count')

    for info in tool_distribution:
        tool_info = {}
        tool_info['tool_id'] = info['tool_id']
        tool_info['tool_name'] = info['tool_name']
        tool_info['tool_count'] = info['tool_count']
        tools_distribution_data_dict[info['tool_id']] = tool_info

    return JsonResponse({"documents_information_dict": documents_information_dict,
                         "tools_distribution_data_dict": tools_distribution_data_dict})


def get_operators(_text: str):
    pattern_keywords_list = [
        'مجوز از ',
        'مجوز از',
        'با مجوز ',
        'مجوز رسمی ',
        'مجوز رسمی از ',
    ]
    pre_cutters = [
        {
            'key': 'ایجاد و فعالیت',
            'include': False,
            'priority': 0,
        },
        {
            'key': 'انتشار',
            'include': True,
            'priority': 0,
        },
        {
            'key': 'فعالیت',
            'include': True,
            'priority': 0,
        },
        {
            'key': 'ایجاد',
            'include': True,
            'priority': 0,
        },
        {
            'key': 'توسط',
            'include': False,
            'priority': 0,
        },
        {
            'key': 'درزمینه',
            'include': False,
            'priority': 50,
        },
        {
            'key': '-',
            'include': False,
            'priority': -100,
        },
        {
            'key': 'ـ',
            'include': False,
            'priority': -100,
        }
    ]
    post_cutters = [
        {
            'key': 'منوط',
            'include': False,
            'priority': 0,
        },
        {
            'key': 'با اهداف',
            'include': False,
            'priority': 0,
        },
        {
            'key': 'به هر طریق',
            'include': False,
            'priority': 50,
        },
        {
            'key': 'ملزم',
            'include': False,
            'priority': 0,
        },
        {
            'key': 'نیاز به اخذ',
            'include': False,
            'priority': 0,
        },
        {
            'key': 'دارای',
            'include': False,
            'priority': 0,
        },
        {
            'key': 'به‌موجب',
            'include': False,
            'priority': 50,
        }
    ]
    operators = []

    for pattern_keyword in pattern_keywords_list:
        split_text = _text.split(pattern_keyword)
        if len(split_text) < 2:
            continue
        for i in range(len(split_text) - 1):
            _keyword = split_text[i]
            _keyword = _keyword.split("ـ")[-1].split("-")[-1]

            temp_list = []
            _min_index = len(_keyword)
            _min = None
            for pre in pre_cutters:
                key = pre['key']
                # if key=='فعالیت':
                #     print(_keyword.find(key))
                _index = _keyword.find(key) - pre['priority']
                if _index + pre['priority'] != -1 and (_min is None or _index < _min_index):
                    _min_index = _index
                    _min = pre
            if _min is not None:
                max_len = len(_keyword.split(_min['key']))
                if max_len > 2:
                    for __index, word_ in enumerate(_keyword.split(_min['key'])):
                        if __index == 0:
                            continue
                        if __index == max_len - 1:
                            break
                        operators.append((_min['key'] if _min['include'] else "") + word_.strip())
                _keyword = (_min['key'] if _min['include'] else "") + _keyword.split(_min['key'])[-1]

            _max_index = -1
            _max = None
            for post in post_cutters:
                key = post['key']
                _index = _keyword.rfind(key) + post['priority']
                if _index - post['priority'] != -1 and (_max is None or _index > _max_index):
                    _max_index = _index
                    _max = post
            if _max is not None:
                _keyword = (_max['key'] if _max['include'] else "") + _keyword.split(_max['key'])[-2]
            if _max is not None or _min is not None:
                operators.append(_keyword.strip())

    return list(dict.fromkeys(operators))


# chunker = False
# tagger = False
#
#
# def once(func):
#     future = None
#     async def once_wrapper(*args, **kwargs):
#         nonlocal future
#         if not future:
#             future = asyncio.create_task(func(*args, **kwargs))
#         return await future
#     return once_wrapper
#
# @once
# async def load_chunker():
#     global chunker
#     if not chunker:
#         chunker = Chunker(model='resources/chunker.model')
#
#
# @once
# async def load_tagger():
#     global tagger
#     if not tagger:
#         tagger = POSTagger(model='resources/postagger.model')
#
#
# future1 = None
# future2 = None
#
#
# async def maybe_initialize_chunker():
#     global future1
#     if not future1:
#         future1 = asyncio.create_task(load_chunker())
#     await future1
#
# async def maybe_initialize_tagger():
#     global future2
#     if not future2:
#         future2 = asyncio.create_task(load_tagger())
#     await future2


# def get_operators(_text:str):
#     # print("----"*10)
#     pattern_keywords_list = [
#         'مجوز از ',
#         'مجوز از',
#         'با مجوز ',
#         'مجوز رسمی ',
#         'مجوز رسمی از ',
#     ]
#
#     cutters = [
#         {
#
#             'key': 'ایجاد و فعالیت',
#             'include': False,
#             'dir': 1,
#         },
#         {
#             'key': 'فعالیت',
#             'include': True,
#             'dir': 1,
#         },
#         {
#             'key': 'انتشار',
#             'include': True,
#             'dir': 1,
#         },
#         {
#             'key': 'ایجاد',
#             'include': True,
#             'dir': 1,
#         },
#         {
#             'key': 'درزمینه',
#             'include': False,
#             'dir': 1,
#         },
#         # {
#         #     'key': 'منوط',
#         #     'include': False,
#         #     'dir': -1,
#         # },
#         # {
#         #     'key': 'با اهداف',
#         #     'include': False,
#         #     'priority': 0,
#         # },
#         # {
#         #     'key': 'به هر طریق',
#         #     'include': False,
#         #     'priority': 50,
#         # },
#         # {
#         #     'key': 'ملزم',
#         #     'include': False,
#         #     'dir': -1,
#         # },
#         # {
#         #     'key': 'نیاز به اخذ',
#         #     'include': False,
#         #     'priority': 0,
#         # },
#         {
#             'key': 'دارای مجوز',
#             'include': False,
#             'dir': -1,
#         },
#         # {
#         #     'key': 'به‌موجب',
#         #     'include': False,
#         #     'priority': 50,
#         # },
#         # {
#         #     'key': 'توسط',
#         #     'include': False,
#         #     'priority': 50,
#         # },
#     ]
#
#     regex_ = r'\[.*?\]'
#     pair = re.compile(regex_)
#
#     operators = []
#
#     sents = sent_tokenize(_text)
#     # print(f'len = {len(sents)}')
#     for sent in sents:
#         sent = sent.split("ـ")[-1].split("-")[-1]
#         sent = sent.replace(" که ", " به متن خاص غیرقابل رویت از ")
#
#         for pattern_keyword in pattern_keywords_list:
#             if pattern_keyword not in sent:
#                 continue
#
#             sent = sent[0:sent.find(pattern_keyword)] + " مجوز است"
#
#
#             tagged = tagger.tag(word_tokenize(sent))
#             tagged = tree2brackets(chunker.parse(tagged))
#             old_tagged = pair.findall(tagged)
#             tagged = []
#
#             for index_ in range(len(old_tagged)):
#                 phrase = old_tagged[index_][1:-1]
#                 # print(phrase)
#
#                 found = False
#                 for cutter in cutters:
#                     if cutter['key'] not in phrase :
#                         continue
#                     if "NP" not in phrase :
#                         continue
#                     phrase = phrase.replace("NP","")
#                     if cutter['dir'] == 1:
#                         phrase = phrase[phrase.find(cutter['key']) + len(cutter['key']):-1]
#                     else:
#                         phrase = phrase[0:phrase.find(cutter['key'])]
#                     tagged.append(((cutter['key'] if cutter['include'] else "") + phrase).strip())
#                     # print(phrase)
#                     # print(((cutter['key'] if cutter['include'] else "") + phrase).strip())
#                     found = True
#                     break
#
#                 # print(f'found = {found}')
#
#                 if not found:
#                     stop = False
#                     added = False
#                     for i in range(index_ - 1, -1, -1):
#                         if "NP" not in old_tagged[i+1] or stop:
#                             break
#                         for cutter_ in cutters:
#                             if cutter_['key'] in old_tagged[i]:
#                                 if cutter_['dir'] == 1:
#                                     tagged.append(phrase.replace("NP", "").strip())
#                                     added = True
#                                     # print(f'found in as pre to {cutter_["key"]}')
#                                 stop = True
#                                 break
#                     if not added:
#                         stop = False
#                         for i in range(index_ + 1, len(old_tagged)):
#                             if "NP" not in old_tagged[i-1] or stop:
#                                 break
#                             for cutter_ in cutters:
#                                 if cutter_['key'] in old_tagged[i]:
#                                     if cutter_['dir'] == -1:
#                                         tagged.append(phrase.replace("NP", "").strip())
#                                         # print(f'found in as post to {cutter_["key"]}')
#                                     stop = True
#                                     break
#             operators += tagged
#     return list(dict.fromkeys(operators))


def GetRegularityParagraphsDetails_Modal(request, document_id, tools_id, area_id, regulator_id, keywords_text):
    # asyncio.run(maybe_initialize_chunker())
    # asyncio.run(maybe_initialize_tagger())
    doc_paragraphs = []
    tools_id = tools_id.split("__")

    if '0' not in tools_id:
        doc_paragraphs = DocumentRegulator.objects.filter(
            document_id__id=document_id, tool_id__id__in=tools_id)
    else:
        doc_paragraphs = DocumentRegulator.objects.filter(
            document_id__id=document_id)

    if regulator_id != 0:
        doc_paragraphs = doc_paragraphs.filter(regulator_id__id=regulator_id)
    else:
        # selected area
        if area_id != 0:
            doc_paragraphs = doc_paragraphs.filter(
                regulator_id__area_id__id=area_id)
        else:
            # all area
            doc_paragraphs = doc_paragraphs

    result = []
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')

        for keyword in keywords_list:
            result += doc_paragraphs.filter(
                paragraph_id__text__icontains=keyword)
    else:
        result = doc_paragraphs

    document_paragraphs_result = []
    unique_paragraphs_result = []
    for res in result:

        paragraph = {}
        paragraph_text = res.paragraph_id.text
        paragraph_tool = res.tool_id.name

        paragraph_regulator = 'نامشخص'
        if res.regulator_id != None:
            paragraph_regulator = res.regulator_id.name

        paragraph['text'] = paragraph_text
        paragraph['tool'] = paragraph_tool
        paragraph['regulator'] = paragraph_regulator

        paragraph_operators = []

        operator_dict = RegulatorOperator.objects.filter(
            document_id__id=document_id,
            tool_id__id=res.tool_id.id,
            paragraph_id__id=res.paragraph_id.id,
            regulator_id=res.regulator_id
        ).values('current_operator_form').distinct()

        for op_form in operator_dict:
            if op_form['current_operator_form'] not in paragraph_operators:
                paragraph_operators.append(op_form['current_operator_form'])

        paragraph['operators'] = paragraph_operators

        if res.id not in unique_paragraphs_result:
            unique_paragraphs_result.append(res.id)
            document_paragraphs_result.append(paragraph)

    document_name = Document.objects.get(id=document_id).name
    return JsonResponse({"document_paragraphs_result": document_paragraphs_result, 'document_name': document_name})


def GetLifeCycleParagraphsDetails_Modal(request, document_id, tools_id, life_cycles, keywords_text):
    tools_id = tools_id.split("__")
    life_cycles = life_cycles.split("__")

    doc_paragraphs = CUBE_RegularityLifeCycle_TableData.objects.filter(
        document_id__id=document_id)

    if '0' not in tools_id:
        doc_paragraphs = doc_paragraphs.filter(tool_id__id__in=tools_id)

    # Filter by life_cycles
    doc_paragraphs = doc_paragraphs.filter(regularity_life_cycle__in=life_cycles)

    L1 = [doc_paragraph.table_data['document_regulator_id'] for doc_paragraph in doc_paragraphs]
    # L2 = [doc_paragraph.table_data['highlights'] for doc_paragraph in doc_paragraphs]
    # DocumentRegulator_ids = dict(zip(L1, L2))

    doc_paragraphs = DocumentRegulator.objects.filter(id__in=L1)

    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')

        doc_paragraphs = doc_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_id__text__icontains=word) for word in keywords_list)))

    document_paragraphs_result = []
    unique_paragraphs_result = []
    for res in doc_paragraphs:

        paragraph = {}
        paragraph_text = res.paragraph_id.text
        paragraph_tool = res.tool_id.name

        paragraph['text'] = paragraph_text
        paragraph['tool'] = paragraph_tool
        # paragraph['highlights'] = DocumentRegulator_ids[res.id]
        # print(paragraph['highlights'])

        if res.id not in unique_paragraphs_result:
            unique_paragraphs_result.append(res.id)
            document_paragraphs_result.append(paragraph)
        # else:
        #     index_ = unique_paragraphs_result.index(res.id)
        #     document_paragraphs_result[index_]['highlights'] = [*document_paragraphs_result[index_]['highlights']
        #         , *paragraph['highlights']]

    document_name = Document.objects.get(id=document_id).name
    return JsonResponse({"document_paragraphs_result": document_paragraphs_result, 'document_name': document_name})


def GetRegulatorsGraphData(request, country_id, tools_id, area_id, regulator_id, keywords_text):
    nodes = []
    edges = []
    regulators_graph_data = {}
    tools_id = tools_id.split("__")

    # Graph Without keywords
    if keywords_text == 'empty':
        selected_regulators = []

        selected_regulators = DocumentRegulator.objects.filter(
            document_id__country_id__id=country_id)

        if '0' not in tools_id:
            selected_regulators = selected_regulators.filter(
                tool_id__id__in=tools_id)

        if regulator_id != 0:
            selected_regulators = selected_regulators.filter(
                regulator_id__id=regulator_id)
        else:
            if area_id != 0:
                selected_regulators = selected_regulators.filter(
                    regulator_id__area_id__id=area_id)

        for res in selected_regulators:

            if res.regulator_id != None:
                # Upper case
                Regulator_Doc_ID = res.document_id.id
                Regulator_Name = res.regulator_id.name
                Regulator_ID = res.regulator_id.id
                Regulator_Area_ID = res.regulator_id.area_id.id
                Regulator_Area_Name = res.regulator_id.area_id.name
                Regulator_Tool_Name = res.tool_id.name
                Regulator_Tool_ID = res.tool_id.id

                Regulator_Operators = get_regulator_operators(
                    Regulator_Doc_ID, Regulator_ID)

                # ---------------------------------------------------------------------
                regulator_node = {'id': Regulator_Name, 'group': 'regulators', 'fill': {
                    'src': "../../static/icons/regulators_icons/regulator1.png"
                }}

                nodes.append(regulator_node)
                # ---------------------------------------------------------------------

                for res in Regulator_Operators:
                    operator_node = {'id': res.operator_id.name, 'group': 'operators', 'fill': {
                        'src': "../../static/icons/regulators_icons/operator1.png"
                    }}

                    nodes.append(operator_node)

                    op_edge = {'from': Regulator_Name, 'to': res.operator_id.name,
                               'source_node_type': 'تنظیم‌گر',
                               'destination_node_type': 'متصدی',
                               'regulator_tool_name': Regulator_Tool_Name,
                               'regulator_id': Regulator_ID,
                               'tool_id': Regulator_Tool_ID,
                               'area_id': Regulator_Area_ID,
                               'operator_id': res.operator_id.id}
                    edges.append(op_edge)

    # Graph With keywords
    else:
        keywords_list = keywords_text.split(',')

        for keyword in keywords_list:
            keyword_node = {'id': keyword, 'group': 'keywords', 'fill': {
                'src': "../../static/icons/keywords_icons/keyword1.png"
            }}
            nodes.append(keyword_node)

            selected_regulators = []

            selected_regulators = DocumentRegulator.objects.filter(
                document_id__country_id__id=country_id, paragraph_id__text__icontains=keyword)

            if '0' not in tools_id:
                selected_regulators = selected_regulators.filter(
                    tool_id__id__in=tools_id)

            if regulator_id != 0:
                selected_regulators = selected_regulators.filter(
                    regulator_id__id=regulator_id)

            else:
                if area_id != 0:
                    selected_regulators = selected_regulators.filter(
                        regulator_id__area_id__id=area_id)

            for res in selected_regulators:

                if res.regulator_id != None:
                    # Upper case
                    Regulator_Doc_ID = res.document_id.id
                    Regulator_Name = res.regulator_id.name
                    Regulator_ID = res.regulator_id.id
                    Regulator_Area_ID = res.regulator_id.area_id.id
                    Regulator_Tool_Name = res.tool_id.name
                    Regulator_Tool_ID = res.tool_id.id

                    Regulator_Operators = get_regulator_operators(
                        Regulator_Doc_ID, Regulator_ID)

                    for res in Regulator_Operators:
                        operator_node = {'id': res.operator_id.name, 'group': 'operators', 'fill': {
                            'src': "../../static/icons/regulators_icons/operator1.png"
                        }}

                        nodes.append(operator_node)

                        op_edge = {'from': Regulator_Name, 'to': res.operator_id.name,
                                   'source_node_type': 'تنظیم‌گر',
                                   'destination_node_type': 'متصدی', 'regulator_tool_name': Regulator_Tool_Name,
                                   'regulator_id': Regulator_ID,
                                   'tool_id': Regulator_Tool_ID,
                                   'area_id': Regulator_Area_ID,
                                   'operator_id': res.operator_id.id}
                        edges.append(op_edge)

                    # ------------------------------------------------------------
                    regulator_node = {'id': Regulator_Name, 'group': 'regulators', 'fill': {
                        'src': "../../static/icons/regulators_icons/regulator1.png"
                    }}

                    nodes.append(regulator_node)

                    edge = {

                        'from': keyword,
                        'to': Regulator_Name,
                        'source_node_type': 'کلیدواژه',
                        'destination_node_type': 'تنظیم‌گر',
                        'regulator_tool_name': Regulator_Tool_Name,
                        'regulator_id': Regulator_ID,
                        'tool_id': Regulator_Tool_ID,
                        'area_id': Regulator_Area_ID,

                    }
                    edges.append(edge)

    regulators_graph_data['nodes'] = nodes
    regulators_graph_data['edges'] = edges

    return JsonResponse({"regulators_graph_data": regulators_graph_data})


def get_regulator_operators(doc_id, regulator_id):
    unique_operators_id = []
    reg_result_operators = []

    res_operators = RegulatorOperator.objects.filter(
        document_id__id=doc_id,
        regulator_id__id=regulator_id).distinct()

    for res in res_operators:
        if res.operator_id.id not in unique_operators_id:
            unique_operators_id.append(res.operator_id.id)
            reg_result_operators.append(res)

    return reg_result_operators


def GetRegulatorEdgeParagraphsByOperator_Modal(request, country_id, tool_id, regulator_id, operator_id):
    result_paragraphs = []
    selected_paragraphs = RegulatorOperator.objects.filter(document_id__country_id__id=country_id,
                                                           tool_id__id=tool_id, regulator_id__id=regulator_id,
                                                           operator_id__id=operator_id)

    for info in selected_paragraphs:
        paragraph_text = info.paragraph_id.text
        paragraph_tool = info.tool_id.name
        document_id = info.document_id.id
        document_name = info.document_id.name
        operator_form = info.current_operator_form

        paragraph = {}
        paragraph['text'] = paragraph_text
        paragraph['tool'] = paragraph_tool
        paragraph['document_id'] = document_id
        paragraph['document_name'] = document_name
        paragraph['operator_form'] = operator_form

        result_paragraphs.append(paragraph)

    return JsonResponse({"result_paragraphs": result_paragraphs})


def GetRegulatorEdgeParagraphsByKeyword_Modal(request, country_id, tool_id, area_id, regulator_id, keyword):
    result_paragraphs = []
    selected_paragraphs = DocumentRegulator.objects.filter(document_id__country_id__id=country_id,
                                                           tool_id__id=tool_id, regulator_id__id=regulator_id,
                                                           regulator_id__area_id__id=area_id,
                                                           paragraph_id__text__icontains=keyword)

    for info in selected_paragraphs:
        paragraph_text = info.paragraph_id.text
        paragraph_tool = info.tool_id.name
        document_id = info.document_id.id
        document_name = info.document_id.name

        paragraph = {}
        paragraph['text'] = paragraph_text
        paragraph['tool'] = paragraph_tool
        paragraph['document_id'] = document_id
        paragraph['document_name'] = document_name

        paragraph_operators = []

        operator_dict = RegulatorOperator.objects.filter(
            document_id__id=document_id,
            tool_id__id=info.tool_id.id,
            paragraph_id__id=info.paragraph_id.id,
            regulator_id=info.regulator_id
        ).values('current_operator_form').distinct()

        for op_form in operator_dict:
            if op_form['current_operator_form'] not in paragraph_operators:
                paragraph_operators.append(op_form['current_operator_form'])

        paragraph['operators'] = paragraph_operators

        result_paragraphs.append(paragraph)

    return JsonResponse({"result_paragraphs": result_paragraphs})


def GetRegularityParagraphsByToolName_Modal(request, country_id, tool_name, area_id, regulator_id, keywords_text):
    tool_paragraphs = DocumentRegulator.objects.filter(
        document_id__country_id__id=country_id, tool_id__name=tool_name)

    if regulator_id != 0:
        tool_paragraphs = tool_paragraphs.filter(regulator_id__id=regulator_id)
    else:
        # selected area
        if area_id != 0:
            tool_paragraphs = tool_paragraphs.filter(
                regulator_id__area_id__id=area_id)
        else:
            # all area
            tool_paragraphs = tool_paragraphs

    result = []
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')

        for keyword in keywords_list:
            result += tool_paragraphs.filter(
                paragraph_id__text__icontains=keyword)
    else:
        result = tool_paragraphs

    tool_paragraphs_result = []
    unique_paragraphs_result = []

    for res in result:

        document_id = res.document_id.id
        document_name = res.document_id.name
        paragraph = {}
        paragraph_text = res.paragraph_id.text
        paragraph_tool = res.tool_id.name

        paragraph_regulator = 'نامشخص'
        if res.regulator_id != None:
            paragraph_regulator = res.regulator_id.name

        paragraph['document_id'] = document_id
        paragraph['document_name'] = document_name

        paragraph['text'] = paragraph_text
        paragraph['tool'] = paragraph_tool
        paragraph['regulator'] = paragraph_regulator

        paragraph_operators = []

        operator_dict = RegulatorOperator.objects.filter(
            document_id__id=document_id,
            tool_id__id=res.tool_id.id,
            paragraph_id__id=res.paragraph_id.id,
            regulator_id=res.regulator_id
        ).values('current_operator_form').distinct()

        for op_form in operator_dict:
            if op_form['current_operator_form'] not in paragraph_operators:
                paragraph_operators.append(op_form['current_operator_form'])

        paragraph['operators'] = paragraph_operators

        if res.id not in unique_paragraphs_result:
            unique_paragraphs_result.append(res.id)
            tool_paragraphs_result.append(paragraph)

    return JsonResponse({"tool_paragraphs_result": tool_paragraphs_result})


def GetMostRepetitiveKeywords(request, country_id, subject_ids):
    subject_ids = subject_ids.split("_")
    subject_ids = [int(i) for i in subject_ids]
    result_dict = {}

    if 0 in subject_ids:
        result = list(
            ExtractedKeywords.objects.filter(definition_id__document_id__country_id=country_id).exclude(word="").values(
                'word').annotate(total=Count('id')).order_by('-total'))[:10]
    else:
        result = list(ExtractedKeywords.objects.filter(definition_id__document_id__country_id=country_id,
                                                       definition_id__document_id__subject_id__in=subject_ids).exclude(
            word="").values('word').annotate(total=Count('id')).order_by('-total'))[:10]

    for res in result:
        word = res['word']
        word_count = res['total']
        result_dict[word] = word_count

    return JsonResponse({"result_dict": result_dict})


def GetKeywordsDefinition(request, country_id, word):
    keywords = ExtractedKeywords.objects.filter(
        word=word, definition_id__document_id__country_id=country_id)

    result = []
    for key in keywords:
        doc_id = key.definition_id.document_id.id
        doc_name = key.definition_id.document_id.name
        def_text = key.definition_id.text
        # preprocessing
        normalizer = Normalizer()

        list_sent = def_text.split("\n")
        keyList = [re.sub(r'\t', '', i[:i.find(":")])
                   for i in list_sent if i.find(":") > -1]
        defList = [re.sub(r'\t', '', i[i.find(":") + 1:])
                   for i in list_sent if i.find(":") > -1]

        for kw, d in zip(keyList, defList):
            kw = normalizer.normalize(kw)

            # Cleaning
            ignoreList = ["!", "@", "$", "%", "^", "&", "*", "(", ")", "_", "+", "-", "/", "*", "'", "،", "؛", ",",
                          ""
                          "{", "}", "[", "]", "«", "»", "<", ">", ".", "?", "؟", "\n", "\t", '"',
                          '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۰', "٫",
                          '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '\u200f']
            for item in ignoreList:
                kw = kw.replace(item, " ")

            kw = [word for word in kw.split(" ") if word != ""]

            alphabet = ["الف", "ب", "پ", "ت", "ث", "ج", "چ", "ح", "خ", "د", "ذ", "ر", "ز", "ژ", "س", "ش", "ص", "ض",
                        "ط", "ظ", "ع", "غ", "ف", "ق", "ک", "گ", "ل", "م", "ن", "و", "ه", "ی", "ا", "آ"]

            if len(kw) > 0:
                if kw[0] in alphabet and " ".join(kw[1:]) == word:
                    res = {'doc_id': doc_id, 'doc_name': doc_name,
                           'def_text': def_text, 'croped_text': word + ': ' + d}
                    result.append(res)
                    break

    return JsonResponse({'result': result})





def GetKeywordsDefinitionByDocumentId(request, document_id, word):
    keyword_result = ExtractedKeywords.objects.get(
        word=word, definition_id__document_id__id=document_id)
    keyword_information = {}

    keyword_information['doc_id'] = keyword_result.definition_id.document_id.id
    keyword_information['doc_name'] = keyword_result.definition_id.document_id.name
    def_text = keyword_result.definition_id.text

    # preprocessing
    normalizer = Normalizer()

    list_sent = def_text.split("\n")
    keyList = [re.sub(r'\t', '', i[:i.find(":")])
               for i in list_sent if i.find(":") > -1]
    defList = [re.sub(r'\t', '', i[i.find(":") + 1:])
               for i in list_sent if i.find(":") > -1]

    for kw, d in zip(keyList, defList):
        kw = normalizer.normalize(kw)

        # Cleaning
        ignoreList = ["!", "@", "$", "%", "^", "&", "*", "(", ")", "_", "+", "-", "/", "*", "'", "،", "؛", ",",
                      ""
                      "{", "}", "[", "]", "«", "»", "<", ">", ".", "?", "؟", "\n", "\t", '"',
                      '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۰', "٫",
                      '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '\u200f']
        for item in ignoreList:
            kw = kw.replace(item, " ")

        kw = [word for word in kw.split(" ") if word != ""]

        alphabet = ["الف", "ب", "پ", "ت", "ث", "ج", "چ", "ح", "خ", "د", "ذ", "ر", "ز", "ژ", "س", "ش", "ص", "ض",
                    "ط", "ظ", "ع", "غ", "ف", "ق", "ک", "گ", "ل", "م", "ن", "و", "ه", "ی", "ا", "آ"]

        if len(kw) > 0:
            if kw[0] in alphabet and " ".join(kw[1:]) == word:
                keyword_information['croped_text'] = word + ': ' + d
                break

    return JsonResponse({'keyword_information': keyword_information})




def SearchDocumentsDefinitionByCountryId(request, country_id, subject_ids):
    subject_ids = subject_ids.split("_")
    subject_ids = [int(i) for i in subject_ids]

    if 0 not in subject_ids:
        keywords = ExtractedKeywords.objects.filter(definition_id__document_id__country_id=country_id,
                                                    definition_id__document_id__subject_id__in=subject_ids).exclude(
            word="")
    else:
        keywords = ExtractedKeywords.objects.filter(
            definition_id__document_id__country_id=country_id).exclude(word="")

    keywords_information = {}

    for key in keywords:
        keyword = key.word
        doc_id = key.definition_id.document_id.id
        doc_name = key.definition_id.document_id.name
        doc_info = {'id': doc_id, 'name': doc_name}

        if keyword not in keywords_information:
            keywords_information[keyword] = [doc_info]
        else:
            document_list = keywords_information[keyword]
            document_list.append(doc_info)
            keywords_information[keyword] = document_list
    return JsonResponse({'keywords_information': keywords_information})


# Window unit
def searchDocumentsByWindowUnit(request, country_id):
    documents_information_result = []

    paragraphs_doc_ids = DocumentParagraphs.objects. \
        filter(document_id__country_id__id=country_id,
               text__icontains='پنجره واحد').values('document_id')

    paragraph_texts = DocumentParagraphs.objects. \
        filter(document_id__country_id__id=country_id,
               text__icontains='پنجره واحد').values('text')

    documents_information = Document.objects.filter(id__in=paragraphs_doc_ids)
    unique_documents = []

    for res in documents_information:
        res_id = int(res.id)
        if res_id not in unique_documents:
            unique_documents.append(res_id)
            document_full_info = GetDocumentById_Local(res_id)
            documents_information_result.append(document_full_info)

    bigram_dict = {}
    trigram_dict = {}
    for res in paragraph_texts:
        splitted_text = res['text'].split(' ')
        for i, word in enumerate(splitted_text):
            if word == 'پنجره' and splitted_text[i + 1] == 'واحد' and len(splitted_text) > i + 4:
                trigram = splitted_text[i + 2] + ' ' + \
                          splitted_text[i + 3] + ' ' + splitted_text[i + 4]
                bigram = splitted_text[i + 2] + ' ' + splitted_text[i + 3]
                if trigram in trigram_dict:
                    trigram_dict[trigram] += 1
                else:
                    trigram_dict[trigram] = 1
                if bigram in bigram_dict:
                    bigram_dict[bigram] += 1
                else:
                    bigram_dict[bigram] = 1

    trigram_chart_data = {}
    i = 1
    for key, value in trigram_dict.items():
        trigram_chart_data[i] = {'name': key, 'count': value}
        i += 1

    bigram_chart_data = {}
    i = 1
    for key, value in bigram_dict.items():
        bigram_chart_data[i] = {'name': key, 'count': value}
        i += 1

    return JsonResponse({
        "documents_information_result": documents_information_result,
        "bigram_chart_data": bigram_chart_data,
        "trigram_chart_data": trigram_chart_data,
    })


def GetWindowUnitParagraphsDetails(request, document_id):
    document_paragraphs = DocumentParagraphs.objects.filter(
        document_id=document_id, text__icontains='پنجره واحد').order_by('number')
    document_paragraphs_result = []
    for res in document_paragraphs:
        document_paragraphs_result.append(
            {'text': res.text, 'number': res.number, 'id': res.id})
    document_name = Document.objects.get(id=document_id).name
    return JsonResponse({"document_paragraphs_result": document_paragraphs_result, 'document_name': document_name})


def GetParagraphReferences(request, paragraph_id):
    temp = ReferencesParagraphs.objects.filter(
        paragraph_id=paragraph_id).values('document_id__name', 'document_id__id')
    paragraph_references = []
    for paragraph_reference in temp:
        references_info = {}
        references_info['doc_id'] = paragraph_reference['document_id__id']
        references_info['doc_name'] = paragraph_reference['document_id__name']

        paragraph_references.append(references_info)
    return JsonResponse({"references": paragraph_references})


def GetParagraphDefinitions(request, document_id, paragraph_id):
    paragraph_text = DocumentParagraphs.objects.get(id=paragraph_id).text
    extracted_keywords = ExtractedKeywords.objects.filter(
        definition_id__document_id=document_id).values('word', 'definition_id__text')
    paragraph_definitions = []
    for keyword in extracted_keywords:
        if keyword['word'] in paragraph_text:
            definition_text = keyword['definition_id__text']
            definition_text = definition_text.split('\n')
            paragraph_definitions = paragraph_definitions + \
                                    [d for d in definition_text if keyword['word'] in d]

    return JsonResponse({"definitions": paragraph_definitions})


def GetCollectiveActorsParagraphsDetails(request, document_id, collective_actor_name):
    collective_actors_list = [collective_actor_name]

    pattern_keyword_list = ['متشکل از', 'مرکب از', 'متشکل‌از', 'مرکب‌از']

    document_paragraphs_result = {}

    for collective_actors in collective_actors_list:
        collective_paragraphs_list = []

        collective_patterns = [(collective_actors + 'ی' + ' ' + pattern_kw) for pattern_kw in pattern_keyword_list]

        if collective_actors == 'کمیته':
            collective_patterns = [(collective_actors + ' ای' + ' ' + pattern_kw) for pattern_kw in
                                   pattern_keyword_list]
            collective_patterns += [(collective_actors + '‌ای' + ' ' + pattern_kw) for pattern_kw in
                                    pattern_keyword_list]

        collective_paragraphs = DocumentParagraphs.objects.filter(
            reduce(operator.or_, (Q(text__icontains=kw) for kw in collective_patterns)),
            document_id=document_id,
        )

        for paragraph in collective_paragraphs:
            collective_paragraphs_list.append(paragraph.text)

        document_paragraphs_result[collective_actors] = collective_paragraphs_list

    document_name = Document.objects.get(id=document_id).name

    return JsonResponse({"document_paragraphs_result": document_paragraphs_result, 'document_name': document_name})


def GetCollectiveActorsParagraphsDetails2(request, document_id, collectives_id, category_id, actors_id, membership_type,
                                          keywords_text):
    collectives_id = collectives_id.split("__")
    actors_id = actors_id.split("__")
    document_name = Document.objects.get(id=document_id).name

    doc_paragraphs = DocumentCollectiveMembers.objects.filter(
        document_id__id=document_id,
        members_count__gt=0)

    if '0' not in collectives_id:
        doc_paragraphs = doc_paragraphs.filter(collective_actor_id__id__in=collectives_id)

    # Filter by keywords
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')
        doc_paragraphs = doc_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_id__text__icontains=' ' + kw) for kw in keywords_list)))

    document_paragraphs_result = {}

    selected_actor_ids = []
    selected_actors = []

    if '0' not in actors_id:
        selected_actors = Actor.objects.filter(id__in=actors_id)
    else:
        if category_id != 0:
            selected_actors = Actor.objects.filter(actor_category_id__id=category_id)

    for actor in selected_actors:
        selected_actor_ids.append(actor.id)

    if len(selected_actor_ids) > 0:
        doc_paragraphs = doc_paragraphs.filter(has_next_paragraph_members=False)

    for res in doc_paragraphs:

        paragraph_id = res.paragraph_id.id
        paragraph_text = res.paragraph_id.text
        para_collective_info = res.members
        collective_name = res.collective_actor_id.name

        has_next_paragraph_members = res.has_next_paragraph_members
        next_paragraphs = []

        if has_next_paragraph_members:
            next_paragraphs = res.next_paragraphs
            next_paragraphs = next_paragraphs.split('\n')

        paragraph_info = {}

        for member_id in para_collective_info:
            if len(selected_actor_ids) > 0:
                if int(member_id) in selected_actor_ids:
                    para_collective_info[member_id]['selected'] = True
                else:
                    para_collective_info[member_id]['selected'] = False
            else:
                para_collective_info[member_id]['selected'] = True

        if len(selected_actor_ids) > 0:
            members_id = [int(member_id) for member_id in para_collective_info.keys() if
                          (not has_next_paragraph_members)]

            OR_membership_condition = (membership_type == 'OR' and any(
                int(member_id) in selected_actor_ids for member_id in para_collective_info))
            And_membership_condition = (membership_type == 'And' and all(
                selected_actor_id in members_id for selected_actor_id in selected_actor_ids))

            if OR_membership_condition or And_membership_condition:
                paragraph_info = {
                    'duties': res.obligation.split('\n') if res.obligation else [],
                    'text': paragraph_text,
                    'collective_name': collective_name,
                    'collective_members': para_collective_info,
                    'has_next_paragraph_members': has_next_paragraph_members,
                    'next_paragraphs': next_paragraphs
                }

                document_paragraphs_result[paragraph_id] = paragraph_info
        else:
            if membership_type == 'OR':
                paragraph_info = {
                    'duties': res.obligation.split('\n') if res.obligation else [],
                    'text': paragraph_text,
                    'collective_name': collective_name,
                    'collective_members': para_collective_info,
                    'has_next_paragraph_members': has_next_paragraph_members,
                    'next_paragraphs': next_paragraphs
                }
                document_paragraphs_result[paragraph_id] = paragraph_info

    return JsonResponse({"document_paragraphs_result": document_paragraphs_result, 'document_name': document_name})


def searchDocumentsByWindowUnitKeyword(request, country_id, keyword):
    paragraphs_information_dict = {}

    keyword_paragraphs = DocumentParagraphs.objects. \
        filter(document_id__country_id__id=country_id,
               text__icontains='پنجره واحد' + ' ' + keyword)

    for paragraph in keyword_paragraphs:
        paragraph_info = {}
        doc_id = paragraph.document_id.id

        paragraph_info['doc_id'] = paragraph.document_id.id
        paragraph_info['doc_name'] = paragraph.document_id.name
        paragraph_info['text'] = paragraph.text

        if doc_id not in paragraphs_information_dict:
            paragraphs_information_dict[doc_id] = [paragraph_info]
        else:
            paragraphs_list = paragraphs_information_dict[doc_id]
            paragraphs_list.append(paragraph_info)
            paragraphs_information_dict[doc_id] = paragraphs_list

    return JsonResponse({
        "paragraphs_information_dict": paragraphs_information_dict})








def GetGeneralDefinitionsByCountry(request, country_id, type, curr_page, text="empty"):
    #     # preprocess and split search text
    #     text = arabic_preprocessing(text).replace("  ", " ")
    search_result = SearchGeneralDefinitions_ES(request, country_id, type, 0, curr_page, text)
    general_definitions = search_result["result"]
    total_hits = search_result["total_hits"]
    curr_page = search_result["curr_page"]
    result = []
    related_docs = {}
    Nodes_data = []
    Edges_data = []
    added_nodes = set()
    country_document_actors = DocumentActor.objects.filter(document_id__country_id__id=country_id)
    for general_definition in general_definitions:
        general_definition = general_definition["_source"]
        keyword = general_definition["keyword"]
        definition = general_definition["text"]
        is_abbreviation = general_definition["is_abbreviation"]
        document_id = general_definition["document_id"]
        document_name = general_definition["document_name"]
        document_year = general_definition["document_approval_date"][0:4]
        document_subject = general_definition["document_subject_name"]
        document_approval_reference = general_definition["document_approval_reference_name"]
        document_level = general_definition["document_level_name"]

        result.append(
            {'word': keyword, 'definition': definition, 'is_abbreviation': is_abbreviation, 'document_id': document_id,
             'document_name': document_name})
        if keyword not in related_docs:
            related_docs[keyword] = [
                {'definition': definition, 'is_abbreviation': is_abbreviation, 'document_id': document_id,
                 'document_name': document_name,
                 'document_year': document_year, 'document_subject': document_subject,
                 'document_approval_reference': document_approval_reference, 'document_level': document_level}]
        else:
            related_docs[keyword].append(
                {'definition': definition, 'is_abbreviation': is_abbreviation, 'document_id': document_id,
                 'document_name': document_name,
                 'document_year': document_year, 'document_subject': document_subject,
                 'document_approval_reference': document_approval_reference, 'document_level': document_level})

        word_id = keyword  # + "_" + str(document_id) + "_" + str(is_abbreviation) + "_" + str(definition)
        word_node = {"id": str(word_id), "name": keyword, "type_name": "keyword", "style": {"fill": "blue"}}
        if word_id not in added_nodes:
            Nodes_data.append(word_node)
            added_nodes.add(word_id)

        keyword_document_actors = country_document_actors.filter(document_id__id=document_id)
        for keyword_document_actor in keyword_document_actors:
            actor_id = keyword_document_actor.actor_id.id
            actor_name = keyword_document_actor.actor_id.name
            actor_type = keyword_document_actor.actor_type_id.name
            actor_node = {"id": str(actor_id), "name": actor_name, "type_name": "actor", "style": {"fill": "red"}}
            if actor_id not in added_nodes:
                Nodes_data.append(actor_node)
                added_nodes.add(actor_id)

            edge_obj = {"source": str(word_id), "source_name": keyword, "target": str(actor_id),
                        "target_name": actor_name, "document_name": document_name, "document_id": document_id,
                        "type": actor_type}  # "weight": weight
            Edges_data.append(edge_obj)

    return JsonResponse(
        {'result': result, 'related_docs': related_docs, 'Nodes_data': Nodes_data, "Edges_data": Edges_data,
         "total_hits": total_hits, "curr_page": curr_page})


def SearchGeneralDefinitions_ES(request, country_id, type, is_term, curr_page, text="empty"):
    fields = [type]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True
    res_query["bool"]["must"] = []

    if not all(field == 'all' for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_definition_fields(res_query, type)

    if text != "empty":
        if (is_term == 1):
            res_query = exact_search_text(res_query, 'keyword-term', text, ALL_FIELDS)
        elif (is_term == 0):
            res_query = exact_search_text(res_query, 'keyword', text, ALL_FIELDS)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentGeneralDefinition.__name__)

    # ---------------------- Get Chart Data -------------------------
    # res_agg = {
    # "approval-ref-agg": {
    #     "terms": {
    #         "field": "approval_reference_name.keyword",
    #         "size": bucket_size
    #         }
    #     }
    # }

    from_value = (curr_page - 1) * search_result_size

    response = client.search(index=index_name,
                             _source_includes=['def_id', 'document_id', 'document_name', 'keyword', 'is_abbreviation',
                                               'text', 'document_approval_date', 'document_approval_reference_name',
                                               'document_level_name', 'document_subject_name'],
                             request_timeout=40,
                             query=res_query,
                             # aggregations = res_agg,
                             from_=from_value,
                             size=search_result_size  # 100
                             )

    result = response['hits']['hits']
    total_hits = response['hits']['total']['value']
    # aggregations = response['aggregations']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    # return JsonResponse({
    #     "result":result,
    #     'total_hits':total_hits
    # })
    return {
        "result": result,
        'total_hits': total_hits,
        "curr_page": curr_page,
        #    'aggregations':aggregations
    }

    # actors_chart_dic = {}
    # doc_ids = []
    # for word in related_docs:
    #     for doc_json in related_docs[word]:
    #         doc_ids.append(doc_json['document_id'])
    #     word1 = word + ":"
    #     # word2 = word + " " + ":"
    #     # words = word.split(" ")
    #     # words = [":"]
    #     words = [word]
    #     # words = [word1]
    #     # words = []
    #     actors_chart_data = getActorsChartData(words, doc_ids)
    #     if len(actors_chart_data) < 1:
    #         temp = {'sum_columns':0, 'column_1':0, 'column_2':0, 'column_3':0}
    #         entropy_dict, parallelism_dict, mean_dict, std_dict, normal_entropy_dict = temp, \
    #                                                                                 {'sum_columns':'صفر', 'column_1':'صفر', 'column_2':'صفر', 'column_3':'صفر'},\
    #                                                                                 temp, temp, temp
    #     else:
    #         entropy_dict, parallelism_dict, mean_dict, std_dict, normal_entropy_dict = chart_entropy(actors_chart_data)

    #     actors_chart_dic[word] = {
    #                         'actors_chart_data': actors_chart_data,
    #                         'entropy_dict': entropy_dict,
    #                         'parallelism_dict': parallelism_dict,
    #                         'mean_dict': mean_dict,
    #                         'std_dict': std_dict,
    #                         'normal_entropy_dict': normal_entropy_dict,
    #                         'column_1': 'salahiat',
    #                         'column_2': 'hamkaran',
    #                         'column_3': 'motevalian',
    #                         }
    # return JsonResponse({'result': result, 'related_docs':related_docs, 'actors_chart_dic':actors_chart_dic})


def GetAllKeywords(request):
    res = DocumentGeneralDefinition.objects.all().values("keyword").distinct()
    result = []
    for r in res:
        result.append(r["keyword"])
        # result.append(r)
    return JsonResponse({'result': result})


def GetKeywordsActorsGraphData(request, country_id, type, text="empty", curr_page=1):
    search_result = SearchGeneralDefinitions_ES(request, country_id, type, 0, curr_page, text)
    general_definitions = search_result["result"]
    Nodes_data = []
    Edges_data = []
    added_nodes = set()

    country_document_actors = DocumentActor.objects.filter(document_id__country_id__id=country_id)
    for general_definition in general_definitions:
        general_definition = general_definition["_source"]
        keyword = general_definition["keyword"]
        document_id = general_definition["document_id"]
        document_name = general_definition["document_name"]

        word_id = keyword  # + "_" + str(document_id) + "_" + str(is_abbreviation) + "_" + str(definition)
        word_node = {"id": str(word_id), "name": keyword, "type_name": "keyword", "style": {"fill": "blue"}}
        if word_id not in added_nodes:
            Nodes_data.append(word_node)
            added_nodes.add(word_id)

        keyword_document_actors = country_document_actors.filter(document_id__id=document_id)
        for keyword_document_actor in keyword_document_actors:
            actor_id = keyword_document_actor.actor_id.id
            actor_name = keyword_document_actor.actor_id.name
            actor_type = keyword_document_actor.actor_type_id.name
            actor_node = {"id": str(actor_id), "name": actor_name, "type_name": "actor", "style": {"fill": "red"}}
            if actor_id not in added_nodes:
                Nodes_data.append(actor_node)
                added_nodes.add(actor_id)

            edge_obj = {"source": str(word_id), "source_name": keyword, "target": str(actor_id),
                        "target_name": actor_name, "document_name": document_name, "document_id": document_id,
                        "type": actor_type}  # "weight": weight
            Edges_data.append(edge_obj)

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})


def GetKeywordActorsGraphData(request, country_id, type, text, curr_page=1):
    search_result = SearchGeneralDefinitions_ES(request, country_id, type, 1, curr_page, text)
    general_definitions = search_result["result"]
    Nodes_data = []
    Edges_data = []
    added_nodes = set()

    country_document_actors = DocumentActor.objects.filter(document_id__country_id__id=country_id)
    for general_definition in general_definitions:
        general_definition = general_definition["_source"]
        keyword = general_definition["keyword"]
        # definition = general_definition["text"]
        # is_abbreviation = general_definition["is_abbreviation"]
        document_id = general_definition["document_id"]
        document_name = general_definition["document_name"]

        word_id = keyword  # + "_" + str(document_id) + "_" + str(is_abbreviation) + "_" + str(definition)
        word_node = {"id": str(word_id), "name": keyword, "type_name": "keyword", "style": {"fill": "blue"}}
        if word_id not in added_nodes:
            Nodes_data.append(word_node)
            added_nodes.add(word_id)

        keyword_document_actors = country_document_actors.filter(document_id__id=document_id)
        for keyword_document_actor in keyword_document_actors:
            actor_id = keyword_document_actor.actor_id.id
            actor_name = keyword_document_actor.actor_id.name
            actor_type = keyword_document_actor.actor_type_id.name
            actor_node = {"id": str(actor_id), "name": actor_name, "type_name": "actor", "style": {"fill": "red"}}
            if actor_id not in added_nodes:
                Nodes_data.append(actor_node)
                added_nodes.add(actor_id)

            edge_obj = {"source": str(word_id), "source_name": keyword, "target": str(actor_id),
                        "target_name": actor_name, "document_name": document_name, "document_id": document_id,
                        "type": actor_type}  # "weight": weight
            Edges_data.append(edge_obj)

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})









# Official references
def searchDocumentsByOfficialReference(request, country_id, subjects_id):
    documents_information_dict = {}
    subjects_id = subjects_id.split("__")

    doc_paragraphs = DocumentParagraphs.objects. \
        filter(document_id__country_id__id=country_id,
               text__icontains='مرجع رسمی')

    if '0' not in subjects_id:
        doc_paragraphs = DocumentParagraphs.objects. \
            filter(document_id__country_id__id=country_id,
                   document_id__subject_id__id__in=subjects_id,
                   text__icontains='مرجع رسمی')

    # Get actor list
    actorsList = []
    actors = Actor.objects.all().values('name')
    for actor in actors:
        actorsList.append(actor['name'])

    for paragraph in doc_paragraphs:
        doc_id = paragraph.document_id.id
        doc_name = paragraph.document_id.name

        doc_info = {}
        document_information = GetDocumentById_Local(doc_id)
        doc_info['name'] = doc_name
        doc_info['subject'] = document_information["subject"]
        doc_info['approval_reference'] = document_information["approval_reference"]
        doc_info['approval_date'] = document_information["approval_date"]

        paragraph_text = paragraph.text
        paragraph_actor = ''

        pattern_keyword_index = paragraph_text.find('مرجع رسمی')
        start_index = pattern_keyword_index + len('مرجع رسمی') + 1
        highlighted_flag = False
        for actor in actorsList:
            actor_index = paragraph_text.find(actor)

            actor_without_prefix = actor.replace('وزارت ', '')
            actor_without_prefix_index = paragraph_text.find(
                actor_without_prefix)
            actor_distance_to_keyword = math.fabs(start_index - actor_index)
            actor_without_prefix_distance_to_keyword = math.fabs(
                start_index - actor_without_prefix_index)

            if actor_distance_to_keyword < 60 or actor_without_prefix_distance_to_keyword < 60:
                highlighted_flag = True
                if actor in paragraph_text or actor_without_prefix in paragraph_text:
                    paragraph_actor = actor

        #  Detect actors before ":"
        if (highlighted_flag == False):
            two_point_index = paragraph_text.find(':')
            if (two_point_index != -1):
                for i in range(two_point_index, 0, -1):
                    if (paragraph_text[i] == 'ـ'):
                        detected_actor = paragraph_text[i + 1:two_point_index]
                        paragraph_actor = detected_actor
                        highlighted_flag = True
                        break

        # Detect actors existed before pattern keyword
        if (highlighted_flag == False):
            pattern_keyword_index = paragraph_text.find('مرجع رسمی')
            if (pattern_keyword_index != -1):
                for i in range(pattern_keyword_index, 0, -1):
                    if (paragraph_text[i] == '،' or paragraph_text[i] == '-'):
                        cropped_text = paragraph_text[i: pattern_keyword_index - 1]
                        terms = cropped_text.split(' ')
                        if (len(terms) <= 3):
                            detected_actor = terms[1]
                            paragraph_actor = detected_actor
                            highlighted_flag = True
                            break

        if doc_id not in documents_information_dict:
            doc_info['actors'] = [paragraph_actor]
            documents_information_dict[doc_id] = doc_info
        else:
            doc_info = documents_information_dict[doc_id]
            doc_actors = doc_info['actors']
            if paragraph_actor not in doc_actors:
                doc_actors.append(paragraph_actor)
                doc_info['actors'] = doc_actors
                documents_information_dict[doc_id] = doc_info

    return JsonResponse({
        "documents_information_dict": documents_information_dict})


def GetOfficialReferencesParagraphs_Detail_Modal(request, document_id):
    document_paragraphs_list = []

    doc_paragraphs = DocumentParagraphs.objects. \
        filter(document_id__id=document_id, text__icontains='مرجع رسمی')

    for paragraph in doc_paragraphs:
        paragraph_text = paragraph.text
        document_paragraphs_list.append(paragraph_text)

    document_name = GetDocumentById_Local(document_id)['name']

    return JsonResponse({
        "document_paragraphs_list": document_paragraphs_list, 'document_name': document_name})


# ##################### General views ##############################


# documents information table view
def searchDocumentsBy__keyword__(request, panel_name, country_id, subjects):
    documents_information_list = []

    subjects_id = subjects.split("__")

    result_docs = CUBE_Template_TableData.objects.filter(country_id=country_id,
                                                         panel_id__panel_name=panel_name)

    if "0" in subjects_id:
        result_docs = result_docs.filter(subject_name='همه')

    else:
        selected_subject_names = Subject.objects.filter(id__in=subjects_id).values('name').distinct()
        result_docs = result_docs.filter(subject_name__in=selected_subject_names)

    for res in result_docs:
        documents_information_list += res.table_data['data']

    sorted_documents_information_list = sorted(documents_information_list, reverse=True,
                                               key=lambda d: d['keywords_count'])

    # Edit index number
    for i in range(0, len(sorted_documents_information_list)):
        sorted_documents_information_list[i]['id'] = i + 1

    return JsonResponse({"documents_information_list": sorted_documents_information_list})


# generate charts data
def Generate__keyword__ChartsData(request, panel_name, country_id, subjects):
    subjects_id = subjects.split("__")

    result_data = CUBE_Template_ChartData.objects.filter(country_id=country_id,
                                                         panel_id__panel_name=panel_name)

    if "0" in subjects_id:
        result_data = result_data.filter(subject_name='همه')

    else:
        selected_subject_names = Subject.objects.filter(id__in=subjects_id).values('name').distinct()
        result_data = result_data.filter(subject_name__in=selected_subject_names)

    # ---------- Generate Data -------------

    subject_data = []
    level_data = []
    approval_year_data = []
    approval_references_data = []
    type_data = []
    actors_data = []

    if len(subjects_id) == 1:

        for res in result_data:
            subject_data = res.subject_chart_data['data']
            approval_references_data = res.approval_reference_chart_data['data']
            level_data = res.level_chart_data['data']
            approval_year_data = res.approval_year_chart_data['data']
            type_data = res.type_chart_data['data']
            actors_data = res.actors_chart_data['data']

    else:

        final_subject_data = {"result": {}, "column_data": []}
        final_level_data = {"result": {}, "column_data": []}
        final_type_data = {"result": {}, "column_data": []}
        final_approval_ref_data = {"result": {}, "column_data": []}
        final_approval_year_data = {"result": {}, "column_data": []}

        final_chart_data = [
            final_subject_data,
            final_level_data,
            final_type_data,
            final_approval_ref_data,
            final_approval_year_data
        ]

        for res in result_data:
            subject_data = res.subject_chart_data['data']
            approval_references_data = res.approval_reference_chart_data['data']
            level_data = res.level_chart_data['data']
            approval_year_data = res.approval_year_chart_data['data']
            type_data = res.type_chart_data['data']

            # ------------------------------------------
            final_subject_data['column_data'] += subject_data
            final_level_data['column_data'] += level_data
            final_type_data['column_data'] += type_data
            final_approval_ref_data['column_data'] += approval_references_data
            final_approval_year_data['column_data'] += approval_year_data

        for chart in final_chart_data:
            column_data = chart['column_data']
            final_result = chart['result']

            for column in column_data:
                column_name = column[0]
                column_count = column[1]

                if column_name not in final_result:
                    final_result[column_name] = column_count
                else:
                    final_result[column_name] += column_count

            chart_data_list = []
            for key, value in final_result.items():
                chart_data_list.append([key, value])

            chart['result'] = chart_data_list

        subject_data = final_chart_data[0]['result']
        level_data = final_chart_data[1]['result']
        type_data = final_chart_data[2]['result']
        approval_references_data = final_chart_data[3]['result']
        approval_year_data = final_chart_data[4]['result']

        # ---------------- actors chart data ------------------------------------
        final_actors_data = {"result": {}, "column_data": []}

        for res in result_data:
            actors_data = res.actors_chart_data['data']
            final_actors_data['column_data'] += actors_data

        final_result = final_actors_data['result']
        actors_column_data = final_actors_data['column_data']

        for column in actors_column_data:
            column_name = column[0]
            motevali_count = column[1]
            hamkar_count = column[2]
            salahiat_count = column[3]

            if column_name not in final_result:
                final_result[column_name] = {
                    'motevali': motevali_count,
                    'hamkar': hamkar_count,
                    'salahiat': salahiat_count
                }
            else:
                final_result[column_name]['motevali'] += motevali_count
                final_result[column_name]['hamkar'] += hamkar_count
                final_result[column_name]['salahiat'] += salahiat_count

        actors_data_list = []
        for actor_name, role_count in final_result.items():
            actors_data_list.append(
                [
                    actor_name,
                    role_count['motevali'],
                    role_count['hamkar'],
                    role_count['salahiat'],
                ])

        actors_data = actors_data_list

    print(subject_data)

    return JsonResponse({'subject_chart_data': subject_data,
                         'approval_references_chart_data': approval_references_data,
                         'level_chart_data': level_data,
                         'approval_year_chart_data': approval_year_data,
                         'type_chart_data': type_data,
                         'actors_chart_data': actors_data,
                         })


# document detail modal view
def Get__keyword__Paragraphs_Detail_Modal(request, document_id, keyword_list):
    keyword_list = keyword_list.split("_")

    document_paragraphs_result = {}

    doc_paragraphs = DocumentParagraphs.objects.filter(
        reduce(operator.or_, (Q(text__icontains=(kw)) for kw in keyword_list)),
        document_id=document_id
    ).values('id', 'text', 'number').order_by('number')

    for paragraph in doc_paragraphs:
        if paragraph['number'] not in document_paragraphs_result:
            paragraph_info = {}
            paragraph_info['id'] = paragraph['id']
            paragraph_info['text'] = paragraph['text']
            document_paragraphs_result[paragraph['number']] = paragraph_info

    document_paragraphs_result = dict(
        sorted(document_paragraphs_result.items(), key=lambda x: x[0]))

    document_name = Document.objects.get(id=document_id).name

    return JsonResponse({
        "document_paragraphs_result": list(document_paragraphs_result.values()), 'document_name': document_name})


# document detail modal view
def Get__Paragraphs_Detail_Modal(request, document_id):
    document_paragraphs_result = {}

    doc_paragraphs = DocumentParagraphs.objects.filter(document_id=document_id).values('id', 'text', 'number').order_by(
        'number')

    for paragraph in doc_paragraphs:
        if paragraph['number'] not in document_paragraphs_result:
            paragraph_info = {}
            paragraph_info['id'] = paragraph['id']
            paragraph_info['text'] = paragraph['text']
            document_paragraphs_result[paragraph['number']] = paragraph_info

    document_paragraphs_result = dict(
        sorted(document_paragraphs_result.items(), key=lambda x: x[0]))

    document_name = Document.objects.get(id=document_id).name

    return JsonResponse({
        "document_paragraphs_result": list(document_paragraphs_result.values()), 'document_name': document_name})


# chart colum modal
def GetPortalDocuments_ByColumn_Modal(request, panel_name, country_id, subjects, chart_type, column_name):
    subjects_id = subjects.split("__")
    document_list = []

    document_result = CUBE_Template_FullData.objects.filter(
        country_id=country_id,
        panel_id__panel_name=panel_name)

    if "0" not in subjects_id:
        document_result = document_result.filter(subject_id__id__in=subjects_id)

    if chart_type == 'subject_chart_data':
        document_result = document_result.filter(subject_name=column_name)

    if chart_type == 'level_chart_data':
        document_result = document_result.filter(level_name=column_name)

    if chart_type == 'type_chart_data':
        document_result = document_result.filter(type_name=column_name)

    if chart_type == 'approval_reference_chart_data':
        document_result = document_result.filter(approval_reference_name=column_name)

    if chart_type == 'approval_year_chart_data':
        document_result = document_result.filter(approval_date__icontains=column_name)

    for res in document_result:
        doc_info = {'document_id': res.document_id.id, 'document_name': res.document_name,
                    'subject_name': res.subject_name, 'type_name': res.type_name,
                    'level_name': res.level_name, 'approval_reference_name': res.approval_reference_name,
                    'approval_date': res.approval_date}
        document_list.append(doc_info)

    return JsonResponse({'document_list': document_list})


# actors chart column modal
def Get_Portal_ActorParagraphs_ByColumn_Modal(request, panel_name, country_id, subjects_id, actor_name, role_name,
                                              keywords_text):
    subject_list = subjects_id.split('__')

    doc_list = CUBE_Template_FullData.objects.filter(
        country_id__id=country_id, panel_id__panel_name=panel_name).values('document_id')

    if "0" not in subject_list:
        doc_list = doc_list.filter(
            subject_id__id__in=subject_list).values('document_id')

    doc_paragraphs = DocumentActor.objects.filter(
        document_id__in=doc_list,
        actor_id__name=actor_name, actor_type_id__name=role_name)

    result = []
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')

        result = doc_paragraphs.filter(reduce(
            operator.or_, (Q(paragraph_id__text__icontains=kw) for kw in keywords_list)))

    else:
        result = doc_paragraphs

    actor_paragraphs_result = {}
    for res in result:

        paragraph_id = res.paragraph_id.id
        document_id = res.document_id.id
        document_name = res.document_id.name
        paragraph_text = res.paragraph_id.text
        paragraph_actor_role = res.actor_type_id.name
        paragraph_actor_form = res.current_actor_form

        if document_id not in actor_paragraphs_result:
            actor_paragraphs_result[document_id] = {
                'document_id': document_id,
                'document_name': document_name,
                'unique_paragraphs': [paragraph_id],
                'paragraph_list': [{
                    'paragraph_text': paragraph_text,
                    'actor_form': paragraph_actor_form
                }]
            }
        else:
            doc_info = actor_paragraphs_result[document_id]

            if paragraph_id not in doc_info['unique_paragraphs']:
                para_info = {
                    'paragraph_text': paragraph_text,
                    'actor_form': paragraph_actor_form
                }

                doc_info['paragraph_list'].append(para_info)
                actor_paragraphs_result[document_id] = doc_info

    return JsonResponse({"actor_paragraphs_result": actor_paragraphs_result})


# ##################### --------------------------------- ##############################

# Actor panel

def GetActorCategoryList(request):
    ActorCategoryList = []

    category_list = ActorCategory.objects.all().values(
        'id', 'name').order_by("name").distinct()

    for category in category_list:
        res = {
            'id': category['id'],
            'category_name': category['name']
        }

        ActorCategoryList.append(res)

    return JsonResponse({"ActorCategoryList": ActorCategoryList})


def GetActorAreaList(request):
    ActorAreaList = []

    area_list = ActorArea.objects.all().values(
        'id', 'name').order_by("name").distinct()

    for area in area_list:
        res = {
            'id': area['id'],
            'area_name': area['name']
        }

        ActorAreaList.append(res)

    return JsonResponse({"ActorAreaList": ActorAreaList})


def GetActorsByCategoryId(reauest, category_id):
    ActorsList = []
    actors = []

    if category_id == 0:
        actors = Actor.objects.all().values(
            'id', 'name').distinct().order_by('name')
    else:
        actors = Actor.objects.filter(actor_category_id__id=category_id).values(
            'id', 'name').distinct().order_by('name')

    for actor in actors:
        res = {
            'id': actor['id'],
            'actor_name': actor['name']
        }

        ActorsList.append(res)

    return JsonResponse({"ActorsList": ActorsList})


def GetActorsByAreaID(reauest, area_id):
    ActorsList = []

    actors = Actor.objects.all().values(
        'id', 'name').distinct().order_by('name')

    if area_id != 0:
        actors = Actor.objects.filter(area__id=area_id).values(
            'id', 'name').distinct().order_by('name')

    for actor in actors:
        res = {
            'id': actor['id'],
            'name': actor['name']
        }

        ActorsList.append(res)

    return JsonResponse({"ActorsList": ActorsList})


def GetSubAreasByAreaId(reauest, area_id):
    SubAreaList = []

    sub_area_list = ActorSubArea.objects.all().values(
        'id', 'name').distinct().order_by('name')

    if area_id != 0:
        sub_area_list = sub_area_list.filter(main_area__id=area_id).values(
            'id', 'name').distinct().order_by('name')

    for sub_area in sub_area_list:
        res = {
            'id': sub_area['id'],
            'name': sub_area['name']
        }

        SubAreaList.append(res)

    return JsonResponse({"SubAreaList": SubAreaList})


def GetActorRoleList(request):
    ActorRoleList = []

    role_list = ActorType.objects.all().values(
        'id', 'name').order_by("name").distinct()

    for role in role_list:
        res = {
            'id': role['id'],
            'role_name': role['name']
        }

        ActorRoleList.append(res)

    return JsonResponse({"ActorRoleList": ActorRoleList})


def SearchDocumentsByActorsKeywords(request, country_id, roles_id, area_id, actors_id, keywords_text):
    documents_information_dict = {}
    doc_paragraphs = []
    roles_id = roles_id.split("__")
    actors_id = actors_id.split('__')

    doc_paragraphs = DocumentActor.objects.filter(document_id__country_id__id=country_id)

    # Filter by roles
    if '0' not in roles_id:
        doc_paragraphs = doc_paragraphs.filter(actor_type_id__id__in=roles_id)

    # Filter by actors
    if '0' not in actors_id:
        doc_paragraphs = doc_paragraphs.filter(actor_id__id__in=actors_id)
    # Filter by category
    elif area_id != 0:
        doc_paragraphs = doc_paragraphs.filter(actor_id__area__id=area_id)

    # Filter by keywords
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')
        doc_paragraphs = doc_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_id__text__icontains=(kw + ' ')) for kw in keywords_list)))

    # Fill documents information dict
    for res in doc_paragraphs:

        doc_id = res.document_id.id
        doc_info = {}
        document_information = GetDocumentById_Local(doc_id)
        doc_info['id'] = doc_id
        doc_info['name'] = res.document_id.name
        doc_info['subject'] = document_information["subject"]
        doc_info['approval_reference'] = document_information["approval_reference"]
        doc_info['approval_date'] = document_information["approval_date"]
        doc_info['role_name'] = res.actor_type_id.name

        if doc_id not in documents_information_dict:

            actor_name = res.actor_id.name

            actor_name += ' (' + res.actor_type_id.name + ')'

            doc_info['actors'] = [actor_name]

            documents_information_dict[doc_id] = doc_info

        else:

            actor_name = res.actor_id.name

            doc_actors = documents_information_dict[doc_id]['actors']

            actor_name += ' (' + res.actor_type_id.name + ')'

            if actor_name not in doc_actors:
                doc_actors.append(actor_name)
                doc_info['actors'] = doc_actors
                documents_information_dict[doc_id] = doc_info

    return JsonResponse({"documents_information_dict": documents_information_dict,
                         "tools_distribution_data_dict": 'tools_distribution_data_dict'})


def SearchDocumentsByActorsKeywords_es(request, country_id, roles_id, area_id, actors_id, keywords_text, curr_page):
    roles_id = roles_id.split("__")
    actors_id = actors_id.split('__')

    res_query = {
        "bool": {
        }
    }

    res_query['bool']['filter'] = []
    res_query = filter_document_actor_fields(
        res_query,
        role_ids=roles_id,
        area_id=area_id,
        actor_ids=actors_id)

    if len(res_query['bool']['filter']) == 0:
        del res_query['bool']['filter']

    if keywords_text != "empty":
        res_query["bool"]["must"] = []
        res_query = filter_document_actor_text(res_query, keywords_text, 'filter' not in res_query['bool'])

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentActor.__name__)

    from_value = (curr_page - 1) * search_result_size

    res_agg = {
        "document-name-agg": {
            "multi_terms": {
                "terms": [{
                    "field": "document_name.keyword",
                },
                    {
                        "field": "document_id",
                    },
                    {
                        "field": "document_subject_name.keyword",
                    }
                ],
                "size": 5000
            },
            "aggs": {
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
            },
        },
    }

    response = client.search(index=index_name,
                             # _source_includes=['actor_id', "actor_name", 'actor_type_id','actor_type_name'],
                             _source_includes=[],
                             request_timeout=40,
                             query=res_query,
                             # aggregations=res_agg,
                             # from_=from_value,
                             # size=search_result_size
                             size=0,
                             # track_total_hits=True,
                             aggregations=res_agg,
                             )

    aggregations = response['aggregations']
    total_hits = len(aggregations['document-name-agg']['buckets'])
    # if total_hits == bucket_size:
    #     total_hits = client.count(body={
    #         "query":res_query
    #     },index=index_name,doc_type='_doc')['count']

    return JsonResponse({
        'total_hits': total_hits,
        "curr_page": curr_page,
        'aggregations': aggregations['document-name-agg']['buckets'][from_value:from_value + search_result_size]
    })


def GetCosineSimilarityActors_ByActorID(request, country_id, actor_id):
    similarity_result = {}
    table_result = []

    role_names = ['همه', 'متولی اجرا', 'همکار', 'دارای صلاحیت اختیاری']
    try:
        selected_actor = ActorTimeSeries.objects.get(
            country_id__id=country_id,
            actor_id__id=actor_id)
        # ---------------- Selected Actor Vector  --------------------
        for role_name in role_names:
            selected_actor_year_vector = selected_actor.time_series_data[role_name]
            selected_actor_values = list(selected_actor_year_vector.values())

            # ---------------- Selected Actor Vector  --------------------

            other_actors = ActorTimeSeries.objects.filter(
                country_id__id=country_id).exclude(actor_id__id=actor_id)

            for res in other_actors:
                actor_ID = res.actor_id.id
                actor_Name = res.actor_id.name

                role_year_vector = res.time_series_data[role_name]
                role_year_value = list(role_year_vector.values())

                cosine_sim = dot(selected_actor_values, role_year_value) / (
                        norm(selected_actor_values) * norm(role_year_value))
                cosine_sim = round(cosine_sim, 2)

                if actor_ID not in similarity_result:
                    similarity_result[actor_ID] = {
                        "actor_name": actor_Name,
                        role_name: cosine_sim if not math.isnan(cosine_sim) else '-'
                    }
                else:
                    similarity_result[actor_ID][role_name] = cosine_sim if not math.isnan(cosine_sim) else '-'

    except:
        pass
    i = 1
    host_url = urlparse(request.build_absolute_uri()).netloc

    for other_actor_id, actor_info in similarity_result.items():
        if any(type(actor_info[key]) is not str for key in actor_info if key != 'actor_name'):
            actor_link = 'http://' + str(host_url) + "/actors_information/?country_id=" + str(
                country_id) + "/?actor_id=" + str(other_actor_id)
            actor_tag = '<a  target="to_blank" href="' + actor_link + '">' + actor_info["actor_name"] + "</a>"

            function = "ComparisonFunction(" + str(country_id) + ",'" + str(actor_id) + "', '" + str(
                other_actor_id) + "', '" + str(actor_info["همه"]) + "')"
            detail_btn = '<button ' \
                         'type="button" ' \
                         'class="btn modal_btn" ' \
                         'data-bs-toggle="modal" ' \
                         'data-bs-target="#Correlation_Comparison_Modal" ' \
                         'onclick="' + function + '"' \
                                                  '>' + 'جزئیات' + '</button>'

            row = {
                "id": i,
                "actor_id": actor_id,
                "actor_name": actor_info["actor_name"],
                "actor_tag": actor_tag,
                "motevali_sim": actor_info["متولی اجرا"],
                "hamkar_sim": actor_info["همکار"],
                "salahiat_sim": actor_info["دارای صلاحیت اختیاری"],
                "total_sim": actor_info["همه"],
                "detail": detail_btn
            }

            table_result.append(row)
            i += 1

    sorted_table_result = sorted(table_result, key=lambda d: d['total_sim'], reverse=True)

    return JsonResponse({"table_result": sorted_table_result})


def GetCorrelatedActors_ByActorID(request, country_id, actor_id):
    correlation_result = {}
    table_result = []

    role_names = ['همه', 'متولی اجرا', 'همکار', 'دارای صلاحیت اختیاری']

    try:
        selected_actor = ActorTimeSeries.objects.get(
            country_id__id=country_id,
            actor_id__id=actor_id)

        for role_name in role_names:
            selected_actor_year_vector = selected_actor.time_series_data[role_name]
            selected_actor_year_count = pd.Series(list(selected_actor_year_vector.values()))

            # ---------------- Selected Actor Vector  --------------------

            selected_area = selected_actor.actor_id.area

            other_actors = ActorTimeSeries.objects.filter(
                country_id__id=country_id,
                actor_id__area=selected_area).exclude(actor_id__id=actor_id)

            for res in other_actors:
                actor_ID = res.actor_id.id
                actor_Name = res.actor_id.name

                role_year_vector = res.time_series_data[role_name]
                other_actor_year_count = pd.Series(list(role_year_vector.values()))
                correlation_value = round(selected_actor_year_count.corr(other_actor_year_count), 2)

                if actor_ID not in correlation_result:
                    correlation_result[actor_ID] = {
                        "actor_name": actor_Name,
                        role_name: correlation_value if not math.isnan(correlation_value) else '-'
                    }
                else:
                    correlation_result[actor_ID][role_name] = correlation_value if not math.isnan(
                        correlation_value) else '-'

    except:
        pass

    i = 1
    host_url = urlparse(request.build_absolute_uri()).netloc

    for other_actor_id, actor_info in correlation_result.items():
        if any(type(actor_info[key]) is not str for key in actor_info if key != 'actor_name'):
            actor_link = 'http://' + str(host_url) + "/actors_information/?country_id=" + str(
                country_id) + "/?actor_id=" + str(other_actor_id)
            actor_tag = '<a  target="to_blank" href="' + actor_link + '">' + actor_info["actor_name"] + "</a>"

            function = "ComparisonFunction(" + str(country_id) + ",'" + str(actor_id) + "', '" + str(
                other_actor_id) + "')"
            detail_btn = '<button ' \
                         'type="button" ' \
                         'class="btn modal_btn" ' \
                         'data-bs-toggle="modal" ' \
                         'data-bs-target="#Correlation_Comparison_Modal" ' \
                         'onclick="' + function + '"' \
                                                  '>' + 'جزئیات' + '</button>'

            row = {
                "id": i,
                "actor_id": actor_id,
                "actor_name": actor_info["actor_name"],
                "actor_tag": actor_tag,
                "motevali_corr": {
                    "options": {
                        "sortValue": (-2 if (actor_info["متولی اجرا"] == '-') else actor_info["متولی اجرا"])
                    },
                    "value": '<span >' + str(actor_info["متولی اجرا"]) + "</span>"
                },
                # "hamkar_corr":actor_info["همکار"],
                "hamkar_corr": {
                    "options": {
                        "sortValue": (-2 if (actor_info["همکار"] == '-') else actor_info["همکار"])
                    },
                    "value": '<span >' + str(actor_info["همکار"]) + "</span>"
                },
                # "salahiat_corr":actor_info["دارای صلاحیت اختیاری"],
                "salahiat_corr": {
                    "options": {
                        "sortValue": (
                            -2 if (actor_info["دارای صلاحیت اختیاری"] == '-') else actor_info["دارای صلاحیت اختیاری"])
                    },
                    "value": '<span >' + str(actor_info["دارای صلاحیت اختیاری"]) + "</span>"
                },
                "total_corr": actor_info["همه"],
                "detail": detail_btn
            }

            table_result.append(row)
            i += 1

    sorted_table_result = sorted(table_result, key=lambda d: d['total_corr'], reverse=True)

    return JsonResponse({"table_result": sorted_table_result})


def GetActorTimeSeries_ChartData_ByKeywords(request, country_id, roles_id, actor_id, keywords_text):
    years_information_dict = {}

    doc_paragraphs = []
    roles_id = roles_id.split("__")

    doc_paragraphs = DocumentActor.objects.filter(document_id__country_id__id=country_id)

    # Not Filter by roles

    doc_paragraphs = doc_paragraphs.filter(actor_id__id=actor_id)

    # Filter by keywords
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')
        doc_paragraphs = doc_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_id__text__icontains=kw + ' ') for kw in keywords_list)))

    # Exclude None date
    doc_paragraphs = doc_paragraphs.annotate(
        approval_date=F('document_id__approval_date')).exclude(
        approval_date__isnull=True)

    for res in doc_paragraphs:
        doc_approval_date = res.approval_date
        doc_year = int(doc_approval_date[:4])

        actor_role_name = res.actor_type_id.name
        actor_paragraph_id = res.paragraph_id.id

        if doc_year != None and doc_year not in years_information_dict:
            years_information_dict[doc_year] = {
                'doc_year': doc_year,
                'roles_info': {
                    'متولی اجرا': [],
                    'همکار': [],
                    'دارای صلاحیت اختیاری': []
                }

            }
            actor_roles_info = years_information_dict[doc_year]['roles_info']
            actor_roles_info[actor_role_name].append(actor_paragraph_id)
            years_information_dict[doc_year]['roles_info'] = actor_roles_info

        elif doc_year != None and doc_year in years_information_dict:
            actor_roles_info_2 = years_information_dict[doc_year]['roles_info']
            if actor_paragraph_id not in actor_roles_info_2[actor_role_name]:
                actor_roles_info_2[actor_role_name].append(actor_paragraph_id)
                years_information_dict[doc_year]['roles_info'] = actor_roles_info_2

    # Calculate role frequency of actors
    years_chart_data = []
    for doc_year in years_information_dict:
        motevali_count = len(years_information_dict[doc_year]['roles_info']['متولی اجرا'])
        hamkar_count = len(years_information_dict[doc_year]['roles_info']['همکار'])
        salahiat_count = len(years_information_dict[doc_year]['roles_info']['دارای صلاحیت اختیاری'])
        total_count = motevali_count + hamkar_count + salahiat_count
        column_data = [doc_year, motevali_count, hamkar_count, salahiat_count, total_count]
        years_chart_data.append(column_data)

    years_chart_data = sorted(years_chart_data, key=itemgetter(0), reverse=False)
    actor_name = Actor.objects.get(id=actor_id).name

    return JsonResponse({"years_chart_data": years_chart_data, 'actor_name': actor_name})


def GetActorTimeSeries_ChartData_ByKeywords_es(request, country_id, roles_id, actor_id, keywords_text):
    years_information_dict = {}

    res_query = {
        "bool": {
        }
    }

    res_query['bool']['filter'] = []
    res_query = filter_document_actor_fields(
        res_query,
        actor_id=actor_id)

    if len(res_query['bool']['filter']) == 0:
        del res_query['bool']['filter']

    if keywords_text != "empty":
        res_query["bool"]["must"] = []
        res_query = filter_document_actor_text(res_query, keywords_text, 'filter' not in res_query['bool'])

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentActor.__name__)

    response = client.search(index=index_name,
                             # _source_includes=['actor_id', "actor_name", 'actor_type_id','actor_type_name'],
                             _source_includes=[
                                 'document_approval_year',
                                 'actor_type_name',
                                 'paragraph_id',
                             ],
                             request_timeout=40,
                             query=res_query,
                             # aggregations=res_agg,
                             # from_=from_value,
                             size=5000
                             # size=0,
                             # track_total_hits=True,
                             # aggregations=res_agg,
                             )

    for res in response['hits']['hits']:
        doc_year = res["_source"]["document_approval_year"]
        # if doc_year == 0:
        #     continue

        actor_role_name = res["_source"]['actor_type_name']
        actor_paragraph_id = res["_source"]['paragraph_id']

        if doc_year not in years_information_dict:
            years_information_dict[doc_year] = {
                'doc_year': doc_year,
                'roles_info': {
                    'متولی اجرا': [],
                    'همکار': [],
                    'دارای صلاحیت اختیاری': []
                }

            }
            actor_roles_info = years_information_dict[doc_year]['roles_info']
            actor_roles_info[actor_role_name].append(actor_paragraph_id)
            years_information_dict[doc_year]['roles_info'] = actor_roles_info

        elif doc_year in years_information_dict:
            actor_roles_info_2 = years_information_dict[doc_year]['roles_info']
            if actor_paragraph_id not in actor_roles_info_2[actor_role_name]:
                actor_roles_info_2[actor_role_name].append(actor_paragraph_id)
                years_information_dict[doc_year]['roles_info'] = actor_roles_info_2

    # Calculate role frequency of actors
    years_chart_data = []
    for doc_year in years_information_dict:
        motevali_count = len(years_information_dict[doc_year]['roles_info']['متولی اجرا'])
        hamkar_count = len(years_information_dict[doc_year]['roles_info']['همکار'])
        salahiat_count = len(years_information_dict[doc_year]['roles_info']['دارای صلاحیت اختیاری'])
        total_count = motevali_count + hamkar_count + salahiat_count
        column_data = [doc_year, motevali_count, hamkar_count, salahiat_count, total_count]
        years_chart_data.append(column_data)

    years_chart_data = sorted(years_chart_data, key=itemgetter(0), reverse=False)
    if len(years_chart_data) > 0 and years_chart_data[0][0] == 0:
        years_chart_data[0][0] = 'نامشخص'
    actor_name = Actor.objects.get(id=actor_id).name

    return JsonResponse({"years_chart_data": years_chart_data,
                         'actor_name': actor_name,
                         'duty_num': len(response['hits']['hits'])})


def GetActorTimeSeries_ChartData(request, country_id, actor_id):
    years_chart_data = []
    lstm_chart_data = []

    try:
        actor_obj = ActorTimeSeries.objects.get(
            country_id__id=country_id,
            actor_id__id=actor_id)

        actor_time_data = actor_obj.time_series_data

        # Calculate role frequency of actors
        for year in actor_time_data['همه']:
            motevali_count = actor_time_data['متولی اجرا'][year]
            hamkar_count = actor_time_data['همکار'][year]
            salahiat_count = actor_time_data['دارای صلاحیت اختیاری'][year]
            total_count = actor_time_data['همه'][year]
            column_data = [int(year), motevali_count, hamkar_count, salahiat_count, total_count]

            years_chart_data.append(column_data)

        years_chart_data = sorted(years_chart_data, key=itemgetter(0), reverse=False)

        ARIMA_predictions, last_year = ARIMA_Prediction(years_chart_data)
        print(ARIMA_predictions)

    except:
        years_chart_data = []
        ARIMA_predictions, last_year = [], 1400

    try:
        actor_obj = ActorTimeSeries.objects.get(
            country_id__id=country_id,
            actor_id__id=actor_id)
        # ---------------- LSTM -----------------------------------------
        actor_lstm_time_data = LSTMPredictionData.objects.get(time_series_data__id=actor_obj.id).prediction_data

        for year in actor_lstm_time_data['همه']:
            total_count = actor_lstm_time_data['همه'][year]
            if total_count < 0:
                total_count = 0
            column_data = [int(year), 0, 0, 0, total_count]

            lstm_chart_data.append(column_data)
    except:
        pass

    actor_name = Actor.objects.get(id=actor_id).name

    return JsonResponse({"years_chart_data": years_chart_data, 'actor_name': actor_name,
                         'predictions': ARIMA_predictions, 'last_year': last_year,
                         'lstm_chart_data': lstm_chart_data})


def GetActorTimeSeries_Agile(request, count_year, type, country_id, area_id):
    actors = Actor.objects.all().distinct().order_by('name')

    if area_id != 0:
        actors = Actor.objects.filter(area__id=area_id).distinct().order_by('name')

    all_type = {
        1: 'همه',
        2: 'متولی اجرا',
        3: 'همکار',
        4: 'دارای صلاحیت اختیاری'
    }

    type = all_type[type]

    res = {'actors': []}

    for actor in actors:
        years_chart_data = []
        proposed_actors_list = []
        try:
            actor_obj = ActorTimeSeries.objects.get(actor_id__id=actor.id, country_id__id=country_id)
        except:
            continue
        if actor.area:
            proposed_actors = Actor.objects.filter(area=actor.area,
                                                   actor_category_id__name='وزارت').distinct().order_by('name')
            for proposed_actor in proposed_actors:
                if actor.id != proposed_actor.id:
                    proposed_actors_list.append(
                        {'id': proposed_actor.id, 'name': proposed_actor.name, 'country_id': country_id,
                         'actor_id': proposed_actor.id, })
        actor_time_data = actor_obj.time_series_data
        start_year = int(list(actor_time_data[type].keys())[0])
        end_year = None
        first_time_flag = False
        dis = True  # is in Inactivity period
        if not actor_time_data[type].get('1401'):
            actor_time_data[type]['1401'] = 1
        for year in actor_time_data[type]:
            count = actor_time_data[type][year]
            if count != 0:
                if dis:
                    end_year = int(year) - 1
                    if end_year - start_year >= count_year and first_time_flag:
                        years_chart_data.append({'start_year': start_year, 'end_year': end_year})
                    dis = False
                start_year = int(year) + 1
                first_time_flag = True
            else:
                dis = True
        if years_chart_data:
            years_chart_data = sorted(years_chart_data, key=itemgetter('start_year'), reverse=False)
            year_count = 0
            for y in years_chart_data:
                year_count += y['end_year'] - y['start_year']
            actor_name = Actor.objects.get(id=actor.id).name
            res['actors'].append(
                {'actor_name': actor_name, 'proposed_actors': proposed_actors_list, 'country_id': country_id,
                 'actor_id': actor.id, "years": years_chart_data, "year_count": year_count})

    return JsonResponse(res)


def ARIMA_Prediction(years_chart_data):
    last_year = 1400

    history_dict = {0: [], 1: [0], 2: [0], 3: [0], 4: [0]}

    for item in years_chart_data:
        for i, value in enumerate(item):
            history_dict[i].append(value)

    predictions = {i: [i] for i in range(last_year + 1, last_year + 3)}

    for i in range(1, 4):
        history = history_dict[i]
        if history != [0]:
            for year in range(last_year + 1, last_year + 3):
                model = ARIMA(history, order=(5, 1, 0))
                model_fit = model.fit()
                output = model_fit.forecast()
                yhat = round(output[0])

                # negative prediction -> 0: only in ui chart
                if yhat < 0:
                    predictions[year].append(0)
                else:
                    predictions[year].append(yhat)

                history.append(yhat)

    predictions = [i + [sum(i[1:])] for i in predictions.values()]

    return [predictions, last_year]


def GetActorYearParagraphs_Line_Modal(request, country_id, actor_name, actor_role_name, doc_year, keywords_text):
    doc_year = str(doc_year)

    res_paragraphs = DocumentActor.objects.filter(document_id__country_id__id=country_id)

    res_paragraphs = res_paragraphs.filter(actor_id__name=actor_name,
                                           document_id__approval_date__icontains=doc_year)

    if actor_role_name != 'برآیند نقش‌ها':
        res_paragraphs = res_paragraphs.filter(
            actor_type_id__name=actor_role_name,
        )

    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')

        res_paragraphs = res_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_id__text__icontains=kw + ' ') for kw in keywords_list))
        )

    year_paragraphs = {}
    for res in res_paragraphs:

        paragraph_id = res.paragraph_id.id
        document_id = res.document_id.id
        document_name = res.document_id.name
        paragraph_text = res.paragraph_id.text
        paragraph_actor_form = res.current_actor_form
        paragraph_actor_role = res.actor_type_id.name

        para_ref_to_general_def = res.ref_to_general_definition

        para_ref_to_general_def_text = ''
        if para_ref_to_general_def:
            para_ref_to_general_def_text = res.general_definition_id.text

        para_ref_to_paragraph = res.ref_to_paragraph
        para_ref_to_para_text = ''

        if para_ref_to_paragraph:
            para_ref_to_para_text = res.ref_paragraph_id.text

        is_ref_actor = (para_ref_to_general_def or para_ref_to_paragraph)

        ref_text = ''

        if para_ref_to_general_def:
            ref_text = para_ref_to_general_def_text
        elif para_ref_to_paragraph:
            ref_text = para_ref_to_para_text

        paragraph_info = {
            'document_id': document_id,
            'document_name': document_name,
            'text': paragraph_text,
            'actor_form': paragraph_actor_form,
            'actor_role': paragraph_actor_role,
            'is_ref_actor': is_ref_actor,
            'ref_text': ref_text
        }

        year_paragraphs[paragraph_id] = paragraph_info

    return JsonResponse({"year_paragraphs": year_paragraphs})


def GetActorYearParagraphs_Line_Modal_es(request, country_id, actor_name, actor_role_name, doc_year, keywords_text,
                                         curr_page):
    doc_year = int(doc_year)

    detail_result_size = 10
    res_query = {
        "bool": {
        }
    }

    res_query['bool']['filter'] = []
    res_query = filter_document_actor_fields(
        res_query,
        doc_year=doc_year,
        role_name=actor_role_name,
        actor_name=actor_name)

    if len(res_query['bool']['filter']) == 0:
        del res_query['bool']['filter']

    if keywords_text != "empty":
        res_query["bool"]["must"] = []
        res_query = filter_document_actor_text(res_query, keywords_text, 'filter' not in res_query['bool'])

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentActor.__name__)

    from_value = (curr_page - 1) * detail_result_size

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

    year_paragraphs = {}

    print(res_query)
    # print(response['hits']['hits'])

    for res in response['hits']['hits']:

        paragraph_id = res["_source"]["paragraph_id"]
        document_id = res["_source"]["document_id"]
        document_name = res["_source"]["document_name"]
        paragraph_text = res["_source"]["attachment"]['content'] if keywords_text == "empty" else \
            res["highlight"]["attachment.content"][0]
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
            'actor_role': paragraph_actor_role,
            'is_ref_actor': is_ref_actor,
            'ref_text': ref_text
        }

        year_paragraphs[paragraph_id] = paragraph_info

    return JsonResponse({"year_paragraphs": year_paragraphs,
                         'max_page': max_page})


def GetKeyWordActorParagraphs_Line_Modal(request, country_id, actor_name, actor_role_name, doc_year):
    doc_year = str(doc_year)

    res_paragraphs = DocumentActor.objects.filter(document_id__country_id__id=country_id)

    res_paragraphs = res_paragraphs.filter(actor_id__name=actor_name,
                                           document_id__approval_date__icontains=doc_year)

    res_paragraphs = res_paragraphs.filter(paragraph_id__text__icontains=' ' + actor_role_name + ' ')

    year_paragraphs = {}
    for res in res_paragraphs:

        paragraph_id = res.paragraph_id.id
        document_id = res.document_id.id
        document_name = res.document_id.name
        paragraph_text = res.paragraph_id.text
        paragraph_actor_form = res.current_actor_form
        paragraph_actor_role = res.actor_type_id.name

        para_ref_to_general_def = res.ref_to_general_definition

        para_ref_to_general_def_text = ''
        if para_ref_to_general_def:
            para_ref_to_general_def_text = res.general_definition_id.text

        para_ref_to_paragraph = res.ref_to_paragraph
        para_ref_to_para_text = ''

        if para_ref_to_paragraph:
            para_ref_to_para_text = res.ref_paragraph_id.text

        is_ref_actor = (para_ref_to_general_def or para_ref_to_paragraph)

        ref_text = ''

        if para_ref_to_general_def:
            ref_text = para_ref_to_general_def_text
        elif para_ref_to_paragraph:
            ref_text = para_ref_to_para_text

        paragraph_info = {
            'document_id': document_id,
            'document_name': document_name,
            'text': paragraph_text,
            'actor_form': paragraph_actor_form,
            'actor_role': paragraph_actor_role,
            'is_ref_actor': is_ref_actor,
            'ref_text': ref_text
        }

        year_paragraphs[paragraph_id] = paragraph_info

    return JsonResponse({"year_paragraphs": year_paragraphs})


def GetActorsComparison_ChartData(request, country_id, roles_id, area_id, actors_id, keywords_text):
    years_information_dict = {
        'متولی اجرا': {},
        'همکار': {},
        'دارای صلاحیت اختیاری': {},
        'برآیند نقش‌ها': {}
    }

    # roles_id = roles_id.split("__")
    actors_id = actors_id.split("__")
    actors_name_list = []

    # if '0' in roles_id:
    roles_id_list = []
    role_objs = ActorType.objects.all().values('id')
    for role in role_objs:
        roles_id_list.append(role['id'])

    doc_paragraphs = DocumentActor.objects.filter(
        document_id__country_id__id=country_id)

    if '0' not in actors_id:
        doc_paragraphs = doc_paragraphs.filter(actor_id__in=actors_id)

    else:
        if area_id != 0:
            doc_paragraphs = doc_paragraphs.filter(actor_id__area__id=area_id)

    # Filter by keywords
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')
        doc_paragraphs = doc_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_id__text__icontains=kw + ' ') for kw in keywords_list)))

    all_role_info_dict = years_information_dict['برآیند نقش‌ها']
    for res in doc_paragraphs:
        doc_approval_date = res.document_id.approval_date
        actor_name = res.actor_id.name

        doc_year = None
        if doc_approval_date != None:
            doc_year = int(doc_approval_date[:4])

            if actor_name not in actors_name_list:
                actors_name_list.append(actor_name)

            if doc_year not in all_role_info_dict:
                all_role_info_dict[doc_year] = {
                    actor_name: 1
                }
            else:
                if actor_name not in all_role_info_dict[doc_year]:
                    all_role_info_dict[doc_year][actor_name] = 1
                else:
                    all_role_info_dict[doc_year][actor_name] += 1

    years_information_dict['برآیند نقش‌ها'] = all_role_info_dict
    list_chart_data = []

    for year, actor_info in all_role_info_dict.items():
        column_data = [year]
        for actor_name in actors_name_list:
            if actor_name in actor_info:
                actor_count = actor_info[actor_name]
                column_data.append(actor_count)
            else:
                column_data.append(0)

        list_chart_data.append(column_data)

    list_chart_data = sorted(list_chart_data, key=itemgetter(0), reverse=False)
    years_information_dict['برآیند نقش‌ها'] = list_chart_data

    for role_id in roles_id_list:
        role_id = int(role_id)
        role_name = ActorType.objects.get(id=role_id).name
        role_info_dict = years_information_dict[role_name]
        role_paragraphs = doc_paragraphs.filter(actor_type_id__id=role_id)
        for res in role_paragraphs:
            doc_approval_date = res.document_id.approval_date
            actor_name = res.actor_id.name

            doc_year = None
            if doc_approval_date != None:
                doc_year = int(doc_approval_date[:4])

                if actor_name not in actors_name_list:
                    actors_name_list.append(actor_name)

                if doc_year not in role_info_dict:
                    role_info_dict[doc_year] = {
                        actor_name: 1
                    }
                else:
                    if actor_name not in role_info_dict[doc_year]:
                        role_info_dict[doc_year][actor_name] = 1
                    else:
                        role_info_dict[doc_year][actor_name] += 1

        years_information_dict[role_name] = role_info_dict
        list_chart_data = []

        for year, actor_info in role_info_dict.items():
            column_data = [year]
            for actor_name in actors_name_list:
                if actor_name in actor_info:
                    actor_count = actor_info[actor_name]
                    column_data.append(actor_count)
                else:
                    column_data.append(0)

            list_chart_data.append(column_data)

        list_chart_data = sorted(list_chart_data, key=itemgetter(0), reverse=False)
        years_information_dict[role_name] = list_chart_data

    return JsonResponse({"years_chart_data": years_information_dict, 'selected_actors': actors_name_list})


def GetActorsComparison_ChartData_es(request, country_id, roles_id, area_id, actors_id, keywords_text):
    years_information_dict = {
        'متولی اجرا': [],
        'همکار': [],
        'دارای صلاحیت اختیاری': [],
        'برآیند نقش‌ها': []
    }

    actors_id = actors_id.split("__")
    actors_name_list = []

    res_query = {
        "bool": {
        }
    }

    res_query['bool']['filter'] = []
    res_query = filter_document_actor_fields(
        res_query,
        area_id=area_id,
        actor_ids=actors_id)

    if len(res_query['bool']['filter']) == 0:
        del res_query['bool']['filter']

    if keywords_text != "empty":
        res_query["bool"]["must"] = []
        res_query = filter_document_actor_text(res_query, keywords_text, 'filter' not in res_query['bool'])

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentActor.__name__)

    # from_value = (curr_page - 1) * search_result_size

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
                    },
                    "aggs": {
                        "document-approval-year-agg": {
                            "terms": {
                                "field": "document_approval_year",
                                "size": bucket_size
                            }
                        },
                    },
                },
                "document-approval-year-agg": {
                    "terms": {
                        "field": "document_approval_year",
                        "size": bucket_size
                    }
                },
            },
        },
    }

    response = client.search(index=index_name,
                             # _source_includes=['actor_id', "actor_name", 'actor_type_id','actor_type_name'],
                             _source_includes=[],
                             request_timeout=40,
                             query=res_query,
                             # aggregations=res_agg,
                             # from_=from_value,
                             # size=search_result_size
                             size=0,
                             # track_total_hits=True,
                             aggregations=res_agg,
                             )

    aggregations = response['aggregations']

    actor_to_year_dict = {
        'متولی اجرا': {},
        'همکار': {},
        'دارای صلاحیت اختیاری': {},
        'برآیند نقش‌ها': {},
    }

    for actor in aggregations['actor-name-agg']['buckets']:
        actor_name = actor["key"][0]
        actors_name_list.append(actor_name)
        for role in actor['actor-type-name-agg']['buckets']:
            role_name = role['key']
            for year in role['document-approval-year-agg']['buckets']:
                year_name = year['key']
                # if year_name == 0:
                #     continue
                if year_name not in actor_to_year_dict[role_name].keys():
                    actor_to_year_dict[role_name][year_name] = {}
                actor_to_year_dict[role_name][year_name][actor_name] = year['doc_count']
        for year in actor['document-approval-year-agg']['buckets']:
            year_name = year['key']
            # if year_name == 0:
            #     continue
            if year_name not in actor_to_year_dict['برآیند نقش‌ها'].keys():
                actor_to_year_dict['برآیند نقش‌ها'][year_name] = {}
            actor_to_year_dict['برآیند نقش‌ها'][year_name][actor_name] = year['doc_count']

    for role, year_dict in actor_to_year_dict.items():
        temp_year_dict = []
        for year, actor_dict in year_dict.items():
            count_array = []
            for actor in actors_name_list:
                if actor in actor_dict.keys():
                    count_array.append(actor_dict[actor])
                else:
                    count_array.append(0)
            temp_year_dict.append([year] + count_array)
        temp_year_dict = sorted(temp_year_dict, key=itemgetter(0), reverse=False)
        # print(temp_year_dict)
        for year in temp_year_dict:
            years_information_dict[role].append(year)

    for key in years_information_dict.keys():
        if len(years_information_dict[key]) > 0 and years_information_dict[key][0][0] == 0:
            years_information_dict[key][0][0] = 'نامشخص'

    return JsonResponse({"years_chart_data": years_information_dict, 'selected_actors': actors_name_list})


def GetPredictionChartsData_ByAtorsID(request, country_id, actor_id, model_name):
    actor_data = ActorTimeSeries.objects.get(country_id__id=country_id, actor_id__id=actor_id)
    actor_id = actor_data.actor_id.id
    actor_name = actor_data.actor_id.name
    prediction_data = GridSearchARIMAPredictionData.objects.get(time_series_data__id=actor_id).prediction_data

    comparison_charts_data = {
        'همه': [],
        'متولی اجرا': [],
        'همکار': [],
        'دارای صلاحیت اختیاری': [],
    }

    prediction_rmse = {
        'همه': 'نامشخص',
        'متولی اجرا': 'نامشخص',
        'همکار': 'نامشخص',
        'دارای صلاحیت اختیاری': 'نامشخص',
    }
    best_parameters = {
        'همه': 'نامشخص',
        'متولی اجرا': 'نامشخص',
        'همکار': 'نامشخص',
        'دارای صلاحیت اختیاری': 'نامشخص',
    }

    for role_name in prediction_data[model_name].keys():

        actor_timeseries_data = prediction_data[role_name]
        actor_prediction_data = prediction_data[model_name][role_name]['Prediction']
        actor_test_prediction_data = prediction_data[model_name][role_name]['Test']
        actor_prediction_rmse = prediction_data[model_name][role_name]['RMSE']
        actor_best_parameters = prediction_data[model_name][role_name]['BestParameters']

        result_chart_data = []

        for year, prediction_count in actor_prediction_data.items():
            real_count = actor_timeseries_data[year] if year in actor_timeseries_data else 0
            test_count = actor_test_prediction_data[year] if year in actor_test_prediction_data else 0

            column_data = [int(year), real_count, test_count, prediction_count]
            result_chart_data.append(column_data)

        comparison_charts_data[role_name] = result_chart_data
        prediction_rmse[role_name] = actor_prediction_rmse
        best_parameters[role_name] = actor_best_parameters

    return JsonResponse({"comparison_charts_data": comparison_charts_data,
                         'prediction_rmse': prediction_rmse,
                         'best_parameters': best_parameters,
                         'actor_name': actor_name})


def getComparisonTrendChartsData_ByAtorsID(request, country_id, source_actor_id, other_actor_id):
    source_actor_data = ActorTimeSeries.objects.get(country_id__id=country_id, actor_id__id=source_actor_id)
    other_actor_data = ActorTimeSeries.objects.get(country_id__id=country_id, actor_id__id=other_actor_id)

    source_actor_name = source_actor_data.actor_id.name
    other_actor_name = other_actor_data.actor_id.name

    comparison_charts_data = {
        'همه': [],
        'متولی اجرا': [],
        'همکار': [],
        'دارای صلاحیت اختیاری': [],
    }

    correlation_values = {
        'همه': None,
        'متولی اجرا': None,
        'همکار': None,
        'دارای صلاحیت اختیاری': None,
    }

    for role_name in source_actor_data.time_series_data.keys():
        source_year_vector = source_actor_data.time_series_data[role_name]
        other_year_vector = other_actor_data.time_series_data[role_name]

        source_year_vector_count = pd.Series(list(source_year_vector.values()))
        other_actor_year_count = pd.Series(list(other_year_vector.values()))

        temp_correlation = round(source_year_vector_count.corr(other_actor_year_count), 2)

        correlation_value = temp_correlation if not math.isnan(temp_correlation) else '-'

        result_chart_data = []
        for year, src_count in source_year_vector.items():
            other_count = other_year_vector[year]
            column = [year, src_count, other_count]
            result_chart_data.append(column)

        comparison_charts_data[role_name] = result_chart_data
        correlation_values[role_name] = correlation_value

    return JsonResponse({"comparison_charts_data": comparison_charts_data,
                         'correlation_values': correlation_values,
                         'source_actor_name': source_actor_name,
                         'other_actor_name': other_actor_name})


def getComparisonSimilarityChartsData_ByActorsID(request, country_id, source_actor_id, other_actor_id):
    similarity_graph_type = ActorGraphType.objects.get(name='گراف کلیدواژگان یکسان')
    edge = ActorsGraph.objects.filter(src_actor_id_id=source_actor_id, graph_type_id=similarity_graph_type,
                                      dest_actor_id_id=other_actor_id, country_id__id=country_id)
    if edge.count() == 0:
        edge = ActorsGraph.objects.filter(dest_actor_id_id=source_actor_id, graph_type_id=similarity_graph_type,
                                          src_actor_id_id=other_actor_id, country_id__id=country_id)[0]
    else:
        edge = edge[0]

    keywords = edge.edge_detail['keywords'].keys()

    right = Actor.objects.get(id=source_actor_id)
    right_paragraphs = DocumentActor.objects.filter(
        reduce(operator.or_, (Q(paragraph_id__text__icontains=word) for word in keywords)),
        actor_id=right, document_id__country_id__id=country_id)
    if edge.role_type != 'همه':
        right_paragraphs = right_paragraphs.filter(actor_type_id__name=edge.role_type)
    right_paragraphs = right_paragraphs.values('paragraph_id__text')

    left = Actor.objects.get(id=other_actor_id)
    left_paragraphs = DocumentActor.objects.filter(
        reduce(operator.or_, (Q(paragraph_id__text__icontains=word) for word in keywords)),
        actor_id=left, document_id__country_id__id=country_id)
    if edge.role_type != 'همه':
        left_paragraphs = left_paragraphs.filter(actor_type_id__name=edge.role_type)
    left_paragraphs = left_paragraphs.values('paragraph_id__text')

    return JsonResponse(
        {
            "right": {
                'name': right.name,
                'id': right.id,
                'forms': right.forms.split('/'),
                'paragraphs': [right_paragraph['paragraph_id__text'] for right_paragraph in right_paragraphs]
            },
            "left": {
                'name': left.name,
                'id': left.id,
                'forms': left.forms.split('/'),
                'paragraphs': [left_paragraph['paragraph_id__text'] for left_paragraph in left_paragraphs]
            },
            'keywords': edge.edge_detail['keywords']
        }
    )


def getComparisonAreaChartsData_ByActorsID(request, country_id, source_actor_id, other_actor_id):
    similarity_graph_type = ActorGraphType.objects.get(name="گراف کلان حوزه ها")
    edge = CUBE_ActorArea_GraphData.objects.filter(src_actor_area_id=source_actor_id,
                                                   graph_type_id=similarity_graph_type,
                                                   dest_actor_area_id=other_actor_id, country_id__id=country_id)
    if edge.count() == 0:
        edge = \
            CUBE_ActorArea_GraphData.objects.filter(dest_actor_area_id=source_actor_id,
                                                    graph_type_id=similarity_graph_type,
                                                    src_actor_area_id=other_actor_id, country_id__id=country_id)[0]
    else:
        edge = edge[0]

    return JsonResponse(edge.edge_detail)


def GetDocumentActorsDetails_Modal(request, document_id, roles_id, area_id, actors_id, keywords_text):
    roles_id = roles_id.split("__")
    actors_id = actors_id.split("__")

    doc_paragraphs = DocumentActor.objects.filter(
        document_id__id=document_id)

    if '0' not in roles_id:
        doc_paragraphs = doc_paragraphs.filter(actor_type_id__id__in=roles_id)

    if '0' not in actors_id:
        doc_paragraphs = doc_paragraphs.filter(actor_id__id__in=actors_id)
    else:
        # selected category
        if area_id != 0:
            doc_paragraphs = doc_paragraphs.filter(
                actor_id__area__id=area_id)
        else:
            # all categories
            doc_paragraphs = doc_paragraphs

    result = []

    # Filter by keywords
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')
        doc_paragraphs = doc_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_id__text__icontains=(kw + ' ')) for kw in keywords_list)))

    document_paragraphs_result = {}

    for res in doc_paragraphs:

        paragraph_id = res.paragraph_id.id
        document_id = res.document_id.id
        document_name = res.document_id.name
        paragraph_text = res.paragraph_id.text
        paragraph_actor_role = res.actor_type_id.name
        paragraph_actor_form = res.current_actor_form
        paragraph_actor_name = res.actor_id.name

        para_ref_to_general_def = res.ref_to_general_definition

        para_ref_to_general_def_text = ''
        if para_ref_to_general_def:
            para_ref_to_general_def_text = res.general_definition_id.text

        para_ref_to_paragraph = res.ref_to_paragraph
        para_ref_to_para_text = ''

        if para_ref_to_paragraph:
            para_ref_to_para_text = res.ref_paragraph_id.text

        is_ref_actor = (para_ref_to_general_def or para_ref_to_paragraph)

        ref_text = ''

        if para_ref_to_general_def:
            ref_text = para_ref_to_general_def_text
        elif para_ref_to_paragraph:
            ref_text = para_ref_to_para_text

        paragraph_info = {
            'document_id': document_id,
            'document_name': document_name,
            'text': paragraph_text,
            'actor_form': paragraph_actor_form,
            'actor_name': paragraph_actor_name,
            'is_ref_actor': is_ref_actor,
            'ref_text': ref_text
        }

        actor_key = paragraph_actor_name + ' (' + paragraph_actor_role + ')'
        if actor_key not in document_paragraphs_result:
            paragraph_dict = {}

            paragraph_dict[paragraph_id] = paragraph_info

            document_paragraphs_result[actor_key] = {
                'paragraph_dict': paragraph_dict,
                'actor_form': paragraph_actor_form,
                'actor_name': paragraph_actor_name,
            }


        else:
            paragraph_dict = document_paragraphs_result[actor_key]['paragraph_dict']
            if paragraph_id not in paragraph_dict:
                paragraph_dict[paragraph_id] = paragraph_info
                document_paragraphs_result[actor_key]['paragraph_dict'] = paragraph_dict

    document_name = Document.objects.get(id=document_id).name
    return JsonResponse({"document_paragraphs_result": document_paragraphs_result, 'document_name': document_name})


def GetDocumentActorsDetails_Modal_es(request, document_id, roles_id, area_id, actors_id, keywords_text, curr_page):
    detail_result_size = 10
    roles_id = roles_id.split("__")
    actors_id = actors_id.split("__")

    res_query = {
        "bool": {
        }
    }

    res_query['bool']['filter'] = []
    res_query = filter_document_actor_fields(
        res_query,
        role_ids=roles_id,
        actor_ids=actors_id)

    if len(res_query['bool']['filter']) == 0:
        del res_query['bool']['filter']

    if keywords_text != "empty":
        res_query["bool"]["must"] = []
        res_query = filter_document_actor_text(res_query, keywords_text, 'filter' not in res_query['bool'])

    document = Document.objects.get(id=document_id)
    document_name = document.name
    country_obj = document.country_id
    index_name = standardIndexName(country_obj, DocumentActor.__name__)

    from_value = (curr_page - 1) * detail_result_size

    # print(res_query)

    response = client.search(index=index_name,
                             _source_includes=['paragraph_id',
                                               'document_id',
                                               "document_name",
                                               'attachment.content',
                                               'actor_name',
                                               'current_actor_form',
                                               'actor_type_name',
                                               'general_definition_text',
                                               'ref_paragraph_text'],
                             request_timeout=40,
                             query=res_query,
                             # aggregations=res_agg,
                             sort=[{'actor_type_id': {"order": "asc"}}],
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
                             track_total_hits=True,
                             )

    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    max_page = ((total_hits - 1) // detail_result_size) + 1

    document_paragraphs_result = {}

    for res in response['hits']['hits']:

        paragraph_id = res["_source"]["paragraph_id"]
        document_id = res["_source"]["document_id"]
        document_name = res["_source"]["document_name"]
        paragraph_text = res["_source"]["attachment"]['content'] if keywords_text == "empty" else \
            res["highlight"]["attachment.content"][0]
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

        actor_key = paragraph_actor_name + ' (' + paragraph_actor_role + ')'
        if actor_key not in document_paragraphs_result:
            paragraph_dict = {}

            paragraph_dict[paragraph_id] = paragraph_info

            document_paragraphs_result[actor_key] = {
                'paragraph_dict': paragraph_dict,
                'actor_form': paragraph_actor_form,
                'actor_name': paragraph_actor_name,
            }


        else:
            paragraph_dict = document_paragraphs_result[actor_key]['paragraph_dict']
            if paragraph_id not in paragraph_dict:
                paragraph_dict[paragraph_id] = paragraph_info
                document_paragraphs_result[actor_key]['paragraph_dict'] = paragraph_dict

    return JsonResponse({"document_paragraphs_result": document_paragraphs_result,
                         'document_name': document_name,
                         'max_page': max_page})


def SearchActorsByKeywords(request, country_id, roles_id, area_id, actors_id, keywords_text):
    actors_information_dict = {}
    roles_id = roles_id.split("__")
    actors_id = actors_id.split('__')

    doc_paragraphs = DocumentActor.objects.filter(document_id__country_id__id=country_id)

    # Filter by roles
    if '0' not in roles_id:
        doc_paragraphs = doc_paragraphs.filter(actor_type_id__id__in=roles_id)

    if '0' not in actors_id:
        doc_paragraphs = doc_paragraphs.filter(actor_id__id__in=actors_id)

    else:
        # Filter by category
        if area_id != 0:
            doc_paragraphs = doc_paragraphs.filter(actor_id__area__id=area_id)

    if keywords_text == 'empty':

        for res in doc_paragraphs:
            actor_id = res.actor_id.id
            actor_name = res.actor_id.name
            actor_role = res.actor_type_id.name
            if actor_id not in actors_information_dict:
                actors_information_dict[actor_id] = {
                    'actor_name': actor_name,
                    'actor_roles': [actor_role],
                    'keywords': [],
                }
            else:
                actor_roles = actors_information_dict[actor_id]['actor_roles']
                if actor_role not in actor_roles:
                    actor_roles.append(actor_role)
                    actors_information_dict[actor_id]['actor_roles'] = actor_roles

    else:
        # filter by keywords
        keywords_list = keywords_text.split(',')

        for keyword in keywords_list:
            keyword_paragraphs = doc_paragraphs.filter(paragraph_id__text__icontains=(keyword + ' '))
            for res in keyword_paragraphs:
                actor_id = res.actor_id.id
                actor_name = res.actor_id.name
                actor_role = res.actor_type_id.name

                if actor_id not in actors_information_dict:
                    actors_information_dict[actor_id] = {
                        'actor_name': actor_name,
                        'actor_roles': [actor_role],
                        'keywords': [keyword],
                    }
                else:
                    actor_roles = actors_information_dict[actor_id]['actor_roles']
                    if actor_role not in actor_roles:
                        actor_roles.append(actor_role)
                        actors_information_dict[actor_id]['actor_roles'] = actor_roles

                    actor_keywords = actors_information_dict[actor_id]['keywords']
                    if keyword not in actor_keywords:
                        actor_keywords.append(keyword)
                        actors_information_dict[actor_id]['keywords'] = actor_keywords

        # actors_information_dict = {k: v for k, v in sorted(actors_information_dict.items(),reverse=True, key=lambda item: item[1]['keywords_count'])}

    return JsonResponse({"actors_information_dict": actors_information_dict})




def filter_actor_supervisor_fields(res_query, area_id, actor_ids):
    actor_ids = [int(item) for item in actor_ids]

    if area_id != 0:
        if 0 in actor_ids:
            actors = Actor.objects.filter(area__id=area_id)
            actor_ids = [int(actor.id) for actor in actors]

    else:
        if 0 in actor_ids:
            return res_query

    source_actor_query = {
        "terms": {
            "source_actor_id": actor_ids,
        }
    }

    supervisor_actor_query = {
        "terms": {
            "supervisor_actor_id": actor_ids,
        }
    }

    multi_or_query = {
        "bool": {
            "should": [source_actor_query, supervisor_actor_query]
        }
    }

    res_query['bool']['filter'].append(multi_or_query)

    return res_query


def filter_document_actor_text(res_query, text, ALL_FIELDS):
    text = text.replace('>', '/').replace('<', '\\').split(",")

    should = [
        {
            "match_phrase": {
                "attachment.content": query
            }
        } for query in text
    ]

    if len(should) == 1:
        title_content_query = should[0]
    else:
        title_content_query = {
            "bool": {
                "should": should
            }
        }

    if ALL_FIELDS:
        res_query = title_content_query
    else:
        res_query['bool']['must'].append(title_content_query)

    return res_query


def filter_collective_actors_text(res_query, text, ALL_FIELDS):
    text = text.replace('>', '/').replace('<', '\\').split(",")

    should = [
        {
            "match_phrase": {
                "attachment.content": query
            }
        } for query in text
    ]

    if len(should) == 1:
        title_content_query = should[0]
    else:
        title_content_query = {
            "bool": {
                "should": should
            }
        }

    if ALL_FIELDS:
        res_query = title_content_query
    else:
        res_query['bool']['must'].append(title_content_query)

    return res_query


def SearchActorsByKeywords_es(request, country_id, roles_id, area_id, actors_id, keywords_text, curr_page):
    roles_id = roles_id.split("__")
    actors_id = actors_id.split('__')

    res_query = {
        "bool": {
        }
    }

    res_query['bool']['filter'] = []
    res_query = filter_document_actor_fields(
        res_query,
        role_ids=roles_id,
        area_id=area_id,
        actor_ids=actors_id)

    if len(res_query['bool']['filter']) == 0:
        del res_query['bool']['filter']

    if keywords_text != "empty":
        res_query["bool"]["must"] = []
        res_query = filter_document_actor_text(res_query, keywords_text, 'filter' not in res_query['bool'])

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentActor.__name__)

    from_value = (curr_page - 1) * search_result_size

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
                             _source_includes=[],
                             request_timeout=40,
                             query=res_query,
                             # aggregations=res_agg,
                             # from_=from_value,
                             # size=search_result_size,
                             size=0,
                             # track_total_hits=True,
                             aggregations=res_agg,
                             )

    print(response['hits']['total']['value'])

    # print(len([item["_source"]["document_name"] for item in response['hits']['hits']]))
    # print([item["_source"]["paragraph_id"] for item in response['hits']['hits']])

    aggregations = response['aggregations']
    total_hits = len(aggregations['actor-name-agg']['buckets'])

    return JsonResponse({
        'total_hits': total_hits,
        "curr_page": curr_page,
        'aggregations': aggregations['actor-name-agg']['buckets'][from_value:from_value + search_result_size]
    })


def GetActorParagraphsDetails_Modal(request, country_id, actor_id, roles_id, keywords_text):
    roles_id = roles_id.split("__")

    doc_paragraphs = DocumentActor.objects.filter(
        document_id__country_id__id=country_id)

    if '0' not in roles_id:
        doc_paragraphs = doc_paragraphs.filter(
            actor_id__id=actor_id, actor_type_id__id__in=roles_id)
    else:
        doc_paragraphs = doc_paragraphs.filter(
            actor_id__id=actor_id)

    result = []
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')

        for keyword in keywords_list:
            result += doc_paragraphs.filter(
                paragraph_id__text__icontains=(keyword + ' '))
    else:
        result = doc_paragraphs

    actor_paragraphs_result = {}
    for res in result:

        paragraph_id = res.paragraph_id.id
        document_id = res.document_id.id
        document_name = res.document_id.name
        paragraph_text = res.paragraph_id.text
        paragraph_actor_role = res.actor_type_id.name
        paragraph_actor_form = res.current_actor_form

        para_ref_to_general_def = res.ref_to_general_definition

        para_ref_to_general_def_text = ''
        if para_ref_to_general_def:
            para_ref_to_general_def_text = res.general_definition_id.text

        para_ref_to_paragraph = res.ref_to_paragraph
        para_ref_to_para_text = ''

        if para_ref_to_paragraph:
            para_ref_to_para_text = res.ref_paragraph_id.text

        is_ref_actor = (para_ref_to_general_def or para_ref_to_paragraph)

        ref_text = ''

        if para_ref_to_general_def:
            ref_text = para_ref_to_general_def_text
        elif para_ref_to_paragraph:
            ref_text = para_ref_to_para_text

        paragraph_info = {
            'document_id': document_id,
            'document_name': document_name,
            'text': paragraph_text,
            'actor_form': paragraph_actor_form,
            'is_ref_actor': is_ref_actor,
            'ref_text': ref_text
        }

        if paragraph_actor_role not in actor_paragraphs_result:
            actor_paragraphs_result[paragraph_actor_role] = {paragraph_id: paragraph_info}
        else:
            paragraphs_dict = actor_paragraphs_result[paragraph_actor_role]
            if paragraph_id not in paragraphs_dict:
                paragraphs_dict[paragraph_id] = paragraph_info
                actor_paragraphs_result[paragraph_actor_role] = paragraphs_dict

    actor_name = Actor.objects.get(id=actor_id).name
    return JsonResponse({"actor_paragraphs_result": actor_paragraphs_result, 'actor_name': actor_name})


def GetActorParagraphsDetails_Modal_es(request, country_id, actor_id, roles_id, keywords_text, curr_page):
    detail_result_size = 10
    roles_id = roles_id.split("__")

    res_query = {
        "bool": {
        }
    }

    res_query['bool']['filter'] = []
    res_query = filter_document_actor_fields(
        res_query,
        role_ids=roles_id,
        actor_ids=[actor_id])

    if len(res_query['bool']['filter']) == 0:
        del res_query['bool']['filter']

    if keywords_text != "empty":
        res_query["bool"]["must"] = []
        res_query = filter_document_actor_text(res_query, keywords_text, 'filter' not in res_query['bool'])

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentActor.__name__)

    from_value = (curr_page - 1) * detail_result_size

    response = client.search(index=index_name,
                             _source_includes=['paragraph_id',
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
                             sort=[{'actor_type_id': {"order": "asc"}}],
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
                             track_total_hits=True,
                             )

    total_hits = response['hits']['total']['value']

    if total_hits == 10000:
        total_hits = client.count(body={
            "query": res_query
        }, index=index_name, doc_type='_doc')['count']

    max_page = ((total_hits - 1) // detail_result_size) + 1

    actor_paragraphs_result = {}
    for res in response['hits']['hits']:
        paragraph_id = res["_source"]["paragraph_id"]
        document_id = res["_source"]["document_id"]
        document_name = res["_source"]["document_name"]
        paragraph_text = res["_source"]["attachment"]['content'] if keywords_text == "empty" else \
            res["highlight"]["attachment.content"][0]
        paragraph_actor_role = res["_source"]["actor_type_name"]
        paragraph_actor_form = res["_source"]["current_actor_form"]

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
            'is_ref_actor': is_ref_actor,
            'ref_text': ref_text
        }

        if paragraph_actor_role not in actor_paragraphs_result:
            actor_paragraphs_result[paragraph_actor_role] = {paragraph_id: paragraph_info}
        else:
            paragraphs_dict = actor_paragraphs_result[paragraph_actor_role]
            if paragraph_id not in paragraphs_dict:
                paragraphs_dict[paragraph_id] = paragraph_info
                actor_paragraphs_result[paragraph_actor_role] = paragraphs_dict
    actor_name = Actor.objects.get(id=actor_id).name
    return JsonResponse({"actor_paragraphs_result": actor_paragraphs_result,
                         'actor_name': actor_name,
                         'max_page': max_page})


def Calculate_words_Frequency_inDoc(word_list):
    words_frequency_dict = {}
    for word in word_list:
        if word not in words_frequency_dict:
            words_frequency_dict[word] = 1
        else:
            words_frequency_dict[word] += 1
    return words_frequency_dict


def load_stop_words():
    stop_words = []
    stop_words_file = str(Path(config.PERSIAN_PATH, 'stopwords.txt'))
    with open(stop_words_file, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            stop_words.append(line)
    f.close()
    return stop_words





# def preprocess(text):
#
#     return text.replace('‌','')

def getActorsWordCloudChartData(request, country_id, area_id, actors_id):
    paragraphs_list_id = list(
        DocumentActor.objects.filter(document_id__country_id__id=country_id, actor_id__id=actors_id).values_list(
            'paragraph_id_id', flat=True))

    paragraphs_text_list = list(
        DocumentParagraphs.objects.filter(id__in=paragraphs_list_id).values_list('text', flat=True))

    text = ''
    for paragraphs_text in paragraphs_text_list:
        #    !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
        text += ' ' + paragraphs_text.translate(str.maketrans('', '', string.punctuation))

    for stop_word in load_stop_words():
        text = text.replace(' ' + stop_word + ' ', ' ')

    word_list = text.split(' ')

    while '' in word_list:
        word_list.remove('')
    while '‌' in word_list:
        word_list.remove('‌')
    while ' ' in word_list:
        word_list.remove(' ')

    frq_word = Calculate_words_Frequency_inDoc(word_list)
    top_items = heapq.nlargest(5, frq_word.items(), key=itemgetter(1))
    top_items = [item[0] for item in top_items]

    # print(top_items)

    paragraphs_list_date = list(DocumentParagraphs.objects.filter(id__in=paragraphs_list_id)
    .values_list('text', 'document_id__approval_date').order_by(
        'document_id__approval_date'))

    text_approval_date_dict = {}
    for word in paragraphs_list_date:
        if word[1] is None:
            continue
        year = word[1][:4]
        if year not in text_approval_date_dict.keys():
            text_approval_date_dict[year] = word[0].translate(str.maketrans('', '', string.punctuation))
        else:
            text_approval_date_dict[year] += ' ' + word[0].translate(str.maketrans('', '', string.punctuation))

    text_approval_date_list = []

    for key, value in text_approval_date_dict.items():
        text_approval_date_list.append(
            [key, value.count(' ' + top_items[0] + ' '), value.count(' ' + top_items[1] + ' '),
             value.count(' ' + top_items[2] + ' '), value.count(' ' + top_items[3] + ' '),
             value.count(' ' + top_items[4] + ' ')])

    print(text_approval_date_list)

    return JsonResponse({"text_approval_date_list": text_approval_date_list, "top_items": top_items})


def GetActorsDistChartData(request, country_id, roles_id, area_id, actors_id, keywords_text):
    actors_information_dict = {}
    roles_id = roles_id.split("__")
    actors_id = actors_id.split("__")

    doc_paragraphs = DocumentActor.objects.filter(document_id__country_id__id=country_id)

    # Filter by roles
    if '0' not in roles_id:
        doc_paragraphs = doc_paragraphs.filter(actor_type_id__id__in=roles_id)

    # Filter by actors
    if '0' not in actors_id:
        doc_paragraphs = doc_paragraphs.filter(actor_id__id__in=actors_id)
    else:
        # Filter by category
        if area_id != 0:
            doc_paragraphs = doc_paragraphs.filter(actor_id__area__id=area_id)

    result = []
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')

        for keyword in keywords_list:
            result += doc_paragraphs.filter(
                paragraph_id__text__icontains=(keyword + ' '))
    else:
        result = doc_paragraphs

    for res in result:
        actor_id = res.actor_id.id
        actor_name = res.actor_id.name
        actor_role_name = res.actor_type_id.name
        actor_paragraph_id = res.paragraph_id.id

        if actor_id not in actors_information_dict:
            actors_information_dict[actor_id] = {
                'actor_name': actor_name,
                'roles_info': {
                    'متولی اجرا': [],
                    'همکار': [],
                    'دارای صلاحیت اختیاری': []
                }

            }
            actor_roles_info = actors_information_dict[actor_id]['roles_info']
            actor_roles_info[actor_role_name].append(actor_paragraph_id)
            actors_information_dict[actor_id]['roles_info'] = actor_roles_info

        else:
            actor_roles_info_2 = actors_information_dict[actor_id]['roles_info']
            if actor_paragraph_id not in actor_roles_info_2[actor_role_name]:
                actor_roles_info_2[actor_role_name].append(actor_paragraph_id)
                actors_information_dict[actor_id]['roles_info'] = actor_roles_info_2

    # Calculate role frequency of actors
    actors_chart_data = []
    for actor_id in actors_information_dict:
        actor_name = actors_information_dict[actor_id]['actor_name']
        motevali_count = len(actors_information_dict[actor_id]['roles_info']['متولی اجرا'])
        hamkar_count = len(actors_information_dict[actor_id]['roles_info']['همکار'])
        salahiat_count = len(actors_information_dict[actor_id]['roles_info']['دارای صلاحیت اختیاری'])
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


def GetActorsDistChartData_es(request, country_id, roles_id, area_id, actors_id, keywords_text):
    actors_information_dict = {}
    roles_id = roles_id.split("__")
    actors_id = actors_id.split("__")

    res_query = {
        "bool": {
        }
    }

    res_query['bool']['filter'] = []
    res_query = filter_document_actor_fields(
        res_query,
        role_ids=roles_id,
        actor_ids=actors_id)

    if len(res_query['bool']['filter']) == 0:
        del res_query['bool']['filter']

    if keywords_text != "empty":
        res_query["bool"]["must"] = []
        res_query = filter_document_actor_text(res_query, keywords_text, 'filter' not in res_query['bool'])

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

    # print(response['aggregations'])

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


def GetMaxMinEffectActorsInAreaChartData(request, country_id, area_id, keywords_text):
    actors_information_dict = {}
    doc_paragraphs = DocumentActor.objects.filter(document_id__country_id__id=country_id)

    # if '0' not in actors_id:
    # Filter by category
    if area_id != 0:
        doc_paragraphs = doc_paragraphs.filter(actor_id__area__id=area_id)

    result = []
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')

        for keyword in keywords_list:
            result += doc_paragraphs.filter(
                paragraph_id__text__icontains=(keyword + ' '))
    else:
        result = doc_paragraphs

    actors_without_duty_years = {}
    all_actors = []
    if area_id == 0:
        actors = Actor.objects.all().values(
            'id', 'name').distinct().order_by('name')
    else:
        actors = Actor.objects.filter(area__id=area_id).values(
            'id', 'name').distinct().order_by('name')
    for actor in actors:
        all_actors.append(actor['name'])
        actors_without_duty_years[actor['name']] = []

    actors_chart_data = []
    actors_chart_data_dic = {}

    result_without_year = list(
        filter(lambda x: x.document_id.approval_date == None, result))  # docs which doesn't have date
    result = filter(lambda x: x.document_id.approval_date != None, result)  # just for docs which have date

    # start without year
    if len(result_without_year) > 0:
        for res in result_without_year:
            actor_id = res.actor_id.id
            actor_name = res.actor_id.name
            actor_role_name = res.actor_type_id.name
            actor_paragraph_id = res.paragraph_id.id
            if actor_id not in actors_information_dict:
                actors_information_dict[actor_id] = {
                    'actor_name': actor_name,
                    'roles_info': {
                        'متولی اجرا': [],
                        'همکار': [],
                        'دارای صلاحیت اختیاری': []
                    }
                }
                actor_roles_info = actors_information_dict[actor_id]['roles_info']
                actor_roles_info[actor_role_name].append(actor_paragraph_id)
                actors_information_dict[actor_id]['roles_info'] = actor_roles_info
            else:
                actor_roles_info_2 = actors_information_dict[actor_id]['roles_info']
                if actor_paragraph_id not in actor_roles_info_2[actor_role_name]:
                    actor_roles_info_2[actor_role_name].append(actor_paragraph_id)
                    actors_information_dict[actor_id]['roles_info'] = actor_roles_info_2
        tmp = []
        # Calculate role frequency of actors in a year
        for actor_id in actors_information_dict:
            actor_name = actors_information_dict[actor_id]['actor_name']
            motevali_count = len(actors_information_dict[actor_id]['roles_info']['متولی اجرا'])
            hamkar_count = len(actors_information_dict[actor_id]['roles_info']['همکار'])
            salahiat_count = len(actors_information_dict[actor_id]['roles_info']['دارای صلاحیت اختیاری'])
            frequency = motevali_count + hamkar_count + salahiat_count
            actor_paragraph__motevali_ids = actors_information_dict[actor_id]['roles_info']['متولی اجرا']
            actor_paragraph_hamkar_ids = actors_information_dict[actor_id]['roles_info']['همکار']
            actor_paragraph_salahiat_ids = actors_information_dict[actor_id]['roles_info']['دارای صلاحیت اختیاری']
            column_data = [actor_name, motevali_count, hamkar_count, salahiat_count, frequency,
                           actor_paragraph__motevali_ids, actor_paragraph_hamkar_ids, actor_paragraph_salahiat_ids]
            # column_data = [actor_name, motevali_count, hamkar_count, salahiat_count , frequency]
            tmp.append(column_data)
        max_year = max(tmp, key=lambda x: x[4])
        min_year = min(tmp, key=lambda x: x[4])
        # max_year_data = [max_year[0], max_year[1], max_year[2], max_year[3], max_year[4] , "نامشخص"] # actor_name, motevali_count, hamkar_count, salahiat_count , frequency, year
        max_year_data = [max_year[0], max_year[1], max_year[2], max_year[3], max_year[4], "نامشخص", max_year[5],
                         max_year[6],
                         max_year[7]]  # actor_name, motevali_count, hamkar_count, salahiat_count , frequency, year
        min_year_data = [min_year[0], min_year[1], min_year[2], min_year[3], min_year[4], "نامشخص", min_year[5],
                         min_year[6], min_year[7]]
        # actors_chart_data.append(max_year_data) # if it is not good use dictionary {}
        # actors_chart_data.append(min_year_data)
        if (max_year == min_year):
            min_year_data = ["ندارد", 0, 0, 0, 0, "نامشخص", None, None, None]

        actors_chart_data_dic["نامشخص"] = [max_year_data, min_year_data]
        actors_chart_data.append(["نامشخص", max_year_data[4], max_year_data[0], min_year_data[4],
                                  min_year_data[0]])  # year , max_frequency , max_actor , min_frequency , min_actor
    ### end without year

    key = lambda x: int(x.document_id.approval_date[0:4])  # or communicated_date[0:4]
    result_per_year = groupby(sorted(result, key=key), key=key)

    for year, year_result in result_per_year:
        tmp_actors = all_actors
        actors_information_dict = {}
        year_result = list(year_result)
        for res in year_result:
            actor_id = res.actor_id.id
            actor_name = res.actor_id.name
            try:
                tmp_actors.remove(actor_name)
            except ValueError:
                pass
            actor_role_name = res.actor_type_id.name
            actor_paragraph_id = res.paragraph_id.id

            if actor_id not in actors_information_dict:
                actors_information_dict[actor_id] = {
                    'actor_name': actor_name,
                    'roles_info': {
                        'متولی اجرا': [],
                        'همکار': [],
                        'دارای صلاحیت اختیاری': []
                    }
                }
                actor_roles_info = actors_information_dict[actor_id]['roles_info']
                actor_roles_info[actor_role_name].append(actor_paragraph_id)
                actors_information_dict[actor_id]['roles_info'] = actor_roles_info

            else:
                actor_roles_info_2 = actors_information_dict[actor_id]['roles_info']
                if actor_paragraph_id not in actor_roles_info_2[actor_role_name]:
                    actor_roles_info_2[actor_role_name].append(actor_paragraph_id)
                    actors_information_dict[actor_id]['roles_info'] = actor_roles_info_2

        tmp = []
        # Calculate role frequency of actors in a year
        for actor_id in actors_information_dict:
            actor_name = actors_information_dict[actor_id]['actor_name']
            motevali_count = len(actors_information_dict[actor_id]['roles_info']['متولی اجرا'])
            hamkar_count = len(actors_information_dict[actor_id]['roles_info']['همکار'])
            salahiat_count = len(actors_information_dict[actor_id]['roles_info']['دارای صلاحیت اختیاری'])
            frequency = motevali_count + hamkar_count + salahiat_count
            actor_paragraph__motevali_ids = actors_information_dict[actor_id]['roles_info']['متولی اجرا']
            actor_paragraph_hamkar_ids = actors_information_dict[actor_id]['roles_info']['همکار']
            actor_paragraph_salahiat_ids = actors_information_dict[actor_id]['roles_info']['دارای صلاحیت اختیاری']
            column_data = [actor_name, motevali_count, hamkar_count, salahiat_count, frequency,
                           actor_paragraph__motevali_ids, actor_paragraph_hamkar_ids, actor_paragraph_salahiat_ids]
            # column_data = [actor_name, motevali_count, hamkar_count, salahiat_count , frequency]
            tmp.append(column_data)

        max_year = max(tmp, key=lambda x: x[4])
        min_year = min(tmp, key=lambda x: x[4])
        # max_year_data = [max_year[0], max_year[1], max_year[2], max_year[3], max_year[4] , year] # actor_name, motevali_count, hamkar_count, salahiat_count , frequency, year
        max_year_data = [max_year[0], max_year[1], max_year[2], max_year[3], max_year[4], year, max_year[5],
                         max_year[6], max_year[
                             7]]  # actor_name, motevali_count, hamkar_count, salahiat_count , frequency, year, actor_paragraph__motevali_ids, actor_paragraph_hamkar_ids, actor_paragraph_salahiat_ids
        min_year_data = [min_year[0], min_year[1], min_year[2], min_year[3], min_year[4], year, min_year[5],
                         min_year[6], min_year[7]]
        # actors_chart_data.append(max_year_data) # if it is not good use dictionary {}
        # actors_chart_data.append(min_year_data)
        if (max_year == min_year):
            min_year_data = ["ندارد", 0, 0, 0, 0, "نامشخص", None, None, None]
        actors_chart_data_dic[year] = [max_year_data, min_year_data]
        actors_chart_data.append([year, max_year_data[4], max_year_data[0], min_year_data[4],
                                  min_year_data[0]])  # year , max_frequency , max_actor , min_frequency , min_actor
        for a in tmp_actors:
            actors_without_duty_years[a].append(year)

    return JsonResponse({"actors_chart_data": actors_chart_data,
                         'actors_chart_data_dic': actors_chart_data_dic,
                         'actors_without_duty_years': actors_without_duty_years,
                         'column_1': 'motevalian',
                         'column_2': 'hamkaran',
                         'column_3': 'salahiat',
                         'column_4': 'frequency'
                         })


def GetMaxMinEffectActorsInAreaChartDataUsingCube(request, country_id, area_id, sub_area_id):
    # id = 0 --> all
    chart_data_json = CUBE_MaxMinEffectActorsInArea_ChartData.objects.filter(country__id=country_id, area_id=area_id,
                                                                             sub_area_id=sub_area_id).first().chart_data
    return JsonResponse({"actors_chart_data": chart_data_json['actors_chart_data'],
                         'actors_chart_data_dic': chart_data_json['actors_chart_data_dic'],
                         'actors_without_duty_years': chart_data_json['actors_without_duty_years'],
                         'column_1': 'motevalian',
                         'column_2': 'hamkaran',
                         'column_3': 'salahiat',
                         'column_4': 'frequency'
                         })


def GetParagraphsByIds_Modal(request, keywords_text):
    paragraphs_id = []
    if request.method == "GET":
        paragraphs_id = request.GET.getlist('paragraphs_id')
        print(paragraphs_id)
        print(request.GET.getlist('paragraphs_id'))

        # body_unicode = request.body.decode('utf-8')
        # body = json.loads(body_unicode)
        # content = body['paragraphs_id']
        # print(content)

        # body = json.loads(request.body.decode('utf-8'))
        # access_token = body.get("paragraphs_id")
        # print(access_token)

        # json_data = json.loads(request.body)
        # print(json_data)
        # print(request.body)

    # doc_paragraphs = DocumentActor.objects.filter(
    #     document_id__country_id__id=country_id,
    #     actor_id__name=actor_name, actor_type_id__name=role_name)

    # result = []
    # if keywords_text != 'empty':
    #     keywords_list = keywords_text.split(',')

    #     result = doc_paragraphs.filter(reduce(
    #         operator.or_, (Q(paragraph_id__text__icontains=kw + ' ') for kw in keywords_list)))

    # else:
    #     result = doc_paragraphs

    # actor_paragraphs_result = {}
    # for res in result:

    #     paragraph_id = res.paragraph_id.id
    #     document_id = res.document_id.id
    #     document_name = res.document_id.name
    #     paragraph_text = res.paragraph_id.text
    #     paragraph_actor_role = res.actor_type_id.name
    #     paragraph_actor_form = res.current_actor_form
    #     paragraph_actor_name = res.actor_id.name

    #     para_ref_to_general_def = res.ref_to_general_definition

    #     para_ref_to_general_def_text = ''
    #     if para_ref_to_general_def:
    #         para_ref_to_general_def_text = res.general_definition_id.text

    #     para_ref_to_paragraph = res.ref_to_paragraph
    #     para_ref_to_para_text = ''

    #     if para_ref_to_paragraph:
    #         para_ref_to_para_text = res.ref_paragraph_id.text

    #     is_ref_actor = (para_ref_to_general_def or para_ref_to_paragraph)

    #     ref_text = ''

    #     if para_ref_to_general_def:
    #         ref_text = para_ref_to_general_def_text
    #     elif para_ref_to_paragraph:
    #         ref_text = para_ref_to_para_text

    #     paragraph_info = {
    #         'document_id': document_id,
    #         'document_name': document_name,
    #         'text': paragraph_text,
    #         'actor_form': paragraph_actor_form,
    #         'actor_name': paragraph_actor_name,
    #         'is_ref_actor': is_ref_actor,
    #         'ref_text': ref_text
    #     }

    #     if paragraph_id not in actor_paragraphs_result:
    #         actor_paragraphs_result[paragraph_id] = paragraph_info

    # return JsonResponse({"actor_paragraphs_result": actor_paragraphs_result})
    return JsonResponse({"test": paragraphs_id})


def GetColumnParagraphsByActorRoleName_Modal(request, country_id, actor_name, role_name, keywords_text):
    doc_paragraphs = DocumentActor.objects.filter(
        document_id__country_id__id=country_id,
        actor_id__name=actor_name, actor_type_id__name=role_name)

    result = []
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')

        result = doc_paragraphs.filter(reduce(
            operator.or_, (Q(paragraph_id__text__icontains=kw + ' ') for kw in keywords_list)))

    else:
        result = doc_paragraphs

    actor_paragraphs_result = {}
    for res in result:

        paragraph_id = res.paragraph_id.id
        document_id = res.document_id.id
        document_name = res.document_id.name
        paragraph_text = res.paragraph_id.text
        paragraph_actor_role = res.actor_type_id.name
        paragraph_actor_form = res.current_actor_form
        paragraph_actor_name = res.actor_id.name

        para_ref_to_general_def = res.ref_to_general_definition

        para_ref_to_general_def_text = ''
        if para_ref_to_general_def:
            para_ref_to_general_def_text = res.general_definition_id.text

        para_ref_to_paragraph = res.ref_to_paragraph
        para_ref_to_para_text = ''

        if para_ref_to_paragraph:
            para_ref_to_para_text = res.ref_paragraph_id.text

        is_ref_actor = (para_ref_to_general_def or para_ref_to_paragraph)

        ref_text = ''

        if para_ref_to_general_def:
            ref_text = para_ref_to_general_def_text
        elif para_ref_to_paragraph:
            ref_text = para_ref_to_para_text

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

    return JsonResponse({"actor_paragraphs_result": actor_paragraphs_result})


def GetColumnParagraphsByActorRoleName_Modal_es(request, country_id, actor_name, role_name, keywords_text, curr_page):
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

    if len(res_query['bool']['filter']) == 0:
        del res_query['bool']['filter']

    if keywords_text != "empty":
        res_query["bool"]["must"] = []
        res_query = filter_document_actor_text(res_query, keywords_text, 'filter' not in res_query['bool'])

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
        paragraph_id = res["_source"]["paragraph_id"]
        document_id = res["_source"]["document_id"]
        document_name = res["_source"]["document_name"]
        paragraph_text = res["_source"]["attachment"]['content'] if keywords_text == "empty" else \
            res["highlight"]["attachment.content"][0]
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




def GetActorsKeywordsGraphData(request, country_id, roles_id, category_id, actors_id, keywords_text):
    nodes = []
    edges = []
    actors_graph_data = {}
    roles_id = roles_id.split("__")
    actors_id = actors_id.split("__")

    keywords_list = keywords_text.split(',')

    for keyword in keywords_list:
        keyword_node = {'id': keyword, 'group': 'keywords', 'fill': {
            'src': "../../static/icons/keywords_icons/keyword1.png"
        }}
        nodes.append(keyword_node)

        selected_actors = []

        selected_actors = DocumentActor.objects.filter(
            document_id__country_id__id=country_id, paragraph_id__text__icontains=keyword + ' ')

        if '0' not in roles_id:
            selected_actors = selected_actors.filter(
                actor_type_id__id__in=roles_id)

        if '0' not in actors_id:
            selected_actors = selected_actors.filter(
                actor_id__id__in=actors_id)

        else:
            if category_id != 0:
                selected_actors = selected_actors.filter(
                    actor_id__actor_category_id__id=category_id)

        for res in selected_actors:
            # Upper case
            Actor_Name = res.actor_id.name
            Actor_ID = res.actor_id.id
            Actor_Role_Name = res.actor_type_id.name
            Actor_Role_ID = res.actor_type_id.id

            actor_node = {'id': Actor_Name, 'group': 'actors', 'fill': {
                'src': "../../static/icons/actors_icons/actor_icon3.png"
            }}

            nodes.append(actor_node)

            edge = {
                'from': Actor_Name,
                'to': keyword,
                'destination_node_type': 'keyword',
                'actor_role_name': Actor_Role_Name,
                'role_id': Actor_Role_ID,
                'actor_id': Actor_ID,

            }
            edges.append(edge)

    actors_graph_data['nodes'] = nodes
    actors_graph_data['edges'] = edges

    return JsonResponse({"actors_graph_data": actors_graph_data})


def GetActorsKeywordsGraphData_es(request, country_id, roles_id, category_id, actors_id, keywords_text):
    nodes = []
    edges = []
    actors_graph_data = {}
    roles_id = roles_id.split("__")
    actors_id = actors_id.split("__")
    keyword_num = 0
    actor_set = set()

    keywords_list = keywords_text.split(',')

    for keyword in keywords_list:

        if keyword == "empty":
            continue

        keyword_node = {'id': keyword, 'group': 'keywords', 'fill': {
            'src': "../../static/icons/keywords_icons/keyword1.png"
        }}
        nodes.append(keyword_node)

        res_query = {
            "bool": {
            }
        }

        res_query['bool']['filter'] = []
        res_query = filter_document_actor_fields(
            res_query,
            role_ids=roles_id,
            actor_ids=actors_id)

        if len(res_query['bool']['filter']) == 0:
            del res_query['bool']['filter']

        res_query["bool"]["must"] = []
        res_query = filter_document_actor_text(res_query, keyword, 'filter' not in res_query['bool'])

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

            },
        }

        response = client.search(index=index_name,
                                 _source_includes=[],
                                 request_timeout=40,
                                 query=res_query,
                                 aggregations=res_agg,
                                 # from_=from_value,
                                 size=0,
                                 # track_total_hits=True,
                                 )

        aggregations = response['aggregations']

        if len(aggregations['actor-name-agg']['buckets']) > 0:
            keyword_num += 1

        for actor in aggregations['actor-name-agg']['buckets']:
            # Upper case
            Actor_Name = actor["key"][0]
            Actor_ID = actor["key"][1]
            actor_set.add(Actor_ID)

            actor_node = {'id': Actor_Name, 'group': 'actors', 'fill': {
                'src': "../../static/icons/actors_icons/actor_icon3.png"
            }}
            nodes.append(actor_node)

            # for role in actor["actor-type-name-agg"]['buckets']:
            #     Actor_Role_Name = role["key"][0]
            #     Actor_Role_ID = role["key"][1]

            edge = {
                'from': Actor_Name,
                'to': keyword,
                'destination_node_type': 'keyword',
                # 'actor_role_name': Actor_Role_Name,
                # 'role_id': Actor_Role_ID,
                'actor_id': Actor_ID,

            }
            edges.append(edge)

    actors_graph_data['nodes'] = nodes
    actors_graph_data['edges'] = edges

    return JsonResponse({"actors_graph_data": actors_graph_data,
                         'actor_num': len(list(actor_set)),
                         'keyword_num': keyword_num})


def GetActorsEdgeParagraphsByKeyword_Modal(request, country_id, actor_id, roles_id, keyword):
    roles_id = roles_id.split("__")

    actor_paragraphs_result = {}

    actor_paragraphs = DocumentActor.objects.filter(
        document_id__country_id__id=country_id,
        actor_id__id=actor_id,
        paragraph_id__text__icontains=keyword + ' ')

    if '0' not in roles_id:
        actor_paragraphs = actor_paragraphs.filter(
            actor_type_id__id__in=roles_id)

    for res in actor_paragraphs:

        paragraph_id = res.paragraph_id.id
        document_id = res.document_id.id
        document_name = res.document_id.name
        paragraph_text = res.paragraph_id.text
        paragraph_actor_role = res.actor_type_id.name
        paragraph_actor_form = res.current_actor_form
        paragraph_actor_name = res.actor_id.name

        para_ref_to_general_def = res.ref_to_general_definition

        para_ref_to_general_def_text = ''
        if para_ref_to_general_def:
            para_ref_to_general_def_text = res.general_definition_id.text

        para_ref_to_paragraph = res.ref_to_paragraph
        para_ref_to_para_text = ''

        if para_ref_to_paragraph:
            para_ref_to_para_text = res.ref_paragraph_id.text

        is_ref_actor = (para_ref_to_general_def or para_ref_to_paragraph)

        ref_text = ''

        if para_ref_to_general_def:
            ref_text = para_ref_to_general_def_text
        elif para_ref_to_paragraph:
            ref_text = para_ref_to_para_text

        paragraph_info = {
            'document_id': document_id,
            'document_name': document_name,
            'text': paragraph_text,
            'actor_form': paragraph_actor_form,
            'actor_name': paragraph_actor_name,
            'is_ref_actor': is_ref_actor,
            'ref_text': ref_text
        }

        if paragraph_actor_role not in actor_paragraphs_result:
            actor_paragraphs_result[paragraph_actor_role] = {paragraph_id: paragraph_info}

        else:
            paragraphs_dict = actor_paragraphs_result[paragraph_actor_role]
            if paragraph_id not in paragraphs_dict:
                paragraphs_dict[paragraph_id] = paragraph_info
                actor_paragraphs_result[paragraph_actor_role] = paragraphs_dict

    return JsonResponse({"actor_paragraphs_result": actor_paragraphs_result})


def GetActorsEdgeParagraphsByKeyword_Modal_es(request, country_id, actor_id, roles_id, keyword, curr_page):
    roles_id = roles_id.split("__")

    detail_result_size = 10
    res_query = {
        "bool": {
        }
    }

    res_query['bool']['filter'] = []
    res_query = filter_document_actor_fields(
        res_query,
        role_ids=roles_id,
        actor_id=actor_id)

    if len(res_query['bool']['filter']) == 0:
        del res_query['bool']['filter']

    if keyword != "empty":
        res_query["bool"]["must"] = []
        res_query = filter_document_actor_text(res_query, keyword, 'filter' not in res_query['bool'])

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentActor.__name__)

    from_value = (curr_page - 1) * detail_result_size

    # print(res_query)

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

    actor_paragraphs_result = {}

    # print(response['hits']['hits'])

    for res in response['hits']['hits']:

        paragraph_id = res["_source"]["paragraph_id"]
        document_id = res["_source"]["document_id"]
        document_name = res["_source"]["document_name"]
        paragraph_text = res["_source"]["attachment"]['content'] if keyword == "empty" else \
            res["highlight"]["attachment.content"][0]
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

        if paragraph_actor_role not in actor_paragraphs_result:
            actor_paragraphs_result[paragraph_actor_role] = {paragraph_id: paragraph_info}

        else:
            paragraphs_dict = actor_paragraphs_result[paragraph_actor_role]
            if paragraph_id not in paragraphs_dict:
                paragraphs_dict[paragraph_id] = paragraph_info
                actor_paragraphs_result[paragraph_actor_role] = paragraphs_dict

    return JsonResponse({"actor_paragraphs_result": actor_paragraphs_result,
                         'max_page': max_page})


def GetActorsSupervisorsGraphData(request, country_id, area_id, actors_id, keywords_text):
    actors_id = actors_id.split("__")
    result_paragraphs = ActorSupervisor.objects.filter(document_id__country_id__id=country_id)

    if '0' in actors_id:
        if area_id != 0:
            result_paragraphs = result_paragraphs.filter(
                Q(source_actor_id__area__id=area_id) |
                Q(supervisor_actor_id__area__id=area_id))

    else:
        result_paragraphs = result_paragraphs.filter(
            Q(source_actor_id__id__in=actors_id) |
            Q(supervisor_actor_id__id__in=actors_id))

    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')

        result_paragraphs = result_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_id__text__icontains=word + ' ') for word in keywords_list)))

    nodes = []
    edges = []
    actors_supervisors_graph_data = {}

    for res in result_paragraphs:
        source_actor_id = res.source_actor_id.id
        source_actor_name = res.source_actor_id.name
        supervisor_id = res.supervisor_actor_id.id
        supervisor_name = res.supervisor_actor_id.name

        source_node = {'id': source_actor_name, 'group': 'source_actors', 'fill': {
            'src': "../../static/icons/actors_icons/actor_icon3.png"
        }}

        nodes.append(source_node)

        supervisor_node = {'id': supervisor_name, 'group': 'supervisors_actors', 'fill': {
            'src': "../../static/icons/actors_icons/supervisor3.png"
        }}

        nodes.append(supervisor_node)
        edge = {
            'from': source_actor_name,
            'to': supervisor_name,
            'source_id': source_actor_id,
            'supervisor_id': supervisor_id}

        edges.append(edge)

    actors_supervisors_graph_data['nodes'] = nodes
    actors_supervisors_graph_data['edges'] = edges

    return JsonResponse({"actors_supervisors_graph_data": actors_supervisors_graph_data})


def GetActorsSupervisorsGraphData_ES(request, country_id, area_id, actors_id, keywords_text):
    actors_id = actors_id.split('__')
    source_set = set()
    sup_set = set()

    res_query = {
        "bool": {
        }
    }

    res_query['bool']['filter'] = []
    res_query = filter_actor_supervisor_fields(res_query, area_id=area_id, actor_ids=actors_id)

    if len(res_query['bool']['filter']) == 0:
        del res_query['bool']['filter']

    if keywords_text != "empty":
        res_query["bool"]["must"] = []
        res_query = filter_document_actor_text(res_query, keywords_text, 'filter' not in res_query['bool'])

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, ActorSupervisor.__name__)

    response = client.search(index=index_name,
                             _source_includes=[
                                 'source_actor_id',
                                 'supervisor_actor_id',
                                 'source_actor_name',
                                 'supervisor_actor_name',
                             ],
                             request_timeout=40,
                             query=res_query,
                             # aggregations=res_agg,
                             # from_=from_value,
                             # size=search_result_size
                             size=5000,
                             # track_total_hits=True,
                             )

    result = response['hits']['hits']

    print(res_query)
    print(len(response['hits']['hits']))

    nodes = []
    edges = []
    actors_supervisors_graph_data = {}

    for res in result:
        source_actor_id = res['_source']['source_actor_id']
        source_actor_name = res['_source']['source_actor_name']
        supervisor_id = res['_source']['supervisor_actor_id']
        supervisor_name = res['_source']['supervisor_actor_name']
        source_set.add(source_actor_id)
        sup_set.add(supervisor_id)

        source_node = {'id': source_actor_name, 'group': 'source_actors', 'fill': {
            'src': "../../static/icons/actors_icons/actor_icon3.png"
        }}

        nodes.append(source_node)

        supervisor_node = {'id': supervisor_name, 'group': 'supervisors_actors', 'fill': {
            'src': "../../static/icons/actors_icons/supervisor3.png"
        }}

        nodes.append(supervisor_node)
        edge = {
            'from': source_actor_name,
            'to': supervisor_name,
            'source_id': source_actor_id,
            'supervisor_id': supervisor_id}

        edges.append(edge)

    actors_supervisors_graph_data['nodes'] = nodes
    actors_supervisors_graph_data['edges'] = edges

    return JsonResponse({"actors_supervisors_graph_data": actors_supervisors_graph_data,
                         'source_num': len(list(source_set)),
                         'sup_num': len(list(sup_set))})


def getActorsInText(substring):
    actors_list = Actor.objects.all().values('id', 'name', 'forms')
    detected_actors = []
    for actor in actors_list:
        actor_forms_list = actor['forms'].split('/')
        for actor_form in actor_forms_list:
            if actor_form in substring:
                detected_actors.append([actor['name'], actor_form])

    return detected_actors


def GetActorsSupervisorsEdge_Modal(request, country_id, source_actor_id, supervisor_id, keywords_text):
    supervisors_paragraphs = ActorSupervisor.objects.filter(
        document_id__country_id__id=country_id,
        source_actor_id__id=source_actor_id, supervisor_actor_id__id=supervisor_id).values(
        'paragraph_id__text', 'paragraph_id__id',
        'document_id__id', 'document_id__name',
        'source_actor_form', 'supervisor_actor_form').annotate(
        paragraph_text=F('paragraph_id__text'),
        document_name=F('document_id__name'),
    )

    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')
        supervisors_paragraphs = supervisors_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_text__icontains=word + ' ') for word in keywords_list)))

    paragraphs_dict_result = {}

    for res in supervisors_paragraphs:
        paragraph_id = res['paragraph_id__id']
        document_id = res['document_id__id']
        document_name = res['document_name']
        paragraph_text = res['paragraph_text']
        source_actor_form = res['source_actor_form']
        supervisor_actor_form = res['supervisor_actor_form']

        paragraphs_dict_result[paragraph_id] = {
            'document_id': document_id,
            'document_name': document_name,
            'paragraph_text': paragraph_text,
            'source_actor_form': source_actor_form,
            'supervisor_actor_form': supervisor_actor_form
        }

    return JsonResponse({"paragraphs_dict_result": paragraphs_dict_result})


def GetActorsSupervisorsEdge_Modal_es(request, country_id, source_actor_id, supervisor_id, keywords_text, curr_page):
    detail_result_size = 10
    res_query = {
        "bool": {
            'filter': [
                {
                    "term": {
                        "supervisor_actor_id": supervisor_id,
                    }
                },
                {
                    "term": {
                        "source_actor_id": source_actor_id,
                    }
                }
            ]
        }
    }

    if keywords_text != "empty":
        res_query["bool"]["must"] = []
        res_query = filter_document_actor_text(res_query, keywords_text, 'filter' not in res_query['bool'])

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, ActorSupervisor.__name__)

    from_value = (curr_page - 1) * detail_result_size

    response = client.search(index=index_name,
                             _source_includes=['paragraph_id',
                                               'document_id',
                                               "document_name",
                                               'attachment.content',
                                               'supervisor_actor_form',
                                               'source_actor_form'],
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

    paragraphs_dict_result = {}

    for res in response['hits']['hits']:
        paragraph_id = res["_source"]["paragraph_id"]
        document_id = res["_source"]["document_id"]
        document_name = res["_source"]["document_name"]
        paragraph_text = res["_source"]["attachment"]['content'] if keywords_text == "empty" else \
            res["highlight"]["attachment.content"][0]
        source_actor_form = res["_source"]["source_actor_form"]
        supervisor_actor_form = res["_source"]["supervisor_actor_form"]

        paragraphs_dict_result[paragraph_id] = {
            'document_id': document_id,
            'document_name': document_name,
            'paragraph_text': paragraph_text,
            'source_actor_form': source_actor_form,
            'supervisor_actor_form': supervisor_actor_form
        }

    return JsonResponse({"paragraphs_dict_result": paragraphs_dict_result, 'max_page': max_page})


def GetActorRolesRadar_ChartData(request, country_id, roles_id, actor_id, keywords_text):
    roles_count_dict = {}
    roles_chart_data = []

    actor_paragraphs = DocumentActor.objects.filter(
        document_id__country_id__id=country_id,
        actor_id__id=actor_id)

    # Filter by keywords
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')
        actor_paragraphs = actor_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_id__text__icontains=' ' + kw) for kw in keywords_list)))

    actor_roles = ActorType.objects.all()

    for actor_role in actor_roles:
        role_name = actor_role.name

        role_count = actor_paragraphs.filter(
            actor_type_id__id=actor_role.id
        ).values('paragraph_id').distinct().count()

        roles_count_dict[role_name] = role_count

    supervisor_count = ActorSupervisor.objects.filter(
        document_id__country_id__id=country_id,
        supervisor_actor_id__id=actor_id).values('paragraph_id').distinct().count()

    regulator_count = DocumentRegulator.objects.filter(
        document_id__country_id__id=country_id,
        regulator_id__actor_id__id=actor_id).values('paragraph_id').distinct().count()

    roles_count_dict['نظارت'] = supervisor_count
    roles_count_dict['تنظیم‌گری'] = regulator_count

    roles_sum = sum(roles_count_dict.values())
    for role_name, role_count in roles_count_dict.items():
        role_percentage = round((role_count / roles_sum) * 100, 2) if roles_sum != 0 else 0
        point_data = {'x': role_name, 'value': role_percentage}

        roles_chart_data.append(point_data)

    return JsonResponse({"roles_chart_data": roles_chart_data})


def GetActorSubjectsRadar_ChartData(request, country_id, roles_id, actor_id, keywords_text):
    subjects_count_dict = {}
    subjects_chart_data = []

    actor_paragraphs = DocumentActor.objects.filter(
        document_id__country_id__id=country_id,
        actor_id__id=actor_id)

    # Filter by keywords
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')
        actor_paragraphs = actor_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_id__text__icontains=' ' + kw) for kw in keywords_list)))

    country_subjects = Document.objects.exclude(subject_name__isnull=True).values('subject_name').distinct()

    for subject in country_subjects:
        subject_name = subject['subject_name']

        subject_count_1 = actor_paragraphs.filter(
            document_id__subject_name=subject_name
        ).values('paragraph_id').distinct().count()

        subject_count_2 = ActorSupervisor.objects.filter(
            document_id__country_id__id=country_id,
            supervisor_actor_id__id=actor_id,
            document_id__subject_name=subject_name).values('paragraph_id').distinct().count()

        subject_count_3 = DocumentRegulator.objects.filter(
            document_id__country_id__id=country_id,
            regulator_id__actor_id__id=actor_id,
            document_id__subject_name=subject_name).values('paragraph_id').distinct().count()

        subject_count = subject_count_1 + subject_count_2 + subject_count_3
        subjects_count_dict[subject_name] = subject_count

    subjects_sum = sum(subjects_count_dict.values())

    for subject_name, subject_count in subjects_count_dict.items():
        subject_percentage = round((subject_count / subjects_sum) * 100, 2) if subjects_sum != 0 else 0

        point_data = {'x': subject_name, 'value': subject_percentage}
        subjects_chart_data.append(point_data)

    return JsonResponse({"subjects_chart_data": subjects_chart_data})


def GetActorGraphTypes(request):
    graph_types = ActorGraphType.objects.all()
    ActorGraphTypes = []

    for gt in graph_types:
        graph_type = {"id": gt.id,
                      "name": gt.name}

        ActorGraphTypes.append(graph_type)

    return JsonResponse({"ActorGraphTypes": ActorGraphTypes})


def Get_Actors_Correlation_GraphData(request, country_id, graph_type_id, role_name, min_sim, max_sim):
    min_sim = round((float(min_sim) / 100), 2)
    max_sim = round((float(max_sim) / 100), 2)

    is_area_graph = ActorGraphType.objects.get(id=graph_type_id).name == "گراف کلان حوزه ها"

    if is_area_graph:
        res_actors = CUBE_ActorArea_GraphData.objects.filter(country_id__id=country_id,
                                                             role_type=role_name, graph_type_id__id=graph_type_id,
                                                             similarity_value__gte=float(min_sim))
    else:
        res_actors = ActorsGraph.objects.filter(country_id__id=country_id,
                                                role_type=role_name, graph_type_id__id=graph_type_id,
                                                similarity_value__gte=float(min_sim))

    res_actors = res_actors.filter(similarity_value__lte=float(max_sim))

    nodes = []
    added_nodes = []
    edges = []
    added_edges = []
    GraphData = {}

    for res in res_actors:
        if is_area_graph:
            source_actor_id = str(res.src_actor_area_id.id)
            source_actor_name = res.src_actor_area_id.name
            dest_actor_id = str(res.dest_actor_area_id.id)
            dest_actor_name = res.dest_actor_area_id.name
        else:
            source_actor_id = str(res.src_actor_id.id)
            source_actor_name = res.src_actor_id.name
            dest_actor_id = str(res.dest_actor_id.id)
            dest_actor_name = res.dest_actor_id.name

        sim = res.similarity_value

        source_node = {'id': source_actor_id, 'name': source_actor_name, "size": 30}

        if source_actor_id not in added_nodes:
            nodes.append(source_node)
            added_nodes.append(source_actor_id)

        dest_node = {'id': dest_actor_id, 'name': dest_actor_name, "size": 30}

        if dest_actor_id not in added_nodes:
            nodes.append(dest_node)
            added_nodes.append(dest_actor_id)

        edge_size = 5
        if max_sim > min_sim:
            norm_sim = (sim - min_sim) / (max_sim - min_sim)
            edge_size = 1 + norm_sim * 4

        if dest_actor_id + source_actor_id not in added_edges:
            edge = {
                'source': source_actor_id,
                'target': dest_actor_id,
                'source_name': source_actor_name,
                'target_name': dest_actor_name,
                'weight': sim * 100,
                'size': edge_size
            }

            edges.append(edge)

            added_edges.append(source_actor_id + dest_actor_id)

    GraphData['nodes'] = nodes
    GraphData['edges'] = edges

    return JsonResponse({"GraphData": GraphData})


def GetSubjectStatistics_ChartData(request, country_id, document_tab_type):
    all_charts_data = CUBE_SubjectStatistics_ChartData.objects.get(
        country_id=country_id,
        document_tab_type=document_tab_type)

    subject_data = all_charts_data.subject_chart_data
    approval_references_data = all_charts_data.approval_reference_chart_data
    level_data = all_charts_data.level_chart_data
    approval_year_data = all_charts_data.approval_year_chart_data
    type_data = all_charts_data.type_chart_data

    return JsonResponse({'subject_chart_data': subject_data['data'],
                         'approval_references_chart_data': approval_references_data['data'],
                         'level_chart_data': level_data['data'],
                         'approval_year_chart_data': approval_year_data['data'],
                         'type_chart_data': type_data['data'],
                         })


def GetSubjectStatistics_Column_Modal(request, country_id, document_tab_type, chart_type, column_name):
    document_list = []

    document_result = CUBE_SubjectStatistics_FullData.objects.filter(
        country_id=country_id, document_tab_type=document_tab_type)

    if chart_type == 'subject_chart_data':
        document_result = document_result.filter(subject_name=column_name)

    if chart_type == 'level_chart_data':
        document_result = document_result.filter(level_name=column_name)

    if chart_type == 'type_chart_data':
        document_result = document_result.filter(type_name=column_name)

    if chart_type == 'approval_reference_chart_data':
        document_result = document_result.filter(approval_reference_name=column_name)

    if chart_type == 'approval_year_chart_data':
        document_result = document_result.filter(approval_date__icontains=column_name)

    for res in document_result:
        doc_info = {'document_id': res.document_id.id, 'document_name': res.document_name,
                    'subject_name': res.subject_name, 'type_name': res.type_name,
                    'level_name': res.level_name, 'approval_reference_name': res.approval_reference_name,
                    'approval_date': res.approval_date}
        document_list.append(doc_info)

    return JsonResponse({'document_list': document_list})


def SearchDocumentsByKeywords(request, country_id, level_id, subject_id, type_id, approval_reference_id, from_year,
                              to_year,
                              place, keywords_text):
    # Filter Documents
    documents_list = Document.objects.filter(country_id_id=country_id)

    if level_id > 0:
        documents_list = documents_list.filter(level_id_id=level_id)

    if subject_id > 0:
        documents_list = documents_list.filter(subject_id_id=subject_id)

    if type_id > 0:
        documents_list = documents_list.filter(type_id_id=type_id)

    if approval_reference_id > 0:
        documents_list = documents_list.filter(
            approval_reference_id_id=approval_reference_id)

    if from_year > 0:
        documents_list = documents_list

    if to_year > 0:
        documents_list = documents_list

    # preprocess and split search text
    kw_list = keywords_text.split(',')

    if place == "عنوان":
        documents_list = documents_list.filter(
            reduce(operator.or_, (Q(name__icontains=kw) for kw in kw_list))).annotate(
            document_id=F('id')).values("document_id")

    elif place == "متن":
        documents_list = DocumentParagraphs.objects.filter(
            reduce(operator.or_, (Q(text__icontains=kw) for kw in kw_list)),
            document_id__in=documents_list).values("document_id")

    elif place == "تعاریف":
        documents_list = DocumentGeneralDefinition.objects.filter(
            reduce(operator.or_, (Q(keyword__icontains=kw) for kw in kw_list)), document_id__in=documents_list).values(
            "document_id")

    else:
        documents_list_title = documents_list.filter(
            reduce(operator.or_, (Q(name__icontains=kw) for kw in kw_list))).annotate(
            document_id=F('id')).values("document_id")

        documents_list_text = DocumentParagraphs.objects.filter(
            reduce(operator.or_, (Q(text__icontains=kw) for kw in kw_list)),
            document_id__in=documents_list).values("document_id")

        documents_list = documents_list_title.union(documents_list_text)

    documents_list = documents_list.distinct()
    # ---------- Generate Data -------------

    documents_information_list = []
    for doc in documents_list:
        # Generate Document List Table Data
        document_id = doc["document_id"]
        document_information = GetDocumentById_Local(document_id)
        document_information["keywords"] = GetExistedKeywords_ByDocumentId(document_id, place, kw_list)
        document_information["keywords_count"] = len(document_information["keywords"])

        documents_information_list.append(document_information)

    return JsonResponse({'documents_information_result': documents_information_list})


def GetExistedKeywords_ByDocumentId(document_id, place, kw_list):
    result_keywords = []

    if 'عنوان' in place:
        document_name = Document.objects.get(id=document_id).name

        for kw in kw_list:
            if kw in document_name:
                result_keywords.append(kw)

    if 'متن' in place:
        for kw in kw_list:

            kw_flag = DocumentParagraphs.objects.filter(
                document_id=document_id,
                text__icontains=kw
            ).exists()

            if kw_flag and kw not in result_keywords:
                result_keywords.append(kw)

    return result_keywords


def GetLocalTextFile(request, name):
    path = os.path.join("./text_files/Persian", name)
    file_text = open(path, mode='r', encoding='utf-8').read()
    return JsonResponse({'file_text': file_text})


def GetAraByCountry_id(request, country_id):
    documents_information_list = []

    result_docs = CUBE_Votes_TableData.objects.filter(country_id=country_id)

    for res in result_docs:
        documents_information_list += res.table_data['data']

    return JsonResponse({"documents_information_list": documents_information_list})


def GetAraChartsData_ByCountryId(request, country_id):
    country_charts = CUBE_Votes_ChartData.objects.get(country_id__id=country_id)

    subject_data = country_charts.subject_chart_data['data']
    approval_references_data = country_charts.approval_reference_chart_data['data']
    level_data = country_charts.level_chart_data['data']
    approval_year_data = country_charts.approval_year_chart_data['data']
    type_data = country_charts.type_chart_data['data']
    keywords_data = country_charts.keywords_chart_data['data']

    return JsonResponse({'subject_chart_data': subject_data,
                         'approval_references_chart_data': approval_references_data,
                         'level_chart_data': level_data,
                         'approval_year_chart_data': approval_year_data,
                         'type_chart_data': type_data,
                         'keywords_chart_data': keywords_data
                         })


def GetPrinciples(request, country, text=''):
    principles = CUBE_Principles_TableData.objects.filter(text__icontains=text, country_id=country)
    result = []
    for p in principles:
        result.append(p.table_data)

    return JsonResponse({'result': result})


def GetPrinciple_ChartsData(request, country, text=''):
    principles = CUBE_Principles_ChartData.objects.filter(principle_name__icontains=text, country_id=country)
    result = []
    for principle in principles:
        subject_data = principle.subject_chart_data['data']
        approval_references_data = principle.approval_reference_chart_data['data']
        level_data = principle.level_chart_data['data']
        approval_year_data = principle.approval_year_chart_data['data']
        type_data = principle.type_chart_data['data']
        documents_information_result_data = principle.documents_information_result_data['data']
        result.append({'subject_chart_data': subject_data,
                       'approval_references_chart_data': approval_references_data,
                       'level_chart_data': level_data,
                       'approval_year_chart_data': approval_year_data,
                       'type_chart_data': type_data,
                       'documents_information_result_data': documents_information_result_data
                       })
    return JsonResponse({'result': result})


def GetMandatoryRegulations(request, country_id):
    result_data = CUBE_MandatoryRegulations_TableData.objects.filter(country_id_id=country_id)
    documents_information_result = []
    unknown_results = []
    for res in result_data:
        table_data = res.table_data
        if table_data['is_unknown']:
            unknown_results.append(table_data)
        else:
            documents_information_result.append(table_data)
    return JsonResponse({'documents_information_result': documents_information_result,
                         'unknown_results': unknown_results})


def CompareRegulatorAndLaw(request, regulator_id):
    mandatory_regulation = CUBE_MandatoryRegulations_TableData.objects.get(document_id_id=regulator_id)
    regulator = Document.objects.get(id=regulator_id)
    regulator_paragraphs = DocumentParagraphs.objects.filter(document_id__id=regulator.id) \
        .order_by('number').values('text')
    regulator_text = [p['text'] for p in regulator_paragraphs]

    law_id = mandatory_regulation.table_data['law_id']
    law = Document.objects.get(id=law_id)
    paras = mandatory_regulation.table_data['paragraphs']
    while len(paras) < 3:
        paras.append(max(paras) + 1)
    law_paragraphs = DocumentParagraphs.objects.filter(document_id__id=law_id,
                                                       id__in=paras).order_by(
        'number').values('text')
    law_text = [p['text'] for p in law_paragraphs]

    last_paragraph_id = max(mandatory_regulation.table_data['paragraphs'])
    last_paragraph = DocumentParagraphs.objects.get(id=last_paragraph_id)
    next_paragraph = DocumentParagraphs.objects.filter(document_id=last_paragraph.document_id,
                                                       id=last_paragraph_id + 1)
    if next_paragraph.count() == 0:
        next_paragraph = ''
    else:
        next_paragraph = next_paragraph[0].text

    return JsonResponse({
        'last_paragraph': max(mandatory_regulation.table_data['paragraphs']),
        'next_paragraph': next_paragraph,
        'regulator_id': regulator.id,
        'regulator_name': regulator.name,
        'regulator_text': regulator_text,
        'law_id': law.id,
        'law_name': law.name,
        'law_text': law_text,
    })


def GetNextParagraph(request, paragraph_id):
    last_paragraph = DocumentParagraphs.objects.get(id=paragraph_id)
    paragraph = DocumentParagraphs.objects.filter(document_id=last_paragraph.document_id, id=paragraph_id + 1)

    if paragraph.count() == 0:
        result = ''
    else:
        result = paragraph[0].text

    return JsonResponse({
        'paragraph_text': result,
    })


def GetMandatoryRegulations2(request, country_id):
    table_data = CUBE_MandatoryRegulations_TableData.objects.filter(country_id_id=country_id)
    chart_data = CUBE_MandatoryRegulations_ChartData.objects.filter(country_id_id=country_id)
    if chart_data.count() > 0:
        chart_data = chart_data[0].chart_data
    else:
        chart_data = {
            'documents_information_result': [],
            'subject_chart_data': {},
            'approval_references_chart_data': {},
            'approval_year_chart_data': {},
        }
    executive_list = []
    for res in table_data:
        executive_list.append(res.table_data)
    return JsonResponse({
        'executive_list': executive_list,
        'documents_information_result': chart_data['documents_information_result'],
        'subject_chart_data': chart_data['subject_chart_data'],
        'approval_references_chart_data': chart_data['approval_references_chart_data'],
        'approval_year_chart_data': chart_data['approval_year_chart_data'],
    })


def GetMandatoryRegulationsDetail(request, regulator_id):
    mandatory_regulation = CUBE_MandatoryRegulations_TableData.objects.get(document_id_id=regulator_id)
    # regulator = Document.objects.get(id=regulator_id)
    # regulator_paragraphs = DocumentParagraphs.objects.filter(document_id__id=regulator.id) \
    #     .order_by('number').values('text')
    # regulator_text = [p['text'] for p in regulator_paragraphs]
    #
    # law_id = mandatory_regulation.table_data['law_id']
    # law = Document.objects.get(id=law_id)
    # paras = mandatory_regulation.table_data['paragraphs']
    # while len(paras) < 3:
    #     paras.append(max(paras)+1)
    # law_paragraphs = DocumentParagraphs.objects.filter(document_id__id=law_id,
    #                                                    id__in=paras).order_by(
    #     'number').values('text')
    # law_text = [p['text'] for p in law_paragraphs]
    #
    # last_paragraph_id = max(mandatory_regulation.table_data['paragraphs'])
    # last_paragraph = DocumentParagraphs.objects.get(id=last_paragraph_id)
    # next_paragraph = DocumentParagraphs.objects.filter(document_id=last_paragraph.document_id,
    #                                                    id=last_paragraph_id+1)
    # if next_paragraph.count() == 0:
    #     next_paragraph = ''
    # else:
    #     next_paragraph = next_paragraph[0].text

    return JsonResponse({
        'paragraph_text': mandatory_regulation.table_data['paragraphs'],
        # 'last_paragraph': max(mandatory_regulation.table_data['paragraphs']),
        # 'next_paragraph': next_paragraph,
        # 'regulator_id': regulator.id,
        # 'regulator_name': regulator.name,
        # 'regulator_text': regulator_text,
        # 'law_id': law.id,
        # 'law_name': law.name,
        # 'law_text': law_text,
    })


# AI Function
def AIGetGraphSimilarityMeasure(request):
    return JsonResponse({'measure_list': [{'id': 1, 'name': 'استفاده از bert'}]})


def AIGetDocSimilarity(request, country_id, measure_id):
    if int(measure_id) == 1:
        result = []
        similarities = AISimilarityDoc.objects.filter(document_id1__country_id=country_id,
                                                      document_id2__country_id=country_id).order_by('sim').values()
        sims = []
        for s in similarities:
            sims.append(s['sim'])
        sims = Counter(sims)
        for key, value in sims.items():
            result.append({"similarity": key, "count": value})
        return JsonResponse({'graph_distribution': result})
    else:
        return JsonResponse({'graph_distribution': [{"similarity": 0, "count": 0}]})


def AIGetGraphEdgesByDocumentIdMeasure(request, country_id, src_doc_id, src_type_id, src_subject_id,
                                       dest_doc_id, dest_type_id, dest_subject_id, measure_id, weight):
    # Filter Documents Source
    src_document_list = []
    if src_doc_id != 0:
        src_document_list.append(src_doc_id)
    else:
        src_document_list = GetDocumentByCountryTypeSubject(
            request, country_id, src_type_id, src_subject_id)

    # Filter Documents Destination
    dest_document_list = []
    if dest_doc_id != 0:
        dest_document_list.append(dest_doc_id)
    else:
        dest_document_list = GetDocumentByCountryTypeSubject(
            request, country_id, dest_type_id, dest_subject_id)

    # Select Graph by Measure and weight
    graph_edge_list = AISimilarityDoc.objects.filter(document_id1__in=src_document_list,
                                                     document_id2__in=dest_document_list,
                                                     sim__gte=float(weight))

    result = []
    for edge in graph_edge_list:

        src_id = edge.document_id1_id
        src_name = edge.document_id1.name
        src_color = "#0"
        if edge.document_id1.type_id != None:
            src_color = edge.document_id1.type_id.color

        dest_id = edge.document_id2_id
        dest_name = edge.document_id2.name
        dest_color = "#0"
        if edge.document_id2.type_id != None:
            dest_color = edge.document_id2.type_id.color

        weight = edge.sim

        res = {
            "src_id": src_id,
            "src_name": src_name,
            "src_color": src_color,
            "dest_id": dest_id,
            "dest_name": dest_name,
            "dest_color": dest_color,
            "weight": weight,
        }

        result.append(res)

    graph_type = Measure.objects.get(id=measure_id).type

    return JsonResponse({'graph_edge_list': result, "graph_type": graph_type})


def AIGetDocSimilarities(request, country_id):
    return JsonResponse({
        'regulator_id': []
    })






























# collective
def SearchDocumentsByCollectiveActorsKeywords(request, country_id, collectives_id, category_id, actors_id,
                                              membership_type, keywords_text, min_members_count):
    documents_information_dict = {}
    doc_paragraphs = []
    collectives_id = collectives_id.split("__")
    actors_id = actors_id.split('__')

    doc_paragraphs = DocumentCollectiveMembers.objects.filter(document_id__country_id__id=country_id,
                                                              members_count__gte=min_members_count)

    # Filter by collectives id
    if '0' not in collectives_id:
        doc_paragraphs = doc_paragraphs.filter(collective_actor_id__id__in=collectives_id)

    # Filter by keywords
    if keywords_text != 'empty':
        keywords_list = keywords_text.split(',')
        doc_paragraphs = doc_paragraphs.filter(
            reduce(operator.or_, (Q(paragraph_id__text__icontains=' ' + kw) for kw in keywords_list)))

    selected_actor_ids = []
    selected_actors = []

    if '0' not in actors_id:
        selected_actors = Actor.objects.filter(id__in=actors_id)
    else:
        if category_id != 0:
            selected_actors = Actor.objects.filter(actor_category_id__id=category_id)

    for actor in selected_actors:
        selected_actor_ids.append(actor.id)

    for res in doc_paragraphs:
        members_info = res.members
        members_count = res.members_count

        doc_id = res.document_id.id
        doc_info = {}
        document_information = GetDocumentById_Local(doc_id)
        doc_info['id'] = doc_id
        doc_info['name'] = res.document_id.name
        doc_info['subject'] = document_information["subject"]
        doc_info['approval_reference'] = document_information["approval_reference"]
        doc_info['approval_date'] = document_information["approval_date"]
        has_next_paragraph_members = res.has_next_paragraph_members

        collective_actor_type_name = res.collective_actor_id.name

        members_count_msg = collective_actor_type_name + (
            'ی با' if (collective_actor_type_name != 'کمیته') else '‌ای با') + ' (' + str(members_count) + ' عضو' + ')'

        if len(selected_actor_ids) != 0:

            if (not has_next_paragraph_members):
                members_id = [int(member_id) for member_id in members_info.keys() if (not has_next_paragraph_members)]

                OR_membership_condition = (membership_type == 'OR' and any(
                    int(member_id) in selected_actor_ids for member_id in members_info))
                And_membership_condition = (membership_type == 'And' and all(
                    selected_actor_id in members_id for selected_actor_id in selected_actor_ids))

                if OR_membership_condition or And_membership_condition:
                    if doc_id not in documents_information_dict:
                        doc_info['collective_counts'] = [members_count_msg]
                        documents_information_dict[doc_id] = doc_info
                    else:
                        doc_info_2 = documents_information_dict[doc_id]
                        doc_info_2['collective_counts'].append(members_count_msg)
                        documents_information_dict[doc_id] = doc_info_2

        else:  # all actors selected
            if membership_type == 'OR':
                if doc_id not in documents_information_dict:
                    doc_info['collective_counts'] = [members_count_msg]
                    documents_information_dict[doc_id] = doc_info
                else:
                    doc_info_2 = documents_information_dict[doc_id]
                    doc_info_2['collective_counts'].append(members_count_msg)
                    documents_information_dict[doc_id] = doc_info_2

    return JsonResponse({"documents_information_dict": documents_information_dict})


def filter_collective_actors_fields(res_query, collectives_id, category_id, actors_id, membership_type,
                                    min_members_count):
    if "0" not in collectives_id:
        collective_actor_query = {
            "terms": {
                "collective_actor_id": collectives_id
            }
        }
        res_query['bool']['filter'].append(collective_actor_query)

    # ---------------------------------------------------------
    if "0" not in actors_id:
        or_actor_query = {
            "terms": {
                "members.id": actors_id
            }
        }
        and_actor_query = [{
            "term": {
                "members.id": actor_id
            }
        } for actor_id in actors_id]

        if membership_type == 'OR':
            res_query['bool']['filter'].append(or_actor_query)
        else:
            res_query['bool']['must'] += and_actor_query

    # ---------------------------------------------------------
    if "0" in actors_id:
        ActorsList = []
        if category_id != 0:
            actors = Actor.objects.filter(actor_category_id__id=category_id).values(
                'id', 'name').distinct().order_by('name')

            for actor in actors:
                ActorsList.append(actor['id'])
        else:
            actors = Actor.objects.values('id', 'name').distinct().order_by('name')

            for actor in actors:
                ActorsList.append(actor['id'])

        or_actor_query = {
            "terms": {
                "members.id": ActorsList
            }
        }
        and_actor_query = [{
            "term": {
                "members.id": actor_id
            }
        } for actor_id in ActorsList]

        if membership_type == 'OR':
            res_query['bool']['filter'].append(or_actor_query)
        else:
            res_query['bool']['must'] += and_actor_query

            # ---------------------------------------------------------
    if (min_members_count > 1):
        members_count_query = {
            "range": {
                "members_count": {
                    "gte": min_members_count,
                }
            }
        }

        res_query['bool']['filter'].append(members_count_query)

    # ----------------------------------------------------------

    return res_query


def SearchDocumentsByCollectiveActorsKeywords_ES(request, country_id, collectives_id, category_id, actors_id,
                                                 membership_type, keywords_text, min_members_count, curr_page=1):
    collectives_id = collectives_id.split("__")
    actors_id = actors_id.split('__')

    fields = [collectives_id, category_id, actors_id, membership_type, min_members_count]

    res_query = {
        "bool": {
        }
    }

    res_query['bool']['filter'] = []
    res_query["bool"]["must"] = []
    if not all(field == 0 for field in fields):
        res_query = filter_collective_actors_fields(res_query, collectives_id, category_id, actors_id, membership_type,
                                                    min_members_count)

    if keywords_text != "empty":
        res_query = filter_collective_actors_text(res_query, keywords_text, 'filter' not in res_query['bool'])

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, DocumentCollectiveMembers.__name__)

    from_value = (curr_page - 1) * search_result_size

    res_agg = {
        "document-name-agg": {
            "multi_terms": {
                "terms": [{
                    "field": "document_name.keyword",
                },
                    {
                        "field": "document_subject_name.keyword",
                    },
                    {
                        "field": "document_id",
                    }],
                "size": 5000
            },
            "aggs": {
                "collective-actor-name-agg": {
                    "multi_terms": {
                        "terms": [{
                            "field": "collective_actor_name.keyword",
                        },
                            {
                                "field": "members_count",
                            }],
                        "size": 5000
                    },
                },
            },
        },
    }

    response = client.search(index=index_name,
                             _source_includes=[],
                             request_timeout=40,
                             query=res_query,
                             from_=from_value,
                             # size=search_result_size
                             size=0,
                             #  track_total_hits=True,
                             aggregations=res_agg,
                             )

    print(res_query)

    aggregations = response['aggregations']
    total_hits = len(aggregations['document-name-agg']['buckets'])
    # total_hits = response['hits']['total']['value']

    return JsonResponse({
        'total_hits': total_hits,
        "curr_page": curr_page,
        'aggregations': aggregations['document-name-agg']['buckets'][from_value:from_value + search_result_size]
    })


def GetChartExecutiveRegulations(request, country_id, area_id, multiselect_actor_value, type_id, from_year, to_year):
    actors_id = multiselect_actor_value.split("__")
    selected_actors = []
    clauses_result = []
    unique_doc_ids = []

    query_result = ExecutiveRegulations.objects.filter(country_id__id=country_id).order_by(
        '-document_id__approval_date')

    if type_id != 0:
        query_result = query_result.filter(document_id__type_id__id=type_id)

    query_result = query_result.annotate(
        approval_year=Cast(Substr('document_id__approval_date', 1, 4), IntegerField()))
    if from_year > 0:
        query_result = query_result.filter(approval_year__gte=from_year)

    if to_year > 0:
        query_result = query_result.filter(approval_year__lte=to_year)

    if '0' in actors_id:
        if area_id != 0:
            selected_actors = Actor.objects.filter(area__id=area_id).values('name')
    else:
        selected_actors = Actor.objects.filter(id__in=actors_id).values('name')

    has_executive_data = {}
    deadline_data = {}
    approval_year_data = {}
    actor_data = {}

    for res in query_result:
        if unique_doc_ids.__len__() < 100:
            doc_id = res.document_id.id
            doc_approval_year = GetDocumentById_Local(doc_id)["approval_date"]
            actor_list = res.actors_info["actors_info"]

            if any(actor_name['name'] in actor_list for actor_name in
                   selected_actors) or selected_actors.__len__() == 0:
                if doc_id not in unique_doc_ids:
                    unique_doc_ids.append(doc_id)

                if res.deadline_status == None:
                    deadline = 'نامشخص'
                else:
                    deadline = res.deadline_status

                if deadline not in deadline_data:
                    deadline_data[deadline] = 1
                else:
                    deadline_data[deadline] += 1

                if res.has_executive not in has_executive_data:
                    has_executive_data[res.has_executive] = 1
                else:
                    has_executive_data[res.has_executive] += 1

                if doc_approval_year != 'نامشخص':
                    doc_approval_year = doc_approval_year[0:4]

                if doc_approval_year not in approval_year_data:
                    approval_year_data[doc_approval_year] = 1
                else:
                    approval_year_data[doc_approval_year] += 1

                for actor in actor_list:
                    if actor not in actor_data:
                        actor_data[actor] = 1
                    else:
                        actor_data[actor] += 1

    has_executive_list = []
    approval_year_list = []
    deadline_list = []
    actor_chart_list = []

    for key, value in has_executive_data.items():
        if key:
            has_executive_list.append(['هست', value])
        else:
            has_executive_list.append(['نیست', value])

    for key, value in approval_year_data.items():
        approval_year_list.append([key, value])

    for key, value in actor_data.items():
        actor_chart_list.append([key, value])

    for key, value in deadline_data.items():
        deadline_list.append([key, value])

    return JsonResponse({"has_executive_list": has_executive_list, 'approval_year_list': approval_year_list,
                         'actor_chart_list': actor_chart_list, 'deadline_list': deadline_list})


def GetExecutiveRegulations(request, country_id, area_id, multiselect_actor_value, type_id, from_year, to_year,
                            curr_page):
    actors_id = multiselect_actor_value.split("__")
    selected_actors = []
    SEARCH_RESULT_SIZE = 100

    query_result = ExecutiveRegulations.objects.filter(country_id__id=country_id). \
        order_by('-document_id__approval_date')

    if type_id != 0:
        query_result = query_result.filter(document_id__type_id__id=type_id)

    query_result = query_result.annotate(
        approval_year=Cast(Substr('document_id__approval_date', 1, 4), IntegerField()))
    if from_year > 0:
        query_result = query_result.filter(approval_year__gte=from_year)

    if to_year > 0:
        query_result = query_result.filter(approval_year__lte=to_year)

    if '0' in actors_id:
        if area_id != 0:
            selected_actors = Actor.objects.filter(area__id=area_id).values('name')
    else:
        selected_actors = Actor.objects.filter(id__in=actors_id).values('name')

    total_hits = query_result.count()
    _from = (curr_page - 1) * SEARCH_RESULT_SIZE
    _to = min(_from + SEARCH_RESULT_SIZE, total_hits)
    query_result = query_result.values('id', 'document_id__id',
                                       'document_id__name',
                                       'clause_info', 'actors_info',
                                       'paragraph_id__text', 'has_executive',
                                       'document_id__approval_date',
                                       'deadline_date', 'deadline_status')[_from:_to]

    clauses_result = []

    for res in query_result:
        # if len(clauses_result) == 10:
        #     break
        doc_id = res['document_id__id']
        doc_name = res['document_id__name']
        clause_info = res['clause_info']
        actors_info = res['actors_info']["actors_info"]
        paragraph_text = res['paragraph_id__text']
        has_executive = res['has_executive']

        if not any(actor_name['name'] in actors_info for actor_name in selected_actors) and \
                not len(selected_actors) == 0:
            continue

        doc_approval_date = res['document_id__approval_date'] if res['document_id__approval_date'] is not None \
            else ' نامشخص '

        deadline_date = res['deadline_date']
        deadline_status = res['deadline_status']

        res_info = {
            'clause_id': res['id'],
            'doc_id': doc_id,
            'doc_name': doc_name,
            'doc_approval_date': doc_approval_date,
            'clause_info': clause_info,
            'actors_info': actors_info,
            'paragraph_text': paragraph_text,
            'has_executive': has_executive,
            'deadline_date': deadline_date,
            'deadline_status': deadline_status,
        }

        clauses_result.append(res_info)
    return JsonResponse({"clauses_result": clauses_result,
                         "total_hits": total_hits,
                         "curr_page": curr_page})


def GetExecutiveClauseParagraph(request, clause_id):
    paragraph_result = ExecutiveRegulations.objects.filter(id=clause_id).values(
        'has_executive',
        'country_id__id',
        'executive_regulation_doc__id',
        'executive_regulation_doc__name',
        'paragraph_id__id',
        'document_id__name',
        'document_id__id',
        'actors_info',
        'deadline_date',
        'found_pattern',
    )
    paragraph_result = paragraph_result[0]
    country = Country.objects.get(id=paragraph_result['country_id__id'])

    executive_doc_paragraphs = []
    executive_doc_name = "آیین نامه‌ای برای این بند یافت نشد."
    executive_doc_id = None
    if paragraph_result['has_executive']:
        executive_doc_id = paragraph_result['executive_regulation_doc__id']
        result = DocumentParagraphs.objects.filter(document_id__id=executive_doc_id).values_list('text', flat=True)
        executive_doc_paragraphs = list(result)
        executive_doc_name = paragraph_result['executive_regulation_doc__name']

    parent_paragraphs = []

    clauses = get_clause_by_paragraph(paragraph_result['paragraph_id__id'],
                                      paragraph_result['document_id__id'],
                                      country)
    extra_clause_type = ['جز', 'ردیف', 'قسمت']
    clauses = [('بند' if clause[0] in extra_clause_type else clause[0], clause[1]) for clause in clauses]
    clauses.reverse()
    doc_paragraphs = get_document_paragraphs(paragraph_result['document_id__id'],
                                             country, ['attachment.content'])
    for i in range(1, len(clauses)):
        clause = clauses[:i]
        clause.reverse()
        clause = " ".join([item[0] + " " + str(item[1]) for item in clause])
        paragraphs = get_paragraphs_by_clause(clause, doc_paragraphs, country)
        if len(paragraphs) == 0:
            continue
        parent_paragraphs.append(paragraphs[0]['_source']['attachment']['content'])
        parent_paragraphs.append("...")

    index_name = standardIndexName(country, DocumentParagraphs.__name__) + "_graph"
    res = client.search(
        _source_includes=['attachment.content'],
        index=index_name,
        query={'term': {'paragraph_id': paragraph_result['paragraph_id__id'], }}
    )
    para_text_list = [res['hits']['hits'][0]['_source']['attachment']['content']]

    paragraph_info_result = {
        "doc_id": paragraph_result['document_id__id'],
        "doc_name": paragraph_result['document_id__name'],
        "text": para_text_list,
        "actors_info": paragraph_result['actors_info']['actors_info'],
        "parent_paragraphs": parent_paragraphs,
        "executive_doc_name": executive_doc_name,
        "executive_doc_paragraphs": executive_doc_paragraphs,
        "executive_doc_id": executive_doc_id,
        "deadline_date": paragraph_result['deadline_date'],
        'found_pattern': paragraph_result['found_pattern'],
    }

    return JsonResponse({"paragraph_info_result": paragraph_info_result})













def GetOldNewDBCountries(reauest, old_db_name, new_db_name):
    old_countries_list = get_country_maps(Country.objects.using(old_db_name).all())
    new_countries_list = get_country_maps(Country.objects.using(new_db_name).all())

    return JsonResponse({"old_countries_list": old_countries_list, "new_countries_list": new_countries_list})


def List2Dict(values_list):
    result_dict = {}
    for row in values_list:
        name = row["name"].replace(" ", "").replace("\u200c", "")
        result_dict[name] = [row["id"], row["name"]]
    return result_dict


def GetCompareDocumentData(reauest, src_country_id):
    compare_object_filter = Compare_Dataset_CUBE.objects.filter(src_country_id_id=src_country_id)

    limit_list = list(set(Compare_Dataset_CUBE.objects.all().values_list("type", flat=True)))
    result_count = []
    for type in limit_list:
        data_count = compare_object_filter.filter(type=type).count()
        result_count.append([type, data_count])

    return JsonResponse({"Compare_Chart_Result": result_count})


def GetDocumentData(reauest, src_country_id, dest_country_id, type):
    result_array = [1]
    if type == "اسناد خاص مبدا":
        print(1)

    elif type in ("اسناد مشابه (مبدا کامل تر)", "اسناد مشابه (مقصد کامل تر)", "اسناد مشترک"):
        document_list = Compare_Dataset_CUBE.objects.filter(src_country_id_id=src_country_id,
                                                            dest_country_id_id=dest_country_id, type=type)
        result_array = []
        for row in document_list:
            src_name = Document.objects.get(id=row.src_document_id_id).name
            dest_name = Document.objects.get(id=row.dest_document_id_id).name
            result_array.append({"src_name": src_name, "dest_name": dest_name})

    elif type == "اسناد خاص مقصد":
        print(2)

    return JsonResponse({"result_array": result_array})




def download_book(request, folder_name, filename):
    dataPath = str(Path(config.DATA_PATH, folder_name))
    file = glob.glob(dataPath + '/' + filename)
    try:
        file = file[0]
        with open(file, 'rb') as f:
            response = HttpResponse(f)
            response['Content-Disposition'] = "attachment; filename=%s" % filename
            return response
    except:
        return HttpResponse(dataPath + '\\' + filename)


def get_all_books(request):
    docs = Document.objects.all().filter(country_id__language='کتاب')
    all_books = {'books': []}
    for doc in docs:
        new_book = {}
        doc_obj = Document.objects.get(id=doc.id)
        try:
            book = Book.objects.get(document_id=doc_obj)
        except:
            book = Book.objects.create(
                document_id=doc_obj,
                name=doc.name
            )
        new_book['id'] = book.id
        new_book['document_id'] = doc.id
        new_book['contry_id'] = doc.country_id.id
        new_book['name'] = book.name
        new_book['publisher_name'] = book.publisher_name
        new_book['subject'] = book.subject
        new_book['year'] = book.year
        new_book['pagecount'] = book.pagecount
        new_book['status'] = book.status
        try:
            new_book['user'] = book.user.username
        except:
            new_book['user'] = ""

        all_books['books'].append(new_book)

    return JsonResponse(all_books)


def submit_book_info_by_publisher(request, book_id):
    try:
        book = Book.objects.filter(id=book_id)
        status = book[0].status
        print(status)
        if status != '1':
            return JsonResponse({"status": "duplicate"})
        username = request.COOKIES.get('username')
        user = User.objects.get(username=username)
        status = '2'
        book.update(status=status, user=user)
        return JsonResponse({"status": "OK"})
    except:
        return JsonResponse({"status": "not found"})


def submit_book_info_by_admin(request, book_id, publishername, book_subject, year, pagecount):
    try:
        book = Book.objects.filter(id=book_id)
        book.update(publisher_name=publishername, subject=book_subject, year=year, pagecount=pagecount)
        return JsonResponse({"status": "OK"})
    except:
        return JsonResponse({"status": "not found"})


def get_book_by_status(request, status):
    books = Book.objects.all()
    if status != '0':
        books = Book.objects.filter(status=status)
    all_books = {'books': []}
    for book in books:
        new_book = {}
        try:
            new_book['id'] = book.id
            new_book['document_id'] = book.document_id.id
            new_book['country_id'] = book.document_id.country_id.id
            new_book['name'] = book.name
            new_book['publisher_name'] = book.publisher_name
            new_book['subject'] = book.subject
            new_book['year'] = book.year
            new_book['pagecount'] = book.pagecount
            new_book['status'] = book.status
            new_book['user'] = book.user.username

            all_books['books'].append(new_book)
        except:
            pass

    return JsonResponse(all_books)


def ChangebookStatus(request, book_id, status):
    try:
        book = Book.objects.filter(id=book_id)
        book.update(status=status)
        return JsonResponse({"status": "OK"})
    except:
        return JsonResponse({"status": "not found"})


def decode_str(string):
    string = string.split('--')
    string = string[:len(string) - 1]
    return string


def GetSimilarity(request, document_id):
    data = {'docs': []}
    # TFIDFWeightObj = TFIDFWeight.objects.get(document=document_id)
    # all_doc_weights = TFIDFWeight.objects.all().filter(document__country_id=TFIDFWeightObj.document.country_id).exclude(document=document_id)

    all_doc_ids = []

    # BM25Obj = SimilarityType.objects.get(name="BM25")
    # all_docBM25Score = DocumentSimilarity.objects.filter(similarity_type__name ="BM25").filter(Q(doc1=document_id) | Q(doc2=document_id))
    all_docBM25Score = DocumentSimilarity.objects.filter(similarity_type__name="BM25").filter(
        doc1=document_id).order_by('-similarity')[:10]

    # DFRObj = SimilarityType.objects.get(name="DFR")
    # all_docDFRScore = DocumentSimilarity.objects.filter(similarity_type__name="DFR").filter(Q(doc1=document_id) | Q(doc2=document_id))
    all_docDFRScore = DocumentSimilarity.objects.filter(similarity_type__name="DFR").filter(doc1=document_id).order_by(
        '-similarity')[:10]

    # DFIObj = SimilarityType.objects.get(name="DFI")
    # all_docDFIScore = DocumentSimilarity.objects.filter(similarity_type__name="DFI").filter(Q(doc1=document_id) | Q(doc2=document_id))
    all_docDFIScore = DocumentSimilarity.objects.filter(similarity_type__name="DFI").filter(doc1=document_id).order_by(
        '-similarity')[:10]

    print(all_docDFRScore.values('doc2_id', 'similarity'))

    all_doc_ids = list(all_docBM25Score.values_list('doc2_id', flat=True)) + \
                  list(all_docDFIScore.values_list('doc2_id', flat=True)) + \
                  list(all_docDFRScore.values_list('doc2_id', flat=True))

    all_doc_ids = list(set(all_doc_ids))

    print(all_doc_ids)
    docs = {}

    DocLDAScoreObj = DocLDAScore.objects.get(document=document_id)
    all_DocLDAScore = DocLDAScore.objects.filter(document__id__in=all_doc_ids).exclude(document=document_id)

    for doc_score in all_DocLDAScore:
        first = decode_str(DocLDAScoreObj.scores)
        second = decode_str(doc_score.scores)
        res = cosine_similarity([first], [second])
        # docs[doc_score.document.id]['LDA_similarity'] = round(res[0][0]*100, 2)

        docs[doc_score.document.id] = {
            'document_id': doc_score.document.id,
            'document_name': doc_score.document.name,
            'LDA_similarity': round(res[0][0] * 100, 2)
        }

    for doc_id in docs:
        print(doc_id)
        doc_id = int(doc_id)

        try:
            docs[doc_id]['BM25_similarity'] = DocumentSimilarity.objects.filter(
                similarity_type__name='BM25',
                doc1__id=document_id, doc2__id=doc_id)[0].similarity
        except:
            docs[doc_id]['BM25_similarity'] = 0

        try:
            docs[doc_id]['DFR_similarity'] = DocumentSimilarity.objects.filter(
                similarity_type__name='DFR',
                doc1__id=document_id, doc2__id=doc_id)[0].similarity
        except:
            docs[doc_id]['DFR_similarity'] = 0

        try:
            docs[doc_id]['DFI_similarity'] = DocumentSimilarity.objects.filter(
                similarity_type__name='DFI',
                doc1__id=document_id, doc2__id=doc_id)[0].similarity
        except:
            docs[doc_id]['DFI_similarity'] = 0

        docs[doc_id]['average_similarity'] = round(
            (docs[doc_id]['BM25_similarity'] + docs[doc_id]['DFR_similarity'] + docs[doc_id]['DFI_similarity']) / 3, 2)

    books = docs.values()
    books = sorted(books, key=lambda k: k['average_similarity'], reverse=True)
    for book in books:
        data['docs'].append(book)
    return JsonResponse(data)


def GetParagraphSimilarity(request, document_id, curr_document_id):
    result = []
    res_para = ParagraphSimilarity.objects.filter(para1__document_id__id=document_id,
                                                  para2__document_id__id=curr_document_id).order_by("-similarity")[:10]

    for row in res_para:

        # try:
        #     src_para = ParagraphSimilarity.objects.get(
        #         para2__id = row.para1.id,para1__id = row.para2.id).highlighted_text.replace(
        #     '<em>','<span class="text-primary bold" >').replace(
        #         '</em>','</span>')
        # except:
        #     src_para = row.para1.text

        src_para = row.para1.text
        src_doc_id = row.para1.document_id.id
        src_doc_name = row.para1.document_id.name

        dest_doc_id = row.para2.document_id.id
        dest_doc_name = row.para2.document_id.name

        dest_para = row.highlighted_text.replace(
            '<em>', '<span class="text-primary bold" >').replace(
            '</em>', '</span>') if row.highlighted_text != None else row.para2.text

        if row.highlighted_text != None:
            highlighted_text = row.highlighted_text.split('<em>')[1:]
            for i in range(len(highlighted_text)):
                highlighted_text[i] = highlighted_text[i].split('</em>')[0]

            highlighted_text = set(highlighted_text)

            for term in highlighted_text:
                h_term = '<span class="text-primary bold"> ' + term + '</span>'
                src_para = src_para.replace(term, '' + h_term)

        score = row.similarity
        res = {
            "src_para": src_para,
            "src_doc_id": src_doc_id,
            "src_doc_name": src_doc_name,
            "dest_para": dest_para,
            "dest_doc_id": dest_doc_id,
            "dest_doc_name": dest_doc_name,
            "score": score,
        }
        result.append(res)

    return JsonResponse({'result': result})





def GetSimilarParagraphs_ByParagraphID(request, paragraph_id):
    similar_paragraphs = []
    para_obj = DocumentParagraphs.objects.get(id=paragraph_id)
    document_id = para_obj.document_id.id
    country_obj = para_obj.document_id.country_id
    index_name = standardIndexName(country_obj, DocumentParagraphs.__name__)
    # index_name = "doticfull_documentparagraphs"

    para_stopword_list = get_stopword_list('rahbari_stopwords.txt')
    doc_stopword_list = get_stopword_list('rahbari_doc_name_stopwords.txt')
    res_stopword_list = list(set(para_stopword_list + doc_stopword_list))

    sim_query = {
        "bool": {
            "must_not": [
                {
                    "term": {
                        "document_id": str(document_id)
                    }
                }
            ],
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
                        "minimum_should_match": "55%",
                        "stop_words": res_stopword_list
                    }
                }
            ]
        }
    }

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'document_name', 'attachment.content'],
                             request_timeout=40,
                             query=sim_query
                             # ,highlight={
                             #     "type": "fvh",
                             #     "fields": {
                             #         "attachment.content":
                             #         {"pre_tags": ["<span class='text-primary fw-bold'>"], "post_tags": ["</span>"],
                             #         "number_of_fragments": 0
                             #         }
                             #     }
                             # }

                             )

    similar_paragraphs = response['hits']['hits']
    print(f"similar_paragraphs:\n {similar_paragraphs}")
    return JsonResponse({'similar_paragraphs': similar_paragraphs})








def get_TFIDF_similarity_for_2_document(request, document1, document2):
    TFIDFWeightObj1 = TFIDFWeight.objects.get(document=document1)
    TFIDFWeightObj2 = TFIDFWeight.objects.get(document=document2)
    CountryWords = CountryTFIDFWords.objects.get(country=TFIDFWeightObj1.document.country_id)

    words_list = []
    docs = {}

    first = decode_str(TFIDFWeightObj1.weights)
    first = list(map(float, first))
    second = decode_str(TFIDFWeightObj2.weights)
    second = list(map(float, second))
    country_words = decode_str(CountryWords.words)

    for i in range(len(country_words)):
        new_word = {}
        new_word['word'] = country_words[i]
        new_word['weight1'] = first[i]
        new_word['weight2'] = second[i]

        words_list.append(new_word)

    words_list = sorted(words_list,
                        key=lambda k: ((k['weight1']) * (k['weight2'])) / (abs((k['weight1']) - (k['weight2'])) + 0.1),
                        reverse=True)[:10]
    # words_list = sorted(words_list, key=lambda k: 1/(abs((k['weight1'])-(k['weight2']))+0.5) + (k['weight1']*k['weight2'])/3 ,reverse=True)[:10]
    docs['words'] = words_list
    book1 = Book.objects.get(document_id=document1).name
    book2 = Book.objects.get(document_id=document2).name
    docs['book1'] = book1
    docs['book2'] = book2

    return JsonResponse(docs)


def get_similarity_for_2_document(request, doc_id_1, doc_id_2, measure):
    if measure == 'TFIDF':
        return get_TFIDF_similarity_for_2_document(request, doc_id_1, doc_id_2)
    print(measure)
    result_row = DocumentSimilarity.objects.get(
        doc1__id=doc_id_1,
        doc2__id=doc_id_2,
        similarity_type__name=measure)

    highlighted_text_dict = {}

    if result_row.highlighted_text:
        highlighted_text = result_row.highlighted_text.split('<em>')[1:]
        for i in range(len(highlighted_text)):
            highlighted_text[i] = highlighted_text[i].split('</em>')[0]

        for i in range(len(highlighted_text)):
            try:
                highlighted_text_dict[highlighted_text[i]] += 1
            except:
                highlighted_text_dict[highlighted_text[i]] = 1

    # highlighted_text_dict = sorted(highlighted_text_dict.items(), key=lambda k: k[1], reverse=True)

    source_doc = DocumentSimilarity.objects.get(
        doc1__id=doc_id_2,
        doc2__id=doc_id_1,
        similarity_type__name=measure)

    doc_name_1 = result_row.doc1.name
    doc_name_2 = result_row.doc2.name

    highlighted_text_dict2 = {}

    if source_doc.highlighted_text:
        highlighted_text = source_doc.highlighted_text.split('<em>')[1:]
        for i in range(len(highlighted_text)):
            highlighted_text[i] = highlighted_text[i].split('</em>')[0]

        for i in range(len(highlighted_text)):
            try:
                highlighted_text_dict2[highlighted_text[i]] += 1
            except:
                highlighted_text_dict2[highlighted_text[i]] = 1

    res_doc = []
    for key in highlighted_text_dict2:
        new_word = {}
        try:
            new_word['word'] = key
            new_word['weight1'] = highlighted_text_dict[key]
            new_word['weight2'] = highlighted_text_dict2[key]
            res_doc.append(new_word)
        except:
            continue

    res_doc = sorted(res_doc,
                     key=lambda k: ((k['weight1']) * (k['weight2'])) / (abs((k['weight1']) - (k['weight2'])) + 0.1),
                     reverse=True)

    return JsonResponse({'words': res_doc, 'book1': doc_name_1, 'book2': doc_name_2})


def get_similarity_highlighted_text(request, doc_id_1, doc_id_2, measure):
    result_row = DocumentSimilarity.objects.get(
        doc1__id=doc_id_1,
        doc2__id=doc_id_2,
        similarity_type__name=measure)

    highlighted_text = result_row.highlighted_text.replace(
        '<em>', '<span class = "text-primary bold">').replace("</em>", "</span>")

    doc_name_1 = result_row.doc1.name
    doc_name_2 = result_row.doc2.name

    result = {
        "doc_name_1": doc_name_1,
        "doc_name_2": doc_name_2,
        "highlighted_text": highlighted_text

    }

    source_doc = DocumentSimilarity.objects.get(
        doc1__id=doc_id_2,
        doc2__id=doc_id_1,
        similarity_type__name=measure)
    source_highlight = source_doc.highlighted_text.replace(
        '<em>', '<span class = "text-primary bold">').replace("</em>", "</span>")

    result["source_highlight"] = source_highlight if source_highlight != None else ''

    return JsonResponse({"result": result})


def create_expertise_sample(request):
    try:
        UserExpertise.objects.get(expertise='تست')
        return JsonResponse({'status': 'already exists'})
    except:
        UserExpertise.objects.create(expertise='تست')
        return JsonResponse({'status': 'OK'})


def get_excels_data_book(request, country_id):
    country = Country.objects.get(id=country_id)
    documents = Document.objects.filter(country_id=country)
    all_book = {'books': [], 'columns': []}
    for document in documents:
        doc_info = {}
        book = Book.objects.get(document_id=document)
        doc_info['document_id'] = document.id
        doc_info['document_standard_name'] = document.name
        doc_info['document_original_name'] = document.file_name
        doc_info['book_publisher_name'] = book.publisher_name
        doc_info['book_subject'] = book.subject
        doc_info['book_year'] = book.year
        doc_info['book_pagecount'] = book.pagecount
        doc_info['book_status'] = book.status
        try:
            doc_info['book_user'] = book.user.username
        except:
            doc_info['book_user'] = ""

        all_book['books'].append(doc_info)

    all_book['columns'] = ['document_id', 'document_standard_name', 'document_original_name', 'book_publisher_name',
                           'book_subject', 'book_year', 'book_pagecount', 'book_status', 'book_user']

    return JsonResponse(all_book)












def GetIndictmentDocs(request):
    result = []

    docs = Indictment.objects.all().annotate(
        approval_year=Cast(Substr('document_id__approval_date', 1, 4), IntegerField())).order_by('-approval_year')
    for row in docs:
        doc_info = {}
        doc_info['doc_id'] = row.document_id.id
        doc_info['doc_name'] = row.document_id.name
        doc_info['doc_approval_date'] = row.document_id.approval_date
        doc_info['approval_year'] = row.approval_year if row.approval_year != None else 'نامشخص'
        doc_info['indictment_number'] = row.indictment_number
        doc_info['categories'] = row.categories
        doc_info['affected_document_name'] = row.affected_document_name

        result.append(doc_info)

    return JsonResponse({"result": result})


def GetStandardDocumentById(request, document_id):
    document = Document.objects.get(id=document_id)
    sta = Standard.objects.get(document_id=document)

    subject = "نامشخص"
    if sta.subject != None:
        subject = sta.subject

    standard_number = "نامشخص"
    if sta.standard_number != None:
        standard_number = sta.standard_number

    branch = "نامشخص"
    if sta.branch != None:
        branch = sta.branch.name

    approval_year = "نامشخص"
    if sta.approval_year != None:
        approval_year = sta.approval_year

    ICS = "نامشخص"
    if sta.approval_year != None:
        ICS = sta.ICS

    file_name_with_extention = "نامشخص"
    if sta.file_name_with_extention != None:
        file_name_with_extention = sta.file_name_with_extention

    result = {"document_id": document.id,
              "subject": subject,
              "standard_number": standard_number,
              "branch": branch,
              "approval_year": approval_year,
              "ICS": ICS,
              "file_name_with_extention": file_name_with_extention
              }
    return JsonResponse({'standard_information': [result]})


def GetStandardsSearchParameters(request, country_id):
    search_parameters = StandardSearchParameters.objects.filter(country__id=country_id)
    parameters_result = {}

    for param in search_parameters:
        para_name = param.parameter_name
        options = param.parameter_values["options"]
        parameters_result[para_name] = options

    return JsonResponse({"parameters_result": parameters_result})


def filter_standard_fields(res_query, branch, subject_category, status, from_year, to_year):
    if branch != 0:
        branch_name = Standard_Branch.objects.get(id=branch).name
        branch_query = {
            "term": {
                "branch.keyword": branch_name
            }
        }
        res_query['bool']['filter'].append(branch_query)
    # ---------------------------------------------------------

    if subject_category != 0:
        branch_name = Standard_Branch.objects.get(id=subject_category).name

        subject_category = branch_name.replace('کمیته ملی', '').strip()

        subject_category_query = {
            "term": {
                "subject_category.keyword": subject_category
            }
        }
        res_query['bool']['filter'].append(subject_category_query)
    # ---------------------------------------------------------
    if status != 0:
        status_name = Standard_Status.objects.get(id=status).name
        status_query = {
            "term": {
                "status.keyword": status_name
            }
        }
        res_query['bool']['filter'].append(status_query)

    # ----------------------------------------------------------
    First_Year = 1000
    Last_Year = 1403

    if from_year != 0 or to_year != 0:
        from_year = from_year if from_year != 0 else First_Year
        to_year = to_year if to_year != 0 else Last_Year

        year_query = {
            "range": {
                "approval_year": {
                    "gte": from_year,
                    "lte": to_year,
                }
            }
        }

        res_query['bool']['filter'].append(year_query)

    return res_query


def SearchDocument_ES_Standard(request, country_id, branch, subject_category, status, from_year, to_year, place, text,
                               search_type):
    fields = [branch, subject_category, status, from_year, to_year]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_standard_fields(res_query, branch, subject_category, status, from_year, to_year)

    if text != "empty":
        res_query["bool"]["must"] = []

        if search_type == 'exact':
            res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
        else:
            res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, Standard.__name__)

    response = client.search(index=index_name,
                             _source_includes=['document_id', 'name', 'branch', 'subject_category',
                                               'status', 'standard_number', 'ICS', 'appeal_number', 'Description',
                                               'approval_year',
                                               'file_name_with_extention'],
                             request_timeout=40,
                             query=res_query,
                             size=100

                             )

    # print("Got %d Hits:" % response['hits']['total']['value'])
    total_hits = response['hits']['total']['value']

    return JsonResponse({
        "result": response['hits']['hits'],
        'total_hits': total_hits})


def GetJudgementTypeByCountryId(request, country_id):
    type_list = JudgmentGraphType.objects.filter(country_id_id=country_id)
    result = []
    for t in type_list:
        res = {"id": t.id, "name": t.name, "color": t.color, "is_checked": t.is_checked}
        result.append(res)
    return JsonResponse({"type_list": result})


def GetStandardTypeByCountryId(request, country_id):
    type_list = StandardGraphType.objects.filter(country_id_id=country_id)
    result = []
    for t in type_list:
        res = {"id": t.id, "name": t.name, "color": t.color, "is_checked": t.is_checked}
        result.append(res)
    return JsonResponse({"type_list": result})


def GetJudgementGraphNodesEdges(request, country_id, selected_type):
    selected_type = selected_type.split("_")
    nodes_list = JudgmentGraphNodesCube.objects.filter(country_id_id=country_id, type_id__in=selected_type)
    edges_list = JudgmentGraphEdgesCube.objects.filter(country_id_id=country_id, src_type_id__in=selected_type,
                                                       target_type__in=selected_type)

    nodes_result = []
    for n in nodes_list:
        nodes_result += list(n.nodes)

    edges_result = []
    for e in edges_list:
        edges_result += list(e.edges)

    return JsonResponse({"Nodes_data": nodes_result, "Edges_data": edges_result})


def GetStandardGraphNodesEdges(request, country_id, selected_type):
    selected_type = selected_type.split("_")
    nodes_list = StandardGraphNodesCube.objects.filter(country_id_id=country_id, type_id__in=selected_type)
    edges_list = StandardGraphEdgesCube.objects.filter(country_id_id=country_id, src_type_id__in=selected_type,
                                                       target_type__in=selected_type)

    nodes_result = []
    for n in nodes_list:
        nodes_result += list(n.nodes)

    edges_result = []
    for e in edges_list:
        edges_result += list(e.edges)

    return JsonResponse({"Nodes_data": nodes_result, "Edges_data": edges_result})


def update_judgment_name(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import Test

    Test.apply(None, file)
    return redirect('zip')


def seen_help(request, url):
    try:
        username = request.COOKIES.get('username')
        seenHelp = UserHelpSeen.objects.filter(user__username=username, url=url)
        if len(seenHelp) > 0:
            return JsonResponse({'seen': True})

        return JsonResponse({'seen': False})
    except:
        return JsonResponse({'seen': False})


def saw_help(request, url):
    username = request.COOKIES.get('username')
    user = User.objects.get(username=username)
    UserHelpSeen.objects.create(user=user, url=url)
    return JsonResponse({})


def get_judge_profile_data(request, judge_id):
    judge = JudgmentJudge.objects.get(id=judge_id)
    judge_name = judge.name
    judgement_datas = Judgment.objects.filter(judge_name__id=judge_id)

    judgments_count = len(judgement_datas)
    judgment_by_year = {}
    judgment_by_subject_type = {}
    judgment_by_complainant = {}
    judgment_by_complaint_from = {}
    judgment_by_categories = {}

    for judgement_data in judgement_datas:
        if (judgement_data.judgment_year != None):
            if judgement_data.judgment_year in judgment_by_year:
                judgment_by_year[judgement_data.judgment_year].append({"judgment_id": judgement_data.id,
                                                                       "judgment_number": judgement_data.judgment_number,
                                                                       "judgment_date": judgement_data.judgment_date
                                                                       })
            else:
                judgment_by_year[judgement_data.judgment_year] = [{"judgment_id": judgement_data.id,
                                                                   "judgment_number": judgement_data.judgment_number,
                                                                   "judgment_date": judgement_data.judgment_date
                                                                   }]

        if (judgement_data.subject_type_display_name != None):
            if judgement_data.subject_type_display_name.name in judgment_by_subject_type:
                judgment_by_subject_type[judgement_data.subject_type_display_name.name].append(
                    {"judgment_id": judgement_data.id,
                     "judgment_number": judgement_data.judgment_number, "judgment_date": judgement_data.judgment_date
                     })
            else:
                judgment_by_subject_type[judgement_data.subject_type_display_name.name] = [
                    {"judgment_id": judgement_data.id,
                     "judgment_number": judgement_data.judgment_number, "judgment_date": judgement_data.judgment_date
                     }]

        if (judgement_data.complainant != None):
            if judgement_data.complainant in judgment_by_complainant:
                judgment_by_complainant[judgement_data.complainant].append({"judgment_id": judgement_data.id,
                                                                            "judgment_number": judgement_data.judgment_number,
                                                                            "judgment_date": judgement_data.judgment_date,
                                                                            "subject_complaint": judgement_data.subject_complaint
                                                                            })
            else:
                judgment_by_complainant[judgement_data.complainant] = [{"judgment_id": judgement_data.id,
                                                                        "judgment_number": judgement_data.judgment_number,
                                                                        "judgment_date": judgement_data.judgment_date,
                                                                        "subject_complaint": judgement_data.subject_complaint
                                                                        }]

        if (judgement_data.complaint_from != None):
            if judgement_data.complaint_from in judgment_by_complaint_from:
                judgment_by_complaint_from[judgement_data.complaint_from].append({"judgment_id": judgement_data.id,
                                                                                  "judgment_number": judgement_data.judgment_number,
                                                                                  "judgment_date": judgement_data.judgment_date,
                                                                                  "subject_complaint": judgement_data.subject_complaint
                                                                                  })
            else:
                judgment_by_complaint_from[judgement_data.complaint_from] = [{"judgment_id": judgement_data.id,
                                                                              "judgment_number": judgement_data.judgment_number,
                                                                              "judgment_date": judgement_data.judgment_date,
                                                                              "subject_complaint": judgement_data.subject_complaint
                                                                              }]

        if (judgement_data.categories != None):
            if judgement_data.categories.name in judgment_by_categories:
                judgment_by_categories[judgement_data.categories.name].append({"judgment_id": judgement_data.id,
                                                                               "judgment_number": judgement_data.judgment_number,
                                                                               "judgment_date": judgement_data.judgment_date,
                                                                               "subject_complaint": judgement_data.subject_complaint
                                                                               })
            else:
                judgment_by_categories[judgement_data.categories.name] = [{"judgment_id": judgement_data.id,
                                                                           "judgment_number": judgement_data.judgment_number,
                                                                           "judgment_date": judgement_data.judgment_date,
                                                                           "subject_complaint": judgement_data.subject_complaint
                                                                           }]

    return JsonResponse({"judge_name": judge_name, "judgment_by_year": judgment_by_year,
                         "judgment_by_subject_type": judgment_by_subject_type,
                         "judgment_by_complainant": judgment_by_complainant,
                         "judgment_by_complainant_from": judgment_by_complaint_from,
                         "judgment_by_categories": judgment_by_categories,
                         "judgments_count": judgments_count})


def get_all_judges(request):
    judges = JudgmentJudge.objects.all().values('id', 'name').distinct().order_by('name')
    judges_map = {}
    for judge in judges:
        judgement_datas = Judgment.objects.filter(judge_name__id=judge["id"])
        judgments_count = len(judgement_datas)

        judgments_by_subject_type = {}
        most_frequent_subject_type = None
        subject_type_count = 0
        for judgment in judgement_datas:
            if (judgment.subject_type_display_name != None):
                if judgment.subject_type_display_name.name in judgments_by_subject_type:
                    judgments_by_subject_type[judgment.subject_type_display_name.name].append(
                        {"judgment_id": judgment.id,
                         "judgment_number": judgment.judgment_number, "judgment_date": judgment.judgment_date
                         })
                else:
                    judgments_by_subject_type[judgment.subject_type_display_name.name] = [{"judgment_id": judgment.id,
                                                                                           "judgment_number": judgment.judgment_number,
                                                                                           "judgment_date": judgment.judgment_date
                                                                                           }]
        if (len(judgments_by_subject_type) > 0):
            most_frequent_subject_type = max(judgments_by_subject_type.items(), key=lambda x: len(x[1]))
        if (most_frequent_subject_type == None):
            subject_type_name = "نامشخص"
            subject_type_count = 0
        else:
            subject_type_name = most_frequent_subject_type[0]
            subject_type_count = len(most_frequent_subject_type[1])

        judges_map[judge["id"]] = {
            "name": judge["name"],
            "judgments_count": judgments_count,
            "most_subject_type_name": subject_type_name,
            "most_subject_type_count": subject_type_count
        }
        # judges_map[judge["id"]] = judge["name"]
    judges_list = sorted(judges_map.items(), key=lambda item: item[1]["judgments_count"], reverse=True)
    return JsonResponse({"result": judges_list})


def get_judge_dashboard_data(request):
    judgements = Judgment.objects.all()
    judgements = filter(lambda x: x.judge_name != None, judgements)
    key = lambda x: int(x.judge_name.id)
    judgements_grouped_by_judge = groupby(sorted(judgements, key=key), key=key)

    judge_informations = {}
    judges_judgements_per_year = {}
    years = set()
    all_years = set()
    subject_types = set()
    categories = set()

    for judge_id, judge_judgments in judgements_grouped_by_judge:
        judge_judgments = list(judge_judgments)
        judge_judgments_count = len(judge_judgments)
        judge_Name = judge_judgments[0].judge_name.name  # JudgmentJudge.filter(id=judge_id).first().name

        judgments_by_year = {}
        judgments_by_subject_type = {}
        # judgments_by_complainant = {}
        # judgments_by_complainant_from = {}
        judgments_by_categories = {}
        for judgment in judge_judgments:

            if (judgment.judgment_year != None):
                if judgment.judgment_year in judgments_by_year:
                    judgments_by_year[judgment.judgment_year].append({"judgment_id": judgment.id,
                                                                      "judgment_number": judgment.judgment_number,
                                                                      "judgment_date": judgment.judgment_date
                                                                      })
                else:
                    judgments_by_year[judgment.judgment_year] = [{"judgment_id": judgment.id,
                                                                  "judgment_number": judgment.judgment_number,
                                                                  "judgment_date": judgment.judgment_date
                                                                  }]

            if (judgment.subject_type_display_name != None):
                if judgment.subject_type_display_name.name in judgments_by_subject_type:
                    judgments_by_subject_type[judgment.subject_type_display_name.name].append(
                        {"judgment_id": judgment.id,
                         "judgment_number": judgment.judgment_number, "judgment_date": judgment.judgment_date
                         })
                else:
                    judgments_by_subject_type[judgment.subject_type_display_name.name] = [{"judgment_id": judgment.id,
                                                                                           "judgment_number": judgment.judgment_number,
                                                                                           "judgment_date": judgment.judgment_date
                                                                                           }]

            if (judgment.categories != None):
                if judgment.categories.name in judgments_by_categories:
                    judgments_by_categories[judgment.categories.name].append({"judgment_id": judgment.id,
                                                                              "judgment_number": judgment.judgment_number,
                                                                              "judgment_date": judgment.judgment_date,
                                                                              })
                else:
                    judgments_by_categories[judgment.categories.name] = [{"judgment_id": judgment.id,
                                                                          "judgment_number": judgment.judgment_number,
                                                                          "judgment_date": judgment.judgment_date,
                                                                          }]

        years.update(judgments_by_year.keys())
        subject_types.update(judgments_by_subject_type.keys())
        categories.update(judgments_by_categories.keys())
        judges_judgements_per_year[judge_Name] = judgments_by_year

        judge_informations[judge_id] = {
            "judgments_count": judge_judgments_count,
            "judge_name": judge_Name,
            "judgments_by_year": judgments_by_year,
            "judgments_by_subject_type": judgments_by_subject_type,
            "judgments_by_categories": judgments_by_categories,
        }

    judge_with_max_judgments = max(judge_informations.items(),
                                   key=lambda x: x[1]['judgments_count'])  # tuple(key,value)
    judge_with_max_judgments = {
        "judge_id": judge_with_max_judgments[0],
        "judge_name": judge_with_max_judgments[1]['judge_name'],
        "judgments_count": judge_with_max_judgments[1]['judgments_count']
    }

    judge_with_max_judgments_in_years = {}
    for year in years:
        judge_withmax_judgments_in_year = max(judge_informations.items(), key=
        lambda x: len(x[1]['judgments_by_year'][year]) if year in x[1]['judgments_by_year'] else 0)
        # informations = judge_withmax_judgments_in_subject[1] # for more data if you need
        judge_with_max_judgments_in_years[year] = {"judge_name": judge_withmax_judgments_in_year[1]["judge_name"],
                                                   "judgments_count": len(
                                                       judge_withmax_judgments_in_year[1]['judgments_by_year'][year]),
                                                   "judge_id": judge_withmax_judgments_in_year[0]}

    judge_with_max_judgments_in_subject_types = {}
    for subject in subject_types:
        judge_withmax_judgments_in_subject = max(judge_informations.items(), key=
        lambda x: len(x[1]['judgments_by_subject_type'][subject]) if subject in x[1][
            'judgments_by_subject_type'] else 0)
        # informations = judge_withmax_judgments_in_subject[1] # for more data if you need
        judge_with_max_judgments_in_subject_types[subject] = {
            "judge_name": judge_withmax_judgments_in_subject[1]["judge_name"],
            "judgments_count": len(judge_withmax_judgments_in_subject[1]['judgments_by_subject_type'][subject]),
            "judge_id": judge_withmax_judgments_in_subject[0]}

    judge_with_max_judgments_in_categories = {}
    for category in categories:
        judge_withmax_judgments_in_category = max(judge_informations.items(), key=
        lambda x: len(x[1]['judgments_by_categories'][category]) if category in x[1]['judgments_by_categories'] else 0)
        # informations = judge_withmax_judgments_in_category[1] # for more data if you need
        judge_with_max_judgments_in_categories[category] = {
            "judge_name": judge_withmax_judgments_in_category[1]["judge_name"],
            "judgments_count": len(judge_withmax_judgments_in_category[1]['judgments_by_categories'][category]),
            "judge_id": judge_withmax_judgments_in_category[0]}
    all_years = list(years)
    all_years.sort()
    return JsonResponse({
        "judge_with_max_judgments": judge_with_max_judgments,
        "judge_with_max_judgments_in_years": judge_with_max_judgments_in_years,
        "judge_with_max_judgments_in_subject_types": judge_with_max_judgments_in_subject_types,
        "judge_with_max_judgments_in_categories": judge_with_max_judgments_in_categories,
        "judges_judgements_per_year": judges_judgements_per_year,
        "years": all_years
    })


def GetRevokedTableData(request, country_id):
    revoked_data = RevokedDocument.objects.filter(country_id_id=country_id)

    result = []
    index = 0
    for revoked in revoked_data:
        src_document_name = Document.objects.get(id=revoked.src_document_id)
        dest_document_name = Document.objects.get(id=revoked.dest_document_id)
        revoked_type_name = RevokedType.objects.get(id=revoked.revoked_type_id)

        dest_para = None
        if revoked.dest_para_id is None:
            dest_para = 'نامشخص'
        else:
            dest_para = revoked.dest_para_id

        res = {"id": revoked.id, "revoked_sub_type": revoked.revoked_sub_type,
               "revoked_type_name": revoked_type_name.name, "revoked_size": revoked.revoked_size,
               "src_document_id": revoked.src_document_id, "src_document_name": src_document_name.name,
               "dest_document_id": revoked.dest_document_id, "dest_document_name": dest_document_name.name,
               "src_para_id": revoked.src_para_id, "dest_para_id": dest_para,
               }

        result.append(res)
        index += 1

    return JsonResponse({"revoked_data": result, 'doc_count': index})


def GetDetailRevokedData(request, src_para_id, dest_para_id, dest_document_id):
    dest_para_list = []
    src_para_text = DocumentParagraphs.objects.get(id=src_para_id).text

    if dest_para_id == 0:
        dest_para_list = list(
            DocumentParagraphs.objects.filter(document_id__id=dest_document_id).values_list('text', flat=True))

    else:
        dest_para_list = [DocumentParagraphs.objects.get(id=dest_para_id).text]

    print(dest_para_list)
    print(src_para_text)

    return JsonResponse({"src_para_text": src_para_text, "dest_para_list": dest_para_list})


def GetDetailRevokedData_2(request, src_para_id, dest_para_id, src_id, dest_id):
    if src_para_id == 0:
        src_para_list = list(DocumentParagraphs.objects.filter(document_id__id=src_id).values_list('text', flat=True))
    else:
        src_para_list = [DocumentParagraphs.objects.get(id=src_para_id).text]

    if dest_para_id == 0:
        if dest_id != 0:
            dest_para_list = list(
                DocumentParagraphs.objects.filter(document_id__id=dest_id).values_list('text', flat=True))
        else:
            dest_para_list = []
    else:
        dest_para_list = [DocumentParagraphs.objects.get(id=dest_para_id).text]

    return JsonResponse({"src_para_list": src_para_list, "dest_para_list": dest_para_list})


def RevokedSearch_ES(request, country_id, RevokedType_text, RevokedSize_text, SubType_text, place, text):
    fields = [RevokedType_text, RevokedSize_text, SubType_text]

    res_query = {
        "bool": {}
    }

    ALL_FIELDS = True

    if not all(field == 0 for field in fields):
        ALL_FIELDS = False
        res_query['bool']['filter'] = []
        res_query = filter_revoked_fields(res_query, RevokedType_text, RevokedSize_text, SubType_text)

    if text != "empty":
        res_query["bool"]["must"] = []
        res_query = exact_revoked_search_text(res_query, place, text, ALL_FIELDS)

    country_obj = Country.objects.get(id=country_id)
    index_name = standardIndexName(country_obj, RevokedDocument.__name__)

    response = client.search(index=index_name,
                             _source_includes=['src_document_id', 'src_document_name',
                                               'dest_document_id', 'dest_document_name', 'revoked_type_name',
                                               'revoked_sub_type', 'revoked_size', 'src_para_id', 'dest_para_id',
                                               'src_approval_date', 'dest_approval_date', 'revoked_clauses'],
                             request_timeout=40,
                             query=res_query,
                             size=100

                             )

    # print("Got %d Hits:" % response['hits']['total']['value'])
    total_hits = response['hits']['total']['value']

    return JsonResponse({
        "result": response['hits']['hits'],
        'total_hits': total_hits})


def filter_revoked_fields(res_query, RevokedType_text, RevokedSize_text, SubType_text):
    if RevokedType_text != '0':
        RevokedType_query = {
            "term": {
                "revoked_type_name.keyword": RevokedType_text
            }
        }
        res_query['bool']['filter'].append(RevokedType_query)

    # ---------------------------------------------------------
    if RevokedSize_text != '0':
        revoked_size_query = {
            "term": {
                "revoked_size.keyword": RevokedSize_text
            }
        }
        res_query['bool']['filter'].append(revoked_size_query)

    # ---------------------------------------------------------
    if SubType_text != '0':
        revoked_sub_type_query = {
            "term": {
                "revoked_sub_type.keyword": SubType_text
            }
        }
        res_query['bool']['filter'].append(revoked_sub_type_query)

    return res_query


def exact_revoked_search_text(res_query, place, text, ALL_FIELDS):
    text = text.replace('>', '/').replace('<', '\\')

    title_query = {
        "bool": {
            "should": [
                {
                    "match_phrase": {
                        "src_document_name": text
                    }
                },
                {
                    "match_phrase": {
                        "dest_document_name": text
                    }
                }
            ]
        }
    }

    if ALL_FIELDS:
        res_query = title_query
    else:
        res_query['bool']['must'].append(title_query)

    return res_query


def remove_unknown_standard_doc(request, country_id):
    doc_count = Document.objects.filter(country_id__id=country_id, name__icontains="نامشخص").count()
    Document.objects.filter(country_id__id=country_id, name__icontains="نامشخص").delete()

    return JsonResponse({'count': doc_count})


def get_judgment_subject_type_display_name(request, name):
    res = JudgmentSubjectTypeDisplayName.objects.filter(name=name).first()
    return JsonResponse({'display_name_id': res.id})
















def GetSubjectAreaGraphNodesEdges(request, country_id, area_id):
    if area_id != 0:
        DataList = SubjectAreaGraphCube.objects.get(country_id_id=country_id, subject_area_id_id=area_id)
        Nodes_data = DataList.nodes
        Edges_data = DataList.edges
    else:
        data_list = SubjectAreaGraphCube.objects.filter(country_id_id=country_id)
        Nodes_data = []
        Edges_data = []
        for data in data_list:
            Nodes_data += data.nodes
            Edges_data += data.edges

    return JsonResponse({"Nodes_data": Nodes_data, "Edges_data": Edges_data})


def GetSubjectSubAreaList(request, area_id):
    sub_area_list = SubjectSubArea.objects.filter(subject_area_id_id=area_id)

    result = []
    for row in sub_area_list:
        row = {"id": row.id, "name": row.name, "color": row.color}
        result.append(row)

    return JsonResponse({"sub_area_list": result})


def GetTrialLawByCountryId(request, country_id, host):
    trial_law = TrialLaw.objects.filter(country_id=country_id).order_by("-main_document_name")

    result_dict = {}

    for row in trial_law:
        main_doc_id = row.main_document_id
        main_doc_name = row.main_document_name
        main_doc_approval_date = "نامشخص" if main_doc_id is None else row.main_document_approval_date
        in_dotic = '<i class="bi bi-x-circle-fill text-danger"></i>' if row.in_dotic == 0 else '<i class="bi bi-check-circle-fill text-success"></i>'

        doc_id = row.document_id
        doc_name = row.document_name
        doc_approval_date = row.document_approval_date

        document_link = 'http://' + host + "/information/?id=" + str(doc_id)
        doc_name = '<a href="' + document_link + '">' + doc_name + "</a>"

        doc_tag = '<tr style="background-color: transparent;">' \
                  '<td style="display: table-cell;">' + doc_name + '</td>' \
                                                                   '<td style="display: table-cell;">' + doc_approval_date + '</td>' \
                                                                                                                             '<tr>'

        if main_doc_id is not None:
            document_link = 'http://' + host + "/information/?id=" + str(main_doc_id)
            main_doc_name = '<a href="' + document_link + '">' + main_doc_name + "</a>"

        if main_doc_name not in result_dict:
            result_dict[main_doc_name] = {"main_doc_name": main_doc_name,
                                          "main_doc_approval_date": main_doc_approval_date,
                                          "in_dotic": in_dotic, "doc_name": doc_tag}
        else:
            result_dict[main_doc_name]["doc_name"] += doc_tag

    i = 1
    result = []
    for key, value in result_dict.items():
        obj = {"id": i, "main_doc_name": value["main_doc_name"],
               "main_doc_approval_date": value["main_doc_approval_date"],
               "in_dotic": value["in_dotic"], "doc_name": value["doc_name"]}
        result.append(obj)
        i += 1

    return JsonResponse({"TrialLawResult": result})


# ------------------- Clustering --------------------























def Get_Topic_Paragraphs(request, country_id, topic_id):
    topic_paragraphs = {}

    result_paragraphs = ParagraphsTopic.objects.filter(
        country__id=country_id,
        topic__id=topic_id
    ).values("paragraph__text", "paragraph__document_id__id",
             "paragraph__document_id__name")[:100]

    for para in result_paragraphs:
        para_text = para["paragraph__text"]
        doc_id = para["paragraph__document_id__id"]
        doc_name = para["paragraph__document_id__name"]

        if doc_id not in topic_paragraphs:
            topic_paragraphs[doc_id] = {
                "doc_name": doc_name,
                "para_list": list()
            }
            topic_paragraphs[doc_id]["para_list"].append(para_text)
        else:
            topic_paragraphs[doc_id]["para_list"].append(para_text)

    return JsonResponse({"topic_paragraphs": topic_paragraphs})












def delete_topic_paragraphs(request):
    ParagraphsTopic.objects.all().delete()
    return HttpResponse("deleted.")







# init Lib



def Preprocessing(text):
    # Cleaning
    ignoreList = ["!", "@", "$", "%", "^", "&", "*", "(", ")", "_", "+", "-", "/", "*", "'", "،", "؛", ",", "{", "}",
                  '\xad', ".", "؟", "?",
                  "[", "]", "«", "»", "<", ">", ".", "?", "؟", "\t", '"', "٫", '0', '1', '2', '3', '4', '5', '6', '7',
                  '8', '9', "\u200c"]
    for item in ignoreList:
        text = text.replace(item, " ")

    # Normalization
    normalizer = Normalizer()
    text = normalizer.normalize(text)
    text = arabic_preprocessing(text)

    # delete multi space
    while "  " in text:
        text = text.replace("  ", " ")

    # strip text
    text = text.lstrip().rstrip()

    return text


def GetSubjectKeywordGraphVersion(request):
    subject_version = SubjectsVersion.objects.all().order_by("name")
    result = []
    for row in subject_version:
        result.append([row.id, row.name])

    return JsonResponse({"Versions": result})


def SubjectKeywordGraphExtractor(request, version):
    graph_object = SubjectKeywordGraphCube.objects.get(version_id=version)
    Nodes, Edges = graph_object.nodes_data, graph_object.edges_data
    return JsonResponse({"Nodes_data": Nodes, "Edges_data": Edges})


def TextSubjectExtractor(request):
    DocumentText = Preprocessing(request.POST.get('DocumentText', ""))
    return JsonResponse({"Document_Result": [],
                         "Document_Text_Highlighted": [],
                         "Subject_Color": [],
                         "Document_Nodes": [],
                         "Document_Edges": [],
                         })


def GetSubjectListByVersionId(request, version):
    graph_object = ParagraphsSubject.objects.filter(version_id=version, document__type_id=2).values(
        "subject1_id").annotate(paragraph_count=Count('id'))
    result = []
    for row in graph_object:
        subject_id = row["subject1_id"]
        subject_name = SubjectList.objects.get(id=subject_id).name
        paragraph_count = row["paragraph_count"]

        res = {
            "subject_id": subject_id,
            "subject_name": subject_name,
            "paragraph_count": paragraph_count,
        }
        result.append(res)

    return JsonResponse({"Subject_Data": result})








def GetSubjectKeywordsListBySubjectId(request, subject_id):
    KeywordsListObjects = SubjectKeywordsList.objects.filter(subject_id=subject_id).order_by("-score", "word")
    result = []
    for row in KeywordsListObjects:
        keyword_word = row.word
        keyword_score = row.score

        result.append({"word": keyword_word, "score": round(keyword_score, 2)})

    return JsonResponse({"Keyword_List": result})


def GetSubjectDocumentChartDataBySubjectId(request, subject_id):
    KeywordsListObjects = list(
        set(ParagraphsSubject.objects.filter(subject1_id=subject_id).values_list("document_id", flat=True)))
    documents_list = Document.objects.filter(id__in=KeywordsListObjects, type_id=2)

    approval_references_data = list(
        documents_list.annotate(data=F('approval_reference_name')).values("data").annotate(count=Count('id')))
    level_data = list(documents_list.annotate(data=F('level_name')).values("data").annotate(count=Count('id')))
    approval_year_data = list(
        documents_list.annotate(data=Cast(Substr('approval_date', 1, 4), IntegerField())).values("data").annotate(
            count=Count('id')))
    type_data = list(documents_list.annotate(data=F('type_name')).values("data").annotate(count=Count('id')))

    return JsonResponse(
        {"approval_references_data": approval_references_data, "level_data": level_data, "type_data": type_data,
         "approval_year_data": approval_year_data})


def CreateDocumentCSVDataBySubjectId(request, subject_id):
    paragraph_list = ParagraphsSubject.objects.filter(subject1_id=subject_id).values_list("document__name",
                                                                                          "paragraph__text",
                                                                                          "subject1_score")
    paragraph_list = np.array(paragraph_list).reshape((-1, 3))

    file_dataframe = pd.DataFrame(paragraph_list, columns=["نام سند", "متن پاراگراف", "امتیاز"])
    file_name = SubjectList.objects.get(id=subject_id).name + ".xlsx"
    file_path = os.path.join(config.MEDIA_PATH, file_name)
    file_dataframe.to_excel(file_path, index=False)

    return JsonResponse({"file_name": file_name})


def GetSubjectDocumentParagraphListBySubjectId(request, subject_id, host):
    paragraph_list = ParagraphsSubject.objects.filter(subject1_id=subject_id, document__type_id=2).order_by(
        "-subject1_score").values("document_id", "document__name", "paragraph__id", "paragraph__text", "subject1_score")
    Number_of_Show = 100
    result = []
    i = 1
    for row in paragraph_list:
        doc_id = row["document_id"]
        doc_name = row["document__name"]
        document_link = 'http://' + host + "/information/?id=" + str(doc_id)
        doc_tag = '<a href="' + document_link + '">' + doc_name + "</a>"
        paragraph_text = row["paragraph__text"]
        paragraph_id = row["paragraph__id"]

        paragraph_link = 'http://' + host + "/sentiment_analysis/?id=" + str(paragraph_id)
        paragraph_tag = '<a ' + \
                        'target="to_blank"  href="' + paragraph_link + '">' + paragraph_text + \
                        "</a>"
        score = row["subject1_score"]

        res = {"id": i, "doc_name": doc_tag, "paragraph_text": paragraph_tag, "score": score}
        result.append(res)

        if i == Number_of_Show:
            break
        i += 1

    return JsonResponse({"ParagraphDataList": result})


def DeleteCreatedCSVFile(request, file_name):
    file_path = os.path.join(config.MEDIA_PATH, file_name)
    os.remove(file_path)


def delete_lda_table(request):
    AIParagraphLDATopic.objects.all().delete()
    AILDAParagraphToTopic.objects.all().delete()
    AI_Paragraph_Subject_By_LDA.objects.all().delete()
    ParagraphLDAScore.objects.all().delete()














def GetSubjectSubjectGraphData(request, country_id, version_id):
    Object = SubjectSubjectGraphCube.objects.get(country_id=country_id, version_id=version_id)
    Nodes_data, Edges_data = Object.nodes_data, Object.edges_data

    return JsonResponse({'Nodes_data': Nodes_data, "Edges_data": Edges_data})







def findActor(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import CompareDocsActors
    CompareDocsActors.apply(None, file)
    return redirect('zip')


def fullProfileAnalysis(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocProvisionsFullProfileAnalysis
    DocProvisionsFullProfileAnalysis.apply(None, file)
    return redirect('zip')


def GetCompareDocumentListDetail(request, src_country_id, type):
    document_list = Compare_Dataset_CUBE.objects.filter(src_country_id_id=src_country_id, type=type)[0:100]
    result = []
    for row in document_list:
        src_doc_name = row.src_document_name
        dest_doc_name = row.dest_document_name
        type = row.type

        res = {"source_name": src_doc_name, "destination_name": dest_doc_name, "type": type}

        result.append(res)

    return JsonResponse({"document_list": result})


def delete_nadarad_document(request):
    Document.objects.filter(id=186010, name='ندارد').delete()
    return HttpResponse("deleted.")


def GetSubjectsListByKeywordId(request, version_id, keyword_name):
    subject_List = SubjectList.objects.filter(version_id=version_id)
    keyword_list = SubjectKeywordsList.objects.filter(subject__in=subject_List, word=keyword_name)
    result = []
    id = 1
    for row in keyword_list:
        keyword = row.word
        subject_name = row.subject.name
        score = round(float(row.score), 2)

        res = {"id": id, "keyword": keyword, "subject_name": subject_name, "score": score}

        result.append(res)

    return JsonResponse({"KeywordList": result})





def clause_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from es_scripts.persian_automate import ClauseExtractor
    ClauseExtractor.apply(file)
    return redirect('zip')


def executive_clauses_extractor(request, id):
    file = get_object_or_404(Country, id=id)
    from es_scripts.persian_automate import ExecutiveClausesExtractor
    ExecutiveClausesExtractor.apply(file)
    return redirect('zip')





# def rahbari_get_real_persons(request, country_id, type_id, label_name, from_year, to_year, place, text,
#                                       search_type, curr_page):
#     fields = [type_id, label_name, from_year, to_year]
#
#     res_query = {
#         "bool": {
#
#         }
#     }
#
#     ALL_FIELDS = True
#
#     if not all(field == 0 for field in fields):
#         ALL_FIELDS = False
#         res_query['bool']['filter'] = []
#         res_query = filter_rahbari_fields(res_query, type_id, label_name, from_year, to_year)
#
#     if text != "empty":
#         res_query["bool"]["must"] = []
#
#         if search_type == 'exact':
#             res_query = exact_search_text(res_query, place, text, ALL_FIELDS)
#         else:
#             res_query = boolean_search_text(res_query, place, text, search_type, ALL_FIELDS)
#
#     country_obj = Country.objects.get(id=country_id)
#     index_name = standardIndexName(country_obj, FullProfileAnalysis.__name__)
#
#     # ---------------------- Get Chart Data -------------------------
#     res_agg = {
#         "rahbari-person-agg":
#             {
#                 "terms": {
#                     "field": "persons.keyword",
#                     "size": bucket_size
#                 }
#             },
#     }
#
#     from_value = (curr_page - 1) * search_result_size
#
#     response = client.search(index=index_name,
#                              request_timeout=40,
#                              query=res_query,
#                              aggregations=res_agg,
#                              from_=from_value,
#                              size=search_result_size
#                              )
#
#     result = response['hits']['hits']
#
#     total_hits = response['hits']['total']['value']
#
#     aggregations = response['aggregations']
#
#     if total_hits == 10000:
#         total_hits = client.count(body={
#             "query": res_query
#         }, index=index_name, doc_type='_doc')['count']
#
#     response = client.search(index=index_name,
#                              request_timeout=40,
#                              query=res_query
#                              )
#     max_score = response['hits']['hits'][0]['_score'] if total_hits > 0 else 1
#     max_score = max_score if max_score > 0 else 1
#
#     return JsonResponse({
#         "result": result,
#         'total_hits': total_hits,
#         'max_score': max_score,
#         "curr_page": curr_page,
#         'aggregations': aggregations})


# def rahbari_get_full_profile_analysis(request, search_type, text):
#     document_id_dict = dict(request.POST)
#     document_ids_str = document_id_dict['document_ids'][0].split(',')
#     document_ids = []
#     for id in document_ids_str:
#         document_ids.append(int(id))
#
#     print(document_ids, len(document_ids))
#     # document = Document.objects.get(id=document_id)
#     # country = Country.objects.get(id=document.country_id.id)
#
#     # local_index = standardIndexName(country, DocumentParagraphs.__name__) + "_graph"
#     local_index = "rahbari_fullprofileanalysis"
#
#     place = 'متن'
#
#     res_query = {
#         "bool": {
#             "filter": {
#                 "terms": {
#                     "document_id": document_ids
#                 }
#             }
#         }
#     }
#
#     if text != "empty":
#         res_query["bool"]["must"] = []
#
#         if search_type == 'exact':
#             res_query = exact_search_text(res_query, place, text, False)
#         else:
#             res_query = boolean_search_text(res_query, place, text, search_type, False)
#
#     response = client.search(index=local_index,
#                              _source_includes=['document_id', 'paragraph_id'],
#                              request_timeout=40,
#                              query=res_query)
#
#     result = response['hits']['hits']
#
#     return JsonResponse({"result": result})


# /****** Advanced ARIMA ******/



def DocAnalysisKnowledgeGraph(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocAnalysisKnowledgeGraph
    DocAnalysisKnowledgeGraph.apply(None, file)
    return redirect('zip')


def DocAnalysisKnowledgeGraphPOS(request, id):
    file = get_object_or_404(Country, id=id)
    from scripts.Persian import DocAnalysisKnowledgeGraphPOS
    DocAnalysisKnowledgeGraphPOS.apply(None, file)
    return redirect('zip')








def GetActorTimeSeries_ChartDataAdvance(request, country_id, actor_id):
    years_chart_data = []
    last_year = 1400
    best_parameters = {
        'همه': 'نامشخص',
        'متولی اجرا': 'نامشخص',
        'همکار': 'نامشخص',
        'دارای صلاحیت اختیاری': 'نامشخص',
    }

    rmse_parameters = {
        'همه': 'نامشخص',
        'متولی اجرا': 'نامشخص',
        'همکار': 'نامشخص',
        'دارای صلاحیت اختیاری': 'نامشخص',
    }
    # new_changes
    pvalue_parameter_f = {
        'همه': 'نامشخص',
        'متولی اجرا': 'نامشخص',
        'همکار': 'نامشخص',
        'دارای صلاحیت اختیاری': 'نامشخص',
    }
    pvalue_parameter_l = {
        'همه': 'نامشخص',
        'متولی اجرا': 'نامشخص',
        'همکار': 'نامشخص',
        'دارای صلاحیت اختیاری': 'نامشخص',
    }
    try:
        actor_obj = ActorTimeSeries.objects.get(
            country_id__id=country_id,
            actor_id__id=actor_id)
        actor_time_data = actor_obj.time_series_data
        # Calculate role frequency of actors
        for year in actor_time_data['همه']:
            motevali_count = actor_time_data['متولی اجرا'][year]
            hamkar_count = actor_time_data['همکار'][year]
            salahiat_count = actor_time_data['دارای صلاحیت اختیاری'][year]
            total_count = actor_time_data['همه'][year]
            column_data = [int(year), motevali_count, hamkar_count, salahiat_count, total_count]
            years_chart_data.append(column_data)

        years_chart_data = sorted(years_chart_data, key=itemgetter(0), reverse=False)

        ARIMA_Predictions_data = \
            AdvancedARIMAPredictionData.objects.get(time_series_data__id=actor_obj.id).prediction_data['ARIMA']
        prediction_chart_data = []
        advance_chart_data = []
        for year in ARIMA_Predictions_data['همه']['PredictionAdvance']:
            if last_year <= int(year):
                motevali_count = ARIMA_Predictions_data['متولی اجرا']['PredictionAdvance'][year]
                hamkar_count = ARIMA_Predictions_data['همکار']['PredictionAdvance'][year]
                salahiat_count = ARIMA_Predictions_data['دارای صلاحیت اختیاری']['PredictionAdvance'][year]
                total_count = ARIMA_Predictions_data['همه']['PredictionAdvance'][year]
                column_data = [int(year), motevali_count, hamkar_count, salahiat_count, total_count]
                advance_chart_data.append(column_data)

        # new changes

        for role_name in ARIMA_Predictions_data.keys():
            actor_best_parameters = ARIMA_Predictions_data[role_name]['BestNewParameters']
            best_parameters[role_name] = actor_best_parameters
            actor_rmse_parameters = ARIMA_Predictions_data[role_name]['RMSE']
            rmse_parameters[role_name] = actor_rmse_parameters
            actor_pvalue_parametr_f = ARIMA_Predictions_data[role_name]['P_VALUE_First']
            pvalue_parameter_f[role_name] = actor_pvalue_parametr_f
            actor_pvalue_parametr_l = ARIMA_Predictions_data[role_name]['P_VALUE_Last']
            pvalue_parameter_l[role_name] = actor_pvalue_parametr_l

    except:
        years_chart_data = []
        advance_chart_data = []
    actor_name = Actor.objects.get(id=actor_id).name

    return JsonResponse({"years_chart_data": years_chart_data, 'actor_name': actor_name,
                         'predictions': advance_chart_data, 'last_year': last_year, 'best_parameters': best_parameters,
                         'RMSE': rmse_parameters, 'P_VALUE_First': pvalue_parameter_f,
                         'P_VALUE_Last': pvalue_parameter_l})


# /****** Advanced ARIMA ******/

















def graph_search(word, text):
    word = arabic_preprocessing(word)
    text = arabic_preprocessing(text)
    if text.startswith(word + " ") or text.endswith(" " + word) or " " + word + " " in text or word == text:
        return True
    return False














