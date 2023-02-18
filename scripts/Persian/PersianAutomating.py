from scripts.Persian import DocsParagraphsExtractor, DocsListExtractor, Preprocessing,  DocsCreateDocumentsListCubeData, DocsCompleteJsonField, AIParagraphTopicLDA
from scripts.Persian import ClusteringGraphData
from scripts.Persian import StaticDataImportDB
from scripts.Persian import DocsParagraphsClustering
from scripts.Persian import SubjectParagraphExtractor
from scripts.Persian import DocsSubjectExtractor2
from scripts.Persian import DocsParagraphsClusteringCubeData,LDAGraphData 
from scripts.Persian import DocProvisionsFullProfileAnalysis,DocsParagraphVectorExtractor
from datetime import datetime

from abdal.settings import LOCAL_SETTING
ENABLE_BERT = LOCAL_SETTING['ENABLE_BERT']

from es_scripts import IngestDocumentsToElastic, IngestParagraphsToElastic, IngestFullProfileAnalysisToElastic



def persian_apply(folder_name, Country, tasks_list, host_url):
    print("start at: ", datetime.now().strftime("%H:%M:%S"))

    tasks_list = tasks_list.split("_")


    print("0. ConvertPdfsToTxt")
    Country.status = "ConvertPdfsToTxt"
    Country.save()
    Preprocessing.convert_all_pdfs_to_txt(folder_name)

    if "renameFilesToStandard" in tasks_list:
        print("1. renameFilesToStandard")
        Country.status = "renameFilesToStandard"
        Country.save()
        Preprocessing.renameFilesToStandard(folder_name)

    if "Preprocess" in tasks_list:

        Country.status = "DocsListExtractor"
        Country.save()

        print("2. DocsListExtractor")
        DocsListExtractor.apply(folder_name, Country)
        # -------------------------------------------------------

        Country.status = "DocsParagraphsExtractor"
        Country.save()

        print("3. DocsParagraphsExtractor")
        DocsParagraphsExtractor.apply(folder_name, Country)



    # if "SubjectParagraphExtractor" in tasks_list:
    #     Country.status = "SubjectParagraphExtractor"
    #     Country.save()
    #
    #     print("26. SubjectParagraphExtractor.")
    #     SubjectParagraphExtractor.apply(folder_name, Country)


    if "StaticDataImportDB" in tasks_list: ####
        Country.status = "StaticDataImportDB"
        Country.save()

        print("4. StaticDataImportDB")
        StaticDataImportDB.apply(folder_name, Country)

    # --- Ingest Documents
    if "IngestDocumentsToElastic" in tasks_list:
        Country.status = "IngestDocumentsToElastic"
        Country.save()

        print("13. IngestDocumentsToElastic.")
        IngestDocumentsToElastic.apply(folder_name, Country)


    # --- Ingest Paragraphs
    if "IngestParagraphsToElastic" in tasks_list:
        Country.status = "IngestParagraphsToElastic"
        Country.save()

        print("14. IngestParagraphsToElastic.")
        IngestParagraphsToElastic.apply(folder_name, Country,1)



    # --- Ingest Paragraphs For Similarity
    if "IngestParagraphsToElastic" in tasks_list:
        Country.status = "IngestParagraphsToElastic"
        Country.save()

        print("15. IngestParagraphsToElastic.")
        IngestParagraphsToElastic.apply(folder_name, Country,0)

    # if "DocsParagraphsClustering" in tasks_list:
    #     Country.status = "DocsParagraphsClustering"
    #     Country.save()

    #     print("17. DocsParagraphsClustering")
    #     DocsParagraphsClustering.apply(folder_name, Country)

    # if "DocsParagraphsClusteringCubeData" in tasks_list:
    #     Country.status = "DocsParagraphsClusteringCubeData"
    #     Country.save()

    #     print("18. DocsParagraphsClusteringCubeData")
    #     DocsParagraphsClusteringCubeData.apply(folder_name, Country)

    if "DocsCreateDocumentsListCubeData" in tasks_list:
        Country.status = "DocsCompleteJsonField"
        Country.save()

        print("19. DocsCompleteJsonField")
        DocsCompleteJsonField.apply(folder_name, Country)

        Country.status = "DocsCreateJsonList"
        Country.save()

        print("20. DocsCreateDocumentsListCubeData")
        DocsCreateDocumentsListCubeData.apply(folder_name, Country)

    # if "AIParagraphTopicLDA" in tasks_list:
    #     Country.status = "AIParagraphTopicLDA"
    #     Country.save()

    #     print("25. AIParagraphTopicLDA.")
    #     AIParagraphTopicLDA.apply(folder_name, Country)


    # if "ClusteringGraphData" in tasks_list:
    #     Country.status = "ClusteringGraphData"
    #     Country.save()

    #     print("27. ClusteringGraphData.")
    #     ClusteringGraphData.apply(Country)

    # if "LDAGraphData" in tasks_list:
    #     Country.status = "LDAGraphData"
    #     Country.save()

    #     print("28. LDAGraphData.")
    #     LDAGraphData.apply(Country)


    # Edit By HuggingFace
    if "DocsSubjectExtractor2" in tasks_list:
        Country.status = "DocsSubjectExtractor2"
        Country.save()
        # New Script
        print("8. DocsSubjectExtractor2")
        DocsSubjectExtractor2.apply(folder_name, Country) #update paragraphs and document


    if "DocsParagraphVectorExtractor" in tasks_list: ####
        Country.status = "DocsParagraphVectorExtractor"
        Country.save()

        print("4. DocsParagraphVectorExtractor")
        DocsParagraphVectorExtractor.apply(folder_name, Country)


    if "DocProvisionsFullProfileAnalysis" in tasks_list:
        Country.status = "DocProvisionsFullProfileAnalysis"
        Country.save()

        print("28. DocProvisionsFullProfileAnalysis.")
        DocProvisionsFullProfileAnalysis.apply(folder_name, Country)

    if "IngestFullProfileAnalysisToElastic" in tasks_list:
        Country.status = "IngestFullProfileAnalysisToElastic"
        Country.save()

        print("28. IngestFullProfileAnalysisToElastic.")
        IngestFullProfileAnalysisToElastic.apply(folder_name, Country)




    print("finished at: ", datetime.now().strftime("%H:%M:%S"))

