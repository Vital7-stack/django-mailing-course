from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Если пользователь только что создан — сразу делаем ему профиль
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Если пользователь старый, но профиля вдруг нет (защита от прошлых ошибок)
        try:
            instance.profile  # Пытаемся обратиться к профилю
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Просто сохраняем профиль, если он есть
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        pass