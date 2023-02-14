
from scripts.Persian import DocsNgramExtractor, DocsLevelExtractor, DocsParagraphsExtractor, DocFeaturesExtractor, \
    DocsDefinitionsExtractor, DocsTFIDFExtractor, DocsListExtractor, \
    Preprocessing, DocsTypeExtractor, \
    DocsGeneralDefinitionsExtractor, DocsCreateDocumentsListCubeData, DocsCompleteJsonField, \
    DocsAnalysisLeadershipSlogan, DocsGraphCubeData, DocsReferencesExtractor2, AIParagraphTopicLDA

from scripts.Persian import  ClusteringGraphData
# from scripts.Persian import StaticDataImportDB,
from scripts.Persian import DocsParagraphsClustering, DocsCreateSubjectCubeData
from scripts.Persian.DocsDefinitionsExtractor import DocsDefinitionsExtractor
from scripts.Persian import SubjectParagraphExtractor
from scripts.Persian import DocsSubjectExtractor2
from scripts.Persian import DocsParagraphsClusteringCubeData,LDAGraphData 
from scripts.Persian import RahbariTypeExtraction, RahabriCoLabelsGraph, RahabriCorrelatedTimeSeriesExtractor, \
    RahabriGraph, RahbariLabelsTimeSeriesExtractor
from datetime import datetime

from abdal.settings import LOCAL_SETTING
ENABLE_BERT = LOCAL_SETTING['ENABLE_BERT']

if ENABLE_BERT:
    from scripts.Persian import AIDocSimilarity

# ------------------- ES Configs -----------------------------------
from abdal.es_config import INGEST_ENABLED
from es_scripts import IngestDocumentsToElastic,IngestParagraphsToElastic
# ------------------- ES Configs -----------------------------------


