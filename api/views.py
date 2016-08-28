import json
import re
import requests

from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from oauth2_provider.models import AccessToken

from api.serializers import UserSerializer, GroupSerializer, ToDoSerializer, MarkupSerializer, \
    PortfolioMessageSerializer, EntrySerializer, EntryWriteSerializer, TagSerializer
from api.models import ToDo, Markup, PortfolioMessage, Entry, Tag

from kiresuahapi.settings import SOCIAL_AUTH_GITHUB_KEY as github_id, SOCIAL_AUTH_GITHUB_SECRET as github_secret, PORT


def auth(request, code):
    try:
        github_token = github_auth(github_id, github_secret, code)
        django_auth = json.loads(convert_auth_token(github_id, github_secret, 'github', github_token).decode('utf-8'))
    except:
        return HttpResponse(json.dumps({'error': 'cannot authenticate the user through github'}),
                            status=400, content_type="application/json")
    try:
        user = User.objects.get(id=AccessToken.objects.get(token=django_auth['access_token']).user_id)
        django_auth['id'] = user.id
        django_auth['username'] = user.username
        django_auth['email'] = user.email
        django_auth['isAdmin'] = user.is_staff
    except:
        django_auth['id'] = None
        django_auth['username'] = None
        django_auth['email'] = None
        django_auth['isAdmin'] = False
    return HttpResponse(json.dumps(django_auth), content_type="application/json")


@csrf_exempt
def revoke(request):
    """
    Given an access token, revoke that token and all other tokens associated with the user
    :param request: HTTP request containing client_id and access_token
    :return: JSON data indicating success or failure
    """

    access_token = request.GET.get('access_token', None)
    client_id = request.GET.get('client_id', None)
    if client_id is not None and access_token is not None:
        url = 'http://localhost:{}/api/invalidate-sessions'.format(PORT)
        data = {'client_id': client_id}
        headers = {'Authorization': 'Bearer {}'.format(access_token)}
        requests.post(url, data=data, headers=headers)
        return HttpResponse(json.dumps({'message': 'User successfully logged out'}),
                        status=200, content_type="application/json")
    return HttpResponse(json.dumps({'error': 'client_id and access_token are required parameters'}),
                        status=400, content_type="application/json")


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
    Handling MSLT entries
    """
    # defining queryset is necessary for Django model permissions
    queryset = Entry.objects.none()

    def get_tag(self, name):
        """
        return the tag object given a tag name - if it does not exist then create it
        :param name: tag name
        :return: Tag object
        """
        try:
            return Tag.objects.get(name=name)
        except:
            tag = Tag.objects.create(name=name)
            tag.save()
            return tag

    def get(self, request, format=None):
        data = Entry.objects.all().order_by('-created')
        serializer = EntrySerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        if 'id' not in data or 'tags' not in data:
            return Response({'error': 'The put request is malformed - id is a required field'}, status=status.HTTP_400_BAD_REQUEST)
        # convert array of tag strings into tag id's
        data['tags'] = [self.get_tag(tag).id for tag in data['tags']]
        serializer = EntryWriteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        data = request.data
        if 'id' not in data or 'tags' not in data:
            return Response({'error': 'The put request is malformed - id is a required field'}, status=status.HTTP_400_BAD_REQUEST)
        # convert array of tag strings into tag id's
        data['tags'] = [self.get_tag(tag).id for tag in data['tags']] if 'tags' in data else []
        entry = Entry.objects.get(id=data['id'])
        serializer = EntryWriteSerializer(entry, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        entry = Entry.objects.get(id=request.data['id'])
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    the client then sends that code here. It is combined with application specific codes and
    then sent to github to retrieve an access token. Then that access token is used to retrieve
    data about the user through the github API. The API data is then returned as JSON back to the
    client.
    :param id: client_id specific to an application
    :param secret: client_secret specific to an application
    :param code: temporary code related to a specific user from github
    :return: json data on user's api
    """
    # try:
    auth_response = requests.post(
        'https://github.com/login/oauth/access_token',
        data=json.dumps({
            'client_id': id,
            'client_secret': secret,
            'code': code
        }),
        headers={'content-type': 'application/json'}
    ).content.decode('utf-8')
    print(auth_response)
    token = re.search(r'access_token=([a-zA-Z0-9]+)', auth_response)
    if token is None:
        raise PermissionError(auth_response)
    return token.group(1)


def convert_auth_token(id, secret, backend, token):
    url = 'http://localhost:{}/api/convert-token?grant_type={}&client_id={}&client_secret={}&backend={}&token={}'\
        .format(PORT, 'convert_token', id, secret, backend, token)
    return requests.post(url).content


def get_user_from_token(token):
    return User.objects.get(id=AccessToken.objects.get(token=token).user_id)