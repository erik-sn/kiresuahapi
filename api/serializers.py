from django.contrib.auth.models import User, Group
from api.models import Article, Tag
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff', 'is_superuser', 'is_active')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class ArticleSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False, read_only=True, context={'request': None})
    tags = TagSerializer(many=True)

    class Meta:
        model = Article
        depth = 1
        fields = ('id', 'owner', 'created', 'modified', 'title', 'description', 'content', 'tags')


class ArticleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('id', 'owner', 'created', 'modified', 'title', 'description', 'content', 'tags')

