from doc.models import ParagraphsSubject, Subject
from doc.models import DocumentParagraphs, Document, DocumentSubject
import after_response
import heapq
from operator import itemgetter
import json
import math
from abdal import config
from pathlib import Path

def concat_dictionary(dict_list):
    result_dict = {}
    for dict_data in dict_list:
        for key, value in dict_data.items():
            if key not in result_dict:
                result_dict[key] = value
            else:
                result_dict[key] += value

    return result_dict


def normalize_dictionary(dictionary):
    sum_value = sum([value for key, value in dictionary.items()])
    factor = 1/sum_value if sum_value > 0 else 0
    result_dict = {}
    for key, value in dictionary.items():
        result_dict[key] = round(dictionary[key] * factor, 3)

    return result_dict



@after_response.enable
def apply(folder_name, Country):
    path = str(Path(config.PERSIAN_PATH, 'result_subject_tabnak_1.txt'))
    file = open(path, encoding="utf8").read()
    file = file.split("\n")
    delimiter = "&!&"

    result_docs = {}
    first = True
    counter = 1
    para_subject_create_list = []
    subject_dictionary = {}

    sub_list = Subject.objects.all()
    for row in sub_list:
        subject_dictionary[row.name] = row.id

    print("Load paragraph dict ...")
    paragraph_dictionary = {}
    para_list = DocumentParagraphs.objects.filter(document_id__country_id=Country)
    for row in para_list:
        paragraph_dictionary[str(row.id)] = row.document_id.id

    for row in file:
        print(counter)
        counter += 1
        try:
            line = row.split(delimiter)
            paragraph_id = line[1]
            data = line[2][1:-1].split("}, ")
            classification_result_dict = {}
            for item in list(data):
                item = item.replace("'", '"')
                if item[-1] != "}":
                    item += "}"
                item = dict(json.loads(item))
                classification_result_dict[item["label"]] = item["score"]

            if first and Subject.objects.all().count() == 0:
                first = False
                for subject in classification_result_dict.keys():
                    row = Subject.objects.create(name=subject)
                    subject_dictionary[subject] = row.id

            document_id = paragraph_dictionary[paragraph_id]

            if document_id not in result_docs:
                result_docs[document_id] = [classification_result_dict]
            else:
                result_docs[document_id].append(classification_result_dict)


            top_3_items = dict(heapq.nlargest(3, classification_result_dict.items(), key=itemgetter(1)))

            result = []
            for subject_name, score in dict(top_3_items).items():
                subject_id = subject_dictionary[subject_name]
                result.append([subject_id,  score, subject_name])

            subject1 = Subject.objects.get(id=result[0][0])
            subject1_score = result[0][1]
            subject1_name = result[0][2]

            subject2 = Subject.objects.get(id=result[1][0])
            subject2_score = result[1][1]
            subject2_name = result[1][2]

            subject3 = Subject.objects.get(id=result[2][0])
            subject3_score = result[2][1]
            subject3_name = result[2][2]

            object = ParagraphsSubject(country=Country,
                                             paragraph_id=paragraph_id,
                                             document_id=document_id,
                                             subject1=subject1,
                                             subject1_score=subject1_score,
                                             subject1_name=subject1_name,
                                             subject2=subject2,
                                             subject2_score=subject2_score,
                                             subject2_name=subject2_name,
                                             subject3=subject3,
                                             subject3_score=subject3_score,
                                             subject3_name=subject3_name)

            para_subject_create_list.append(object)
        except Exception as e:
            print("Error", e)

    batch_size = 10000
    slice_count = math.ceil(para_subject_create_list.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, para_subject_create_list.__len__())
        sub_list = para_subject_create_list[start_idx:end_idx]
        ParagraphsSubject.objects.bulk_create(sub_list)

    doc_subject_create_list = []
    for doc_id, document_subject in result_docs.items():
        document_subject = concat_dictionary(document_subject)

        document_subject = normalize_dictionary(document_subject)

        top_1_items = dict(heapq.nlargest(1, document_subject.items(), key=itemgetter(1)))

        main_subject_name = list(top_1_items.keys())[0]
        main_subject_weight = top_1_items[main_subject_name]
        main_subject = Subject.objects.get(name=main_subject_name)
        Document.objects.filter(id=doc_id).update(subject_id=main_subject, subject_name=main_subject_name,
                                                  subject_weight=main_subject_weight)
        for subject, weight in document_subject.items():
            subject = Subject.objects.get(name=subject)
            object = DocumentSubject(document_id_id=doc_id, subject_id=subject, weight=weight)
            doc_subject_create_list.append(object)

    batch_size = 10000
    slice_count = math.ceil(doc_subject_create_list.__len__() / batch_size)
    for i in range(slice_count):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, doc_subject_create_list.__len__())
        sub_list = doc_subject_create_list[start_idx:end_idx]
        DocumentSubject.objects.bulk_create(sub_list)

    print("Done . . .")





