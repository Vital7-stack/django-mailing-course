from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Recipient(models.Model):
    """Получатель рассылки (клиент)"""
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='Ф. И. О.')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Message(models.Model):
    """Шаблон письма"""
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """Рассылка"""
    STATUS_CREATED = 'Создана'
    STATUS_RUNNING = 'Запущена'
    STATUS_COMPLETED = 'Завершена'

    STATUS_CHOICES = [
        (STATUS_CREATED, STATUS_CREATED),
        (STATUS_RUNNING, STATUS_RUNNING),
        (STATUS_COMPLETED, STATUS_COMPLETED),
    ]

    start_time = models.DateTimeField(verbose_name='Дата и время начала')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания')
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name='Статус'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name='Сообщение'
    )
    recipients = models.ManyToManyField(
        Recipient,
        verbose_name='Получатели'
    )

    # Новое поле: владелец рассылки
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Владелец'
    )

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    def update_status(self):
        """Пересчитывает статус по текущему времени и сохраняет его"""
        now = timezone.now()
        if now < self.start_time:
            new_status = self.STATUS_CREATED
        elif self.start_time <= now <= self.end_time:
            new_status = self.STATUS_RUNNING
        else:
            new_status = self.STATUS_COMPLETED

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

    def __str__(self):
        return f"Рассылка #{self.id} — {self.message.subject}"


class Attempt(models.Model):
    """Попытка отправки письма"""
    STATUS_SUCCESS = 'Успешно'
    STATUS_FAILED = 'Не успешно'

    STATUS_CHOICES = [
        (STATUS_SUCCESS, STATUS_SUCCESS),
        (STATUS_FAILED, STATUS_FAILED),
    ]

    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name='Время попытки')
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        verbose_name='Статус попытки'
    )
    server_response = models.TextField(blank=True, null=True, verbose_name='Ответ сервера')
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Рассылка'
    )

    class Meta:
        verbose_name = 'Попытка'
        verbose_name_plural = 'Попытки'

    def __str__(self):
        return f"Попытка #{self.id} для рассылки {self.mailing.id}"


