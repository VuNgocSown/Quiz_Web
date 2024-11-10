# urls.py
from django.urls import path
from . import views
from quiz import views as quiz_views
urlpatterns = [
    path('', views.my_classes, name='my_classes'),
    path('request_class/', views.request_class, name='request_class'),
    path('create_class/', views.create_class, name='create_class'),
    path('approve_request/<int:request_id>/', views.approve_request, name='approve_request'),
    path('reject_request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('class_detail/<int:class_id>/', views.class_detail, name='class_detail'),
    path('start_quiz/<int:quiz_id>/', quiz_views.quiz_view, name='start_quiz'),
    path('quiz_result/<int:quiz_id>/<int:quiz_result_id>', quiz_views.quiz_result_view, name='quiz_result'),
    path('class_detail/<int:class_id>/mark_quiz/<int:quiz_id>/', quiz_views.mark_quiz, name='mark_quiz'),
    path('quiz_leaderboard/<int:quiz_id>', quiz_views.quiz_leaderboard_view, name='quiz_leaderboard'),
    path('', quiz_views.already_taken, name='already_taken'),
    path('approve_all_requests/<int:class_id>/', views.approve_all_requests, name='approve_all_requests'),
    path('add_members/<int:class_id>/', views.add_members, name='add_members'),
    path('import_members/<int:class_id>/', views.import_members, name='import_members'),
    path('class/<int:class_id>/export/', views.export_members, name='export_members'),
    path('class_detail/<int:class_id>/addquiz/', quiz_views.addQuiz, name='addquiz'),
    path('class_detail/<int:class_id>/addquiz/createquizfromdb/', quiz_views.create_quiz_from_db, name='create_quiz_from_db'),
    path('uploadQuiz', quiz_views.create_quiz_from_excel, name='create_quiz_from_excel'),
    path('upload_success/', quiz_views.upload_success, name='upload_success'),
    path('all_student_answers/<int:quiz_id>/<int:quiz_result_id>', quiz_views.all_quiz_result_view, name='all_student_answers'),
    path('activate_quiz/<int:quiz_id>/', quiz_views.activate_quiz, name='activate_quiz'),
    
]