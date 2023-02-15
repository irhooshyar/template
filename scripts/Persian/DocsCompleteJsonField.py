from doc.models import  Document, CUBE_DocumentJsonList, DocumentActor
from django.db.models import  F

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


def apply(folder_name, Country):
    Document.objects.filter(country_id=Country).update(json_text=None)

    doc_list = Document.objects.filter(country_id=Country)
    i = 0
    for document in doc_list:

        print(i/doc_list.__len__())
        i +=1


        date = "نامشخص"
        year = "نامشخص"
        if document.date is not None:
            date = document.date
            year = date[0:4]

        category = "نامشخص"
        if document.category_name is not None:
            category = document.category_name

        subject_name = "نامشخص"
        if document.subject_name is not None:
            subject_name = document.subject_name

        result = {"id": document.id,
                  "name": document.name,
                  "country_id": document.country_id_id,
                  "country": document.country_id.name,
                  "subject_id": document.subject_id_id,
                  "subject": subject_name,
                  "category_id": document.category_id_id,
                  "category": category,
                  "date": date,
                  "year": year,
                  }

        Document.objects.filter(id=document.id).update(json_text=result)




