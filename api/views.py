import requests
import re
from itertools import chain

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, AllowAny, IsAuthenticated

from api.models import Article, Tag
from api.serializers import GroupSerializer, ArticleSerializer, ArticleWriteSerializer, TagSerializer

from rest_framework.response import Response

from core.settings import SOCIAL_AUTH_GITHUB_KEY, SOCIAL_AUTH_GITHUB_SECRET, CLIENT_ID, CLIENT_SECRET
from api.serializers import UserSerializer
from api.oauth import generate_github_access_token, convert_to_auth_token, get_user_from_token


@api_view(['POST'])
@permission_classes((AllowAny, ))
def authenticate(request, code):
    github_token = generate_github_access_token(SOCIAL_AUTH_GITHUB_KEY, SOCIAL_AUTH_GITHUB_SECRET, code)
    django_auth_token = convert_to_auth_token(CLIENT_ID, CLIENT_SECRET, 'github', github_token)
    user = get_user_from_token(django_auth_token)
    return Response({'token': django_auth_token, 'user': UserSerializer(user).data}, status=200)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def revoke_access_token(request, access_token):
    """
    Given an access token, revoke that token and all other tokens associated with the user
    :param request: HTTP request containing client_id and access_token
    :return: JSON data indicating success or failure
    """
    url = 'https://devsandbox.io/api/auth/invalidate-sessions/'
    data = {
        'client_id': CLIENT_ID,
    }
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    requests.post(url, data=data, headers=headers)
    return Response({'message': 'User successfully logged out'}, status=200)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def refresh_access_token(request, refresh_token):
    """
    Given an access token, revoke that token and all other tokens associated with the user
    :param request: HTTP request containing client_id and access_token
    :return: JSON data indicating success or failure
    """
    url = 'https://devsandbox.io/api/auth/token/'
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


@api_view(['GET'])
@permission_classes((AllowAny, ))
def search_articles_tags(request, search_term):
    articles = Article.objects.filter(Q(title__icontains=search_term) |
                                      Q(description__icontains=search_term) |
                                      Q(tags__name__icontains=search_term))
    article_serializer = ArticleSerializer(articles, many=True, context={'request': request})
    return Response(article_serializer.data, 200)


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.none()
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )
    lookup_field = 'url_title'

    def get_queryset(self):
        return Article.objects.all().order_by('-created')

    @staticmethod
    def clean_title(title):
        removed_spaces = title.lower().replace(' ', '-')
        url_title = re.sub('[^0-9a-zA-Z\-]+', '', removed_spaces)
        return url_title

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT']:
            return ArticleWriteSerializer
        return ArticleSerializer

    def get_tag(self, tag):
        """
        return the tag object given a tag name - if it does not exist then create it
        :param name: tag name
        :return: Tag object
        """
        try:
            return Tag.objects.get(name=tag['name'])
        except ObjectDoesNotExist:
            tag = Tag(name=tag['name'])
            tag.save()
            return tag

    def retrieve(self, request, url_title=None, **kwargs):
        try:
            article = Article.objects.get(url_title=url_title)
            return Response(self.get_serializer_class()(article, context={'request': request}).data)
        except ObjectDoesNotExist:
            return Response(status=404)

    def list(self, request, **kwargs):
        articles = Article.objects.order_by('-created')
        if not request.user.is_staff:
            articles = articles.filter(published=True)

        search_term = request.GET.get('search', None)
        if search_term:
            article_list = articles.filter(Q(title__icontains=search_term) |
                                           Q(description__icontains=search_term) |
                                           Q(tags__name__icontains=search_term))
            article_dict = {a.title: a for a in article_list}  # remove duplicates from tag join
            articles = list(article_dict.values())

        serializer = self.get_serializer_class()(articles, many=True, context={'request': request})
        return Response(serializer.data, 200)

    def create(self, request, **kwargs):
        data = request.data
        if 'tags' not in data:
            return Response({'detail': 'tags: This field is required'}, 400)
        if 'title' not in data:
            return Response({'detail': 'title: This field is required'}, 400)

        # convert array of tag strings into tag id's
        data['tags'] = [self.get_tag(tag).id for tag in data['tags']]
        data['url_title'] = self.clean_title(data['title'])
        serializer = self.get_serializer_class()(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, 201)
        return Response(serializer.errors, status=400)

    def update(self, request, id=None, **kwargs):
        data = request.data
        if 'tags' not in data:
            return Response({'detail': 'tags: This field is required'}, 400)
        if 'title' not in data:
            return Response({'detail': 'title: This field is required'}, 400)

        # convert array of tag strings into tag id's
        data['tags'] = [self.get_tag(tag).id for tag in data['tags']]
        data['url_title'] = self.clean_title(data['title'])
        article = Article.objects.get(id=id)
        serializer = self.get_serializer_class()(article, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('-created')
    serializer_class = TagSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )


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

