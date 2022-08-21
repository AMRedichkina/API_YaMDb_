from django.db import models
from django.contrib.auth.models import AbstractUser

from .utils import role_choices


class User(AbstractUser):
    """
    Расширенная модель пользователя. Помимо основны предустановленных полей
    включает в себя поля bio (Биография) и role (роль на сайте), - варианты
    даны utils/role_choices.
    """

    role = models.CharField(
        choices=role_choices.ROLES,
        max_length=role_choices.max_length,
        default=role_choices.ROLES[0][0],
    )
    bio = models.TextField(
        blank=True,
    )
    email = models.EmailField(
        blank=False,
        max_length=150,
    )
    username = models.CharField(
        max_length=150,
        blank=False,
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
        null=True
    )
    last_name = models.CharField(
        max_length=150,
        null=True
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.is_superuser or self.role == role_choices.ROLES[2][0]

    @property
    def is_moderator(self):
        return self.role == role_choices.ROLES[1][0]


class EmailVerification(models.Model):
    """
    Модель для верификации почты новых пользователей. Хранит два значения:
    username (имя пользователя) и confirmation_code (4-значный код,
    отправляемый на почту новым пользователям).
    """

    username = models.CharField(
        max_length=20,
        null=True,
    )
    confirmation_code = models.CharField(
        max_length=4,
        null=True,
    )
