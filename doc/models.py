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
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500)
    email = models.CharField(max_length=500)
    mobile = models.CharField(null=True, max_length=500)
    username = models.CharField(max_length=500)
    password = models.CharField(max_length=500)
    role = models.ForeignKey(UserRole, null=True, on_delete=models.CASCADE)
    avatar = models.TextField(null=True)
    last_login = models.CharField(max_length=500)
    is_super_user = models.IntegerField(default=0)
    is_active = models.IntegerField(default=0)
    enable = models.IntegerField(default=0)
    account_activation_token = models.CharField(null=True, max_length=500)
    account_acctivation_expire_time = models.DateTimeField(default=datetime.utcnow, blank=True)
    email_confirm_code = models.CharField(null=True, max_length=500)
    reset_password_token = models.CharField(null=True, max_length=500)
    reset_password_expire_time = models.DateTimeField(default=datetime.utcnow, blank=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, FistName: {self.first_name}, LastName: {self.last_name}, UserName: {self.username}'


class MainPanels(models.Model):
    id = models.AutoField(primary_key=True)
    panel_persian_name = models.CharField(max_length=500)
    panel_english_name = models.CharField(max_length=250, unique=True)

    class Meta:
        app_label = 'doc'
        unique_together = ('panel_persian_name', 'panel_english_name',)

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
    panel_persian_name = models.CharField(max_length=500)
    panel_english_name = models.CharField(max_length=250, unique=True)

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


class Level(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}'

class Type(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=1000)
    color = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}, Color: {self.color}'


class ApprovalReference(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}'


class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)
    language = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}'


class ActorCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)  # سازمان, وزارت, مرکز


class ActorArea(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)  # انرژی، اقتصادی


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


class SubjectKeyWords(models.Model):
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    word = models.CharField(null=True, max_length=250)
    place = models.CharField(null=True, max_length=250)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Subject_Id: {self.subject_id}, Word: {self.word}'


class Document(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=3000)
    file_name = models.TextField(null=True)

    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)

    level_id = models.ForeignKey(Level, null=True, on_delete=models.CASCADE)
    level_name = models.CharField(null=True, max_length=500)

    subject_id = models.ForeignKey(Subject, null=True, on_delete=models.CASCADE)
    subject_name = models.CharField(null=True, max_length=500)
    subject_weight = models.FloatField(default=0)

    subject_area_name = models.TextField(null=True)
    subject_sub_area_name = models.TextField(null=True)
    subject_sub_area_weight = models.FloatField(default=0)
    subject_sub_area_entropy = models.FloatField(default=0)

    type_id = models.ForeignKey(Type, null=True, on_delete=models.CASCADE)
    type_name = models.CharField(null=True, max_length=500)

    approval_reference_id = models.ForeignKey(ApprovalReference, null=True, on_delete=models.CASCADE)
    approval_reference_name = models.CharField(null=True, max_length=500)

    approval_date = models.CharField(null=True, max_length=500)
    communicated_date = models.CharField(null=True, max_length=500)

    motevalian = models.CharField(null=True, max_length=2000)
    hamkaran = models.CharField(null=True, max_length=2000)
    salahiat = models.CharField(null=True, max_length=2000)
    supervisors = models.CharField(null=True, max_length=2000)

    actors_chart_data = models.JSONField(null=True)

    word_count = models.IntegerField(null=True)
    distinct_word_count = models.IntegerField(null=True)
    stopword_count = models.IntegerField(null=True)

    json_text = models.JSONField(null=True)

    # Advisory Opinions
    advisory_opinion_count = models.IntegerField(null=True, default=0)

    # Interpretation Rules
    interpretation_rules_count = models.IntegerField(null=True, default=0)

    revoked_type_name = models.TextField(null=True, default='معتبر')
    revoked_sub_type = models.TextField(null=True)
    revoked_size = models.TextField(default='کل مصوبه')
    revoked_clauses = models.TextField(null=True, default='کل مصوبه')

    organization_name = models.TextField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.name}, Country_ID: {self.country_id}'



class SimilarityType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)  # BM25 , TFIDF

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Type: {self.name}'


class DocumentSimilarity(models.Model):
    id = models.AutoField(primary_key=True)
    doc1 = models.ForeignKey(Document, null=True, on_delete=models.CASCADE, related_name='doc1')
    doc2 = models.ForeignKey(Document, null=True, on_delete=models.CASCADE, related_name='doc2')
    similarity_type = models.ForeignKey(SimilarityType, null=True, on_delete=models.CASCADE,
                                        related_name='similarity_type')
    similarity = models.FloatField(null=True, default=0)
    highlighted_text = models.TextField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, similarity: {self.similarity}, similarity_type: {self.similarity_type}'


