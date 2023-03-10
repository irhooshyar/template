import json

from abdal import es_config
import base64
from django.db.models import F
from es_scripts.ES_Index import ES_Index
from scripts.Persian.Preprocessing import standardIndexName
from doc.models import FullProfileAnalysis, Document


# ---------------------------------------------------------------------------------

class FullProfileIndex(ES_Index):
    def __init__(self, name, settings, mappings, paragraph_document_fields):
        super().__init__(name, settings, mappings)
        self.paragraph_document_fields = paragraph_document_fields

    def generate_docs(self, files_dict, records):
        for record in records:
            record_id = record['id']

            paragraph_id = record['paragraph_id']
            paragraph_text = record['paragraph_text']
            document_id = record['document_id']
            document_name = record['document_name']
            classification_subject = record['classification_subject']
            source_name = record['source_name']
            sentiment = record['sentiment']

            persons_list = json.loads(str(record['persons']).replace('"',"").replace("'", '"').replace("\\", '\\\\'))

            locations_list = json.loads(str(record['locations']).replace('"',"").replace("'", '"').replace("\\", '\\\\'))

            organizations_list = json.loads(str(record['organizations']).replace('"',"").replace("'", '"').replace("\\", '\\\\'))


            persons = [item['word'] for item in persons_list] if len(persons_list) != 0 else ['بدون شخص حقیقی']
            locations = [item['word'] for item in locations_list] if len(locations_list) != 0 else ['بدون موقعیت مکانی']
            organizations = [item['word'] for item in organizations_list] if len(organizations_list) != 0 else ['بدون ذکر سازمان']

            date = self.paragraph_document_fields[paragraph_id]['date']
            document_date = record['document_date'] if record['document_date']  != None else 'نامشخص'

            time = self.paragraph_document_fields[paragraph_id]['time']
            document_time = time if time != None else 'نامشخص'

            labels = self.paragraph_document_fields[paragraph_id]['labels']
            document_labels = labels if labels != None else 'نامشخص'

            doc_category_name = self.paragraph_document_fields[paragraph_id]['category_name']
            category_name = doc_category_name if doc_category_name != None else 'نامشخص'

            doc_subject_name = self.paragraph_document_fields[paragraph_id]['subject_name']
            subject_name = doc_subject_name if doc_subject_name != None else 'نامشخص'


            text_bytes = bytes(paragraph_text, encoding="utf8")
            base64_bytes = base64.b64encode(text_bytes)
            base64_text = (str(base64_bytes)[2:-1])
            base64_file = base64_text

            new_doc = {
                "paragraph_id": paragraph_id,
                "document_id": document_id,
                'sentiment': sentiment,
                'persons': persons,
                'locations': locations,
                "document_name": document_name,
                'organizations': organizations,
                'persons_object': persons_list,
                'locations_object': locations_list,
                'classification_subject': classification_subject,
                'organizations_object': organizations_list,
                "document_date": document_date,
                "document_time": document_time,
                "document_labels": document_labels,
                "category_name": category_name,
                "subject_name": subject_name,
                "source_name":source_name,
                "data": base64_file
            }

            new_document = {
                "_index": self.name,
                "_id": record_id,
                "pipeline": "attachment",
                "_source": new_doc,
            }
            yield new_document


import after_response

@after_response.enable
def apply(folder, Country):
    settings = {}
    mappings = {}
    paragraph_document_fields = {}
    model_name = FullProfileAnalysis.__name__

    index_name = standardIndexName(Country, model_name)

    country_lang = Country.language

    if country_lang in ["فارسی", "استاندارد"]:
        settings = es_config.Paragraphs_Settings_2
        mappings = es_config.FullProfileAnalysis_Mappings

    records = FullProfileAnalysis.objects.filter(
        country__id=Country.id).annotate(
        document_id=F('document_paragraph__document_id__id'),
        document_name=F('document_paragraph__document_id__name'),
        document_date=F('document_paragraph__document_id__date'),
        paragraph_text=F('document_paragraph__text'),
        paragraph_id=F('document_paragraph__id'),
        source_name = F('document_paragraph__document_id__country_id__name')
    ).values('id','source_name', 'document_id', 'document_name', 'paragraph_text', 'paragraph_id', 'sentiment',
             'classification_subject', 'persons', 'locations', 'organizations','document_date')

    counter = 0
    all_objects = Document.objects.all()
    print("objects fetched successfully")
    objects_array = list(all_objects)
    Document_objects_dictionary = {item.id: item for item in objects_array}
    print("dictionary is ok")
    for record in records:
        counter += 1
        document_id = record['document_id']
        paragraph_id = record['paragraph_id']

        try:
            Document_record = Document_objects_dictionary[document_id]
            paragraph_document_fields[paragraph_id] = {'date': Document_record.date,
                                                       'time': Document_record.time,
                                                       'labels': Document_record.labels,
                                                        'category_name': Document_record.category_name,
                                                        'subject_name': Document_record.subject_name}
        except:
            paragraph_document_fields[paragraph_id] = {'date': 'نامشخص', 'year': 0,
                                                       'labels': 'نامشخس', 'type': 'نامشخص'}
            print(counter, "------error-------", document_id, paragraph_id)

    print("=========== Ingest topics paragraphs ================")

    # If index exists -> delete it.
    if ES_Index.CLIENT.indices.exists(index=index_name):
        ES_Index.CLIENT.indices.delete(index=index_name, ignore=[400, 404])
        print(f"{index_name} deleted!")

    new_index = FullProfileIndex(index_name, settings, mappings, paragraph_document_fields)
    new_index.create()
    new_index.bulk_insert_documents(folder, records, do_parallel=True)

    print("Done ...........")
