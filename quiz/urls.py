from django.urls import path
from . import views

urlpatterns = [
    path('link', views.link, name='link'),
    path('sown', views.sown, name='sown'),
]
