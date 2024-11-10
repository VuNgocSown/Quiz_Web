from django.urls import path
from . import views
# import authviews
from django.contrib.auth import views as authviews
handler404 = 'account.views.custom_404'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('edit_profile/', views.editProfile, name='edit_profile'),
    path('',views.registerOk,name='registerOk'),
    path('manage/', views.manage, name='account_management'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('upload_excel/', views.upload_excel, name='upload_excel'),
    path('create_accounts/', views.create_accounts, name='create_accounts'),
    path('check_account_creation_progress/', views.check_account_creation_progress, name='check_account_creation_progress'),
    path('change_password/', views.change_password, name='change_password'),

    path('reset_password/', authviews.PasswordResetView.as_view(template_name="Reset_password_form.html"), name='reset_password'),
    path('reset_password_done/', authviews.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', authviews.PasswordResetConfirmView.as_view(template_name="password_reset_comfirm.html"), name='password_reset_confirm'),
    path('reset_password_complete/', authviews.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name='password_reset_complete'),
]


