# import json

# from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline, MT5Tokenizer, MT5ForConditionalGeneration, AutoModelForSequenceClassification
# from doc.models import FullProfileAnalysis
# from doc.models import DocumentParagraphs
# import after_response
# import math

# from pathlib import Path
# from abdal import config
# from scripts.Persian import Preprocessing
# from doc.models import Document,DocumentParagraphs
# import threading
# from itertools import chain
# import time
# from django.db.models.functions import Length


# taggingSentenceTokenizer = AutoTokenizer.from_pretrained("HooshvareLab/bert-base-parsbert-ner-uncased")
# taggingSentenceModel = AutoModelForTokenClassification.from_pretrained(
#     "HooshvareLab/bert-base-parsbert-ner-uncased")
# taggingSentencePipeline = pipeline('ner', model=taggingSentenceModel, tokenizer=taggingSentenceTokenizer)

# sentimentAnalyserTokenizer = MT5Tokenizer.from_pretrained("persiannlp/mt5-base-parsinlu-sentiment-analysis")
# sentimentAnalyserModel = MT5ForConditionalGeneration.from_pretrained("persiannlp/mt5-base-parsinlu-sentiment-analysis")

# classificationSentenceTokenizer = AutoTokenizer.from_pretrained("m3hrdadfi/albert-fa-base-v2-clf-persiannews")
# classificationSentenceModel = AutoModelForSequenceClassification.from_pretrained(
#     "m3hrdadfi/albert-fa-base-v2-clf-persiannews")
# classificationSentencePipeline = pipeline('text-classification', model=classificationSentenceModel,
#                                           tokenizer=classificationSentenceTokenizer, top_k=None)


# def Slice_Dict(docs_dict, n):
#     results = []

#     docs_dict_keys = list(docs_dict.keys())
#     step = math.ceil(docs_dict.keys().__len__() / n)
#     for i in range(n):
#         start_idx = i * step
#         end_idx = min(start_idx + step, docs_dict_keys.__len__())
#         res = {}
#         for j in range(start_idx, end_idx):
#             key = docs_dict_keys[j]
#             res[key] = docs_dict[key]
#         results.append(res)

#     return results

# def apply(folder_name, Country):

#     t = time.time()
#     FullProfileAnalysis.objects.filter(country_id=Country.id).delete()

#     print('paragraphs is going to select')
#     selected_paragraphs = DocumentParagraphs.objects.filter(
#         document_id__country_id__id=Country.id).annotate(text_len=Length('text')).filter(
#     text_len__gt=80).values()

#     print('paragraphs selected', len(selected_paragraphs))

#     print('start processing......................................')


#     Thread_Count = config.Thread_Count
#     Result_Create_List = [None] * Thread_Count


#     Paragraph_Dictionary = {}
#     for para in selected_paragraphs:
#         Paragraph_Dictionary[para['id']] = para['text']

#     Sliced_Para = Slice_Dict(Paragraph_Dictionary, Thread_Count)
#     thread_obj = []
#     thread_number = 0
#     for S in Sliced_Para:
#         thread = threading.Thread(target=Extract_Sentiment, args=(S, Result_Create_List, thread_number, Country))
#         thread_obj.append(thread)
#         thread_number += 1
#         thread.start()
#     for thread in thread_obj:
#         thread.join()

#     Result_Create_List = list(chain.from_iterable(Result_Create_List))

#     batch_size = 10000
#     slice_count = math.ceil(Result_Create_List.__len__() / batch_size)
#     for i in range(slice_count):
#         start_idx = i * batch_size
#         end_idx = min(start_idx + batch_size, Result_Create_List.__len__())
#         sub_list = Result_Create_List[start_idx:end_idx]
#         FullProfileAnalysis.objects.bulk_create(sub_list)

#     print("time ", time.time() - t)

# def delete_empty_line(line_list):
#     result_line = []
#     for line in line_list:
#         if len(line.replace(" ", "").replace("\t", "")) > 10:
#             result_line.append(line.replace("\t", "").replace("  ", " "))
#     return result_line


