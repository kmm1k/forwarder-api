from django.db import models


class Forwarding(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    deleted = models.DateTimeField(null=True)
    from_chat = models.CharField(max_length=100, blank=True, default='')
    to_chats = models.CharField(max_length=1000, blank=True, default='')

    class Meta:
        ordering = ['created']
        app_label = ('bot')


class TagGroups(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(max_length=100, blank=True, default='')
    usernames = models.CharField(max_length=1000, blank=True, default='')

    class Meta:
        ordering = ['created']
        app_label = ('bot')


class TagForwarding(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(max_length=100, blank=True, default='')
    to_chats = models.CharField(max_length=1000, blank=True, default='')

    class Meta:
        ordering = ['created']
        app_label = ('bot')