from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    return HttpResponse("Salam, bu Polls tətbiqinin ana səhifəsidir.")
