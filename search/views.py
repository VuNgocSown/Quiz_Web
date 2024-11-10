from django.shortcuts import render
from .models import Video
from .forms import SearchForm

def search(request):
    query = request.GET.get('query')
    videos = Video.objects.filter(title__icontains=query) if query else []
    form = SearchForm()
    return render(request, 'search_results.html', {'form': form, 'videos': videos})


