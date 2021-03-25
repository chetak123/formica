from django.shortcuts import render, redirect
from django.http import JsonResponse
# Create your views here.
from .serializer import TaskSerializer
from .models import Task
from rest_framework.decorators import api_view
from rest_framework.response import Response 
import requests
import environ 
from dotenv import load_dotenv
import os
load_dotenv()


redirect_url_discord = "https://discord.com/api/oauth2/authorize?client_id=728306573696303135&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Foauth2%2Flogin%2Fredirect%2F&response_type=code&scope=identify"
@api_view(["GET"])
def index(request):
    print(os.getenv("CLIENT_ID"))
    api_urls = {
        "List":"/list/",
        "Detail View":"/list-detail/<str:pk>/",
        "Create":"/list-create/",
        "Update":"/list-update/<str:pk>/",
        "Delete":"/list-delete/<str:pk>/"
    }
    return Response(api_urls)


def discord_login(request): 
    return redirect(redirect_url_discord)

def discord_login_redirect(request):
    code = request.GET.get('code')
    print(code)
    credentials = exchange_code(code)
    return JsonResponse(credentials)

def exchange_code(code):
    data = {
        "client_id":os.getenv("CLIENT_ID"),
        "client_secret":os.getenv("CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:8000/oauth2/login/redirect/", 
        "scope": "identify"
    }
    headers = {
        "Content-type": "application/x-www-form-urlencoded"
    }
    response = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    #print(response.json())
    credentials = response.json()
    access_token = credentials['access_token']
    response = requests.get("https://discord.com/api/v6/users/@me", headers={
        'Authorization': 'Bearer %s' % access_token
    })
    user = response.json()
    return user

@api_view(["GET"])
def tasklist(request):
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def taskdetail(request, pk):
    task = Task.objects.get(id=pk)
    serializer = TaskSerializer(task, many=False)
    return Response(serializer.data)


@api_view(["POST"])
def listcreate(request):
    serializer = TaskSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()

    return(serializer.data)

@api_view(["POST"])
def listupdate(request, pk):
    task = Task.objects.get(id=pk)
    serializer = TaskSerializer(instance=task, data=request.data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(["DELETE", "GET"])
def listdelete(request, pk): 
    task = Task.objects.get(id=pk)
    task.delete()

    return Response("Succesfully Deleted")