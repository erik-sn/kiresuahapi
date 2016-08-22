import json
import re
import requests

from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.serialzers import UserSerializer, GroupSerializer, ToDoSerializer, MarkupSerializer, \
    PortfolioMessageSerializer, EntrySerializer, TagSerializer
from api.models import ToDo, Markup, PortfolioMessage, Entry, Tag
from kiresuahapi.settings import GITHUB_MARKUP_CLIENT_SECRET as client_secret
from kiresuahapi.settings import GITHUB_MARKUP_CLIENT_ID as client_id


def auth(request, code):
    raw_data = github_auth(client_id, client_secret, code)
    user_data = json.loads(raw_data.content.decode('utf-8'))
    login = user_data['login']
    id = user_data['id']
    try:
        user = User.objects.get(username=login)
    except:
        user = User.objects.create_user(username=login, id=id)
        user.save()
    return HttpResponse(raw_data, content_type="application/json")


class ToDoList(generics.ListCreateAPIView):
    """
    Method to handle requests with no pk specified:
        1. POST - insert an object
        2. GET - retrieve a list of objects
    """
    queryset = ToDo.objects.all()
    serializer_class = ToDoSerializer


class ToDoDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Method to handle requests with a pk specified:
        1. GET - one object
        2. PUT - Inserts/Updates another object
        3. DELETE - deletes one object
    """
    queryset = ToDo.objects.all()
    serializer_class = ToDoSerializer


class MarkupList(generics.ListCreateAPIView):
    """
    Method to handle requests with no pk specified:
        1. POST - insert an object
        2. GET - retrieve a list of objects
    """
    def get_queryset(self):
        return Markup.objects.all().filter(user=self.kwargs['id']).order_by('-created')
    serializer_class = MarkupSerializer


class MarkupDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Method to handle requests with a pk specified:
        1. GET - one object
        2. PUT - Inserts/Updates another object
        3. DELETE - deletes one object
    """
    queryset = Markup.objects.all()
    serializer_class = MarkupSerializer


class EntryView(APIView):
    """
    Method to handle requests with no pk specified:
        1. POST - insert an object
        2. GET - retrieve a list of objects
    """
    def get_tag(self, name):
        try:
            return Tag.objects.get(name=name).id

        except:
            tag = Tag.objects.create(name=name)
            tag.save()
            return tag.id

    def get(self, request, format=None):
        data = Entry.objects.all()
        serializer = EntrySerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        data['tags'] = [self.get_tag(tag) for tag in data['tags']]
        serializer = EntrySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        data = request.data
        data['tags'] = [self.get_tag(tag) for tag in data['tags']]
        entry = Entry.objects.get(id=data['id'])
        serializer = EntrySerializer(entry, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        entry = Entry.objects.get(id=request.data['id'])
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EntryDetail(APIView):
    """
    Method to handle requests with a pk specified:
        1. GET - one object
        2. PUT - Inserts/Updates another object
        3. DELETE - deletes one object
    """
    def put(self, request, format=None):
        data = request.data
        data['tags'] = [self.get_tag(tag) for tag in data['tags']]
        serializer = EntrySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagList(APIView):
    """
    Method to handle requests with no pk specified:
        1. POST - insert an object
        2. GET - retrieve a list of objects
    """
    def get(self, request, format=None):
        data = Tag.objects.all()
        serializer = TagSerializer(data, many=True)
        return Response(serializer.data)


class PortFolioMessageList(generics.ListCreateAPIView):
    """
    Method to handle requests with no pk specified:
        1. POST - insert an object
        2. GET - retrieve a list of objects
    """
    queryset = PortfolioMessage.objects.all()
    serializer_class = PortfolioMessageSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


def github_auth(id, secret, code):
    """
    Part of the Github OAuth workflow - a code is generated by github and sent to the client,
    the client then sends that code here. It is combined with applications pecific codes and
    then sent to github to retrieve an access token. Then that access token is used to retrieve
    data about the user through the github API. The API data is then returned as JSON back to the
    client.
    :param id: client_id specific to an application
    :param secret: client_secret specific to an application
    :param code: temporary code related to a specific user from github
    :return: json data on user's api
    """
    try:
        auth_response = requests.post(
            'https://github.com/login/oauth/access_token',
            data=json.dumps({
                'client_id': id,
                'client_secret': secret,
                'code': code
            }),
            headers={'content-type': 'application/json'}
        ).content.decode('utf-8')
        token = re.search(r'access_token=([a-zA-Z0-9]+)', auth_response).group(1)
    except:
        return 'could not retrieve user data'
    return requests.get('https://api.github.com/user?access_token={}'.format(token))
