from django.contrib.auth.models import Group, User
from django.utils import timezone
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from bot.models import Forwarding, Tagger, TagForwarding
from bot.serializers import GroupSerializer, UserSerializer, ForwardingSerializer, TaggerSerializer, \
    TagForwardingSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class ForwardingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Forwarding.objects.all()
    serializer_class = ForwardingSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaggerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Tagger.objects.all()
    serializer_class = TaggerSerializer
    permission_classes = [permissions.IsAuthenticated]


class TagForwardingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = TagForwarding.objects.all()
    serializer_class = TagForwardingSerializer
    permission_classes = [permissions.IsAuthenticated]