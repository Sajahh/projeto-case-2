from django.db import models
from auth_class.models import CustomUser as User
import uuid
from datetime import timedelta
from django.utils import timezone


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_valid(self):
        # Verifica se o token foi criado nas últimas 24 horas e não foi utilizado
        return not self.used and (timezone.now() - self.created_at) < timedelta(hours=24)