class RahbariSimilarity(models.Model):
    id = models.AutoField(primary_key=True)
    doc1 = models.ForeignKey(Document, null=True, on_delete=models.CASCADE, related_name='rahbari_doc1')
    doc2 = models.ForeignKey(Document, null=True, on_delete=models.CASCADE, related_name='rahbari_doc2')
    similarity_type = models.ForeignKey(SimilarityType, null=True, on_delete=models.CASCADE,
                                        related_name='rahbari_similarity_type')
    similarity = models.FloatField(null=True, default=0)
    highlighted_text = models.TextField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, similarity: {self.similarity}, similarity_type: {self.similarity_type}'


class RahbariLabelsGraph(models.Model):
    id = models.AutoField(primary_key=True)
    source_label = models.TextField(null=True)
    target_label = models.TextField(null=True)

    source_node = models.JSONField(null=True)
    target_node = models.JSONField(null=True)

    edge = models.JSONField(null=True)

    common_document_count = models.IntegerField(null=True, default=0)
    common_document_list = models.TextField(null=True)


class RahbariType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(null=True)


class RahbariTypeKeyword(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(RahbariType, on_delete=models.CASCADE, null=True)
    keyword = models.TextField(null=True)


class RahbariDocumentKeywords(models.Model):
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True)
    type = models.ForeignKey(RahbariType, on_delete=models.CASCADE, null=True)
    keyword = models.ForeignKey(RahbariTypeKeyword, on_delete=models.CASCADE, null=True)
    title_count = models.IntegerField(null=True)
    text_count = models.IntegerField(null=True)


class RahbariDocumentType(models.Model):
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True)
    type = models.ForeignKey(RahbariType, on_delete=models.CASCADE, null=True)
    score = models.FloatField(null=True, default=0)


class Rahbari(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE, related_name='rahbari_document')
    document_name = models.TextField(null=True)
    document_file_name = models.TextField(null=True)
    rahbari_date = models.CharField(null=True, max_length=500)
    rahbari_year = models.CharField(null=True, max_length=500)
    labels = models.TextField(null=True)
    type = models.ForeignKey(Type, null=True, on_delete=models.CASCADE, related_name='rahbari_type')
    rahbari_type = models.ForeignKey(RahbariType, null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class Measure(models.Model):
    id = models.AutoField(primary_key=True)
    persian_name = models.CharField(null=True, max_length=500)
    english_name = models.CharField(null=True, max_length=500)
    type = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Name: {self.persian_name}'


class Slogan(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.CharField(null=True, max_length=500)
    year = models.IntegerField(null=True)
    keywords = models.TextField(null=True)

    def __str__(self):
        return f'ID: {self.id}, year: {self.year}'


class SloganSynonymousWords(models.Model):
    id = models.AutoField(primary_key=True)
    slogan = models.ForeignKey(Slogan, on_delete=models.CASCADE)
    words = models.TextField(null=True)
    year = models.IntegerField()

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Slogan: {self.slogan}, Word: {self.word}'


class SloganAnalysis(models.Model):
    id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    docYear = models.IntegerField(null=True)
    sloganYear = models.IntegerField(null=True)
    number_per_doc = models.IntegerField(null=True)
    number_per_len = models.IntegerField(null=True)
    doc_ids = models.TextField(null=True)

    def __str__(self):
        return f'ID: {self.id}, year: {self.year}'


class SloganAnalysisUsingSynonymousWords(models.Model):
    id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    docYear = models.IntegerField(null=True)
    sloganYear = models.IntegerField(null=True)
    number_per_doc = models.IntegerField(null=True)
    number_per_len = models.IntegerField(null=True)
    doc_ids = models.TextField(null=True)

    def __str__(self):
        return f'ID: {self.id}, year: {self.year}'


class CUBE_SloganAnalysis_ChartData(models.Model):
    id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    sloganYear = models.IntegerField(null=True)
    subject_chart_data = models.JSONField(null=True)
    level_chart_data = models.JSONField(null=True)
    approval_reference_chart_data = models.JSONField(null=True)


class CUBE_SloganAnalysis_FullData(models.Model):
    id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)

    sloganYear = models.IntegerField(null=True)

    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    document_name = models.CharField(null=True, max_length=1000)

    subject_name = models.CharField(null=True, max_length=500)

    level_name = models.CharField(null=True, max_length=500)

    approval_reference_name = models.CharField(null=True, max_length=500)

    approval_date = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country_id} , Document Name: {self.document_name}'


