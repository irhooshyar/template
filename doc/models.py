from datetime import datetime

from django.db import models
from django.db.models.base import Model


class UserExpertise(models.Model):
    id = models.AutoField(primary_key=True)
    expertise = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'doc'


class UserRole(models.Model):
    id = models.AutoField(primary_key=True)
    persian_name = models.CharField(null=True, max_length=500)
    english_name = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.persian_name}'


class User(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    mobile = models.CharField(null=True, max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    role = models.ForeignKey(UserRole, null=True, on_delete=models.CASCADE)
    avatar = models.TextField(null=True)
    last_login = models.CharField(max_length=50)
    is_super_user = models.IntegerField(default=0)
    is_active = models.IntegerField(default=0)
    enable = models.IntegerField(default=0)
    account_activation_token = models.CharField(null=True, max_length=100)
    account_acctivation_expire_time = models.DateTimeField(default=datetime.utcnow, blank=True)
    email_confirm_code = models.CharField(null=True, max_length=100)
    reset_password_token = models.CharField(null=True, max_length=100)
    reset_password_expire_time = models.DateTimeField(default=datetime.utcnow, blank=True)
    other_expertise = models.CharField(null=True, max_length=500)
    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, FistName: {self.first_name}, LastName: {self.last_name}, UserName: {self.username}'


class MainPanels(models.Model):
    id = models.AutoField(primary_key=True)
    panel_persian_name = models.CharField(max_length=100)
    panel_english_name = models.CharField(max_length=100, unique=True)

    class Meta:
        app_label = 'doc'
        unique_together = ('panel_persian_name', 'panel_english_name')

    def __str__(self):
        return f'ID: {self.id}, panel_name: {self.panel_persian_name}'


class User_Expertise(models.Model):
    id = models.AutoField(primary_key=True)
    experise_id = models.ForeignKey(UserExpertise, null=True, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'doc'


class Panels(models.Model):
    id = models.AutoField(primary_key=True)
    parent = models.ForeignKey(MainPanels, null=True, on_delete=models.CASCADE)
    panel_persian_name = models.CharField(max_length=100)
    panel_english_name = models.CharField(max_length=100, unique=True)

    class Meta:
        app_label = 'doc'
        unique_together = ('panel_persian_name', 'panel_english_name',)

    def __str__(self):
        return f'ID: {self.id}, panel_name: {self.panel_persian_name}'


class UserPanels(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    panel = models.ForeignKey(Panels, null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'doc'
        unique_together = ('panel', 'user',)

    def __str__(self):
        return f'panel_id: {self.panel_id}, user_id: {self.user_id}'


class DeployServer(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    deploy_time = models.CharField(max_length=500)
    detail = models.CharField(max_length=500)

    class Meta:
        app_label = 'doc'


class UserLogs(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    user_ip = models.CharField(max_length=500)
    page_url = models.CharField(null=True, max_length=10000)
    visit_time = models.CharField(max_length=500)
    detail_json = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, user_id: {self.user_id}, page_url: {self.page_url}'


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)
    file = models.FileField(null=True, blank=True, upload_to='upload')

    file_name = models.CharField(null=True, max_length=500)
    language = models.CharField(null=True, max_length=500)
    status = models.CharField(null=True, blank=True, max_length=1000, default="Done")

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}, Language: {self.language}'


class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}'


class ActorCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)  # سازمان, وزارت, مرکز


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)  # سازمان, وزارت, مرکز
    language = models.CharField(default="فارسی", max_length=500)


class Label(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(null = True)
    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class Document(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(null=True)
    file_name = models.TextField(null=True)

    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)

    category_id = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)
    category_name = models.CharField(null=True, max_length=500)

    subject_id = models.ForeignKey(Subject, null=True, on_delete=models.CASCADE)
    subject_name = models.CharField(null=True, max_length=500)
    subject_weight = models.FloatField(default=0)

    labels = models.TextField(null=True) #concate by comma

    date = models.CharField(null=True, max_length=500)
    time = models.CharField(null=True, max_length=500)
    json_text = models.JSONField(null=True)
    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}, Country_ID: {self.country_id}'



class DocumentParagraphs(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    text = models.TextField(null=True, max_length=1000)
    number = models.IntegerField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Number: {self.number}'


class DocumentSubject(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, null=True, on_delete=models.CASCADE)
    weight = models.FloatField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Subject_ID: {self.subject_id}, Measure_ID: {self.measure_id}, Weight: {self.weight}'


class ParagraphsSubject(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    paragraph = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE)

    subject1 = models.ForeignKey(Subject, null=True, on_delete=models.CASCADE, related_name='subject1')
    subject1_score = models.FloatField(null=True, default=0)
    subject1_name = models.CharField(null=True, max_length=500)

    subject2 = models.ForeignKey(Subject, null=True, on_delete=models.CASCADE, related_name='subject2')
    subject2_score = models.FloatField(null=True, default=0)
    subject2_name = models.CharField(null=True, max_length=500)

    subject3 = models.ForeignKey(Subject, null=True, on_delete=models.CASCADE, related_name='subject3')
    subject3_score = models.FloatField(null=True, default=0)
    subject3_name = models.CharField(null=True, max_length=500)


class CUBE_DocumentJsonList(models.Model):
    id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    json_text = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country_id} , Json_Text: {self.json_text}'


class AIParagraphLDATopic(models.Model):
    id = models.AutoField(primary_key=True)
    topic_id = models.IntegerField(default=0)
    topic_name = models.CharField(null=True, max_length=10)
    words = models.JSONField(null=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    correlation_score = models.FloatField(null=True)
    dominant_subject_name = models.CharField(null=True, max_length=1000)
    subjects_list_chart_data_json = models.JSONField(null=True)
    paragraph_count = models.IntegerField(default=0)
    number_of_topic = models.IntegerField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, topic_id: {self.topic_id}, words: {self.words}, correlation_score: {self.correlation_score}, dominant_subject_name: {self.dominant_subject_name},'


class AILDAResults(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    number_of_topic = models.IntegerField(default=0)
    heatmap_chart_data = models.JSONField(null=True)
    topic_size_chart_data = models.JSONField(null=True)
    similarity_chart_data = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, country: {self.country}, number_of_topic: {self.number_of_topic}, heatmap_chart_data: {self.heatmap_chart_data}'


class AI_Paragraph_Subject_By_LDA(models.Model):
    id = models.AutoField(primary_key=True)
    paragraph = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    subject = models.CharField(null=True, max_length=500)
    subject_predict = models.CharField(null=True, max_length=500)
    topic = models.ForeignKey(AIParagraphLDATopic, null=True, on_delete=models.CASCADE)
    Accuracy = models.FloatField(default=0)
    number_of_topic = models.IntegerField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country: {self.country}, subject: {self.subject}, subject_predict: {self.subject_predict}, topic: {self.topic}, Accuracy: {self.Accuracy}'


class AILDAParagraphToTopic(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    paragraph = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE)
    topic = models.ForeignKey(AIParagraphLDATopic, null=True, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    number_of_topic = models.IntegerField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country: {self.country}, paragraph: {self.paragraph}, topic: {self.topic}, score: {self.score}'


class ParagraphLDAScore(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    paragraph = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE)
    scores = models.CharField(max_length=1000, null=True)
    number_of_topic = models.IntegerField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country: {self.country}, paragraph: {self.paragraph}, scores: {self.scores}'


class Recommendation(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=500)
    recommendation_text = models.TextField(max_length=100000)
    rating_value = models.IntegerField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class ReportBug(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    panel_id = models.ForeignKey(MainPanels, null=True, on_delete=models.CASCADE)
    branch_id = models.ForeignKey(Panels, null=True, on_delete=models.CASCADE)
    report_bug_text = models.TextField(max_length=100000)
    date = models.CharField(null=True, max_length=500)
    checked = models.BooleanField(default=False)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class DocumentCommentHashTag(models.Model):
    id = models.AutoField(primary_key=True)
    hash_tag = models.TextField(max_length=500)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class DocumentComment(models.Model):
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(null=True)
    is_accept = models.IntegerField(default=0)
    show_info = models.BooleanField(default=False)
    time = models.CharField(null=True, max_length=1000)
    hash_tags = models.ForeignKey(DocumentCommentHashTag, null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'



class DocumentCommentVote(models.Model):
    id = models.AutoField(primary_key=True)
    document_comment = models.ForeignKey(DocumentComment, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agreed = models.BooleanField()
    created_at = models.DateTimeField(default=datetime.utcnow, blank=True)
    modified_at = models.DateTimeField(default=datetime.utcnow, blank=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'

class DocumentNote(models.Model):
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField(null=True)
    time = models.CharField(null=True, max_length=1000)
    starred = models.BooleanField(default=False)
    docLabel = models.TextField(null=True, default='بدون برچسب')

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class DocumentNoteHashTag(models.Model):
    id = models.AutoField(primary_key=True)
    document_note = models.ForeignKey(DocumentNote, null=True, on_delete=models.CASCADE)
    hash_tag = models.CharField(max_length=500)


class UserFollow(models.Model):
    id = models.AutoField(primary_key=True)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.utcnow, blank=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class SearchParameters(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    parameter_name = models.CharField(null=True, max_length=500)
    parameter_values = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class ParagraphsFeatures(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    feature_extractor = models.CharField(null=True, max_length=50)  # TF-IDF/lda/
    features = models.JSONField(null=True)
    ngram_type = models.CharField(null=True, max_length=50)  # (1, 1),(2, 2),

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, CountryNameID: {self.country}'


class FeatureSelectionAlgorithm(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=50)  # ANOVA/DecisionTree/

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, name: {self.name}'


class ClusteringAlgorithm(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(null=True, max_length=50)  # k-means/lda/
    input_vector_type = models.CharField(null=True, max_length=50)  # TF-IDF/LDA/BERT
    ngram_type = models.CharField(null=True, max_length=50)  # (1, 1),(2, 2),
    cluster_count = models.IntegerField(default=0)
    abbreviation = models.CharField(null=True, max_length=50)  # KMS-25-(2-2)-T

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, CountryNameID: {self.name}'


class ClusterTopic(models.Model):
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(null=True, max_length=50)
    words = models.JSONField(null=True)
    algorithm = models.ForeignKey(ClusteringAlgorithm, null=True, on_delete=models.CASCADE)  # k-means/lda/
    frequent_keyword_subject = models.CharField(null=True, max_length=50)
    second_frequent_keyword_subject = models.CharField(null=True, max_length=50)
    entropy = models.FloatField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, CountryID: {self.words}'


class UserTopicLabel(models.Model):
    id = models.AutoField(primary_key=True)
    topic = models.ForeignKey(ClusterTopic, null=True, on_delete=models.CASCADE)  # k-means/lda/
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    quality_score = models.CharField(null=True, default="بدون امتیاز", max_length=100)
    label = models.CharField(null=True, default="بدون برچسب", max_length=100)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class UserLDATopicLabel(models.Model):
    id = models.AutoField(primary_key=True)
    topic = models.ForeignKey(AIParagraphLDATopic, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    quality_score = models.CharField(null=True, default="بدون امتیاز", max_length=100)
    label = models.CharField(null=True, default="بدون برچسب", max_length=100)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class ClusteringGraphData(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    algorithm = models.ForeignKey(ClusteringAlgorithm, null=True, on_delete=models.CASCADE)
    centroids_nodes_data = models.JSONField(null=True)
    centroids_edges_data = models.JSONField(null=True)
    subject_keywords_nodes_data = models.JSONField(null=True)
    subject_keywords_edges_data = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country}'


class LDAGraphData(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    number_of_topic = models.IntegerField(default=0)

    centroids_nodes_data = models.JSONField(null=True)
    centroids_edges_data = models.JSONField(null=True)
    subject_keywords_nodes_data = models.JSONField(null=True)
    subject_keywords_edges_data = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country}'


class TopicDiscriminantWords(models.Model):
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    topic = models.ForeignKey(ClusterTopic, null=True, on_delete=models.CASCADE)  # k-means/lda/
    f_algorithm = models.ForeignKey(FeatureSelectionAlgorithm, null=True, on_delete=models.CASCADE)
    discriminant_words_chart_data = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country}'


class CUBE_Clustering_TableData(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    algorithm = models.ForeignKey(ClusteringAlgorithm, null=True, on_delete=models.CASCADE)
    table_data = models.JSONField(null=True)
    dict_table_data = models.JSONField(null=True)
    clusters_data = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country}'


class ClusteringResults(models.Model):
    id = models.AutoField(primary_key=True)

    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    algorithm = models.ForeignKey(ClusteringAlgorithm, null=True, on_delete=models.CASCADE)
    heatmap_chart_data = models.JSONField(null=True)
    similarity_chart_data = models.JSONField(null=True)
    cluster_size_chart_data = models.JSONField(null=True)
    silhouette_score = models.FloatField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country}'


class ClusteringEvaluationResults(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(null=True, max_length=50)  # k-means/lda/
    input_vector_type = models.CharField(null=True, max_length=50)  # TF-IDF/LDA/BERT
    ngram_type = models.CharField(null=True, max_length=50)  # (1, 1),(2, 2)

    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)

    silhouette_score_chart_data = models.JSONField(null=True)
    elbow_inertia_chart_data = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country}'


class ParagraphsTopic(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    paragraph = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE)
    topic = models.ForeignKey(ClusterTopic, null=True, on_delete=models.CASCADE)
    score = models.IntegerField(default=1)
    keyword_subject = models.CharField(null=True, max_length=200)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country}'


class FeatureSelectionResults(models.Model):
    id = models.AutoField(primary_key=True)

    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    c_algorithm = models.ForeignKey(ClusteringAlgorithm, null=True, on_delete=models.CASCADE)
    f_algorithm = models.ForeignKey(FeatureSelectionAlgorithm, null=True, on_delete=models.CASCADE)
    important_words_chart_data = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country}'


class KnowledgeGraphVersion(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)
    username = models.CharField(max_length=500, null=True)


class KnowledgeGraphData(models.Model):
    id = models.AutoField(primary_key=True)
    version = models.ForeignKey(KnowledgeGraphVersion, null=True, on_delete=models.CASCADE)
    nodes = models.JSONField(null=True)
    edges = models.JSONField(null=True)


class FullProfileAnalysis(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    document_paragraph = models.ForeignKey(DocumentParagraphs, on_delete=models.CASCADE, null=True)

    sentiment = models.CharField(max_length=500)
    classification_subject = models.CharField(max_length=100)
    persons = models.TextField(default='')
    locations = models.TextField(default='')
    organizations = models.TextField(default='')

    def __str__(self):
        return f'ID: {self.id}, loc: {self.locations}, per: {self.persons}, org: {self.organizations}, doc-pr: {self.document_paragraph}'


class ParagraphVectorType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(null=True)
    class Meta:
        app_label = 'doc'


class ParagraphVector(models.Model):
    id = models.AutoField(primary_key=True)

    paragraph = models.ForeignKey(DocumentParagraphs, on_delete=models.CASCADE, null=True)
    vector_type = models.ForeignKey(ParagraphVectorType, on_delete=models.CASCADE, null=True)
    vector_value = models.JSONField(null=True)
    class Meta:
        app_label = 'doc'


class ActorArea(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)


class ActorType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)  # motevali, hamkar, salahiat
    pattern_keywords = models.CharField(null=True, max_length=1000)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Type: {self.name}'


class Actor(models.Model):
    id = models.AutoField(primary_key=True)
    actor_category_id = models.ForeignKey(ActorCategory, null=True, on_delete=models.CASCADE)
    name = models.CharField(null=True, max_length=500)
    forms = models.CharField(null=True, max_length=1000)
    # sub_area = models.ForeignKey(to=ActorSubArea,null=True, on_delete=models.CASCADE)
    area = models.ForeignKey(to=ActorArea, null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}'


class DocumentActor(models.Model):
    Individual = 'منفرد'
    Plural = 'اشتراکی'
    CollectiveMember = 'جمعی'

    DUTY_TYPE_CHOICES = [
        (Individual, 'Individual'),
        (Plural, 'Plural'),
        (CollectiveMember, 'CollectiveMember'),
    ]

    duty_type = models.CharField(
        null=True, max_length=500,
        choices=DUTY_TYPE_CHOICES,
        default=Individual)

    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    actor_id = models.ForeignKey(Actor, null=True, on_delete=models.CASCADE)
    actor_type_id = models.ForeignKey(ActorType, null=True, on_delete=models.CASCADE)
    paragraph_id = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE, related_name='paragraph_id')
    current_actor_form = models.CharField(null=True, max_length=1000)
    ref_to_general_definition = models.BooleanField(default=False)

    ref_to_paragraph = models.BooleanField(default=False)
    ref_paragraph_id = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE,related_name='ref_paragraph_id')

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Actor_ID: {self.actor_id}, Actor_Type_ID: {self.actor_type_id}, Paragraph_ID: {self.paragraph_id}'