# def Extract_Sentiment(Paragraph_Dict, Result_Create_List, thread_number, Country):
#     Create_List = []
#     f = 0
#     for para_id, para_text in Paragraph_Dict.items():
#         print(f"{f}/{len(Paragraph_Dict.keys())}")
#         try:
#             classification_model_result = text_classifications_analysis(para_text)
#             tagging_model_result = text_tagging_analysis(para_text)
#             classification_result = process_text_classification_model(classification_model_result['result'])
#             tagging_result = process_text_tagging_model(tagging_model_result['result'], para_text)

#             sentiment_model_result = text_sentiment_analysis(para_text)
#             sentiment_result = process_text_sentiment_model(sentiment_model_result['result'][0])

#             obj = FullProfileAnalysis(country=Country, sentiment=sentiment_result,
#                                            classification_subject=classification_result, persons=tagging_result['persons'],
#                                            locations=tagging_result['locations'], organizations=tagging_result['organizations'],
#                                            document_paragraph_id=para_id)


#             # obj = FullProfileAnalysis(country=Country,
#             #                           classification_subject=classification_result, persons=tagging_result['persons'],
#             #                                locations=tagging_result['locations'], organizations=tagging_result['organizations'],
#             #                                document_paragraph_id=para_id)

#             Create_List.append(obj)

#         except Exception as e:
#             print("....................................................")
#             print(f)
#             print(".......ERROR: ", "paragraphID: ", para_id)
#             print(e)
#             print("....................................................")


#         f += 1

#     Result_Create_List[thread_number] = Create_List


# def text_sentiment_analysis(text):
#     input_ids = sentimentAnalyserTokenizer.encode(text, return_tensors="pt")
#     res = sentimentAnalyserModel.generate(input_ids)
#     output = sentimentAnalyserTokenizer.batch_decode(res, skip_special_tokens=True)
#     return {"result": output}


# def text_classifications_analysis(text):
#     try:
#         output = classificationSentencePipeline(text)
#         return {"result": output}
#     except:
#         window_size = 250
#         text_parts = text.split(".")
#         result = []

#         counter = 0

#         while counter < len(text_parts):
#             my_text = text_parts[counter] + "."

#             for j in range(counter + 1, len(text_parts)):
#                 new_text = text_parts[j]
#                 if len(my_text.split(" ")) + len(new_text.split(" ")) <= window_size:
#                     my_text = my_text + new_text + "."
#                 else:
#                     counter = j - 1
#                     break
#             else:
#                 counter = len(text_parts) - 1
#             try:
#                 output = classificationSentencePipeline(my_text)
#             except:
#                 output = "ERROR"
#                 return {"result": output}

#             result.extend(output)

#             counter = counter + 1

#         final_result = []
#         for i in range(8):
#             label = result[0][i]['label']
#             score = 0

#             for j in range(len(result)):
#                 array = result[j]

#                 for obj in array:
#                     if obj['label'] == label:
#                         score += obj['score']
#                         break

#             final_result.append({'label': label, 'score': score / len(result)})

#         return {"result": result}


# def text_tagging_analysis(text):
#     try:
#         output = taggingSentencePipeline(text)
#         return {"result": output}
#     except:
#         window_size = 250
#         text_parts = text.split(".")
#         result = []

#         counter = 0

#         while counter < len(text_parts):
#             my_text = text_parts[counter] + "."
#             current_counter = counter

#             for j in range(counter + 1, len(text_parts)):
#                 new_text = text_parts[j]
#                 if len(my_text.split(" ")) + len(new_text.split(" ")) <= window_size:
#                     my_text = my_text + new_text + "."
#                 else:
#                     counter = j - 1
#                     break
#             else:
#                 counter = len(text_parts) - 1

#             try:
#                 output = taggingSentencePipeline(my_text)
#             except:
#                 output = "ERROR"
#                 return {"result": output}

#             char_count = 0
#             for i in range(current_counter):
#                 char_count = char_count + len(text_parts[i]) + 1

#             for item in output:
#                 item['start'] += char_count
#                 item['end'] += char_count

#             result.extend(output)

#             counter = counter + 1

#         return {"result": result, "text": text}


