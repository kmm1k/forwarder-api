from django.contrib.auth.models import Group, User
from rest_framework import serializers
from bot.models import Forwarding, TagGroups, TagForwarding, ChatsWithBot


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class ForwardingSerializer(serializers.HyperlinkedModelSerializer):
    to_chats = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Forwarding
        fields = ['id', 'from_chat', 'to_chats']


class TagGroupSerializer(serializers.HyperlinkedModelSerializer):
    usernames = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = TagGroups
        fields = ['id', 'tag', 'usernames']


class TagForwardingSerializer(serializers.HyperlinkedModelSerializer):
    to_chats = serializers.ListField(child=serializers.CharField())
    allowed_users = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = TagForwarding
        fields = ['id', 'tag', 'to_chats', 'allowed_users']


class ChatsWithBotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChatsWithBot
        fields = ['id', 'chat_id', 'name']
