from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    id_notion = models.CharField(max_length=100, null=False, blank=True)
    USERNAME_FIELD = 'email'
    email = models.EmailField(unique=True)
    REQUIRED_FIELDS = []