def persian_apply(folder_name, Country, tasks_list, host_url):
    print("start at: ", datetime.now().strftime("%H:%M:%S"))

    tasks_list = tasks_list.split("_")


    print("0. ConvertPdfsToTxt")
    Country.status = "ConvertPdfsToTxt"
    Country.save()
    Preprocessing.convert_all_pdfs_to_txt(folder_name)

    if "renameFilesToStandard" in tasks_list: ####
        print("1. renameFilesToStandard")
        Country.status = "renameFilesToStandard"
        Country.save()
        Preprocessing.renameFilesToStandard(folder_name)

    if "Preprocess" in tasks_list: ####

        Country.status = "DocsListExtractor"
        Country.save()

        print("2. DocsListExtractor")
        DocsListExtractor.apply(folder_name, Country)
        # -------------------------------------------------------

        Country.status = "DocsParagraphsExtractor"
        Country.save()

        print("3. DocsParagraphsExtractor")
        DocsParagraphsExtractor.apply(folder_name, Country)


    if "StaticDataImportDB" in tasks_list: ####
        Country.status = "StaticDataImportDB"
        Country.save()

        print("4. StaticDataImportDB")
        # StaticDataImportDB.apply(folder_name, Country)

    if "DocsTFIDFExtractor" in tasks_list: ####
        Country.status = "DocsTFIDFExtractor"
        Country.save()

        print("5. DocsTFIDFExtractor")
        DocsTFIDFExtractor.apply(folder_name, Country)

    if "Docs2gramExtractor" in tasks_list: ####
        Country.status = "Docs2gramExtractor"
        Country.save()

        print("6. Docs2gramExtractor")
        DocsNgramExtractor.apply(folder_name, 2, Country)

    if "Docs3gramExtractor" in tasks_list: ####
        Country.status = "Docs3gramExtractor"
        Country.save()

        print("7. Docs3gramExtractor")
        DocsNgramExtractor.apply(folder_name, 3, Country)

    if "DocFeaturesExtractor" in tasks_list: ####
        Country.status = "DocFeaturesExtractor"
        Country.save()

        print("8. DocFeaturesExtractor")
        DocFeaturesExtractor.apply(folder_name, Country)


    if "DocsTypeExtractor" in tasks_list: ####
        Country.status = "DocsTypeExtractor"
        Country.save()

        print("9. DocsTypeExtractor")
        DocsTypeExtractor.apply(folder_name, Country)

    if "DocsLevelExtractor" in tasks_list: ####
        Country.status = "DocsLevelExtractor"
        Country.save()

        print("10. DocsLevelExtractor")
        DocsLevelExtractor.apply(folder_name, Country)

    if "DocsGeneralDefinitionsExtractor" in tasks_list: ####
        Country.status = "DocsGeneralDefinitionsExtractor"
        Country.save()

        print("11. DocsGeneralDefinitionsExtractor")
        DocsGeneralDefinitionsExtractor.apply(folder_name, Country)
    
    # New
    if "DocsSubjectExtractor2" in tasks_list: ####
        Country.status = "DocsSubjectExtractor2"
        Country.save()

        print("12. DocsSubjectExtractor2")
        DocsSubjectExtractor2.apply(folder_name, Country)


    # ----------------- Ingestions ---------------------------

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

    # --------------------------------------------------------

    if "DocsReferencesExtractor" in tasks_list: #### No RUN
        Country.status = "DocsReferencesExtractor"
        Country.save()

        print("15. DocsReferencesExtractor")
        

        DocsReferencesExtractor2.apply(folder_name, Country)

    if "DocsDefinitionsExtractor" in tasks_list: ####
        Country.status = "DocsDefinitionsExtractor"
        Country.save()

        print("16. DocsDefinitionsExtractor")
        f = DocsDefinitionsExtractor()
        f.apply(folder_name, Country)
        del f
        
    
    if "DocsParagraphsClustering" in tasks_list: ####
        Country.status = "DocsParagraphsClustering"
        Country.save()

        print("17. DocsParagraphsClustering")
        DocsParagraphsClustering.apply(folder_name, Country)

    if "DocsParagraphsClusteringCubeData" in tasks_list: ####
        Country.status = "DocsParagraphsClusteringCubeData"
        Country.save()

        print("18. DocsParagraphsClusteringCubeData")
        DocsParagraphsClusteringCubeData.apply(folder_name, Country)
    # ----------------- CUBE DATA ---------------------------

    if "DocsCreateDocumentsListCubeData" in tasks_list: ####
        Country.status = "DocsCompleteJsonField"
        Country.save()

        print("19. DocsCompleteJsonField")
        DocsCompleteJsonField.apply(folder_name, Country)

        Country.status = "DocsCreateJsonList"
        Country.save()

        print("20. DocsCreateDocumentsListCubeData")
        DocsCreateDocumentsListCubeData.apply(folder_name, Country)

    if "DocsCreateSubjectCubeData" in tasks_list: ####
        Country.status = "DocsCreateSubjectCubeData"
        Country.save()

        print("21. DocsCreateSubjectCubeData.")
        DocsCreateSubjectCubeData.apply(folder_name, Country, host_url)
    
    
    if "DocsAnalysisLeadershipSlogan" in tasks_list:
        Country.status = "DocsAnalysisLeadershipSlogan"
        Country.save()

        print("22. DocsAnalysisLeadershipSlogan")
        DocsAnalysisLeadershipSlogan.apply(folder_name, Country)
    

    if "DocsGraphCubeData" in tasks_list:
        Country.status = "DocsGraphCubeData"
        Country.save()

        print("23. DocsGraphCubeData")
        DocsGraphCubeData.apply(folder_name, Country, host_url)


    # ----------------- AI ---------------------------
    if "AIDocSimilarity" in tasks_list:
        Country.status = "AIDocSimilarity"
        Country.save()

        print("24. AIDocSimilarity.")
        if ENABLE_BERT:
            AIDocSimilarity.apply(folder_name, Country)
        else:
            print("Bert is disable!")


    if "AIParagraphTopicLDA" in tasks_list:
        Country.status = "AIParagraphTopicLDA"
        Country.save()

        print("25. AIParagraphTopicLDA.")
        AIParagraphTopicLDA.apply(folder_name, Country)

    if "SubjectParagraphExtractor" in tasks_list:
        Country.status = "SubjectParagraphExtractor"
        Country.save()

        print("26. SubjectParagraphExtractor.")
        SubjectParagraphExtractor.apply(folder_name, Country)

    if "ClusteringGraphData" in tasks_list:
        Country.status = "ClusteringGraphData"
        Country.save()

        print("27. ClusteringGraphData.")
        ClusteringGraphData.apply(Country)

    if "LDAGraphData" in tasks_list:
        Country.status = "LDAGraphData"
        Country.save()

        print("28. LDAGraphData.")
        LDAGraphData.apply(Country)

    if "RahbariTypeExtraction" in tasks_list:
        Country.status = "RahbariTypeExtraction"
        Country.save()

        print("29. RahbariTypeExtraction.")
        RahbariTypeExtraction.apply(Country)
    
    if "RahabriCoLabelsGraph" in tasks_list:
        Country.status = "RahabriCoLabelsGraph"
        Country.save()

        print("30. RahabriCoLabelsGraph.")
        RahabriCoLabelsGraph.apply(Country)
    
    if "RahabriCorrelatedTimeSeriesExtractor" in tasks_list:
        Country.status = "RahabriCorrelatedTimeSeriesExtractor"
        Country.save()

        print("31. RahabriCorrelatedTimeSeriesExtractor.")
        RahabriCorrelatedTimeSeriesExtractor.apply(Country)
    
    if "RahabriGraph" in tasks_list:
        Country.status = "RahabriGraph"
        Country.save()

        print("32. RahabriGraph.")
        RahabriGraph.apply(Country)
    
    if "RahbariLabelsTimeSeriesExtractor" in tasks_list:
        Country.status = "RahbariLabelsTimeSeriesExtractor"
        Country.save()

        print("33. RahbariLabelsTimeSeriesExtractor.")
        RahbariLabelsTimeSeriesExtractor.apply(Country)
    


    print("finished at: ", datetime.now().strftime("%H:%M:%S"))

