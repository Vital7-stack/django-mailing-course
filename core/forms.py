from django import forms
from .models import Mailing
from django.utils import timezone
from django.conf import settings

class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'recipients']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if not start_time or not end_time:
            return cleaned_data

        # Защита от ошибки часовых поясов
        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time, timezone=settings.TIME_ZONE)
            cleaned_data['start_time'] = start_time

        if timezone.is_naive(end_time):
            end_time = timezone.make_aware(end_time, timezone=settings.TIME_ZONE)
            cleaned_data['end_time'] = end_time

        # Проверка 1: Дата начала не в прошлом
        if start_time < timezone.now():
            self.add_error('start_time', "Дата начала рассылки не может быть в прошлом.")

        # Проверка 2: Начало раньше конца
        if start_time >= end_time:
            self.add_error('end_time', "Дата начала должна быть строго раньше даты окончания.")

        return cleaned_data