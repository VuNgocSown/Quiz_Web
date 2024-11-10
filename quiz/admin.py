from django.contrib import admin
from .models import Category,Quiz,Option,Question,QuizResult,StudentAnswer,QuestionGen,QuizAttempt,OptionGen,FullStudentAnswer

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_text', 'question_type', 'CLO', 'quiz_id', 'difficulty')

class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_id', 'option_text', 'is_correct')
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'category','duration', 'quiz_file', 'created_at', 'updated_at')
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_id', 'quiz_result_id', 'answer_text')

class QuestionGenAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'CLO', 'difficulty', 'question_type', 'category', 'topic', 'subtopic')
    list_filter = ('difficulty', 'question_type', 'category', 'topic', 'subtopic')
    search_fields = ('question_text', 'CLO', 'topic', 'subtopic')

    fieldsets = (
         (None, {
            'fields': ('question_text', 'CLO', 'difficulty', 'question_type', 'category', 'topic', 'subtopic')
        }),
        # ('Options', {
        #     'fields': ('option_1', 'option_2', 'option_3', 'option_4', 'correct_answer'),
        #     'classes': ('mcq_options',),
        # }),
    )

    class Media:
        js = ('admin/js/question_type_toggle.js',)
admin.site.register(Category)
admin.site.register(Quiz,QuizAdmin)
admin.site.register(Option,OptionAdmin)
admin.site.register(Question,QuestionAdmin)
admin.site.register(QuizResult)
admin.site.register(StudentAnswer,StudentAnswerAdmin)
admin.site.register(QuestionGen,QuestionGenAdmin)
admin.site.register(QuizAttempt)
admin.site.register(OptionGen)
admin.site.register(FullStudentAnswer)




