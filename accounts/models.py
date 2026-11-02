from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfile(models.Model):
    ROLE_USER = 'user'
    ROLE_MANAGER = 'manager'

    ROLE_CHOICES = [
        (ROLE_USER, 'Пользователь'),
        (ROLE_MANAGER, 'Менеджер'),
    ]

    class Meta:
        verbose_name = 'Профиль пользователя'  # Для одной штуки (в меню)
        verbose_name_plural = 'Профили пользователей'  # Для списка (в заголовке таблицы)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'  # <-- ЭТОГО НЕ ХВАТАЛО, чтобы убрать слово USER
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_USER,
        verbose_name='Роль'
    )

    is_blocked = models.BooleanField(
        default=False,
        verbose_name='Заблокирован'
    )

    def __str__(self):
        # Используем human-readable название роли вместо ключа ('user' -> 'Пользователь')
        role_display = dict(self.ROLE_CHOICES).get(self.role, self.role)
        return f"{self.user.username} ({role_display})"
