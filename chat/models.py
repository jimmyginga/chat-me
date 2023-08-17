from django.db import models
from authentication.models import User

class Chat(models.Model):
    users = models.ManyToManyField(User)
