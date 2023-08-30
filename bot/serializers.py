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
    class Meta:
        model = Forwarding
        fields = ['id', 'from_chat', 'to_chats']


class TaggerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TagGroups
        fields = '__all__'


class TagForwardingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TagForwarding
        fields = '__all__'
