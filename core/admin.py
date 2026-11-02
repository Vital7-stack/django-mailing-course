from django.contrib import admin
from .models import Recipient, Message, Mailing, Attempt
from .forms import MailingForm  # <-- ВАЖНО: импортируем созданную форму

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'comment')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject',)

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'start_time', 'end_time', 'status')
    form = MailingForm  # <-- ВАЖНО: указываем нашу форму с валидацией

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'attempt_time', 'status', 'server_response')