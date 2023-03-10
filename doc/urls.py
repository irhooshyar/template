from django.urls import path
from doc import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_zip_file, name='zip'),
    path('update/<int:id>/<str:language>/', views.update_doc, name='update'),
    path('delete/<int:id>/<str:language>/', views.delete_doc, name='delete'),
    path('fullProfileAnalysis/<int:id>/', views.fullProfileAnalysis, name='fullProfileAnalysis'),

    path('get_task_list/', views.get_task_list, name='get_task_list'),
    path('static_data_import_db/<int:id>/<str:language>/', views.static_data_import_db, name='static_data_import_db'),
    path('update_docs_from_excel/<int:id>/', views.update_docs_from_excel, name='update_docs_from_excel'),

    path('search_parameters_to_db/<int:id>/', views.search_parameters_to_db, name='search_parameters_to_db'),
    path('rahbari_search_parameters_to_db/<int:id>/', views.rahbari_search_parameters_to_db,
         name='rahbari_search_parameters_to_db'),
    path('create_judgments_table/<int:id>/', views.create_judgments_table, name='create_judgments_table'),
    path('create_standards_table/<int:id>/', views.create_standards_table, name='create_standards_table'),
    path('collective_static_data_to_db/<int:id>/', views.collective_static_data_to_db,
         name='collective_static_data_to_db'),
    path('document_json_list/<int:id>/', views.document_json_list, name='document_json_list'),
    path('actors_static_data_to_db/<int:id>/', views.actors_static_data_to_db, name='actors_static_data_to_db'),
    path('regulators_static_import_db/<int:id>/', views.regulators_static_import_db,
         name='regulators_static_import_db'),
    path('GetParagraphSubjectContent/<int:paragraph_id>/<int:version_id>/', views.GetParagraphSubjectContent,
         name='GetParagraphSubjectContent'),
    path('GetUnknownDocuments/', views.GetUnknownDocuments, name='GetUnknownDocuments'),
    path('information/', views.information, name='information'),
    path('document_profile/', views.information, name='document_profile'),
    path('following_document_comments/', views.following_document_comments, name='following_document_comments'),
    path('notes/', views.notes, name='notes'),
    path('graph2/', views.graph2, name='graph2'),
    path('es_search/', views.es_search, name='search'),
    path('dendrogram/<int:country_id>/<str:ngram_type>/', views.dendrogram, name='dendrogram'),
    path('decision_tree/<int:country_id>/<int:clustering_algorithm_id>/', views.decision_tree, name='decision_tree'),
    path('comparison/', views.comparison, name='comparison'),
    path('GetDetailDocumentById/<int:country_id>/<int:document_id>/', views.GetDetailDocumentById,
         name='GetDetailDocumentById'),
    path('rahbari_document_get_full_profile_analysis/<int:country_id>/<int:document_id>/',
         views.rahbari_document_get_full_profile_analysis, name='rahbari_document_get_full_profile_analysis'),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("forgot-password/<str:email>/", views.forgot_password_by_email, name="forgot_password_by_email"),
    path("resend/<str:email>", views.reset_password_check, name="reset_password_check"),
    path("forgot-password/<str:email>/<str:code>/<str:password>", views.reset_password, name="reset_password"),
    #path("reset-password/<str:user_id>/<str:token>", views.reset_password_check, name="reset_password_check"),
    #path("reset-password/<str:user_id>/<str:token>/<str:password>", views.reset_password, name="reset_password"),
    #path("Confirm-Email/<str:user_id>/<str:token>", views.email_check, name="email_check"),
    #path("Confirm-Email/<str:user_id>/<str:token>/<str:code>", views.user_activation, name="user_activation"),
    path("signup/<str:email>", views.resend_email_code, name="resend_email_code"),
    path("signup/<str:email>/<str:code>", views.signup_user_activation, name="signup_user_activation"),
    #path("resend-email/", views.resend_email, name="resend_email"),
    #path("resend-email/<str:email>/", views.resend_email_code, name="resend_email_code"),
    path("admin/", views.Admin, name="admin"),
    path("manage_users_tab/", views.ManageUsersTab, name="manage_users_tab"),
    path("getAcceptedUsers/<str:value>/", views.getAcceptedUsers, name="getAcceptedUsers"),
    path("manage_users/", views.ManageUsers, name="manage_users"),
    path("get_permissions_excel/", views.GetPermissionsExcel, name="get_permissions_excel"),
    path("get_allowed_panels/", views.GetAllowedPanels, name="get_allowed_panels"),
    path("get_allowed_panels/<str:username>/", views.GetPermissions, name="get_allowed_panels_by_username"),
    path("get_all_panels/", views.GetAllPanels, name="get_allowed_panels_by_username"),
    path("create_panels/", views.CreatePanel, name="create_panels"),
    path("create_or_delete_user_panels/<str:panel_name>/<str:username>/", views.CreateOrDeleteUserPanel,
         name="create_or_delete_user_panels"),
    path("create_or_delete_user_mainpanels/<str:panel_name>/<str:username>/", views.CreateOrDeleteUserMainPanel,
         name="create_or_delete_user_mainpanels"),
    path("admin_waiting_user/", views.getRegisteredUser, name="admin_waiting_user"),
    path("admin_confirm_waiting_user/", views.getRegisteredUser2, name="admin_confirm_waiting_user"),
    path("admin_accepted_user/", views.seeAcceptedUser, name="admin_accepted_user"),
    path("super_admin_user_log/", views.showUserLogs, name="super_admin_user_log"),
    path("deploy_server_log/", views.showDeployLogs, name="deploy_server_log"),
    path("admin_user_recommendation/", views.get_user_recommendation, name="admin_user_recommendation"),
    path("get_user_recommendations/<str:username>/", views.get_user_recommendations, name="get_user_recommendations"),
    path("admin_user_report_bug/", views.get_user_report_bug, name="admin_user_report_bug"),
    path("admin_accept_user_comments/", views.seeAllComment, name="admin_accept_user_comments"),
    path("admin_confirm_user_comments/", views.seeAllComment2, name="admin_confirm_user_comments"),
    path("admin_upload/", views.admin_upload, name="admin_upload"),
    path('recommendation/', views.recommendation, name='recommendation'),
    path('report_bug/', views.report_bug, name='report_bug'),
    path("delete_user/<int:user_id>/", views.DeleteUser, name='DeleteUser'),
    path('GetBM25Similarity/<int:document_id>/', views.GetBM25Similarity, name='GetBM25Similarity'),
    path('GetDocumentsSimilarity/<int:document_id>/', views.GetDocumentsSimilarity, name='GetDocumentsSimilarity'),
    path('similarityDetail/<int:main_document_id>/<int:selected_document_id>/<str:selected_country_name>/',
         views.similarityDetail, name='similarityDetail'),
    path('GetDocumentById/<int:id>/', views.GetDocumentById, name='GetDocumentById'),
    path('GetDocumentsByCountryId_Modal/<int:country_id>/<int:start_index>/<int:end_index>/',
         views.GetDocumentsByCountryId_Modal, name='GetDocumentsByCountryId_Modal'),
    path('GetCountryById/<int:id>/', views.GetCountryById, name='GetCountryById'),
    path('GetSubjectsByCountryId/<int:country_id>/', views.GetSubjectsByCountryId, name='GetSubjectsByCountryId'),
    path(
        'SearchDocument_ES/<int:country_id>/<int:category_id>/<int:subject_id>/<int:from_year>/<int:to_year>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/',
        views.SearchDocument_ES, name='SearchDocument_ES'),
    
    path(
        'GetSentimentTrend_ChartData/<int:country_id>/<int:category_id>/<int:subject_id>/<int:from_year>/<int:to_year>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/',
        views.GetSentimentTrend_ChartData, name='GetSentimentTrend_ChartData'),

    
    
    path(
        'SearchDocuments_Column_ES/<str:country_name>/<str:subject_name>/<str:category_name>/<str:from_year>/<str:to_year>/<str:sentiment>/<str:field_name>/<str:field_value>/<str:place>/<str:text>/<str:search_type>/<int:curr_page>/',
        views.SearchDocuments_Column_ES, name='SearchDocuments_Column_ES'),

    path(
        'GetActorsChartData_ES_2/<int:country_id>/<int:level_id>/<int:subject_id>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<int:revoked_type_id>/<str:place>/<str:text>/<str:search_type>/',
        views.GetActorsChartData_ES_2, name='GetActorsChartData_ES_2'),
    path('GetSearchDetails_ES/<int:document_id>/<str:search_type>/<str:text>/', views.GetSearchDetails_ES,
         name='GetSearchDetails_ES'),
    path('GetSearchDetails_ES_2/<int:document_id>/<str:search_type>/<str:text>/', views.GetSearchDetails_ES_2,
         name='GetSearchDetails_ES_2'),
    path('GetActorsList/', views.GetActorsList, name='GetActorsList'),
    path('GetActorsDict/', views.GetActorsDict, name='GetActorsDict'),
    path('GetDocActorParagraphs_Column_Modal/<int:document_id>/<str:actor_name>/<str:role_name>/',
         views.GetDocActorParagraphs_Column_Modal, name='GetDocActorParagraphs_Column_Modal'),
    path('follow/<str:follower_username>/<int:following_user_id>/', views.follow, name='follow'),
    path('unfollow/<str:follower_username>/<int:following_user_id>/', views.unfollow, name='unfollow'),
    path('GetFollowings/<str:follower_username>/', views.GetFollowings, name='GetFollowings'),
    path('GetUserComments/<int:user_id>/<int:hashtag_id>/', views.GetUserComments, name='GetUserComments'),
    path('GetAllUsers_Commented/<str:user_name>/<str:user_type>/', views.GetAllUsers_Commented,
         name='GetAllUsers_Commented'),
    path('GetActorsPararaphsByDocumentId/<int:document_id>/', views.GetActorsPararaphsByDocumentId,
         name='GetActorsPararaphsByDocumentId'),
    path('GetDocumentContent/<int:document_id>/', views.GetDocumentContent, name='GetDocumentContent'),
    path('GetDocumentSubjectContent/<int:document_id>/<int:version_id>/', views.GetDocumentSubjectContent,
         name='GetDocumentSubjectContent'),
    path(
        'SaveUser/<str:firstname>/<str:lastname>/<str:email>/<str:phonenumber>/<int:role>/<str:username>/<str:password>/<str:ip>/<str:expertise>/',
        views.SaveUser, name='SaveUser'),
    path('CheckUserLogin/<str:username>/<str:password>/<str:ip>/', views.CheckUserLogin, name='CheckUserLogin'),
    path('changeUserState/<int:user_id>/<str:state>/', views.changeUserState, name='changeUserState'),
    path('change_user_status/<str:username>/<str:status>/', views.change_user_status, name='change_user_status'),
    path('changeCommentState/<int:comment_id>/<str:state>/', views.changeCommentState, name='changeCommentState'),
    path('GetDocumentCommentVoters/<int:document_comment_id>/<str:agreed>/', views.GetDocumentCommentVoters,
         name='GetDocumentCommentVoters'),
    path('GetUserRole/', views.GetUserRole, name='GetUserRole'),
    path('GetUserExpertise/', views.GetUserExpertise, name='GetUserExpertise'),
    path('UserLogSaved/<str:username>/<str:url>/<str:ip>/', views.UserLogSaved, name='UserLogSaved'),
    path('UserDeployLogSaved/<str:username>/<str:detail>/', views.UserDeployLogSaved, name='UserDeployLogSaved'),
    path('Recommendations/<str:first_name>/<str:last_name>/<str:email>/<str:recommendation_text>/<int:rating_value>/',
         views.Recommendations, name='Recommendations'),
    path('Recommendations2/<str:recommendation_text>/<int:rating_value>/',views.Recommendations2, name='Recommendations'),
    path('CreateDocumentComment/<int:document>/<str:comment>/<str:username>/<str:comment_show_info>/<str:time>/',
         views.CreateDocumentComment, name='CreateDocumentComment'),
    path('CreateHashTagForDocumentComment/<int:comment_id>/<str:hash_tag>/', views.CreateHashTagForDocumentComment,
         name='CreateHashTagForDocumentComment'),
    path('GetAllUserCommentHashtags/', views.GetAllUserCommentHashtags, name='GetAllUserCommentHashtags'),
    path('CreateReportBug/<str:username>/<str:report_bug_text>/<str:panel_id>/<str:branch_id>/', views.CreateReportBug,
         name='CreateReportBug'),
    path('ChangeReportBugCheckStatus/<int:report_bug_id>/', views.ChangeReportBugCheckStatus,
         name='ChangeReportBugCheckStatus'),
    path('GetReportBugByFilter/<str:panel_id>/<str:branch_id>/<str:status>/', views.GetReportBugByFilter,
         name='GetReportBugByFilter'),
    path('GetDocumentComments/<int:document>/<str:username>/', views.GetDocumentComments, name='GetDocumentComments'),
    path('CreateDocumentNote/<int:document>/<str:note>/<str:username>/<str:time>/<str:label>/',
         views.CreateDocumentNote, name='CreateDocumentNote'),
    path('CreateHashTagForNote/<int:note_id>/<str:hash_tag>/', views.CreateHashTagForNote, name='CreateHashTagForNote'),
    path('GetDocumentNotes/<int:document>/<str:username>/', views.GetDocumentNotes, name='GetDocumentNotes'),
    path('ToggleNoteStar/<int:note_id>/', views.ToggleNoteStar, name='ToggleNoteStar'),

    path('changeVoteState/<str:username>/<int:document_comment>/<str:state>/', views.changeVoteState,
         name='changeVoteState'),
    path('UserLogSaved/<str:username>/<str:url>/<str:sub_url>/<str:ip>/', views.UserLogSaved, name='UserLogSaved'),

    path('getUserLogs/<int:user_id>/<str:time_start>/<str:time_end>/', views.getUserLogs, name='getUserLogs'),
    path('getChartLogs/<int:user_id>/<str:time_start>/<str:time_end>/', views.getChartLogs, name='getChartLogs'),
    path('getTableUserLogs/<int:user_id>/<str:time_start>/<str:time_end>/', views.getTableUserLogs,
         name='getTableUserLogs'),
    path('getUserChartLogs/<int:user_id>/<str:time_start>/<str:time_end>/', views.getUserChartLogs,
         name='getUserChartLogs'),
    path('GetAllNotesInTimeRange/<str:username>/<str:time_start>/<str:time_end>/', views.GetAllNotesInTimeRange,
         name='GetAllNotesInTimeRange'),
    path(
        'GetNotesInTimeRangeFilterLabelHashtag/<str:username>/<str:time_start>/<str:time_end>/<str:label>/<str:hashtag>/',
        views.GetNotesInTimeRangeFilterLabelHashtag, name='GetNotesInTimeRangeFilterLabelHashtag'),
    path('getUserDeployLogs/', views.getUserDeployLogs, name='getUserDeployLogs'),
    path('UploadFile/<str:country>/<str:language>/<str:tasks_list>/', views.UploadFile, name='UploadFile'),
    path('GetGeneralDefinition2/<int:document_id>/', views.GetGeneralDefinition2, name='GetGeneralDefinition2'),
    path(
        'GetColumnParagraphsByActorRoleName_Modal_es_2/<str:actor_name>/<str:role_name>/<int:curr_page>/<int:country_id>/<int:level_id>/<int:subject_id>/<int:type_id>/<int:approval_reference_id>/<int:from_year>/<int:to_year>/<int:from_advisory_opinion_count>/<int:from_interpretation_rules_count>/<int:revoked_type_id>/<str:place>/<str:text>/<str:search_type>/',
        views.GetColumnParagraphsByActorRoleName_Modal_es_2, name='GetColumnParagraphsByActorRoleName_Modal_es_2'),
    path('AI_predict_subject_LDA/<int:country_id>/<int:number_of_topic>/', views.GetDocumentsPredictSubjectLDA,
         name='GetDocumentsPredictSubjectLDA'),
    path("AI_topics/", views.AI_topics, name='AI_topics'),
    path("paragrraph_clustering/", views.paragrraph_clustering, name='paragrraph_clustering'),
    path("AIGetLDATopic/<int:country_id>/<int:number_of_topic>/<str:username>/", views.AIGetLDATopic,
         name='AIGetLDATopic'),
    path("AILDADocFromTopic/<int:topic_id>/", views.AILDADocFromTopic, name='AILDADocFromTopic'),
    path("AILDAWordCloudTopic/<int:topic_id>/", views.AILDAWordCloudTopic, name='AILDAWordCloudTopic'),
    path("AILDASubjectChartTopic/<int:topic_id>/", views.AILDASubjectChartTopic, name='AILDASubjectChartTopic'),
    path('ShowMyUserProfile/', views.ShowMyUserProfile, name='ShowMyUserProfile'),
    path('GetMyUserProfile/', views.GetMyUserProfile, name='GetMyUserProfile'),
    path('SetMyUserProfile/', views.SetMyUserProfile, name='SetMyUserProfile'),
    path('ChangePassword/<str:old_password>/<str:new_password>/', views.ChangePassword, name='ChangePassword'),
    path('ShowUserProfile/', views.ShowUserProfile, name='ShowUserProfile'),
    path('GetUserProfile/<int:id>/', views.GetUserProfile, name='GetUserProfile'),
    path('account/self/', views.self, name='self'),
    path('get_pending_followers/', views.get_pending_followers, name='get_pending_followers'),
    path('accept_follower/<int:id>/', views.accept_follower, name='accept_follower'),
    path('reject_follower/<int:id>/', views.reject_follower, name='reject_follower'),
    path('GetUnknownDocuments/', views.GetUnknownDocuments, name='GetUnknownDocuments'),
    path('ingest_documents_to_index/<int:id>/<str:language>/', views.ingest_documents_to_index,
         name='ingest_documents_to_index'),
    path('ingest_document_actor_to_index/<int:id>/<str:language>/', views.ingest_document_actor_to_index,
         name='ingest_document_actor_to_index'),
    path('ingest_actor_supervisor_to_index/<int:id>/<str:language>/', views.ingest_actor_supervisor_to_index,
         name='ingest_actor_supervisor_to_index'),
    path('ingest_spatiotemporal_to_index/<int:id>/', views.ingest_spatiotemporal_to_index,
         name='ingest_spatiotemporal_to_index'),
    path('ingest_judgments_to_index/<int:id>/<str:language>/', views.ingest_judgments_to_index,
         name='ingest_judgments_to_index'),
    path('ingest_revoked_documents/<int:id>/<str:language>/', views.ingest_revoked_documents,
         name='ingest_revoked_documents'),
    path('ingest_paragraphs_to_index/<int:id>/<str:language>/<int:is_for_ref>/', views.ingest_paragraphs_to_index,
         name='ingest_paragraphs_to_index'),
    path('ingest_standard_documents_to_index/<int:id>/<str:language>/', views.ingest_standard_documents_to_index,
         name='ingest_standard_documents_to_index'),
    path('ingest_terminology_to_index/<int:id>/<str:language>/', views.ingest_terminology_to_index,
         name='ingest_terminology_to_index'),
    path('ingest_full_profile_analysis_to_elastic/<int:id>/', views.ingest_full_profile_analysis_to_elastic,
         name='ingest_full_profile_analysis_to_elastic'),
    path('ingest_rahbari_to_index/<int:id>/', views.ingest_rahbari_to_index,
         name='ingest_rahbari_to_index'),
    path('ingest_rahbari_to_sim_index/<int:id>/', views.ingest_rahbari_to_sim_index,
         name='ingest_rahbari_to_sim_index'),
    path('ingest_document_collective_members_to_index/<int:id>/', views.ingest_document_collective_members_to_index,
         name='ingest_document_collective_members_to_index'),
    path('ingest_clustering_paragraphs_to_index/<int:id>/<str:language>/', views.ingest_clustering_paragraphs_to_index,
         name='ingest_clustering_paragraphs_to_index'),
    path('GetSearchDetails_ES_Rahbari/<int:document_id>/<str:search_type>/<str:text>/',
         views.GetSearchDetails_ES_Rahbari, name='GetSearchDetails_ES_Rahbari'),
    path('rahbari_similarity_calculation/<int:id>/', views.rahbari_similarity_calculation,
         name='rahbari_similarity_calculation'),
    path('ingest_standard_documents_to_sim_index/<int:id>/<str:language>/',
         views.ingest_standard_documents_to_sim_index, name='ingest_standard_documents_to_sim_index'),
    path('paragraphs_similarity_calculation/<int:id>/', views.paragraphs_similarity_calculation,
         name='paragraphs_similarity_calculation'),
    path('rahbari_paragraphs_similarity_calculation/<int:id>/', views.rahbari_paragraphs_similarity_calculation,
         name='rahbari_paragraphs_similarity_calculation'),
    path('update_file_name_extention/<int:id>/', views.update_file_name_extention, name='update_file_name_extention'),
    path('revoked_types_to_db/<int:id>/', views.revoked_types_to_db, name='revoked_types_to_db'),
    path('subject_area_keywords_to_db/<int:id>/', views.subject_area_keywords_to_db,
         name='subject_area_keywords_to_db'),
    path('rahbari_update_fields_from_file/<int:id>/', views.rahbari_update_fields_from_file,
         name='rahbari_update_fields_from_file'),
    path('clustering_algorithms_to_db/<int:id>/', views.clustering_algorithms_to_db,
         name='clustering_algorithms_to_db'),
    path('rahbari_labels_to_db/<int:id>/', views.rahbari_labels_to_db,
         name='rahbari_labels_to_db'),
    path('GetDoticSimDocument_ByTitle/<str:document_name>/', views.GetDoticSimDocument_ByTitle,
         name='GetDoticSimDocument_ByTitle'),
    path('get_rahbari_document_actor/<int:document_id>/', views.get_rahbari_document_actor,
         name='get_rahbari_document_actor'),
    path("ManualClustering/", views.ManualClustering, name='ManualClustering'),
    path("BoostingSearchParagraph_ES/<int:country_id>/<int:curr_page>/<int:result_size>/",
         views.BoostingSearchParagraph_ES, name='BoostingSearchParagraph_ES'),
    path(
        "rahbari_document_classification_chart_column/<int:document_id>/<str:subject>/<int:curr_page>/<int:result_size>/",
        views.rahbari_document_classification_chart_column, name='rahbari_document_classification_chart_column'),
    path(
        "rahbari_document_name_chart_column/<int:document_id>/<str:name>/<str:field_name>/<int:curr_page>/<int:result_size>/",
        views.rahbari_document_name_chart_column, name='rahbari_document_name_chart_column'),

    path(
        "rahbari_document_actor_chart_column/<int:document_id>/<str:name>/<int:curr_page>/<int:result_size>/",
        views.rahbari_document_actor_chart_column, name='rahbari_document_actor_chart_column'),

    path(
        "export_rahbari_document_chart_column/<int:document_id>/<str:text>/<str:keyword>/<int:curr_page>/<int:result_size>/",
        views.export_rahbari_document_chart_column, name='export_rahbari_document_chart_column'),

    path(
        "BoostingSearchKnowledgeGraph_ES/<int:country_id>/<str:field_name>/<str:field_value>/<str:language>/<str:search_type>/<int:curr_page>/<int:result_size>/",
        views.BoostingSearchKnowledgeGraph_ES, name='BoostingSearchKnowledgeGraph_ES'),

    path(
        "BoostingSearchParagraph_Column_ES/<int:country_id>/<str:field_name>/<str:field_value>/<int:curr_page>/<int:result_size>/",
        views.BoostingSearchParagraph_Column_ES, name='BoostingSearchParagraph_Column_ES'),

    # ----------- LDA heatmap -----------------
    path("AIGet_Topic_Centers_CahrtData/<int:country_id>/<int:number_of_topic>/", views.AIGet_Topic_Centers_CahrtData,
         name='AIGet_Topic_Centers_CahrtData'),
    path('GetLDAGraphData/<int:country_id>/<int:number_of_topic>/', views.GetLDAGraphData,
         name='GetLDAGraphData'),

    path('GetLDAKeywordGraphData/<int:country_id>/<int:number_of_topic>/', views.GetLDAKeywordGraphData,
         name='GetLDAKeywordGraphData'),

    path('save_lda_topic_label/<str:topic_id>/<str:username>/<str:label>/', views.save_lda_topic_label,
         name='save_lda_topic_label'),

    # -------------- Clustering ----------------
    path(
        'GetParagraph_Clusters/<int:country_id>/<str:algorithm_name>/<str:vector_type>/<int:cluster_count>/<str:ngram_type>/<str:username>/',
        views.GetParagraph_Clusters, name='GetParagraph_Clusters'),
    path(
        'Get_ClusterCenters_ChartData/<int:country_id>/<str:algorithm_name>/<str:vector_type>/<int:cluster_count>/<str:ngram_type>/',
        views.Get_ClusterCenters_ChartData, name='Get_ClusterCenters_ChartData'),
    path(
        'Get_ClusteringAlgorithm_DiscriminatWords_ChartData/<int:country_id>/<str:algorithm_name>/<str:vector_type>/<int:cluster_count>/<str:ngram_type>/',
        views.Get_ClusteringAlgorithm_DiscriminatWords_ChartData,
        name='Get_ClusteringAlgorithm_DiscriminatWords_ChartData'),

    path('Get_Clustering_Vocabulary/<int:country_id>/<str:vector_type>/<str:ngram_type>/',
         views.Get_Clustering_Vocabulary,
         name='Get_Clustering_Vocabulary'),

    path(
        'Get_ClusteringEvaluation_Silhouette_ChartData/<int:country_id>/<str:algorithm_name>/<str:vector_type>/<str:ngram_type>/',
        views.Get_ClusteringEvaluation_Silhouette_ChartData, name='Get_ClusteringEvaluation_Silhouette_ChartData'),
    path('save_topic_label/<str:topic_id>/<str:username>/<str:label>/', views.save_topic_label,
         name='save_topic_label'),
    path(
        'Get_Topic_Paragraphs_ES/<int:country_id>/<str:topic_id>/<int:result_size>/<int:curr_page>/<int:get_paragraphs>/<int:get_aggregations>/',
        views.Get_Topic_Paragraphs_ES, name='Get_Topic_Paragraphs_ES'),
    path(
        'Get_Topic_Paragraphs_Column_ES/<int:country_id>/<str:topic_id>/<str:field_name>/<str:field_value>/<int:curr_page>/<int:result_size>/',
        views.Get_Topic_Paragraphs_Column_ES, name='Get_Topic_Paragraphs_Column_ES'),
    path(
        'Get_ANOVA_Word_Paragraphs_Column_ES/<int:country_id>/<str:topic_id>/<str:word>/<int:curr_page>/<int:result_size>/',
        views.Get_ANOVA_Word_Paragraphs_Column_ES, name='Get_ANOVA_Word_Paragraphs_Column_ES'),
    path(
        'Export_ANOVA_Word_Paragraphs_Column_ES/<int:country_id>/<str:topic_id>/<str:word>/<str:username>/<int:curr_page>/<int:result_size>/',
        views.Export_ANOVA_Word_Paragraphs_Column_ES, name='Export_ANOVA_Word_Paragraphs_Column_ES'),

    path('Excel_Topic_Paragraphs_ES/<int:country_id>/<str:topic_id>/<int:result_size>/<int:curr_page>/<str:username>/',
         views.Excel_Topic_Paragraphs_ES, name='Excel_Topic_Paragraphs_ES'),

    path('Get_Topic_Anova_ChartData/<int:country_id>/<str:topic_id>/', views.Get_Topic_Anova_ChartData,
         name='Get_Topic_Anova_ChartData'),
    path('Get_Topic_TagCloud_ChartData/<int:country_id>/<str:topic_id>/', views.Get_Topic_TagCloud_ChartData,
         name='Get_Topic_TagCloud_ChartData'),
    path(
        'GetClusteringGraphData/<int:country_id>/<str:algorithm_name>/<str:algorithm_vector_type>/<int:cluster_size>/<str:ngram_type>/',
        views.GetClusteringGraphData,
        name='GetClusteringGraphData'),
    path(
        'GetClusterKeywordGraphData/<int:country_id>/<str:algorithm_name>/<str:algorithm_vector_type>/<int:cluster_size>/<str:ngram_type>/',
        views.GetClusterKeywordGraphData,
        name='GetClusterKeywordGraphData'),
    path(
        'GetKeywordClustersData/<int:country_id>/<str:algorithm_name>/<str:algorithm_vector_type>/<int:cluster_size>/<str:keyword>/',
        views.GetKeywordClustersData,
        name='GetKeywordClustersData'),
    path('GetKeywordLDAData/<int:country_id>/<int:cluster_size>/<str:username>/<str:keyword>/', views.GetKeywordLDAData,
         name='GetKeywordLDAData'),
    path('knowledgeGraph/', views.knowledgeGraph, name='knowledgeGraph'),
    path('SaveKnowledgeGraph/<str:graph_name>/<str:username>/<int:graph_id>/', views.SaveKnowledgeGraph,
         name='SaveKnowledgeGraph'),
    path('DeleteKnowledgeGraph/<int:graph_id>/', views.DeleteKnowledgeGraph, name='DeleteKnowledgeGraph'),
    path('sentiment_analysis/', views.sentiment_analysis_panel, name='sentimentAnalysis'),
    path('tagAnalyser/<str:text>/', views.tagging_analyser, name='tag_analysis'),
    path('sentimentAnalyser/<str:text>/', views.sentiment_analyser, name='sentiment_analysis'),
    path('classificationAnalyser/<str:text>/', views.classification_analyser,
         name='classification_analysis'),
    path('auto_translator/<str:text>/', views.auto_translator,
         name='auto_translator'),
    path('GetParagraphBy_ID/<int:paragraph_id>/', views.GetParagraphBy_ID,
         name='GetParagraphBy_ID'),
    path('GetAllKnowledgeGraphList/<str:username>/', views.GetAllKnowledgeGraphList,
         name='GetAllKnowledgeGraphList'),
    path('GetKnowledgeGraphData/<int:version_id>/', views.GetKnowledgeGraphData,
         name='GetKnowledgeGraphData'),
    path('GetTextSummary/', views.GetTextSummary,
         name='GetTextSummary'),
    path('insert_docs_to_rahbari_table/<int:id>/', views.insert_docs_to_rahbari_table,
         name='insert_docs_to_rahbari_table'),
    # ES_USER_LOG
    path('getChartLogs_ES/<int:user_id>/<str:time_start>/<str:time_end>/', views.getChartLogs_ES,
         name='getChartLogs_ES'),

    path('getTableUserLogs_ES/<int:user_id>/<str:time_start>/<str:time_end>/', views.getTableUserLogs_ES,
         name='getTableUserLogs_ES'),

    path('getUserLogs/<int:user_id>/<str:time_start>/<str:time_end>/', views.getUserLogs, name='getUserLogs'),

    path('getUserLogs_ES/<int:user_id>/<str:time_start>/<str:time_end>/<int:curr_page>/<int:page_size>/',
         views.getUserLogs_ES, name='getUserLogs_ES'),

    path('ingest_userlogs_to_index/<int:id>/<str:language>/', views.userlogs_to_index,
         name='ingest_userlogs_to_index'),

    path('GetSearchParameters/<int:country_id>/', views.GetSearchParameters, name='GetSearchParameters'),
    path('GetSimilarParagraphs_ByParagraphID/<int:paragraph_id>/', views.GetSimilarParagraphs_ByParagraphID,
         name='GetSimilarParagraphs_ByParagraphID'),

    path('GetSemanticSimilarParagraphs_ByParagraphID/<int:paragraph_id>/',
         views.GetSemanticSimilarParagraphs_ByParagraphID, name='GetSemanticSimilarParagraphs_ByParagraphID'),
    path("AILDASubjectChartTopicGetInformation/<int:topic_id>/<str:subject_name>/<int:curr_page>/<int:result_size>/",
         views.AILDASubjectChartTopicGetInformation, name='AILDASubjectChartTopicGetInformation'),

    path(
        "AILDASubjectChartTopicGetInformationExport/<int:topic_id>/<str:subject_name>/<int:curr_page>/<int:result_size>/",
        views.AILDASubjectChartTopicGetInformationExport, name='AILDASubjectChartTopicGetInformationExport'),

    path('resource_profile/', views.resource_profile, name='resource_profile'),
    path('GetResourceInformation/', views.GetResourceInformation, name='GetResourceInformation'),


    path('save_log/', views.save_log, name='save_log')
]
