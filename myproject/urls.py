from django.contrib import admin
from django.urls import include, path
from django.shortcuts import render

def home(request):
    return render(request, "polls/home.html")

urlpatterns = [
    path('', home),  # Ana səhifə
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
]

