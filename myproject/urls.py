from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Salam, Django Layihən işlədi! 😊</h1><p>Polls səhifəsinə keçmək üçün <a href='/polls/'>buraya kliklə</a>.</p>")

urlpatterns = [
    path('', home),  # Ana səhifə
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
]

