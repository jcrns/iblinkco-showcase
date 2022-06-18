from django.shortcuts import render
from .models import BlogPost

# Homepage function
def home(request):
    return render(request, 'blog/blog.html', { 'posts': BlogPost.objects.all(), "nav_black_link" : True})