# def process_text_sentiment_model(sentiment_model_result):
#     if sentiment_model_result == "mixed" or sentiment_model_result == "neutral":
#         return "احساس خنثی یا ترکیبی از مثبت و منفی"
#     elif sentiment_model_result == "borderline":
#         return "احساس خنثی یا ترکیبی از مثبت و منفی"
#     elif sentiment_model_result == "no sentiment expressed":
#         return "بدون ابراز احساسات"
#     elif sentiment_model_result == "very positive":
#         return 'احساس بسیار مثبت'
#     elif sentiment_model_result == "positive":
#         return 'احساس مثبت'
#     elif sentiment_model_result == "very negative":
#         return 'احساس بسیار منفی'
#     elif sentiment_model_result == "negative":
#         return 'احساس منفی'
#     else:
#         return '----'


# def process_text_classification_model(classification_model_result):
#     classification_array = classification_model_result[0]

#     max_score = 0
#     max_label = ''
#     for item in classification_array:
#         if item['score'] > max_score:
#             max_score = item['score']
#             max_label = item['label']

#     return max_label


# def process_text_tagging_model(tagging_model_result, paragraph_text):
#     taggingJson = tagging_model_result
#     taggingJson.sort(key=sort_json)

#     taggingPersonArray = []
#     taggingLocationArray = []
#     taggingOrganizationArray = []
#     taggingDateArray = []
#     taggingMoneyArray = []
#     taggingTimeArray = []
#     taggingPercentArray = []
#     taggingFacilityArray = []
#     taggingProductArray = []
#     taggingEventArray = []

#     for i in range(len(taggingJson)):
#         item_object = taggingJson[i]

#         item_object_start = item_object['entity'].split("-")[0]
#         item_object_end = item_object['entity'].split("-")[1]
#         if item_object_start == "I":
#             continue

#         if item_object_end not in ["person", "location", "organization", "date", "time", "money", "percent", "facility",
#                                    "product", "event"]:
#             continue

#         end_word_index = item_object['end']
#         start_word_index = item_object['start']

#         for j in range(i + 1, len(taggingJson)):
#             iObject = taggingJson[j]

#             if iObject['entity'][0] == "B":
#                 break

#             iObject_entity = iObject['entity'].split("-")[1]
#             if iObject_entity != item_object_end:
#                 taggingJson[j]['entity'] = taggingJson[j]['entity'].replace("I", "B")
#                 break

#             if end_word_index + 10 < iObject['start']:
#                 taggingJson[j]['entity'] = taggingJson[j]['entity'].replace("I", "B")
#                 break

#             end_word_index = iObject['end']

#         word = paragraph_text[start_word_index:end_word_index]
#         result_item = {'word': word, 'start': start_word_index, 'end': end_word_index}

#         item_object_entity = item_object['entity'].split("-")[1]
#         if item_object_entity == "person":
#             taggingPersonArray.append(result_item)
#         elif item_object_entity == "location":
#             taggingLocationArray.append(result_item)
#         elif item_object_entity == "organization":
#             taggingOrganizationArray.append(result_item)
#         elif item_object_entity == "date":
#             taggingDateArray.append(result_item)
#         elif item_object_entity == "time":
#             taggingTimeArray.append(result_item)
#         elif item_object_entity == "money":
#             taggingMoneyArray.append(result_item)
#         elif item_object_entity == "percent":
#             taggingPercentArray.append(result_item)
#         elif item_object_entity == "facility":
#             taggingFacilityArray.append(result_item)
#         elif item_object_entity == "product":
#             taggingProductArray.append(result_item)
#         elif item_object_entity == "event":
#             taggingEventArray.append(result_item)

#     return {'persons': str(taggingPersonArray), 'locations': str(taggingLocationArray),
#             'organizations': str(taggingOrganizationArray), 'dates': str(taggingDateArray),
#             'times': str(taggingTimeArray), 'moneys': str(taggingMoneyArray),
#             'percents': str(taggingPercentArray), 'facilities': str(taggingFacilityArray),
#             'product': str(taggingProductArray), 'events': str(taggingEventArray)}


# def sort_json(item):
#     return item['start']