class DocumentSubject(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, null=True, on_delete=models.CASCADE)
    measure_id = models.ForeignKey(Measure, null=True, on_delete=models.CASCADE)
    weight = models.FloatField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Subject_ID: {self.subject_id}, Measure_ID: {self.measure_id}, Weight: {self.weight}'


class DocumentTFIDF(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    word = models.CharField(null=True, max_length=1000)
    count = models.IntegerField(default=0)
    weight = models.FloatField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Word: {self.word}, Count: {self.count}, Weight: {self.weight}'


class DocumentSubjectKeywords(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    subject_keyword_id = models.ForeignKey(SubjectKeyWords, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    place = models.CharField(null=True, max_length=500)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Subject_Keyword_Id: {self.subject_keyword_id}, Count: {self.count}, Place: {self.place}'



class DocumentParagraphs(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    text = models.TextField(null=True, max_length=1000)
    number = models.IntegerField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Number: {self.number}'



class ParagraphSimilarity(models.Model):
    id = models.AutoField(primary_key=True)
    para1 = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE, related_name='para1')
    para2 = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE, related_name='para2')
    para_similarity_type = models.ForeignKey(SimilarityType, null=True, on_delete=models.CASCADE,
                                             related_name='para_similarity_type')
    similarity = models.FloatField(null=True, default=0)
    highlighted_text = models.TextField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, similarity: {self.similarity}, similarity_type: {self.similarity_type}'


class RahbariParagraphSimilarity(models.Model):
    id = models.AutoField(primary_key=True)
    para1 = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE, related_name='rahbari_para1')
    para2 = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE, related_name='dotic_para2')
    para_similarity_type = models.ForeignKey(SimilarityType, null=True, on_delete=models.CASCADE)
    similarity = models.FloatField(null=True, default=0)
    highlighted_text = models.TextField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, similarity: {self.similarity}, similarity_type: {self.similarity_type}'


class DocumentGeneralDefinition(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    keyword = models.CharField(null=True, max_length=2000)
    text = models.TextField(null=True, max_length=5000)
    is_abbreviation = models.BooleanField(null=True, default=False)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, keyword: {self.keyword}'



class DocumentNgram(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    text = models.CharField(null=True, max_length=5000)
    gram = models.IntegerField(default=1)
    count = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Text: {self.text}, Gram: {self.gram}, Count: {self.count}'


class DocumentDefinition(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    text = models.TextField(null=True, max_length=5000)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}'


class ExtractedKeywords(models.Model):
    id = models.AutoField(primary_key=True)
    definition_id = models.ForeignKey(DocumentDefinition, null=True, on_delete=models.CASCADE)
    word = models.CharField(null=True, max_length=1000)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Definition_Id: {self.definition_id}, Name: {self.word}'


class ReferencesParagraphs(models.Model):
    id = models.AutoField(primary_key=True)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    paragraph_id = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Document_References_Id: {self.document_id}, Document_Paragraphs_Id: {self.paragraph_id}'


class Graph(models.Model):
    id = models.AutoField(primary_key=True)
    src_document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE, related_name='src_doc_id')
    dest_document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE, related_name='dest_doc_id')
    measure_id = models.ForeignKey(Measure, null=True, on_delete=models.CASCADE)
    weight = models.FloatField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Src_Document_ID: {self.src_document_id}, Dest_Document_ID: {self.dest_document_id}, Measure_ID: {self.measure_id}, Weight: {self.weight}'



class Graph_Cube(models.Model):
    id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    measure_id = models.ForeignKey(Measure, null=True, on_delete=models.CASCADE)
    threshold = models.FloatField(default=0)
    edge_count = models.IntegerField(default=0)
    nodes_data = models.JSONField(null=True)
    edges_data = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, country_id: {self.country_id}, threshold: {self.threshold}'


class Graph_Distribution_Cube(models.Model):
    id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    measure_id = models.ForeignKey(Measure, null=True, on_delete=models.CASCADE)
    threshold = models.FloatField(default=0)
    edge_count = models.IntegerField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, country_id: {self.country_id}, threshold: {self.threshold}'

class CUBE_DocumentJsonList(models.Model):
    id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    document_id = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    json_text = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country_id} , Json_Text: {self.json_text}'


