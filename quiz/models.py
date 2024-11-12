from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from allClass.models import MyClass
class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Quiz(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    class_id = models.ForeignKey(MyClass, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True, blank=True)
    quiz_file = models.FileField(upload_to='quiz/' , null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.IntegerField(default=45)
    total_questions = models.IntegerField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    active = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return self.title
    
    

class Question(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice Question'),
        ('FIB', 'Fill in the Blank'),
    ]
    #  add category as foreign key
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True, blank=True)
    # add subtopic
    topic = models.TextField(null=True, blank=True)
    subtopic = models.TextField(null=True, blank=True)
    id = models.AutoField(primary_key=True)
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES)
    CLO = models.IntegerField(default=1)
    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    question_text = models.TextField()
    difficulty = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.question_text}'

class Option(models.Model):
    id = models.AutoField(primary_key=True)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.option_text}"

class QuizResult(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    correct_answers = models.IntegerField()
    incorrect_answers = models.IntegerField()
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.user_id.username} - {self.quiz_id.title}- {self.score}"


class StudentAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    quiz_result_id = models.ForeignKey(QuizResult, on_delete=models.CASCADE)
    answer_text = models.TextField()
    score = models.FloatField(default=0)
    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    studen_id = models.CharField(max_length=15, blank=True, null=True)
    is_mark = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.question_id.question_text} - {self.answer_text}'

from django.db import models

class QuestionGen(models.Model):
    id = models.AutoField(primary_key=True)
    question_text = models.TextField()
    topic = models.TextField()  # Thay đổi từ CharField thành TextField
    subtopic = models.TextField()  # Thay đổi từ CharField thành TextField
    difficulty = models.IntegerField(default=1)
    CLO = models.IntegerField(default=1)
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice Question'),
        ('FIB', 'Fill in the Blank'),
    ]
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.question_text}'


# them vao de cho moi de chi duoc phep lam 1 lan voi moi user
class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'quiz')

class OptionGen(models.Model):
    id = models.AutoField(primary_key=True)
    question_id = models.ForeignKey(QuestionGen, on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.option_text}"


class FullStudentAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    quiz_result_id = models.ForeignKey(QuizResult, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE, default = None, null = True)
    option_1 = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='option_1', default = None, null = True)
    option_2 = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='option_2', default = None, null = True)
    option_3 = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='option_3', default = None, null = True)
    option_4 = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='option_4', default = None, null=True)
    answer_text = models.TextField()
    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.question_id.question_text}'