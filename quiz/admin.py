from django.contrib import admin
from .models import Category,Quiz,Option,Question,QuizResult,StudentAnswer,QuizAttempt,FullStudentAnswer

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_text', 'question_type', 'CLO', 'quiz_id', 'difficulty')

class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_id', 'option_text', 'is_correct')
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'category','duration', 'quiz_file', 'created_at', 'updated_at')
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_id', 'quiz_result_id', 'answer_text')

admin.site.register(Category)
admin.site.register(Quiz,QuizAdmin)
admin.site.register(Option,OptionAdmin)
admin.site.register(Question,QuestionAdmin)
admin.site.register(QuizResult)
admin.site.register(StudentAnswer,StudentAnswerAdmin)
admin.site.register(QuizAttempt)
admin.site.register(FullStudentAnswer)