class CUBE_Subject_TableData(models.Model):
    id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)

    subject_id = models.ForeignKey(Subject, null=True, on_delete=models.CASCADE)
    subject_name = models.CharField(null=True, max_length=1000)

    table_data = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country_id} , Subject_Name: {self.subject_name}'


# ----------------------------------- AI -------------------------------------------

class AILDATopic(models.Model):
    id = models.AutoField(primary_key=True)
    topic_id = models.IntegerField(default=0)
    words = models.JSONField(null=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    correlation_score = models.FloatField(null=True)
    dominant_subject_name = models.CharField(null=True, max_length=1000)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.words}'


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
        return f'ID: {self.id}, Country: {self.country}, Paragraph: {self.Paragraph}, subject: {self.subject}, subject_predict: {self.subject_predict}, topic: {self.topic}, Accuracy: {self.Accuracy}'


class AILDADocToTopic(models.Model):
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    topic = models.ForeignKey(AILDATopic, null=True, on_delete=models.CASCADE)
    score = models.FloatField(default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.topics}'


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


class TFIDFWeight(models.Model):
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    weights = models.TextField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class CountryTFIDFWords(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    words = models.TextField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


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


class Report_Bug2(models.Model):
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


class DocumentComment2(models.Model):
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(null=True)
    is_accept = models.IntegerField(default=0)
    show_info = models.BooleanField(default=False)
    time = models.CharField(null=True, max_length=1000)
    # Add a m2m with HashTags
    hash_tags = models.ForeignKey(DocumentCommentHashTag, null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'



class DocumentCommentVote(models.Model):
    id = models.AutoField(primary_key=True)
    document_comment = models.ForeignKey(DocumentComment2, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agreed = models.BooleanField()
    created_at = models.DateTimeField(default=datetime.utcnow, blank=True)
    modified_at = models.DateTimeField(default=datetime.utcnow, blank=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class NoteHashTag(models.Model):
    hash_tag = models.CharField(max_length=500, primary_key=True)
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
    # Add a m2m with HashTags
    hash_tags = models.ManyToManyField(NoteHashTag)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


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


class RahbariSearchParameters(models.Model):
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
        return f'ID: {self.id}, Countryname_ID: {self.country}'


class FeatureSelectionAlgorithm(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=50)  # ANOVA/DecisionTree/

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, name: {self.name}'


class ClusteringAlorithm(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(null=True, max_length=50)  # k-means/lda/
    input_vector_type = models.CharField(null=True, max_length=50)  # TF-IDF/LDA/BERT
    ngram_type = models.CharField(null=True, max_length=50)  # (1, 1),(2, 2),
    cluster_count = models.IntegerField(default=0)
    abbreviation = models.CharField(null=True, max_length=50)  # KMS-25-(2-2)-T

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Countryname_ID: {self.name}'


class ClusterTopic(models.Model):
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(null=True, max_length=50)
    words = models.JSONField(null=True)
    algorithm = models.ForeignKey(ClusteringAlorithm, null=True, on_delete=models.CASCADE)  # k-means/lda/
    frequent_keyword_subject = models.CharField(null=True, max_length=50)
    second_frequent_keyword_subject = models.CharField(null=True, max_length=50)
    entropy = models.FloatField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.words}'


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
    algorithm = models.ForeignKey(ClusteringAlorithm, null=True, on_delete=models.CASCADE)
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
        return f'ID: {self.id}, Country_ID: {self.words}'


class CUBE_Clustering_TableData(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    algorithm = models.ForeignKey(ClusteringAlorithm, null=True, on_delete=models.CASCADE)
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
    algorithm = models.ForeignKey(ClusteringAlorithm, null=True, on_delete=models.CASCADE)
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
        return f'ID: {self.id}, Country_ID: {self.words}'


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
        return f'ID: {self.id}, Country_ID: {self.topic}'


class FeatureSelectionResults(models.Model):
    id = models.AutoField(primary_key=True)

    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    c_algorithm = models.ForeignKey(ClusteringAlorithm, null=True, on_delete=models.CASCADE)
    f_algorithm = models.ForeignKey(FeatureSelectionAlgorithm, null=True, on_delete=models.CASCADE)
    important_words_chart_data = models.JSONField(null=True)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Country_ID: {self.country}'


class SubjectsVersion(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=200)


class SubjectList(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)
    version = models.ForeignKey(SubjectsVersion, null=True, on_delete=models.CASCADE)
    color = models.CharField(null=True, max_length=200)


class SubjectKeywordsList(models.Model):
    id = models.AutoField(primary_key=True)
    word = models.CharField(null=True, max_length=500)
    subject = models.ForeignKey(SubjectList, null=True, on_delete=models.CASCADE)
    degree = models.IntegerField(default=1)
    score = models.FloatField(default=1)


class SubjectKeywordGraphCube(models.Model):
    id = models.AutoField(primary_key=True)
    version = models.ForeignKey(SubjectsVersion, null=True, on_delete=models.CASCADE)
    nodes_data = models.JSONField(null=True)
    edges_data = models.JSONField(null=True)


class SubjectSubjectGraphCube(models.Model):
    id = models.AutoField(primary_key=True)
    version = models.ForeignKey(SubjectsVersion, null=True, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    nodes_data = models.JSONField(null=True)
    edges_data = models.JSONField(null=True)


class ParagraphsSubject(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    paragraph = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE)
    version = models.ForeignKey(SubjectsVersion, null=True, on_delete=models.CASCADE)

    subject1 = models.ForeignKey(SubjectList, null=True, on_delete=models.CASCADE, related_name='subject1')
    subject1_score = models.FloatField(null=True, default=0)
    subject1_name = models.CharField(null=True, max_length=500)
    subject1_keywords = models.JSONField(null=True)

    subject2 = models.ForeignKey(SubjectList, null=True, on_delete=models.CASCADE, related_name='subject2')
    subject2_score = models.FloatField(null=True, default=0)
    subject2_name = models.CharField(null=True, max_length=500)
    subject2_keywords = models.JSONField(null=True)

    subject3 = models.ForeignKey(SubjectList, null=True, on_delete=models.CASCADE, related_name='subject3')
    subject3_score = models.FloatField(null=True, default=0)
    subject3_name = models.CharField(null=True, max_length=500)
    subject3_keywords = models.JSONField(null=True)


class KnowledgeGraphVersion(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=True, max_length=500)
    username = models.CharField(max_length=500, null=True)


class KnowledgeGraphData(models.Model):
    id = models.AutoField(primary_key=True)
    version = models.ForeignKey(KnowledgeGraphVersion, null=True, on_delete=models.CASCADE)
    nodes = models.JSONField(null=True)
    edges = models.JSONField(null=True)


class hugginfaceActors(models.Model):
    id = models.AutoField(primary_key=True)
    country_id = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    name = models.CharField(null=True, max_length=500)
    text = models.TextField(default='no text saved')


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


class RahbariLabel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(null = True)
    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class RahbariLabelsTimeSeries(models.Model):
    id = models.AutoField(primary_key=True)
    rahbari_label = models.ForeignKey(RahbariLabel, on_delete=models.CASCADE, null=True)
    time_series_data = models.JSONField(null = True)
    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class RahbariLabelsTimeSeriesGraph(models.Model):
    id = models.AutoField(primary_key=True)

    source_label = models.ForeignKey(RahbariLabel, on_delete=models.CASCADE, null=True,related_name="source_rahbari_label")
    target_label = models.ForeignKey(RahbariLabel, on_delete=models.CASCADE, null=True,related_name="target_rahbari_label")

    correlation_score = models.FloatField(null=True, default=0)

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}'


class RahbariGraphType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(null=True)
    en_name = models.TextField(null=True)
    max_weight = models.FloatField(null=True, default=0)
    weight_list = models.TextField(null=True)
    histogram_data = models.JSONField(null=True)
    histogram_title = models.TextField(null=True)
    is_label = models.IntegerField(default=0)
    is_document = models.IntegerField(default=0)

class RahbariGraph(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(RahbariGraphType, on_delete=models.CASCADE, null=True)
    nodes_data = models.JSONField(null=True)
    edges_data = models.JSONField(null=True)



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
    general_definition_id = models.ForeignKey(DocumentGeneralDefinition, null=True, on_delete=models.CASCADE)

    ref_to_paragraph = models.BooleanField(default=False)
    ref_paragraph_id = models.ForeignKey(DocumentParagraphs, null=True, on_delete=models.CASCADE,related_name='ref_paragraph_id')

    class Meta:
        app_label = 'doc'

    def __str__(self):
        return f'ID: {self.id}, Document_ID: {self.document_id}, Actor_ID: {self.actor_id}, Actor_Type_ID: {self.actor_type_id}, Paragraph_ID: {self.paragraph_id}'
