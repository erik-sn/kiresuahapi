from django.contrib.auth.models import User, Group
from api.models import Article, Tag
from rest_framework import serializers
from rest_framework.reverse import reverse


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff', 'is_superuser', 'is_active')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name', 'test')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name')


class ArticleSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, article):
        request = self.context['request']
        return reverse(
            viewname='article_title',
            args=[article.id],
            request=request)

    class Meta:
        model = Article
        depth = 1
        fields = ('id', 'created', 'modified', 'title', 'text', 'url_title',
                  'description', 'tags', 'url')


class ArticleWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ('id', 'owner', 'title', 'text', 'url_title', 'description',
                  'tags')
