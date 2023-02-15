from doc.models import ParagraphsSubject, Subject
from doc.models import DocumentParagraphs, Document, DocumentSubject
import time
import after_response
import heapq
from transformers import AutoTokenizer, pipeline, AutoModelForSequenceClassification
from operator import itemgetter
classificationSentenceTokenizer = AutoTokenizer.from_pretrained("m3hrdadfi/albert-fa-base-v2-clf-persiannews")
classificationSentenceModel = AutoModelForSequenceClassification.from_pretrained("m3hrdadfi/albert-fa-base-v2-clf-persiannews")
classificationSentencePipeline = pipeline('text-classification', model=classificationSentenceModel,
                                          tokenizer=classificationSentenceTokenizer, top_k=None)


def concat_dictionary(dict_list):
    result_dict = {}
    for dict_data in dict_list:
        print(dict_data)
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


def text_classifications_analysis(text):
    try:
        output = classificationSentencePipeline(text)
        return {"result": output}
    except:
        window_size = 250
        text_parts = text.split(".")
        result = []

        counter = 0

        while counter < len(text_parts):
            my_text = text_parts[counter] + "."

            for j in range(counter + 1, len(text_parts)):
                new_text = text_parts[j]
                if len(my_text.split(" ")) + len(new_text.split(" ")) <= window_size:
                    my_text = my_text + new_text + "."
                else:
                    counter = j - 1
                    break
            else:
                counter = len(text_parts) - 1
            try:
                output = classificationSentencePipeline(my_text)
            except:
                output = "ERROR"
                return {"result": output}

            result.extend(output)

            counter = counter + 1

        final_result = []
        for i in range(8):
            label = result[0][i]['label']
            score = 0

            for j in range(len(result)):
                array = result[j]

                for obj in array:
                    if obj['label'] == label:
                        score += obj['score']
                        break

            final_result.append({'label': label, 'score': score / len(result)})

        return {"result": result}


@after_response.enable
def apply(folder_name, Country):
    Country.status = "Docs_Subject_Extractor"
    Country.save()

    document_list = Document.objects.filter(country_id=Country).all()

    first = True
    i = 1
    for document in document_list:

        print(i/document_list.__len__())
        i += 1

        document_id = document.id

        paragraph_list = DocumentParagraphs.objects.filter(document_id=document)
        document_subject = []
        for paragraph in paragraph_list:
            paragraph_id = paragraph.id

            paragraph_text = paragraph.text
            classification_result = text_classifications_analysis(paragraph_text)['result'][0]
            classification_result_dict = {}
            for item in classification_result:
                classification_result_dict[item['label']] = item['score']
            document_subject.append(classification_result)


            if first:
                first = False
                for subject in classification_result_dict.keys():
                    Subject.objects.create(name=subject)

            top_3_items = dict(heapq.nlargest(3, classification_result_dict.items(), key=itemgetter(1)))


            result = []
            for subject_name, score in dict(top_3_items).items():
                subject_id = Subject.objects.get(name=subject_name).id
                result.append([subject_id, score])

            subject1 = Subject.objects.get(id=result[0][0])
            subject1_score = result[0][1]
            subject1_name = subject1.name

            subject2 = None if result[1][1] > 0 else Subject.objects.get(id=result[1][0])
            subject2_score = None if result[1][1] > 0 else result[1][1]
            subject2_name = None if result[1][1] > 0 else subject2.name

            subject3 = None if result[2][1] > 0 else Subject.objects.get(id=result[2][0])
            subject3_score = None if result[2][1] > 0 else result[2][1]
            subject3_name = None if result[2][1] > 0 else subject3.name


            ParagraphsSubject.objects.create(country=Country,
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

        document_subject = concat_dictionary(document_subject)
        document_subject = normalize_dictionary(document_subject)

        top_1_items = dict(heapq.nlargest(1, document_subject.items(), key=itemgetter(1)))

        main_subject_name = list(top_1_items.keys())[0]
        main_subject_weight = top_1_items[main_subject_name]
        main_subject = Subject.objects.get(main_subject_name)
        Document.objects.filter(id=document.id).update(subject_id=main_subject, subject_name=main_subject_name,
                                                       subject_weight=main_subject_weight)

        for subject, weight in document_subject.items():
            subject = Subject.objects.get(name=subject)
            DocumentSubject.objects.create(document_id_id= document_id, subject_id=subject, weight=weight)


    print("Done . . .")





