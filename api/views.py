import requests

from django.contrib.auth.models import User, Group
from rest_framework import viewsets, generics
from rest_framework.decorators import api_view

from api.models import Article, Tag
from api.serializers import GroupSerializer, ArticleSerializer

from rest_framework.response import Response

from core.settings import SOCIAL_AUTH_GITHUB_KEY, SOCIAL_AUTH_GITHUB_SECRET, CLIENT_ID, CLIENT_SECRET
from api.serializers import UserSerializer
from api.oauth import generate_github_access_token, convert_to_auth_token, get_user_from_token


@api_view(['POST'])
def authenticate(request, code):
    github_token = generate_github_access_token(SOCIAL_AUTH_GITHUB_KEY, SOCIAL_AUTH_GITHUB_SECRET, code)
    django_auth_token = convert_to_auth_token(CLIENT_ID, CLIENT_SECRET, 'github', github_token)
    user = get_user_from_token(django_auth_token)
    return Response({'token': django_auth_token, 'user': UserSerializer(user).data}, status=200)


@api_view(['POST'])
def revoke_access_token(request, access_token):
    """
    Given an access token, revoke that token and all other tokens associated with the user
    :param request: HTTP request containing client_id and access_token
    :return: JSON data indicating success or failure
    """
    url = 'http://localhost:8000/api/auth/invalidate-sessions/'
    data = {
        'client_id': CLIENT_ID,
    }
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    requests.post(url, data=data, headers=headers)
    return Response({'message': 'User successfully logged out'}, status=200)


@api_view(['POST'])
def refresh_access_token(request, refresh_token):
    """
    Given an access token, revoke that token and all other tokens associated with the user
    :param request: HTTP request containing client_id and access_token
    :return: JSON data indicating success or failure
    """
    url = 'http://localhost:8000/api/auth/token/'
    params = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
    }
    response = requests.post(url, params=params)
    response_dict = response.json()
    if response.status_code == 401:
        return Response(response_dict, status=401)
    user = get_user_from_token(response_dict)
    return Response({'token': response_dict, 'user': UserSerializer(user).data}, status=200)


class ArticleView(generics.ListCreateAPIView, generics.UpdateAPIView):
    queryset = Article.objects.all().order_by('-created')
    serializer_class = ArticleSerializer

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

    # def post(self, request, format=None):
    #     data = request.data
    #     if 'id' not in data or 'tags' not in data:
    #         return Response({'error': 'The put request is malformed - id is a required field'}, status=status.HTTP_400_BAD_REQUEST)
    #     # convert array of tag strings into tag id's
    #     data['tags'] = [self.get_tag(tag).id for tag in data['tags']]
    #     serializer = EntryWriteSerializer(data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request, format=None):
    #     data = request.data
    #     if 'id' not in data or 'tags' not in data:
    #         return Response({'error': 'The put request is malformed - id is a required field'}, status=status.HTTP_400_BAD_REQUEST)
    #     # convert array of tag strings into tag id's
    #     data['tags'] = [self.get_tag(tag).id for tag in data['tags']] if 'tags' in data else []
    #     entry = Entry.objects.get(id=data['id'])
    #     serializer = EntryWriteSerializer(entry, data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

