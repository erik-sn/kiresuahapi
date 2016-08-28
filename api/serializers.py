from django.contrib.auth.models import User, Group
from api.models import ToDo, Markup, PortfolioMessage, Entry, Tag
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'groups')


class GroupSerializer(serializers.ModelSerializer):
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
    owner = UserSerializer(many=False, read_only=True, context={'request': None})

    class Meta:
        model = Entry
        depth = 1
        fields = ('id', 'owner', 'created', 'modified', 'title', 'description', 'content', 'tags')


class EntryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ('id', 'owner', 'created', 'modified', 'title', 'description', 'content', 'tags')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'created', 'modified', 'name')


class PortfolioMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioMessage
        fields = ('name', 'email', 'phoneNumber', 'message', 'created', 'modified')
