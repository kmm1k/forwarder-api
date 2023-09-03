from django.db import models


class Forwarding(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    deleted = models.DateTimeField(null=True)
    from_chat = models.CharField(max_length=1000, blank=False)
    to_chats = models.JSONField(blank=False)

    class Meta:
        ordering = ['created']
        app_label = ('bot')


class TagGroups(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(max_length=1000, blank=False)
    usernames = models.JSONField(blank=False)

    class Meta:
        ordering = ['created']
        app_label = ('bot')


class TagForwarding(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(max_length=1000, blank=False)
    to_chats = models.JSONField(blank=False)
    allowed_users = models.JSONField(blank=False)

    class Meta:
        ordering = ['created']
        app_label = ('bot')