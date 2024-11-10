from django.shortcuts import render,HttpResponse
from django.contrib.auth.decorators import login_required
# Create your views here.

def home(request):
    return render(request,'index.html')
@login_required(login_url='login')
def welcome(request):
    return render(request, 'home.html')
def not_support(request):
    return render(request,'not_support.html')
