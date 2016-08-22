from django.contrib.auth.models import User, Group
from api.models import ToDo, Markup, PortfolioMessage, Entry, Tag
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class ToDoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDo
        fields = ('title', 'description', 'created', 'modified')


class MarkupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Markup
        fields = ('id', 'title', 'description', 'text', 'created', 'user', 'modified')


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ('id', 'created', 'modified', 'title', 'description', 'content', 'tags')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'created', 'modified', 'name')


class PortfolioMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioMessage
        fields = ('name', 'email', 'phoneNumber', 'message', 'created', 'modified')
