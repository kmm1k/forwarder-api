from django.contrib.auth.models import Group, User
from rest_framework import serializers
from bot.models import Forwarding, TagGroups, TagForwarding


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class ForwardingSerializer(serializers.HyperlinkedModelSerializer):
    from_chat = serializers.ListField(child=serializers.CharField())
    to_chats = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Forwarding
        fields = ['id', 'from_chat', 'to_chats']


class TagGroupSerializer(serializers.HyperlinkedModelSerializer):
    tag = serializers.ListField(child=serializers.CharField())
    usernames = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = TagGroups
        fields = ['id', 'tag', 'usernames']


class TagForwardingSerializer(serializers.HyperlinkedModelSerializer):
    tag = serializers.ListField(child=serializers.CharField())
    to_chats = serializers.ListField(child=serializers.CharField())
    allowed_users = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = TagForwarding
        fields = ['id', 'tag', 'to_chats', 'allowed_users']
